import argparse
import os
from unittest import result
from tools import basic_tool
WID_ROOT = 'app_behavior/WidImageResolver'
TIME_OUT = 3600

def set_args():
    parser = argparse.ArgumentParser(
        description='WidImageResolver: get all images and thier widgets.')
    parser.add_argument('-r', '--wid_root',
                        dest='wid_root',
                        default=WID_ROOT,
                        help='path to wid root dir')
    parser.add_argument('-t', '--timeout',
                        dest='time_out',
                        metavar='TIMEOUT',
                        default=TIME_OUT,
                        required=False,
                        help='timeout in seconds')
    # for every app
    parser.add_argument('-a', '--apkdir',
                        dest='apk_dir',
                        required=True,
                        help='dir to the APK')
    parser.add_argument('--log',
                        dest='log_path',
                        metavar='LOG_FILE',
                        default='',
                        required=False,
                        help='save log to disk')
    return parser

def run_wid(apk_dir, result_dir):
    log = os.path.join(result_dir, "wid_log.txt")
    parser = set_args()
    args = [
        '-a', apk_dir,
        '--log', log,
    ]
    args, unknown = parser.parse_known_args(args)
    cp_jars = basic_tool.extract_jar_libs(os.path.join(args.wid_root, "lib"))
    cp_jars = ":" + os.path.join(args.wid_root, "bin") + cp_jars
    cp_jars = ":" + os.path.join(args.wid_root, "resourses") + cp_jars
    cmd = [
        "java","-Xmx12G",
        "-classpath", cp_jars,
        "edu.cwru.android.ui.WidgetIDIconMappingMain",
        args.apk_dir,
    ]
    log = open(log, mode="w")
    basic_tool.run_cmd(args.time_out, cmd, log)
    log.close()
    


if __name__ == '__main__':
    apk_dirs = ['/home/data/xiu/code-translation/code/guibat/apk']
    # apk_dirs = ['/home/data/yuec/DeepIntent/data/example/benign', '/home/data/yuec/DeepIntent/data/example/malicious']
    result_dir = 'data'
    for apk_dir in apk_dirs:
        run_wid(apk_dir, result_dir)