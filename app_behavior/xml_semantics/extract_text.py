# -*- coding: UTF-8 -*-

import os
from tools import basic_tool
import cv2
import numpy as np
from keras.models import load_model
from app_behavior.xml_semantics.translate_text import check_default_language

from app_behavior.xml_semantics.conf import check_conf, ExtractionConf
from app_behavior.xml_semantics.tools import ProcessPrinter,image_decompress
from app_behavior.xml_semantics.load_data import load_data
from app_behavior.xml_semantics.handle_layout_text import handle_layout_text
from app_behavior.xml_semantics.handle_embedded_text import extract_drawable_image, load_east_model, extract_embedded_text
from app_behavior.xml_semantics.handle_resource_text import handle_resource_text
from app_behavior.xml_semantics.translate_text import translate_any_to_english
from app_behavior.xml_semantics.conf import ExtractionConfArgumentParser


labels = ['location-point'
,'home'
,'video'
,'contact'
,'calendar'
,'microphone'
,'sms'
,'heart'
,'storage-directory'
,'arrow'
,'mail'
,'camera'
,'recording'
,'gallery'
,'share-up'
,'trash'
,'storage-download-upload'
,'search'
,'star'
,'phone'
,'setting'
,'play'
,'storage-disk'
,'share-network'
,'arrow-1'
,'plus'
,'location-marker']

thresholds = [0.99
,0.9
,0.99
,0.95
,0.9995
,0.999
,0.99
,0.9
,0.99
,0.95
,0.9
,0.99
,0.9
,0.99
,0.9
,0.9
,0.99
,0.9
,0.9
,0.993
,0.9
,0.9
,0.99
,0.9
,0.9
,0.9
,0.99]


def extract_contextual_texts(data, drawable_images, path_app, path_east,
                             search_range='parent',
                             ocr_size=(320, 320), ocr_padding=0.1, enable_ocr_cache=True,
                             is_translate=True, enable_translate_cache=True,
                             log_level=0):
    # extract layout texts
    print('extracting layout texts')
    layout_texts = extract_layout_texts(data, path_app, search_range, log_level)

    # extract embedded texts
    print('extracting embedded texts')
    app2lang = get_app2lang(data, layout_texts)
    east_model = load_east_model(path_east)
    embedded_texts = extract_embedded_texts(data, drawable_images, app2lang, east_model,
                                            ocr_size, ocr_padding, enable_ocr_cache, log_level)

    # translate layout texts and embedded texts
    # if is_translate:
    #     print('translating')
    #     layout_texts = translate_texts(data, layout_texts, enable_translate_cache, log_level)
    #     embedded_texts = translate_texts(data, embedded_texts, enable_translate_cache, log_level)

    # extract resource texts
    print('extracting resource texts')
    resource_texts = extract_resource_texts(data, log_level)

    # merge extracted texts
    assert len(data) == len(layout_texts) == len(embedded_texts) == len(resource_texts)
    results = [[resource_texts[i] , embedded_texts[i], layout_texts[i]] for i in range(len(data))]
    return results


