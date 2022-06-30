import os
from app_behavior.components import gator, wid, image2widget, ic3, callgraph
from app_behavior.xml_semantics import extract_text
g_fp_result = "data/gator_result.txt"

from tools import basic_tool


def get_torun_apps(apk_dir, gator_result_file):
    apk_list = []
    gator_result = basic_tool.readContentLists_withoutbr(gator_result_file)
    apks = basic_tool.getAllFiles(apk_dir, [], '.apk')
    for apk_file in apks:
        name = os.path.basename(apk_file)
        if name+'	SUCCESS' in gator_result:
            gator_path = os.path.join(result_dir, 'output', name+'.json')
            if os.path.exists(gator_path):
                apk_list.append(apk_file)
    return list(set(apk_list))


def main(apk_dirs, result_dir):
    for apk_dir in apk_dirs:
        apps = basic_tool.getAllFiles(apk_dir, [], '.apk')
        print('gator start')
        gator.main(apps, result_dir)
        torun_apps = get_torun_apps(apk_dir, g_fp_result)
        # once start
        print('wid start')
        if not (os.path.exists('wid_finish.txt') and apk_dir in basic_tool.readContentLists_withoutbr('wid_finish.txt')):
            wid.run_wid(apk_dir, result_dir)
            basic_tool.writeContex_mode('wid_finish.txt',apk_dir+'\n','a+')
        print('ic3 start')
        if not (os.path.exists('ic3_finish.txt') and apk_dir in basic_tool.readContentLists_withoutbr('ic3_finish.txt')):
            ic3.run_ic3(torun_apps, result_dir)
            basic_tool.writeContex_mode('ic3_finish.txt',apk_dir+'\n','a+')
        # once ends
        print('image2widget start')
        image2widget.run_img2widget(apk_dir, result_dir)
        print('callgraph start')
        callgraph.run_callgraph(apps, apk_dir, result_dir)
        print('text extract')
        extract_text.main(torun_apps, result_dir)
        
        
     
if __name__ == "__main__":
    # apk_dirs = ['/home/data/xiu/code-translation/code/guibat/apk']
    # apk_dirs = ['/home/data/yuec/DeepIntent/data/example/benign', '/home/data/yuec/DeepIntent/data/example/malicious'] # finish
    apk_dirs = ['/home/data/xiu/apks/benign/fromzz']
    result_dir = 'data'
    main(apk_dirs, result_dir)