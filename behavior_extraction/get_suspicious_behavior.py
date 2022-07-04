
import sys
from tools import nlp_tool
from tools.nlp_tool import get_lemmatize_data
from behavior_extraction.conf import cmp, deal_strings, get_file_path, get_items, get_name_of_method, get_split_names_from_node, in_filters_words, set_args
from tools import basic_tool
import os
import multiprocessing as mp
from behavior_extraction.read_graph_file import read_dot
g_process_size = 30
g_lock = None
TIME_OUT_FILE = 'time_out_api_sequence.txt'
#[png_name, [android_id, text_name, text_content], embedded_texts, AI_predic, parent_layout]

def read_layout_string(strings):
    result = []
    for item in strings:
        if item[2] != '':
            result.append(item[2])
    return result

def get_widget_string(strings):
    tmp_result = []
    widget_id = ''
    if strings[0][0] != []: # png_name
        tmp_result +=strings[0][0]
    if strings[0][1][2] != '': # text_content
        tmp_result.append(strings[0][1][2])
    if strings[0][3] != []: # AI_predic
        tmp_result +=strings[0][3]  
    if strings[0][2] != []: # embedded_texts
        tmp_result +=strings[0][2]
    if strings[0][4] != []: # parent_layout
        tmp_result +=read_layout_string(strings[0][4])
    return tmp_result, widget_id

def get_node_items(source, result=[]):
    for item in source:
        if isinstance(item, list):
            get_node_items(item, result)
        else:
            result.append(item)
            break
    return result

def analyze_path(path_list):
    for path in path_list:
        paths = get_node_items(path, [])
        for i, node in enumerate(paths):
            if 'latitu' in node.lower() or 'camera' in node.lower():
                print()
    print()
        

def get_ui_semantics(semantics, string_dic, semantics_dic, filters_words):
    tag = ''
    widget = semantics['widget']
    results = []
    if semantics['xml'] == []: 
        tag = 'app' #means the function node has no xmls, extract all strings
        if tag in semantics_dic:
            return semantics_dic[tag]
    for widget_item in widget:
        widget_id = widget_item[0]
        for strings in widget_item[1]: 
            # print("strings: ",strings)
            tmp_result, tmp_widget_id = get_widget_string(strings)
            tmp_widget_xml = strings[1][0]
            widget_sig = tmp_widget_xml+'.'+tmp_widget_id
            # if widget_sig == 'fragment_morining_athkar.xml.ShareBtn':
            #     print()
            if tmp_widget_id == '':
                keywords_result = deal_strings(tmp_result, string_dic, filters_words)
                results += keywords_result
            else:
                if widget_sig in semantics_dic and widget_sig!='':
                    keywords_result = semantics_dic[widget_sig]
                    results += keywords_result
                    continue
                keywords_result = deal_strings(tmp_result, string_dic, filters_words)
                results += keywords_result
                semantics_dic[widget_sig] = keywords_result
    results = list(set(results))
    semantics_dic[tag] = results
    return results

def contains_important_apis(args, android_path_list, app_semantics):
    api_to_name_dic = basic_tool.read_json(basic_tool.readContentText(args.api_to_name_dic_path))
    name_to_api_dic = basic_tool.read_json(basic_tool.readContentText(args.name_to_api_dic_path))
    semantics_dic, string_dic, attention_ui_match, attention_ui_unmatch = {}, {}, {}, {}
    suspicious_behavior, important_apis, widget_list, path_list = [], [], [], []
    tag = ''
    for app_semantic in app_semantics:
        widget_list.append(['', [app_semantic]])
    app_semantics_dic = {'widget':widget_list, 'xml':[]}
    if not os.path.exists(args.app_result_dir):
        os.makedirs(args.app_result_dir)
    for i, path in enumerate(android_path_list):
        tmp_suspicious_behavior = []
        path = get_items(path, [])
        important_apis.append('----------------------------')
        suspicious_path = False
        for j, node in enumerate(path):
            suspicious = False
            semantics = list(node.values())[0]
            node = list(node.keys())[0]
            if semantics['xml'] == []:
                tag = 'app'
            else:
                tag = semantics['xml'][0]
            if len(path) > 10000 and tag == 'app':
                continue
            split_names = get_split_names_from_node(node, api_to_name_dic, name_to_api_dic)
            api_lem_items, api_lem_tags = get_lemmatize_data(split_names)
            contains, api_keywords = in_filters_words(api_lem_items, args.attention_library)
            if not contains:
                continue
            important_apis.append(str(node+'    \t'+str(api_keywords)))
            ui_keywords = get_ui_semantics(semantics, string_dic, semantics_dic, args.attention_library)
            # add ui keyword
            app_ui_keywords = get_ui_semantics(app_semantics_dic, string_dic, semantics_dic, args.attention_library)
            tmp_words = ''
            words = cmp(api_keywords, ui_keywords)
            words_ui = cmp(api_keywords, app_ui_keywords)
            if len(words) > 0:
                suspicious = True
                suspicious_path = True
            tmp_words = tag+':'+str(words)+'\t'+'app'+str(words_ui)
            if suspicious:
                tmp_words = tmp_words+'\t'+'ui-unmatch'
            tmp_suspicious_behavior.append(node+'\t'+tmp_words)
        if suspicious_path:
            suspicious_behavior += tmp_suspicious_behavior
            suspicious_behavior.append('--------------------------------')
    basic_tool.writeContentLists(os.path.join(args.app_result_dir,"{}_important_path.txt".format(args.app_name)), important_apis)
    basic_tool.writeContentLists(os.path.join(args.app_result_dir,"{}_suspicious_behaviors.txt".format(args.app_name)), suspicious_behavior)



