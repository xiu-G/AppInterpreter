import argparse
import os
import multiprocessing as mp
import shutil
from tools import basic_tool, apk_tool


IC3_ROOT = 'app_behavior/ic3'
TIME_OUT = 3600
g_process_size = 10
IC3_JAR = 'app_behavior/ic3/ic3.jar'
IC3_JAR2 = 'app_behavior/ic3/ic3-0.2.0-full.jar'
RETARGEDED_JAR = 'app_behavior/ic3/RetargetedApp.jar'
CC = 'app_behavior/ic3/cc.properties'
ANDROID_SDK_ROOT = '/home/data/xiu/android-sdk'

def set_args():
    parser = argparse.ArgumentParser(
        description='IC3: get intercomponent relationship.')
    parser.add_argument('-r', '--ic3_root',
                        dest='ic3_root',
                        default=IC3_ROOT,
                        help='path to root dir')
    parser.add_argument('--ic3_jar',
                        dest='ic3_jar',
                        default=IC3_JAR,
                        help='filepath of ic3 jar')
    parser.add_argument('--ic3_jar2',
                        dest='ic3_jar2',
                        default=IC3_JAR2,
                        help='filepath of ic3 jar')
    parser.add_argument('--retargeted_jar', '--retargeted_jar',
                        dest='retargeted_jar',
                        default=RETARGEDED_JAR,
                        help='filepath of retargeted jar')
    parser.add_argument('-c', '--cc',
                        dest='cc',
                        default=CC,
                        help='filepath of ic3 jar')
    
    parser.add_argument('-t', '--timeout',
                        dest='time_out',
                        metavar='TIMEOUT',
                        default=TIME_OUT,
                        help='timeout in seconds')
    parser.add_argument('--sdk',
                        dest='sdk_path',
                        metavar='ANDROID_SDK',
                        # required=False,
                        default=ANDROID_SDK_ROOT,
                        help='path to the Android SDK ($ANDROID_SDK by default)')
    ## apk
    parser.add_argument('-a', '--apk',
                        dest='apk_file',
                        default='',
                        help='apk file path')
    parser.add_argument('-n', '--name',
                        dest='apk_name',
                        default='',
                        help='apk name')
    
    parser.add_argument('-o', '--output_file',
                        dest='output_file',
                        default='',
                        help='dir to output result')

    parser.add_argument('--log',
                        dest='log_path',
                        metavar='LOG_FILE',
                        default='',
                        required=False,
                        help='save log to disk')
    parser.add_argument('--api',
                        dest='api_level',
                        metavar='API_LEVEL',
                        default='-1',
                        required=False,
                        help='specify API level')
    parser.add_argument('--retarget_path',
                        dest='retarget_path',
                        default='',
                        help='retarget path')

    return parser

def run_ic3_1(args):
    output = open(args.log_path, mode="w")
    android_platform = os.path.join(args.sdk_path, 'platforms')
    cmd = [
        'java',
        '-jar',
        args.ic3_jar,
        '-a',
        args.apk_file,
        '-apkormanifest',
        args.apk_name,
        '-cp',
        android_platform,
        '-db',
        args.cc,
        '-protobuf',
        args.output_file,
    ]
    basic_tool.run_cmd(args.time_out, cmd, output)
    # output.close()
    return output

def run_ic3_2(args, output):
    # output = open(args.log_path, mode="w")
    android_jar =os.path.join(args.sdk_path, 'platforms', 'android-'+str(args.api_level), 'android.jar')
    retargetedPath = os.path.join(os.path.join(result_dir, "testspace"), args.apk_name+'.apk')
    cmd1 = [
        'java', '-Xmx24000m', '-jar',
        args.retargeted_jar, 
        android_jar, 
        args.apk_file,
        retargetedPath,
    ]
    basic_tool.run_cmd(args.time_out, cmd1, output)
    
    cmd2 = [        
        'java', '-Xmx24000m', '-jar', 
        args.ic3_jar2,
        '-apkormanifest', args.apk_file,
        '-input', retargetedPath, 
        '-cp', android_jar,
        '-db', args.cc,
        '-dbname', 'cc', 
        '-protobuf', args.output_file,
    ]
    basic_tool.run_cmd(args.time_out, cmd2, output)
    output.close()
    if os.path.exists(retargetedPath):
        shutil.rmtree(retargetedPath)
    
def run(args):
    output = run_ic3_1(args)
    if len(os.listdir(args.output_file))==1:
        return
    run_ic3_2(args, output)
    if len(os.listdir(args.output_file))==0:
        shutil.rmtree(args.output_file)

def run_ic3(apps, result_dir):
    log_dir = os.path.join(result_dir, "ic3_logs")
    basic_tool.mkdir(log_dir)
    basic_tool.mkdir(os.path.join(result_dir, "testspace"))
    to_handle_apps = []
    for i in range(len(apps)):
        ic3_log_file = os.path.join(log_dir, os.path.splitext(os.path.basename(apps[i]))[0]+'.txt')
        if os.path.exists(ic3_log_file):
            continue
        to_handle_apps.append(apps[i])

    p = mp.Pool(g_process_size)
    for i in range(len(to_handle_apps)):
        parser = set_args()
        app_path = apps[i]
        app = os.path.splitext(os.path.basename(app_path))[0]
        ic3_app_path = os.path.join(result_dir, "ic3_output", app)
        decode_dir = os.path.join(result_dir, 'decode_dir', app)
        if not os.path.exists(decode_dir):
            decode_dir = ''
        basic_tool.mkdir(ic3_app_path)
        api_version = apk_tool.get_api_version(app_path, decode_dir)
        log = os.path.join(log_dir, app+'.txt')
        args = [
            '--log', log,
            '-o', ic3_app_path,
            '-a', app_path,
            '-n', app,
            '--api', str(api_version),
        ]
        args, unknown = parser.parse_known_args(args)
        # run(args)
        p.apply_async(run, args=(args))  
    p.close()
    p.join()

if __name__ == '__main__':
    apk_dirs = ['/home/data/xiu/apks/sample_malware']
    result_dir = 'data'
    for apk_dir in apk_dirs:
        apps = basic_tool.getAllFiles(apk_dirs, [], '.apk')
        run_ic3(apps, result_dir)