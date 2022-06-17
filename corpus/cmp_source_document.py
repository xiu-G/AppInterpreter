import codecs

f1 = r'D:\Project\CodeComment\current\base_corpus.txt'
f2 = r'data\source_words\api_description_bak.txt'

def get_api(doc_file):
    api_dic = {}
    with codecs.open(doc_file, "r", "gb18030") as r:
        contents = r.readlines()
        for i, line in enumerate(contents):
            if line.strip()=='':
                continue
            try:
                items = eval(line.strip())
                api = items[0]
            except Exception:
                api = line.strip()
            if (' ') in api[api.index('('):]:
                api = api.replace(api[api.index('('):], api[api.index('('):].replace(' ',''))
            api = api.replace('abstract ','').replace(',String',',java.lang.String').replace('(String','(java.lang.String')
            items = api.split()
            clazz = items[0][1:]
            function = items[-1].split('(')[0]
            if api not in api_dic:
                api_dic[clazz+function] = ''
    return api_dic
    
api_dic_source = get_api(f1)
api_dic_doc = get_api(f2)

i = 0
for api in api_dic_source:
    if api not in api_dic_doc:
        if ': public ' in api or ': protected ' in api:
            continue
        print(api)
        i += 1
print(len(api_dic_source))
print(len(api_dic_doc))
print(i)

i=0
for api in api_dic_doc:
    if api not in api_dic_source:
        if ': public ' in api or ': protected ' in api or '<' in api:
            continue
        print(api)
        i += 1
print(i)