def extract_widgets(path_app, app_name, output, log_level=0):
    """Extract drawable images for each (app, img, layout) tuple.

    :param data_pa:
        List, each row contains (app, img, layout, permissions) tuple.
    :param path_app:
        String, the path of the decoded Apps.
    :param log_level:
        Int, 0 to 2, silent, or normal (process bar), or verbose mode.

    :return:
        List, compressed images.
    """
    # xml_dict = {}
    # dirs = os.listdir(path_app)
    # for app_name in dirs:
    # xml_dict[app_name] = {}
        # if not ('99999999999' in app_name or '1311761931' in app_name or '5cb8e0edb' in app_name):
        #     continue
    json_1 = os.path.join(output, app_name+'.apk.json')
    json_2 = os.path.join(output, app_name+'.json')
    if not (os.path.exists(json_1) and os.path.exists(json_2)):
        return None, None
    dic_1 = basic_tool.read_json(basic_tool.readContentText(json_1))
    dic_2 = basic_tool.read_json(basic_tool.readContentText(json_2))
    widget_results = []
    for node in dic_1:
        if '|' not in node['name']:
            continue
        layout = node['name'].split('|')[-1].split(']')[0].split('layout_')[-1]+'.xml'

        # if layout not in xml_dict[app_name].keys():
        #     xml_dict[app_name][layout] = []

        views = node['views']
        for view in views:
            widget_id = view['name']
            if '|' in widget_id and 'widget' in widget_id and 'Layout' not in widget_id:   #('Image' in widget_id  or 'Text' in widget_id or 'Button' in widget_id):
                widget_id = widget_id.split('|')[1].split(']')[0]

                images = view['images']
                if len(images) > 0:
                    for image in images:
                        image_name = image.split('|')[-1].split('drawable_')[-1].split(']')[0]
                        if (app_name, image_name, widget_id, layout) not in widget_results:
                            widget_results.append((app_name, image_name, widget_id, layout))
                else:
                    image_name = ''
                    if (app_name, image_name, widget_id, layout) not in widget_results:
                        widget_results.append((app_name, image_name, widget_id, layout))

                    # xml_dict[app_name][layout].append((image_name))
            

    for node in dic_2:
        layout = node['name']
        tags = node['tags']
        for tag_item in tags:
            images = tag_item['imgs']
            for img in images:
                attribute = img['attribute']
                if attribute == 'background':
                    continue
                image_name = img['value'].split('/')[-1]
                if not tag_item['idName']:
                    widget_id = ''
                else:
                    widget_id = tag_item['idName'].split('/')[-1]

                if (app_name, image_name, widget_id, layout) not in widget_results:
                    widget_results.append((app_name, image_name, widget_id, layout))
    results = []
    log_helper = ProcessPrinter(len(widget_results) / 20, log_level)
    for app_name, img_name, widget_id, layout in widget_results:
        if img_name != '':
            result, result_path, result_traces = extract_drawable_image(app_name, img_name, path_app)
        else:
            result = None
        results.append(result)
        log_helper.update('[image]', app_name, img_name, layout, ':',
                          (result[0], result[1]) if result is not None else result)
    log_helper.finish()

    return results, widget_results  #, xml_dict


def extract_layout_texts(data_pa, path_app, search_range, log_level=0):
    results = []
    log_helper = ProcessPrinter(len(data_pa) / 20, log_level)
    for app_name, img_name, id, layout in data_pa:
        # result = handle_layout_text(app_name, img_name, layout, path_app, search_range)
        result = handle_layout_text(app_name, id, layout, path_app, search_range)
        results.append(result)
        log_helper.update('[layout]', app_name, img_name, layout, ':', result)
    log_helper.finish()

    return results


def get_app2lang(data_pa, layout_texts):
    

    # collect all the layout texts appeared in the app
    app_texts = {}  # app -> all the layout texts
    for i in range(len(data_pa)):
        app_name = data_pa[i][0]
        if app_name not in app_texts:
            app_texts[app_name] = []
        app_texts[app_name].extend(layout_texts[i])

    app2lang = {app_name: check_default_language(texts) for app_name, texts in app_texts.items()}
    return app2lang


def extract_embedded_texts(data_pa, drawable_images, app2lang, east_model,
                           ocr_size, ocr_padding, enable_cache=True, log_level=0):
    results = []
    log_helper = ProcessPrinter(len(data_pa) / 20, log_level)
    for i in range(len(data_pa)):
        app_name, img_name, id, layout = data_pa[i]
        if drawable_images[i] == None:
            result = []
        else:
            result = extract_embedded_text(app_name, img_name, drawable_images[i], east_model,
                                        app2lang[app_name], 'english',
                                        ocr_size, ocr_padding, enable_cache)
        results.append(result)
        log_helper.update('[embedded]', app_name, img_name, layout, ':', result)
    log_helper.finish()

    return results


