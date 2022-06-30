import os
import pickle
import sys
from tools import basic_tool, nlp_tool
from behavior_extraction.read_graph_file import read_dot
from behavior_extraction.conf import set_args
import multiprocessing as mp

g_process_size = 10
TIME_OUT_FILE = 'time_out_api_sequence.txt'

def get_file_path(result_dir, name_apk, app_name):
    dot_dir = os.path.join(result_dir, 'dot_output', app_name)
    dot_path = ''
    if os.path.exists(dot_dir):
        files = os.listdir(dot_dir)
        for f in files:
            if f.endswith('.dot'):
                dot_path = os.path.join(dot_dir, f)
                break
    apk_json_path = os.path.join(result_dir, 'output', name_apk+'.json')
    text_result_path = os.path.join(result_dir, 'text_results', 'results_{}.result'.format(app_name))
    if os.path.exists(dot_path) and os.path.exists(apk_json_path) and os.path.exists(text_result_path):
        return dot_path, apk_json_path, text_result_path
    else:
        return '', '', ''



def get_items(source, result=[]):
    for item in source:
        if isinstance(item, list):
            get_items(item, result)
        else:
            result.append({item: {'widget':source[1], 'xml':source[2]}})
            break
    return result



def in_filters_words(strings, filters_words):
    contains = False
    keywords = []
    for item in strings:
        if item in filters_words:
            contains = True
            keywords.append(item)
    return contains, keywords

def get_name_of_method(api):
    tmps = api.strip().split()
    clazz = tmps[0].replace('/','.')
    name = tmps[2]
    strings = ' '.join([clazz.split('.')[-1][:-1], name.split('(')[0]])
    # method, strings = map_method(api)
    split_names = nlp_tool.deal_words(strings)
    split_names = ' '.join(split_names)
    return split_names

# trans strings and return keywords
def deal_strings(strings, string_dic, filters_words):
    string_result = []
    for string in strings:
        if string not in string_dic:
            tmp_string = nlp_tool.split_string(string)  # long time
            api_lem_items, api_lem_tags = nlp_tool.get_lemmatize_data(tmp_string.split())
            contains, ui_keywords = in_filters_words(api_lem_items, filters_words)
            string_dic[string] = {'deal_string':tmp_string, 'keywords':ui_keywords}
            ui_keywords = string_dic[string]['keywords']
        else:
            ui_keywords = string_dic[string]['keywords']
        string_result += ui_keywords
    return string_result

'''
get widget string
'''
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

'''
tag: app, xml(node xml). widget id
'''
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
'''
cmp two keywords
'''
def cmp(api_keywords, ui_keywords):
    words = [word for word in api_keywords if word not in ui_keywords]
    return words

'''
save semantics_dic, string_dic
'''
# @func_set_timeout(time_limit)
def contains_important_apis(args, app_semantics, android_path_list):
    semantics_dic, string_dic, tmp_words_api, tmp_api_words, tmp_words_api_ui, tmp_api_words_ui = {}, {}, {}, {}, {}, {}
    important_apis, widget_list = [], []
    tag = ''
    for app_semantic in app_semantics:
        widget_list.append(['', [app_semantic]])
    app_semantics_dic = {'widget':widget_list, 'xml':[]}
    if not os.path.exists(args.app_result_dir):
        os.makedirs(args.app_result_dir)
    for i, path in enumerate(android_path_list):
        path = get_items(path, [])
        important_apis.append('----------------------------')
        for j, node in enumerate(path):
            semantics = list(node.values())[0]
            node = list(node.keys())[0]
            if semantics['xml'] == []:
                tag = 'app'
            else:
                tag = semantics['xml'][0]
            if len(path) > 10000 and tag == 'app':
                continue
            split_names = get_name_of_method(node)
            api_lem_items, api_lem_tags = nlp_tool.get_lemmatize_data(split_names.split())
            contains, api_keywords = in_filters_words(api_lem_items, args.filters_words)
            if  not contains:
                continue
            important_apis.append(str(node+'    \t'+str(api_keywords)))
            ui_keywords = get_ui_semantics(semantics, string_dic, semantics_dic, args.filters_words)
            # add ui keyword
            app_ui_keywords = get_ui_semantics(app_semantics_dic, string_dic, semantics_dic, args.filters_words)
            words = cmp(api_keywords, ui_keywords)
            words_ui = cmp(api_keywords, app_ui_keywords)
            if len(words) > 0 and tag != 'app':
                if node == '<':
                    print()
                for word in words:
                    if (node in tmp_api_words and (word,tag) not in tmp_api_words[node]) or node not in tmp_api_words:
                        tmp_api_words.setdefault(node, []).append((word,tag))
                    if (word in tmp_words_api and (node,tag) not in tmp_words_api[word]) or word not in tmp_words_api:
                        tmp_words_api.setdefault(word, []).append((node,tag))
            if len(words_ui) > 0:
                for word in words_ui:
                    if (node in tmp_api_words_ui and (word,tag) not in tmp_api_words_ui[node]) or node not in tmp_api_words_ui:
                        tmp_api_words_ui.setdefault(node, []).append((word,tag))
                    if (word in tmp_words_api_ui and (node,tag) not in tmp_words_api_ui[word]) or word not in tmp_words_api_ui:
                        tmp_words_api_ui.setdefault(word, []).append((node,tag))
    basic_tool.write_json(semantics_dic, os.path.join(args.filters_behaviors_dir,"{}_semantics_dic.json".format(args.app_name)))
    basic_tool.write_json(string_dic, os.path.join(args.filters_behaviors_dir,"{}_string_dic.json".format(args.app_name)))
    basic_tool.write_json(tmp_words_api, os.path.join(args.filters_behaviors_dir,"{}_attention_words.json".format(args.app_name)))
    basic_tool.write_json(tmp_words_api_ui, os.path.join(args.filters_behaviors_dir,"{}_attention_words_ui.json".format(args.app_name)))
    basic_tool.write_json(tmp_api_words, os.path.join(args.filters_behaviors_dir,"{}_attention_apis.json".format(args.app_name)))
    basic_tool.write_json(tmp_api_words_ui, os.path.join(args.filters_behaviors_dir,"{}_attention_apis_ui.json".format(args.app_name)))
    basic_tool.writeContentLists(args.important_api_path, important_apis)


