
import argparse
import os
import sys
from tools.apk_tool import get_name_from_node
from tools import nlp_tool
TIME_OUT_FILE = 'time_out_api_sequence.txt'

def set_args():
    parser = argparse.ArgumentParser(
        description='behavior extraction')
        # add_argument('--path_app', type=str, required=True)
    parser.add_argument('--filters_words', default=[], type=list)
    parser.add_argument('--attention_library', default=[], type=list)
    parser.add_argument('--third_libs', default=[], type=list)
    parser.add_argument('--api_to_name_dic_path', default='', type=str)
    parser.add_argument('--name_to_api_dic_path', default='', type=str)
    parser.add_argument('--result_dir_root', default='data', type=str)
    parser.add_argument('--filters_behaviors_dir', default='', type=str)
    
    parser.add_argument('-a', '--apk_file', dest='apk_file', default='', type=str)
    parser.add_argument('--app_name', default='', type=str)
    parser.add_argument('--app_result_dir', default='', type=str)
    parser.add_argument('--important_api_path', default='', type=str)
    parser.add_argument('--suspicious_behavior_path', default='', type=str)
    return parser



def get_file_path(result_dir, name_apk, app_name):
    dot_dir = os.path.join(result_dir, 'dot_output', app_name)
    dot_path = ''
    if os.path.exists(dot_dir):
        files = os.listdir(dot_dir)
        for f in files:
            if f.endswith('.dot') and not f.startswith('<'):
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


def get_name_of_method(api, name_to_api_dic):
    strings = get_name_from_node(api).replace(':',' ')
    # method, strings = map_method(api)
    if strings in name_to_api_dic:
        split_names = name_to_api_dic[strings]['name']
    else:
        split_names = nlp_tool.deal_words(strings)
    return split_names
    
def in_filters_words(strings, filters_words):
    contains = False
    keywords = []
    for item in strings:
        if item in filters_words:
            contains = True
            keywords.append(item)
    return contains, keywords


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
cmp two keywords
'''
def cmp(api_keywords, ui_keywords):
    words = [word for word in api_keywords if word not in ui_keywords]
    return words

def get_split_names_from_node(node, api_to_name_dic, name_to_api_dic):
    if node in api_to_name_dic:
        api_names = api_to_name_dic[node]
        if api_names in name_to_api_dic:
            split_names = name_to_api_dic[api_names]['name']
        else:
            split_names = nlp_tool.deal_words(api_names.replace(':',' '))
    else:
        split_names = get_name_of_method(node, name_to_api_dic)
    return split_names