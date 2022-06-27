#!/usr/bin/env python3

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from tools import basic_tool
import multiprocessing as mp
from tools import apk_tool
from tools.apk_tool import add_google, decode_apk


g_lock = None
g_skip_handled = True
g_redo_failed = True
g_fp_result = "data/gator_result.txt"
g_process_size = 10
ANDROID_SDK_ROOT = '/home/data/xiu/android-sdk'
GATOR_ROOT = "app_behavior/gator"
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
                        dest='gator_path',
                        default=GATOR_ROOT,
                        help='path to gator root dir')
    parser.add_argument('-c', '--client',
                        dest='client',
                        default=["-client", "WTGDemoClient"],
                        help='gator client')
    parser.add_argument('-v', '--verbose',
                        dest='verbose',
                        action='store_true',
                        default=False,
                        help='verbose mode')
    parser.add_argument('-kd', '--keep_decoded',
                        dest='keep_decoded',
                        default=True,
                        help='remain decode dir')
    parser.add_argument('-g', '--google',
                        dest='google',
                        action='store_true',
                        default=False,
                        help='add Google support')
    
    parser.add_argument('-t', '--timeout',
                        dest='time_out',
                        metavar='TIMEOUT',
                        # default='600',
                        default=TIME_OUT,
                        required=False,
                        help='timeout in seconds')
    parser.add_argument('-apktool', '--apktool_file',
                        dest='apktool',
                        # default='600',
                        default='app_behavior/gator/apktool.jar',
                        required=False,
                        help='the path of apktool.jar')
    
    # for every app
    parser.add_argument('-p', '--apk',
                        dest='apk_path',
                        metavar='APK',
                        required=True,
                        help='path to the APK')
    parser.add_argument('--api',
                        dest='api_level',
                        metavar='API_LEVEL',
                        default='-1',
                        required=False,
                        help='specify API level')
    parser.add_argument('-d', '--decode_dir',
                        dest='decode_dir',
                        required=True,
                        help='decode dir of the app')
    parser.add_argument('--log',
                        dest='log_path',
                        metavar='LOG_FILE',
                        default='',
                        required=False,
                        help='save log to disk')
    return parser

def invoke_gator_on_apk(args, output):
    args.api_level = 29
    i_level_num = int(args.api_level)
    platform_api_dir = os.path.join(args.sdk_path, "platforms", "android-" + str(i_level_num))
    cp_jars = basic_tool.extract_jar_libs(os.path.join(args.gator_path, "lib"))
    cp_jars = ":" + os.path.join(args.gator_path, "bin") + cp_jars
    platform_jars = os.path.join(platform_api_dir, "android.jar")
    if args.google:
        platform_jars = add_google(args.sdk_path, i_level_num, platform_jars)
    platform_jars += ":{0}/deps/android-support-annotations.jar" \
                     ":{0}/deps/android-support-v4.jar" \
                     ":{0}/deps/android-support-v7-appcompat.jar" \
                     ":{0}/deps/android-support-v7-cardview.jar" \
                     ":{0}/deps/android-support-v7-gridlayout.jar" \
                     ":{0}/deps/android-support-v7-mediarouter.jar" \
                     ":{0}/deps/android-support-v7-palette.jar" \
                     ":{0}/deps/android-support-v7-preference.jar" \
                     ":{0}/deps/android-support-v7-recyclerview.jar".format(args.gator_path)
    # Finished computing platform libraries

    cmd = ["java", "-Xmx12G",
           "-classpath", cp_jars,
           "presto.android.Main",
           "-sootandroidDir", args.gator_path,
           "-sdkDir", args.sdk_path,
           "-listenerSpecFile", os.path.join(args.gator_path, 'listeners.xml'),
           '-wtgSpecFile', os.path.join(args.gator_path, 'wtg.xml'),
           '-resourcePath', os.path.join(args.decode_dir, 'res'),
           '-manifestFile', os.path.join(args.decode_dir, 'AndroidManifest.xml'),
           "-project", args.apk_path,
           "-apiLevel", "android-" + str(args.api_level),
           '-guiAnalysis',
           '-benchmarkName', os.path.basename(args.apk_path),
           "-android", platform_jars,]
    cmd.extend(args.client)
    if args.verbose:
        cmd.append('-verbose')
    print(' '.join(cmd))
    if args.time_out==0:
        return subprocess.run(cmd, stdout=output, stderr=output)
    else:
        try:
            return subprocess.run(cmd, stdout=output, stderr=output, timeout=args.time_out)
        except subprocess.TimeoutExpired:
            return -50

