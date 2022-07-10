import os
from tools import basic_tool

def cmp_behaviors(apk_dic, sus_dir):
    for app in apk_dic:
        sus_file = os.path.join(sus_dir, app, "{}_suspicious_behaviors.txt".format(app))
        if os.path.exists(sus_file):
            print(sus_file)
            keywords = {}
            contents = basic_tool.readContentLists_withoutbr(sus_file)
            for line in contents:
                items = line.split('\t')
                try:
                    tmp_keywords = eval(items[1].split(':')[1])
                except:
                    tmp_keywords = []
                for word in tmp_keywords:
                    if word not in keywords:
                        keywords[word] = [items[0]]
                    else:
                        if items[0] not in keywords[word]:
                            keywords[word].append(items[0])
            for keyword in keywords:
                print(keyword, keywords[keyword])

def read_deepintent_data(file_path):
    data = basic_tool.load_pkl_data(file_path)
    apk_dic = {}
    for i, data_tmp in enumerate(data):
        texts = data_tmp[1]
        apk = texts[0][0][0]
        xml = texts[0][1]
        id = texts[0][2]
        layout_texts = texts[0][3]
        embedded_texts = texts[0][4]
        res_texts = texts[0][5]
        handlers = texts[1]
        functions = texts[2]
        scores = data_tmp[2]
        scores_dic = {'network':scores[0], 'location':scores[1], 'microphone':scores[2], 'sms':scores[3],'camera':scores[4], 'call':scores[5], 'storage':scores[6], 'contacts':scores[7]}
        if apk not in apk_dic:
            apk_dic[apk] = {}
        for per in scores_dic:
            if scores_dic[per] > 0:
                if per in apk_dic[apk]:
                    apk_dic[apk][per].append({scores_dic[per]:functions})
                else:
                    apk_dic[apk][per] = [{scores_dic[per]:functions}]
    return apk_dic

if __name__ == '__main__':
    file_path = "results.pkl"
    sus_dir = 'data/filters_behaviors_dir'
    apk_dic = read_deepintent_data(file_path)
    cmp_behaviors(apk_dic, sus_dir)