def translate_texts(data_pa, texts, enable_cache=True, log_level=0):
    assert len(data_pa) == len(texts)

    results = []
    log_helper = ProcessPrinter(sum([len(t) for t in texts]) / 20, log_level)
    for i in range(len(data_pa)):
        app_name, img_name, id, layout = data_pa[i]
        translated = []
        for t in texts[i]:
            if len(t) == 2:
                r = translate_any_to_english(t[1], enable_cache)
                translated.append([t[0], r])
                log_helper.update('[translate]', app_name, img_name, layout, ':', t[1], '->', r)
            else:
                r = translate_any_to_english(t, enable_cache)
                translated.append([t, r])
                log_helper.update('[translate]', app_name, img_name, layout, ':', t, '->', r)
        results.append(translated)
    log_helper.finish()

    return results


def extract_resource_texts(data_pa, log_level=0):
    results = []
    log_helper = ProcessPrinter(len(data_pa) / 20, log_level)
    for app_name, img_name, id, layout in data_pa:
        if img_name != '':
            result = handle_resource_text(img_name)
        else:
            result = []
        results.append(result)
        log_helper.update('[res]', app_name, img_name, layout, ':', result)
    log_helper.finish()

    return results


def execute_with_conf(conf):
    apps = conf.path_apks
    to_handle_apps = []
    for i, app in enumerate(apps):
        app_name = os.path.splitext(os.path.basename(app))[0]
        result_file = os.path.join(conf.path_save, "results_" + app_name + ".txt")
        if os.path.exists(result_file):
            continue
        to_handle_apps.append(app)

    model = load_model(os.path.join(conf.path_result_root, 'final_resources_model.h5'))
    text_dic = {}
    for i, app in enumerate(to_handle_apps):
        app_name = os.path.splitext(os.path.basename(app))[0]
        print(str(i) , app_name)
        result_file = os.path.join(conf.path_save, "results_+" + app_name + ".txt")
        xml_string_path = os.path.join(conf.path_xmlstring, app_name + ".txt")
        if os.path.exists(result_file):
            continue
        # extract drawable images
        print('extracting drawable images')
        log_level = check_conf(conf.log_level, {0, 1, 2}, 0)

        #data_pa [app_name, img_name, android_id, layout_name]
        drawable_images, data_pa = extract_widgets(conf.path_app, app_name, conf.path_gator, conf.log_level)
        if data_pa==None:
            continue
        # extract texts, format: resource_texts, embedded_texts, layout_texts([id,text])
        print('extracting texts')
        search_range = check_conf(conf.layout_text_range, {'parent', 'total'}, 'parent')
        enable_ocr_cache = check_conf(conf.enable_ocr_cache, {True, False}, True)
        is_translate = check_conf(conf.enable_translate, {True, False}, True)
        enable_translate_cache = check_conf(conf.enable_translate_cache, {True, False}, True)
        texts = extract_contextual_texts(data_pa, drawable_images, conf.path_app, conf.path_east,
                                        search_range,
                                        (conf.ocr_width, conf.ocr_height), conf.ocr_padding, enable_ocr_cache,
                                        is_translate, enable_translate_cache,
                                        log_level)

        # merge and save the triple, <image, texts, permissions>
        print('finished and save')
        assert len(data_pa) == len(drawable_images) == len(texts)
        # img_data format: [(compressed_img), [[res_texts], [android_id], [embedded_texts], [AI_predict], [layout_texts]], xml_name]
        # text_data format: [[layout_texts], xml_name]
        # data = [[drawable_images[i]] + [texts[i]] + [data_pa[i][-1]] for i in range(len(data_pa))]
        # data = [[texts[i]] + [data_pa[i][-1]] for i in range(len(data_pa))]
        data = []
        for i in range(len(drawable_images)):
            widget_name = ''
            widget_content = ''
            for item in texts[i][2]:
                # print(item(0))
                # print(data_pa[i][2])
                if item[0] == data_pa[i][2]:
                    widget_name = item[1]
                    widget_content = item[2]
            texts[i].insert(1,[data_pa[i][2],widget_name,widget_content])   #android_id
            # print(texts[i])
            # embedded_texts = texts[i][1]
            # print(embedded_texts)
            if drawable_images[i] != None:
                image_mode, image_size, image = drawable_images[i]
                # print(image_size)
                image = image_decompress(image_mode, image_size, image)
            # img_show = image
            # print(image.shape)
                if len(np.array(image).shape) == 3 and np.array(image).shape[2] == 3:
                    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR).astype('float32')
                    # print(image.shape)
                    image = cv2.resize(image, (128,128), interpolation = cv2.INTER_AREA)
                    # print(image)
                    image = image / 255.0
                    image = np.array([image])

                    cnn_prediction = model.predict(image)	
                    predicted = cnn_prediction[0]
                    predicted_label = ''
                    
                    confidence_index = np.argmax(predicted)
                    confidence = predicted[confidence_index]        	    
                    
                    # if confidence >= thresholds[confidence_index]:
                    if confidence > 0.85:
                        predicted_label = labels[confidence_index]
                        # if len(embedded_texts) == 0:
                        #     img_show.save("imgs/" + str(i) + "_" + predicted_label + "_" + str(confidence) + ".png")
                        #     print("predicted_label: ",predicted_label)
                        texts[i].insert(3, [predicted_label])
                        # data.append([[drawable_images[i]], texts[i], [data_pa[i][-1]]])  
                    else:
                        texts[i].insert(3, [])
                else:
                    texts[i].insert(3, [])
            else:
                texts[i].insert(3, [])
            # img_data.append([[drawable_images[i]], texts[i], [data_pa[i][-1]]]) 
            data.append([texts[i], [data_pa[i][-1]]])   
            # data.append([texts[i], [data_pa[i][-1]]]) 

        for tmp in data:
            string_tmp = tmp[0][1][2]
            android_id = tmp[0][1][0]
            xml = tmp[1][0]
            if string_tmp!='':
                text_dic.setdefault(string_tmp, []).append({'xml':xml,'widget':android_id})
        basic_tool.mkdir(conf.path_save)
        fp = open(conf.path_save + "/results_" + app_name + ".txt",'w')
        for item in data:
            fp.write(str(item))
            fp.write('\n')
        fp.close()

        pkl_path = conf.path_save + "/results_" + app_name + ".result"
        # save_pkl_data(conf.path_save, data)
        basic_tool.save_pkl_data(pkl_path, data)
        
        basic_tool.mkdir(conf.path_xmlstring)
        basic_tool.write_json(text_dic, xml_string_path)