def extract_important_api(args):
    name_apk = os.path.split(args.apk_file)[1]
    app_name = os.path.splitext(name_apk)[0]
    dot_path, apk_json_path, text_result_path = get_file_path(args.result_dir_root, name_apk, app_name)
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
    else:
        contains_important_apis(args, app_semantics, android_path_list)
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

def main(apk_dir, result_dir):
    apps = basic_tool.getAllFiles(apk_dir, [], '.apk')
    filters_behaviors_dir = os.path.join(result_dir, 'filters_behaviors_dir')
    third_libs_file = os.path.join(result_dir, 'liteRadar_3rdLibs')
    api_to_name_file = os.path.join(result_dir, 'source_words/database/api_list_dir/api_apiname.json')
    args = [
        'filter_keywords_file', os.path.join('behavior_filters', 'filter_result_3.txt'),
        'third_libs', basic_tool.readContentLists_withoutbr(third_libs_file),
        'api_to_name_file', api_to_name_file,
        'filters_behaviors_dir', filters_behaviors_dir,
    ]
    to_handle_apps = []
    for app in apps:
        important_api_path = os.path.join(filters_behaviors_dir, app_name,"{}_important_path.txt".format(app_name))
        name_apk = os.path.split(app)[1]
        app_name = os.path.splitext(os.path.basename(app))[0]
        if os.path.exists(important_api_path):
            continue
        if os.path.exists(TIME_OUT_FILE):
            time_out = basic_tool.readContentLists_withoutbr(TIME_OUT_FILE)
        dot_path, apk_json_path, text_result_path = get_file_path(result_dir, name_apk, app_name)
        if dot_path == '':
            continue 
        elif dot_path in time_out:
            continue
        to_handle_apps.append(app)

    # p = mp.Pool(g_process_size)
    # global g_lock
    # g_lock = mp.Lock()
    for app in to_handle_apps:
        name_apk = os.path.split(app)[1]
        app_name = os.path.splitext(name_apk)[0]
        parser = set_args()
        args += [
            '-a', app, 
            '--app_result_dir', os.path.join(filters_behaviors_dir, app_name),
            '--important_api_path', os.path.join(filters_behaviors_dir, app_name,"{}_important_path.txt".format(app_name))

        ]
        args, unknown = parser.parse_known_args(args)
        result = extract_important_api(args)
        write_timeout_results(result)
        # p.apply_async(func=extract_important_api, 
        #                 args=(args,),
        #                 callback=write_timeout_results)    
    # p.close()
    # p.join()

if __name__ == '__main__':
    apk_dirs = ['/home/data/yuec/DeepIntent/data/example/benign', '/home/data/yuec/DeepIntent/data/example/malicious'] # finish
    for apk_dir in apk_dirs:
        main(apk_dir)
    