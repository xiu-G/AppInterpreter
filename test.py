from logging import handlers
from re import T
from tools import basic_tool

file1 = '/mnt/e/WorkSpace/data/dot_output/com.voicenotebook.voicenotebook.apk.wtg.dot'
file2 = '/mnt/e/WorkSpace/data/dot_output/2.txt'

def deal_file(contents):
    dic = {}
    for line in contents:
        line = ''.join([i for i in line if not i.isdigit()])
        line = line.replace(';','')
        if '->' in line:
            items = line.split('\\n')
            key = '\\n'.join([items[0],items[1],items[2],items[3],items[4]])
            tmp_keys = []
            for i in items:
                if i.startswith('handler:'):
                    tmps=line.split('\\n')[-3][9:][1:-1].split('>')
                    for tmp in tmps:
                        if tmp.startswith('<'):
                            tmp_keys.append(tmp+'>')
                        elif tmp.startswith(', <'):
                            tmp_keys.append(tmp[2:]+'>')
            dic.setdefault(key, []).append(tmp_keys)
        elif line not in dic:
            dic[line] = ''
    return dic

contents1 = basic_tool.readContentLists_withoutbr(file1)
dic1 = deal_file(contents1)

contents2 = basic_tool.readContentLists_withoutbr(file2)
dic2 = deal_file(contents2)


for key in dic1:
    if '->' in key:
        if key not in dic2:
            print(key)
            print(dic1[key])
        else:
            handlers1 = dic1[key].sort()
            handlers2 = dic2[key].sort()
            if handlers1 != handlers2:
                print(key)
    elif '->' not in key and key not in dic2:
        print(key)

for key in dic2:
    if '->' in key:
        if key not in dic1:
            print(key)
            print(dic2[key])
        else:
            handlers1 = dic1[key].sort()
            handlers2 = dic2[key].sort()
            if handlers1 != handlers2:
                print(key)
    elif '->' not in key and key not in dic1:
        print(key)
