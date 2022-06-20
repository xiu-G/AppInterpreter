import os
import json
from readGraphFile import run_read_graph
from javacode import get_java_code
from tools import basic_tool
from runmodel import run
import configs
from androguard.misc import AnalyzeAPK

   
def construct_configs(apk_path):
    tmp_config = configs.Configs
    tmp_config.apk_path = apk_path
    apk_name = os.path.splitext(os.path.split(apk_path)[1])[0]
    dot_path = os.path.join(tmp_config.dot_dir, apk_name+".dot")
    tmp_config.dot_path = dot_path
    dex_path = os.path.join(tmp_config.dex_dir, apk_name+".apk")
    tmp_config.dex_path = dex_path
    path_path = os.path.join(tmp_config.path_dir, apk_name+".txt")
    tmp_config.path_path = path_path
    java_path = os.path.join(tmp_config.java_dir, apk_name+".java")
    tmp_config.java_path = java_path
    json_path = os.path.join(tmp_config.json_dir, apk_name+".json")
    tmp_config.json_path = json_path
    comment_path = os.path.join(tmp_config.comment_dir, apk_name+".txt")
    tmp_config.comment_path = comment_path
    return tmp_config

# run java flowdroid and get dex file, dot file
def get_dex_dot(config):
    args = [
        "-process-dir", config.apk_path,
        "-dex-dir", config.dex_dir,
        "-android-jars", config.platforms_dir,
        "-dot-path", config.dot_path,
        "-callback-path", config.callback_file
    ]
    if os.path.exists(config.dex_path):
        os.remove(config.dex_path)
    cmd = "java -cp /tmp/cp_ybk4ec9gxdjgyq3uls8dea4k.jar runcode.Main "+" ".join(args)
    os.system(cmd)

'''
read dot file and get node and path
'''
def get_cg_paths(config):
    # graph = run_read_graph.read_graph_file(config.dot_path)
    graph = run_read_graph.read_graph_file(config.dot_path, False)
    paths = graph.get_paths()
    write_out_dic = {"nodes":[], "paths":[]}
    for node in graph.gdict:
        write_out_dic["nodes"].append(node)
    for path in paths:
        write_out_dic["paths"].append(path)
        # for node in path:
        #     print(node)
        # print('-------------------------------')
    basic_tool.write_json(write_out_dic, config.path_path)

    return write_out_dic

'''
read nodes and use androguard to get java code and json file
'''
def java_source_code(config, path_dic):
    nodes = path_dic["nodes"]
    code_list = get_java_code.get_code(config.apk_path, nodes)
    basic_tool.write_json_list(code_list, config.json_path)
    get_java_code.write_code(code_list, config.java_path)
    
'''
run translate model
'''
def run_model(config):
    args = [
        "--model_type","roberta",
        "--model_name_or_path","microsoft/codebert-base",
        "--load_model_path", os.path.join(config.model_dir, "pytorch_model.bin"),
        "--file_path", config.json_path,
        "--output_path",config.comment_path,
        "--max_source_length","256",
                "--max_target_length","128",
                "--beam_size","10",
                "--eval_batch_size","64"
    ]
    run.main(args)
    
    

if __name__=="__main__":
    apk_list = ["/home/data/xiu/code-translation/code/runCodeComment/FlowDroid/soot-infoflow-android/testAPKs/ReturnParameterTest.apk"]
    for apk_path in apk_list:
        config = construct_configs(apk_path)
        # get_dex_dot(config)
        # get path
        path_dic = get_cg_paths(config)
        # get java code
        java_source_code(config, path_dic)
        # run model 
        run_model(config)