import argparse
import os
import multiprocessing as mp
from tools import apk_tool, basic_tool


g_process_size = 10
ANDROID_SDK_ROOT = '/home/data/xiu/android-sdk'
CALLGRAPH_ROOT = "app_behavior/callgraph"
TIME_OUT = 3600

def set_args():
    parser = argparse.ArgumentParser(
        description='GATOR: Program Analysis Toolkit For Android.')
    parser.add_argument('--sdk',
                        dest='sdk_path',
                        metavar='ANDROID_SDK',
                        # required=False,
                        default=ANDROID_SDK_ROOT,
                        help='path to the Android SDK ($ANDROID_SDK by default)')
    parser.add_argument('-r', '--root',
                        dest='callgraph_root',
                        default=CALLGRAPH_ROOT,
                        help='path to gator root dir')
    parser.add_argument('--result_dir',
                        dest='result_dir',
                        default="",
                        help='path to result dir')
    
    parser.add_argument('-t', '--timeout',
                        dest='time_out',
                        default=TIME_OUT,
                        required=False,
                        help='timeout in seconds')
    
    # for every app
    parser.add_argument('-p', '--apk',
                        dest='apk_path',
                        metavar='APK',
                        required=True,
                        help='path to the APK')
    parser.add_argument('--dir',
                        dest='apk_dir',
                        default='',
                        help='dir to the APKs')
    parser.add_argument('--api',
                        dest='api_level',
                        metavar='API_LEVEL',
                        default='-1',
                        help='specify API level')

    parser.add_argument('-d', '--decode_dir',
                        dest='decode_dir',
                        help='decode dir of the app')

    parser.add_argument('--log',
                        dest='log_path',
                        metavar='LOG_FILE',
                        default='',
                        help='save log to disk')
    return parser

def run_callgraph_apk(args):
    output = open(args.log_path, mode="w")
    cp_jars = basic_tool.extract_jar_libs(os.path.join(args.callgraph_root, "lib"))
    cp_jars = ":" + os.path.join(args.callgraph_root, "target/classes") + cp_jars
    android_sdk_platforms = os.path.join(args.sdk_path, 'platforms')
    cmd = [
        "java","-Xmx12G",
        # "-cp", cp_jars,
        "-cp", 'cp_2ukkfip8eyv6melu86s0pju0n.jar',
        "runcode.APKCallGraph",
        args.apk_path,
        args.apk_dir,
        os.path.join(args.result_dir,"img2widgets/"),
        os.path.join(args.result_dir,"permission_output/"),
        os.path.join(args.result_dir,"ic3_output/"),
        str(args.api_level),
        android_sdk_platforms,
    ]
    for item in cmd:
        print(item)
    basic_tool.run_cmd(args.time_out, cmd, output)
    output.close()


def run_callgraph(apps, apk_dir, result_dir):
    to_handle_apps = []
    log_dir = os.path.join(result_dir, "dot_logs")
    for i in range(len(apps)):
        dot_log_file = os.path.join(log_dir, os.path.splitext(os.path.basename(apps[i]))[0]+'.txt')
        if os.path.exists(dot_log_file):
            continue
        to_handle_apps.append(apps[i])
    
    p = mp.Pool(g_process_size)

    for index, app in enumerate(to_handle_apps):
        name = os.path.basename(app)
        app_name,ext = os.path.splitext(name)
        dot_dir = os.path.join(result_dir, 'dot_output', app_name)
        if not os.path.exists(dot_dir):
            os.makedirs(dot_dir)
        decode_dir = os.path.join(result_dir, 'decode_dir', app_name)
        if not os.path.exists(decode_dir):
            decode_dir = ''
        api_level = apk_tool.get_api_version(app, decode_dir)
        log = os.path.join(result_dir, 'dot_logs',app_name+'.txt')
        parser = set_args()
        args = [
            '-p', app,
            '--dir', apk_dir,
            '--api', str(api_level),
            '--log', log,
            '--result_dir', result_dir,
        ]
        args, unknown = parser.parse_known_args(args)
        run_callgraph_apk(args)
        # p.apply_async(run_callgraph_apk, args=(args))  
    p.close()
    p.join()

if __name__ == '__main__':
    # apk_dirs = ['/home/data/xiu/code-translation/code/guibat/apk']
    apk_dirs = ['/home/data/xiu/code-translation/code/guibat/apk']
    result_dir = 'data'
    for apk_dir in apk_dirs:
        apps = basic_tool.getAllFiles(apk_dir, [], '.apk')
        run_callgraph(apk_dir, apps, result_dir)