def after_gator(args):
    r, apk_name, msg = args
    result_type = {
        0: "SUCCESS",
        -1: "DECODE_ERROR",
        -2: "TIMEOUT",
        -3: "GATOR_ERROR"
    }

    print("<finish>{}({}) {}".format(apk_name, msg, "fail" if r != 0 else "success"))
    # g_lock.acquire()
    with open(g_fp_result, mode="a") as fo:
        print("{}\t{}".format(apk_name, result_type[r]), file=fo)
    # g_lock.release()
    sys.stdout.flush()

def run_gator(args, msg):
    apk_name = os.path.basename(args.apk_path)
    print("<start>{}({})".format(apk_name, msg))
    # create output file
    b_out2file = False
    if args.log_path == '':
        output = sys.stdout
    elif isinstance(args.log_path, str):
        b_out2file = True
        output = open(args.log_path, mode="w")

    # decode apk to temp folder
    frame_dir = tempfile.mkdtemp()
    print("Extract APK at:", args.decode_dir, ". Frameworks:", frame_dir, file=output)
    if not os.path.exists(args.decode_dir):
        dec_ret = decode_apk(args.apktool, args.apk_path, args.decode_dir, frame_dir, output=output)
        dec_ret = dec_ret.returncode
        shutil.rmtree(frame_dir)
        print("Frameworks removed!", file=output)
        if dec_ret != 0:
            if not args.keep_decoded:
                shutil.rmtree(args.decode_dir)
                print("Extracted APK resources removed!", file=output)
            if b_out2file:
                output.close()
            return -1, apk_name, msg
    api_level = apk_tool.get_api_version(args.apk_path, args.decode_dir)
    args.api_level = api_level
    gator_ret = invoke_gator_on_apk(args,output)
    if isinstance(gator_ret, int):
        assert gator_ret == -50
        gator_ret = -2
    elif gator_ret.returncode != 0:
        gator_ret = -3
    else:
        gator_ret = gator_ret.returncode
    if not args.keep_decoded:
        shutil.rmtree(args.decode_dir)
        print("Extracted APK resources removed!", file=output)
    if b_out2file:
        output.close()
    return gator_ret, apk_name, msg

def get_to_handle_apps(apps):
    apps_handled = []
    if os.path.exists(g_fp_result):
        if not g_skip_handled:
            os.remove(g_fp_result)
        else:
            with open(g_fp_result, mode="r") as fi:
                for line in fi:
                    apk_name, r = line.strip().split("\t")
                    if g_redo_failed and r != "SUCCESS":
                        continue
                    apps_handled.append(apk_name)
            if g_redo_failed:
                with open(g_fp_result, mode="w") as fo:
                    for apk_name in apps_handled:
                        print("{}\t{}".format(apk_name, "SUCCESS"), file=fo)
    to_handle_apps = []
    for i in range(0, len(apps)):
        app_path = apps[i]
        app = os.path.split(app_path)[1]
        if app in apps_handled:
            print("<handled>{}({}/{})".format(app, i, len(apps)))
            continue
        if not app.endswith(".apk"):
            continue
        to_handle_apps.append(app_path)
    return to_handle_apps
        
def main(apps, result_dir):
    print("app total size:", len(apps))
    output_dirs = ["output", "dot_output", "log_output"]
    for output_dir in output_dirs:
        output_dir = os.path.join(result_dir, output_dir)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    # skip settings
    to_handle_apps = get_to_handle_apps(apps)
    for i in range(0, len(to_handle_apps)):
        app_path = apps[i]
        app = os.path.split(app_path)[1]
        decode_dir = os.path.join(result_dir, 'decode_dir', os.path.splitext(app)[0])
        fp_output = os.path.join(os.path.join(result_dir, "log_output"), app.replace(".apk", ".log"))
        args = [
            '-p', app_path,
            '-d', decode_dir,
            '--log', fp_output,
            '-api', '29',
        ]
        parser = set_args()
        args, unknown = parser.parse_known_args(args)
        msg = "{}/{}".format(i, len(apps))
        result_gator = run_gator(args, msg)
        after_gator(result_gator)
        # pool.apply_async(func=run_gator,
        #                  args=(configs, msg, fp_output, g_timeout),
        #                  callback=after_gator)

    # pool.close()
    # pool.join()


if __name__ == '__main__':
    apk_dir = '/home/data/xiu/code-translation/code/guibat/apk'
    apps = basic_tool.getAllFiles(apk_dir, [], '.apk')
    result_dir = 'data'
    GATOR_OPTIONS = ["-client", "WTGDemoClient"]
    main(apps, result_dir)