def main(apps, result_dir):
    args = [
    '--path_apks', apps,
    '--path_app',  os.path.join(result_dir, 'decode_dir'),
    '--path_east', os.path.join(result_dir, 'frozen_east_text_detection.pb'),
    '--path_save', os.path.join(result_dir, 'text_results'),
    '--path_gator', os.path.join(result_dir, 'output'),
    '--path_xmlstring', os.path.join(result_dir, 'strings', 'xml_strings'),
    '--path_result_root', result_dir,
    ]
    parser = ExtractionConfArgumentParser()
    args_conf = parser.parse(args)
    execute_with_conf(args_conf)

if __name__ == '__main__':
    #1) program analysis results, could be '.csv' or zipped '.csv', 
    #2) decoded apps, the program assume all the related apps are decoded in one folder,
    #3) pre-trained EAST model (could be download from BaiduYun), which is used in embedded text extraction.
    # /home/data/xiu/apks/BBL
    apk_dir = ''
    apps = []
    result_dir = ''
    args = [
    '--path_apks', apps,
    '--path_app',  os.path.join(result_dir, 'decode_dir'),
    '--path_east', os.path.join(result_dir, 'frozen_east_text_detection.pb'),
    '--path_save', os.path.join(result_dir, 'text_results'),
    '--path_gator', os.path.join(result_dir, 'output'),
    '--path_xmlstring', os.path.join(result_dir, 'strings', 'xml_strings'),
    ]
    main(apk_dir, result_dir)
