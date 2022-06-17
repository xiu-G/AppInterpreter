import urllib.request
import ssl
import sys
import io
from bs4 import BeautifulSoup as soup
import argparse
import time
from selenium import webdriver
import re
import codecs

def read_des(doc_file):
    result_dic = {}
    to_run = {}
    with codecs.open(doc_file, "r", "gb18030") as r:
        contents = r.readlines()
        for i, line in enumerate(contents):
            if line.strip()=='':
                continue
            items = eval(line.strip())
            api = items[0]
            class_name, function_name, sigature = get_api_names(api)
            link = sigature.split(':')[0]
            if '\xa0' in api:
                to_run[link] = ''
                continue
            if link in result_dic:
                continue
            else:
                result_dic[link] = ''
            # result_dic[sigature] = items[1]
    return result_dic, to_run

def get_api_names(api):
    tmps = api.strip().split()
    clazz = tmps[0].replace('/','.').replace('$','.')
    try:
        name = tmps[-1]
    except Exception:
        name = tmps[1]
    sigature = ': '.join([clazz[1:].split(':')[0].split('<')[0], name.split('(')[0]])
    class_name = clazz[1:].split('.')[-1].split('<')[0][:-1]
    function_name = name.split('(')[0]
    return class_name, function_name, sigature

ssl._create_default_https_context = ssl._create_stdlib_context
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/51.0.2704.63 Safari/537.36'}

# origin_link = 'https://developer.android.google.cn/reference/classes'
origin_link = 'https://developer.android.google.cn/reference/androidx/classes'
origin_req=urllib.request.Request(
                url=origin_link,
                headers=headers
                )
origin_resp=urllib.request.urlopen(origin_req)

origin_data=origin_resp.read().decode('utf-8')

# print('content:',data)
# print(type(data))
origin_soup = soup(origin_data,'lxml')
target_tds = origin_soup.find_all('td',attrs={'class':'jd-linkcol'})

# category_links = re.findall(r"href=\"(.+?)\"",str(target_ul))

save_file = './api_androidx_description.txt'
# finish_dic, torun = read_des(save_file)
finish_file = './finish.txt'

# class_list_file = open('./list.txt')
# class_lists = []
# for line in class_list_file.readlines():
#     class_lists.append(line.strip())
# print(class_lists)

flag = False

# def judge_in(name, class_lists):
#     for item in class_lists:
#         if name in item:
#             return True
#     return False

for i, target_td in enumerate(target_tds):
    # print(target_td)
    name = target_td.a.text
    # print(name)
    # if not judge_in(name, class_lists):
    #     continue

    link = target_td.a.get('href')
    class_tmp = '.'.join(link.split('/')[2:])
    # if class_tmp not in torun:
    #     continue
    # print(link)
    api_link = "https://developer.android.google.cn" + link
    print(api_link)
    if 'androidx/tvprovider/media/tv/PreviewProgram.Builder' in api_link:
        flag = True
    if flag == False:
        continue
    print(str(i), str(len(target_tds)), api_link)
    fp_finish = open(finish_file,'a+')
    fp_finish.write(str(api_link))
    fp_finish.write('\n')
    fp_finish.close()

    second_req=urllib.request.Request(
                url=api_link,
                headers=headers
                )
    second_resp=urllib.request.urlopen(second_req)

    second_data=second_resp.read().decode('utf-8')
    second_soup = soup(second_data,'lxml')

    try:
        class_name = second_soup.find_all('td',attrs={'class':'jd-inheritance-class-cell'})[-1].text.replace('\xa0','').strip()
        class_name = class_name.replace(', ',',')
    except Exception as e:
        class_name = '.'.join(link[1:].replace('/','.').split('.')[1:])
    # print(class_name)

    method_tables = second_soup.find_all('table',attrs={'id':'pubmethods'})
    if len(method_tables) > 0:
        method_table = method_tables[0]
    # print(method_table)
        api_infos = method_table.children
        for index, api_info in enumerate(api_infos):
            if index > 2 and len(str(api_info))>1:
            # if index == 19:
                # print("-------{}---------".format(len(str(api_info))))
                # print(api_info)
                tds = api_info.children
                return_type = ''
                for index2, td in enumerate(tds):
                    if index2 == 1:
                        if not 'href' in str(td):
                            items = td.text.strip().split('\n')
                            return_type = items[-1]
                            if len(items)>1 and items[-2].endswith('>'):
                                return_type = items[-2].strip()+' '+items[-1]
                            # print(return_type)
                        else:
                            a_links = td.findChildren('a')
                            for index_a, a in enumerate(a_links):
                                tmp_return_type = ''
                                # return_link = td.a.get('href')
                                return_link = a.get('href')
                                # print(return_link)
                                if 'https://developer.android.google.cn' not in return_link:
                                    return_link = 'https://developer.android.google.cn' + return_link
                                try:
                                    third_req=urllib.request.Request(
                                                url=return_link,
                                                headers=headers
                                                )
                                    print(third_req)
                                    third_resp=urllib.request.urlopen(third_req)
                                    third_data=third_resp.read().decode('utf-8')
                                    third_soup = soup(third_data,'lxml')
                                
                                    tmp_return_type = third_soup.find_all('td',attrs={'class':'jd-inheritance-class-cell'})[-1].text.strip()
                                except:
                                    tmp_return_type = return_link.replace('https://developer.android.google.cn/reference/','').replace('/','.')
                                if len(a_links) > 1:
                                    if index_a == 0:
                                        tmp_return_type = tmp_return_type.split('<')[0]+'<'
                                    if index_a == len(a_links)-1:
                                        tmp_return_type = tmp_return_type+'>'
                                return_type += tmp_return_type.replace('\n',' ').replace(',\xa0',',')
                        while '  ' in return_type:
                            return_type = return_type.replace('  ',' ')
                    if index2 == 3:
                        # print('----------------')
                        # print(td)
                        method = re.findall(r"href=\"(.+?)\"",str(td))[0]
                        method = method.split('#')[-1].replace('&lt;','<').replace('&gt;','>').replace('%20','')
                        # print(method)

                        description = ''
                        for index3, item in enumerate(td):
                            if index3>2 and len(str(item))>1:
                                # print("------------")
                                # print(item.text)
                                try:
                                    description += item.text.strip() + '\n'
                                except:
                                    continue
                        # print(description)
                info = ['<{}: {} {}>'.format(class_name,return_type,method), description]
                print(info)
                fp_save = open(save_file,'a+')
                fp_save.write(str(info))
                fp_save.write('\n')
                fp_save.close()
                print(info)
            
        # sys.exit()

    # sys.exit()
