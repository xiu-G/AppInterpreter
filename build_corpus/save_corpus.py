import codecs
import re
import sys
from tools import basic_tool
# 词组形式
source_base_dir = 'data/source_words/database/android/f_base'
api_references_dir = 'data/source_words/database/android/api_reference'
api_source_result = 'data/source_words/database/api_list_dir/api_source_list.txt'
api_reference_result = 'data/source_words/database/api_list_dir/api_reference_list.txt'
api_list_result = 'data/source_words/database/api_list_dir/android_api_list.txt'
api_name_list_result = 'data/source_words/database/api_list_dir/android_apiname_list.txt'
android_corpus_result = 'data/source_words/database/api_list_dir/android_corpus.txt'
apiname_api_map_result = 'data/source_words/database/api_list_dir/apiname_api.json'
def read_current_txt(dirs):
    files = basic_tool.getAllFiles(dirs, [], '.txt')
    api_lists = []
    for f in files:
        contents = basic_tool.readContentLists(f)
        class_name = ''
        for line in contents:
            line = line.strip()
            # if 'registerContextAwareService' in line:
            #     print()
            if line:
                words = line.split(' ')
                # print(words)
                if ('package' in words) and ('{' in words):
                    package_name = words[1]
                elif ('class' in words) and ('{' in words):
                    index = words.index('class') + 1
                    class_name = words[index]
                elif ('enum' in words) and ('{' in words):
                    index = words.index('enum') + 1
                    class_name = words[index]
                elif ('interface' in words) and ('{' in words):
                    index = words.index('interface') + 1
                    class_name = words[index]
                elif ('@interface' in words) and ('{' in words):
                    index = words.index('@interface') + 1
                    class_name = words[index]
                elif words[0] == 'method' or words[0]=='ctor':
                    method_items = line.strip().split()
                    new_items = []
                    marks = False
                    left = 0
                    for item in method_items:
                        if item.startswith('@'):
                            left += item.count('(')
                            left -= item.count(')')
                            marks = True
                            if left == 0:
                                marks = False
                            continue
                        # if (item.endswith('},') or 'permission' in item)and marks:
                        #     continue
                        if marks and left>0:
                            left += item.count('(')
                            left -= item.count(')')
                            if left == 0:
                                marks = False
                            continue
                        else:
                            marks = False
                            new_items.append(item)
                    line_new = ' '.join(new_items)
                    methed_info = line_new.split(')')[0]
                    method_name_info = methed_info.split('(')[0]
                    # <java.util.concurrent.ConcurrentHashMap<K,V>: <U> U reduceEntries(long, java.util.function.Function<java.util.Map.Entry<K, V>, ? extends U>, java.util.function.BiFunction<? super U, ? super U, ? extends U>)>
                    # <java.time.chrono.ChronoZonedDateTime<Dextendsjava.time.chrono.ChronoLocalDate>: boolean isSupported(java.time.temporal.TemporalUnit)>
                    pattern = re.compile(r'@[A-Za-z|.|]*')
                    try:
                        method_param = methed_info.split('(')[1]
                        method_param = pattern.sub('', method_param).replace(' ','')
                    except Exception:
                        print('here')
                    info_split = method_name_info.split(' ')
                    return_type = info_split[-2]
                    if return_type == 'public' or return_type == 'protected':
                        return_type = ''
                    if info_split[-3].endswith('>'): # <T> xxx
                        return_type = ' '.join([info_split[-3], info_split[-2]])
                    if info_split[-2].endswith('>') and '<' not in info_split[-2]:
                        # ['method', 'public', 'abstract', 'java.util.SortedMap<K,', 'V>', 'subMap']
                        tmp_info_index = 0
                        tmp_list = []
                        while('<' not in info_split[-2-tmp_info_index]):
                            tmp_list.append(info_split[-2-tmp_info_index])
                            tmp_info_index += 1
                        tmp_list.append(info_split[-2-tmp_info_index])
                        tmp_list.reverse()
                        return_type = ''.join(tmp_list)

                    method_name = info_split[-1]

                    method = method_name + '(' + method_param + ')'
                    save_data = '<' + package_name + '.' + class_name + ': ' + return_type + ' ' + method + '>'
                    # save_data = save_data.replace('@IntRange','int').replace('@FloatRange)','float')

                    save_data = pattern.sub('', save_data)
                    api_lists.append(save_data.replace('  ',' '))
                else:
                    continue
                while class_name.endswith(','):
                    class_name += words[index+1]
                    index += 1
                if '<' in class_name and '>' not in class_name:
                    while(not class_name.endswith('>')):
                        class_name += words[index+1]
                        index += 1
    return list(set(api_lists))

def read_reference_file(doc_file):
    api_list = []
    with codecs.open(doc_file, "r", "gb18030") as r:
        contents = r.readlines()
        for i, line in enumerate(contents):
            if line.strip()=='':
                continue
            items = eval(line.strip())
            api = items[0]
            api_list.append(api)
    return api_list

def read_reference_list():
    files = basic_tool.getAllFiles(api_references_dir, [], '')
    api_list = []
    for f in files:
        api_list += read_reference_file(f)
    return list(set(api_list))

def save_database():
    source_api_lists = read_current_txt(source_base_dir)
    print(len(source_api_lists))
    basic_tool.writeContentLists(api_source_result, source_api_lists)
    reference_api_lists = read_reference_list()
    print(len(reference_api_lists))
    basic_tool.writeContentLists(api_reference_result, reference_api_lists)
    total_api_list = source_api_lists + reference_api_lists
    total_api_list = list(set(total_api_list))
    print(len(total_api_list))
    basic_tool.writeContentLists(api_list_result, total_api_list)

def get_api_name(api_lists):
    name_dic = {}
    name2api_dic = {}
    api2name_dic = {}
    for api in api_lists:
        items = api.split()
        package = items[0][1:]
        clazz = package.split('.')[-1].split('<')[0]
        function = items[-1].split('(')[0]
        if clazz+':'+function not in name_dic:
            name_dic[clazz+':'+function] = ''
            name2api_dic[clazz+':'+function] = [api]
        else:
            name2api_dic[clazz+':'+function].append(api)
        api2name_dic[api] = clazz+':'+function

    return name_dic, name2api_dic, api2name_dic

def save_name():
    source_api_lists = basic_tool.readContentLists_withoutbr(api_source_result)
    reference_api_lists = basic_tool.readContentLists_withoutbr(api_reference_result)
    api_lists = basic_tool.readContentLists_withoutbr(api_list_result)
    source_api_name, name2api_dic, api2name_dic = get_api_name(source_api_lists)
    reference_api_name, name2api_dic, api2name_dic = get_api_name(reference_api_lists)
    api_names, name2api_dic, api2name_dic = get_api_name(api_lists)
    print(len(source_api_name))
    print(len(reference_api_name))
    print(len(api_names))
    basic_tool.writeContentLists(api_name_list_result, list(api_names.keys()))

def split_name():
    pass

def save_corpus():
    api_lists = basic_tool.readContentLists_withoutbr(api_list_result)
    api_names, name2api_dic, api2name_dic = get_api_name(api_lists)



if __name__ == '__main__':
    # save_database()
    save_name()