def get_suspicious_behavior(args):
    # get_attention_words 
    name_apk = os.path.split(args.apk_file)[1]
    app_name = os.path.splitext(name_apk)[0]
    dot_path, apk_json_path, text_result_path = get_file_path(result_dir, name_apk, app_name)
    output = os.popen("aapt dump badging %s" % args.apk_file).read()
    try:
        packages = output.split("package: name='")[-1].split("'")[0].strip()
    except Exception as e:
        packages = ''
    contents = basic_tool.readContentLists(dot_path)
    graph = read_dot.construct_graph_without_dummyMainMethod(contents, dot_path, packages)
    ui_info = basic_tool.read_json(basic_tool.readContentText(apk_json_path))
    widget_info = basic_tool.load_pkl_data(text_result_path)
    graph.set_semantics(widget_info)
    app_semantics = graph.semantics
    path_list, android_path_list = graph.get_paths(ui_info, widget_info, args.third_libs)
    if path_list==[] and android_path_list==[]:
        return False, dot_path
    # ui match an ui unmatch
    contains_important_apis(args, android_path_list, app_semantics)
    
    # ui match save to attention words
    # ui unmatch save to suspicious behavior 
    return True, dot_path

def write_timeout_results(result):
    success, dot_path = result
    if success:
        return
    g_lock.acquire()
    with open(TIME_OUT_FILE, mode="a") as fo:
        print("{}".format(dot_path), file=fo)
    g_lock.release()
    sys.stdout.flush()     


def main(apps, result_dir):
    # apps = basic_tool.getAllFiles(apk_dir, [], '.apk')
    filters_behaviors_dir = os.path.join(result_dir, 'filters_behaviors_dir')
    attention_file = os.path.join(result_dir, 'attention_library.txt')
    method_dic_path = os.path.join(result_dir, 'source_words/database/api_list_dir/api_apiname.json')
    third_libs_file = os.path.join(result_dir, 'liteRadar_3rdLibs')
    third_libs = basic_tool.readContentLists_withoutbr(third_libs_file)
    result_word_json = os.path.join(result_dir, 'source_words/database/api_list_dir/apiname_api.json')
    attention_words = basic_tool.readContentLists_withoutbr(attention_file)
    
    to_handle_apps = []
    for i, app in enumerate(apps):
        app_name = os.path.splitext(os.path.basename(app))[0]
        name_apk = os.path.split(app)[1]
        time_out = []
        if os.path.exists(TIME_OUT_FILE):
            time_out = basic_tool.readContentLists_withoutbr(TIME_OUT_FILE)
        suspicious_behavior = os.path.join(filters_behaviors_dir, app_name,"{}_suspicious_behaviors.txt".format(app_name))
        if os.path.exists(suspicious_behavior):
            continue
        dot_path, apk_json_path, text_result_path = get_file_path(result_dir, name_apk, app_name)
        if dot_path == '':
            continue 
        elif dot_path in time_out:
            continue
        to_handle_apps.append(app)
    
    p = mp.Pool(g_process_size)
    global g_lock
    g_lock = mp.Lock()
    for i, app in enumerate(to_handle_apps):
        print(str(i), str(len(to_handle_apps)), app)
        name_apk = os.path.split(app)[1]
        app_name = os.path.splitext(name_apk)[0]
        suspicious_behavior_path = os.path.join(filters_behaviors_dir, app_name,"{}_suspicious_behaviors.txt".format(app_name))
        parser = set_args()
        args = [
            '--filters_behaviors_dir', filters_behaviors_dir,
            '--third_libs', third_libs,
            '--attention_library', attention_words,
            '--api_to_name_dic_path', method_dic_path,
            '--name_to_api_dic_path', result_word_json,
            '-a', app, 
            '--app_result_dir', os.path.join(filters_behaviors_dir, app_name),
            '--suspicious_behavior_path', suspicious_behavior_path,
            '--app_name', app_name,
        ]
        args, unknown = parser.parse_known_args(args)
        # result = get_suspicious_behavior(args)
        # write_timeout_results(result)
        p.apply_async(func=get_suspicious_behavior, 
                        args=(args,),
                        callback=write_timeout_results)    
    p.close()
    p.join()
    
if __name__ == '__main__':
    apk_dirs = ['/home/data/yuec/DeepIntent/data/example/benign', '/home/data/yuec/DeepIntent/data/example/malicious'] # finish
    result_dir = 'data'
    apps = []
    for apk_dir in apk_dirs:
        apps += basic_tool.getAllFiles(apk_dir, [], '.apk')
    main(apps, result_dir)