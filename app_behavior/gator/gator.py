#!/usr/bin/env python3

import argparse
import glob
import os
import shutil
import subprocess
import sys
from subprocess import call, TimeoutExpired
import tempfile
from tools import basic_tool
import multiprocessing as mp
from tools import apk_tool
from tools.apk_tool import add_google, decode_apk


gator_dir = os.path.dirname(os.path.realpath(__file__))
g_lock = None
g_skip_handled = True
g_redo_failed = True
g_fp_result = "data/gator_result.txt"
g_process_size = 10

class GlobalConfigs:
    def __init__(self, g_gator_root="", g_sdk_dir=""):
        self.GATOR_ROOT = g_gator_root
        self.SDK_ROOT = g_sdk_dir
        self.GATOR_OPTIONS = ["-client", "WTGDemoClient"]
        self.KEEP_DECODE = True
        self.ADD_GOOGLE = False
        self.VERVOSE = False
        self.APK_PATH = ""
        self.API_LEVEL = -1
        self.DECODED_DIR = ""
        self.TIMEOUT = 3600


def set_args():
    parser = argparse.ArgumentParser(
        description='GATOR: Program Analysis Toolkit For Android.')

    subparsers = parser.add_subparsers(dest='command',
                                       metavar='COMMAND')
    subparsers.required = True

    parser_analyze= subparsers.add_parser('-p', '--apk',
                                dest='apkpath',
                                metavar='APK',
                                required=True,
                                help='path to the APK')

    parser_analyze.add_argument('-d', '--debug',
                                dest='debug',
                                action='store_true',
                                default=False,
                                help='debug mode (print out the Java command)')

    parser_analyze.add_argument('-v', '--verbose',
                                dest='verbose',
                                action='store_true',
                                default=False,
                                help='verbose mode')

    parser_analyze.add_argument('--sdk',
                                dest='sdkpath',
                                metavar='ANDROID_SDK',
                                required=False,
                                help='path to the Android SDK ($ANDROID_SDK by default)')

    parser_analyze.add_argument('--log',
                                dest='logpath',
                                metavar='LOG_FILE',
                                default='',
                                required=False,
                                help='save log to disk')

    parser_analyze.add_argument('-t', '--timeout',
                                dest='timeout',
                                metavar='TIMEOUT',
                                # default='600',
                                default='36000',
                                required=False,
                                help='timeout in seconds')

    parser_analyze.add_argument('-g', '--google',
                                dest='google',
                                action='store_true',
                                default=False,
                                help='add Google support')

    parser_analyze.add_argument('--api',
                                dest='apilevel',
                                metavar='API_LEVEL',
                                required=False,
                                default='-1',
                                help='specify API level')

    parser_analyze.add_argument('-o', '--outputFile',
                            dest='outputFile',
                            metavar='outputFile',
                            required=True,
                            help='path to the output location')
    return parser

def invoke_gator_on_apk(
        apk_path,
        decode_dir,
        api_level,
        android_sdk_path,
        benchmark_name,
        options,
        configs,
        output=None,
        timeout=0,
):
    soot_android_path = configs.GATOR_ROOT
    s_level_num = api_level[api_level.find('-') + 1:]
    i_level_num = int(s_level_num)
    platform_api_dir = os.path.join(android_sdk_path, "platforms", "android-" + str(i_level_num))
    cp_jars = basic_tool.extract_jar_libs(os.path.join(soot_android_path, "lib"))
    cp_jars = ":" + os.path.join(soot_android_path, "bin") + cp_jars

    platform_jars = os.path.join(platform_api_dir, "android.jar")
    if configs.ADD_GOOGLE:
        platform_jars = add_google(android_sdk_path, i_level_num, platform_jars)
    platform_jars += ":{0}/deps/android-support-annotations.jar" \
                     ":{0}/deps/android-support-v4.jar" \
                     ":{0}/deps/android-support-v7-appcompat.jar" \
                     ":{0}/deps/android-support-v7-cardview.jar" \
                     ":{0}/deps/android-support-v7-gridlayout.jar" \
                     ":{0}/deps/android-support-v7-mediarouter.jar" \
                     ":{0}/deps/android-support-v7-palette.jar" \
                     ":{0}/deps/android-support-v7-preference.jar" \
                     ":{0}/deps/android-support-v7-recyclerview.jar".format(soot_android_path)
    # Finished computing platform libraries

    cmd = ["java", "-Xmx12G",
           "-classpath", cp_jars,
           "presto.android.Main",
           "sootandroidDir", soot_android_path,
           "-sdkDir", android_sdk_path,
           "-listenerSpecFile", os.path.join(soot_android_path, 'listeners.xml'),
           '-wtgSpecFile', os.path.join(soot_android_path, 'wtg.xml'),
           '-resourcePath', os.path.join(decode_dir, 'res'),
           '-manifestFile', os.path.join(decode_dir, 'AndroidManifest.xml'),
           "-project", apk_path,
           "-apiLevel", "android-" + str(s_level_num),
           '-guiAnalysis',
           '-benchmarkName', benchmark_name,
           "-android", platform_jars,]
    cmd.extend(options)
    # for line in cmd:
    #     print(line)

    if configs.VERVOSE:
        cmd.append('-verbose')

    if timeout == 0:
        return subprocess.run(cmd, stdout=output, stderr=output)
    else:
        try:
            return subprocess.run(cmd, stdout=output, stderr=output, timeout=timeout)
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
    g_lock.acquire()
    with open(g_fp_result, mode="a") as fo:
        print("{}\t{}".format(apk_name, result_type[r]), file=fo)
    g_lock.release()
    sys.stdout.flush()

def run_gator(configs, msg, output=None, timeout=0):
    apk_name = os.path.basename(configs.APK_PATH)
    print("<start>{}({})".format(apk_name, msg))
    # create output file
    b_out2file = False
    if output is None:
        output = sys.stdout
    elif isinstance(output, str):
        b_out2file = True
        output = open(output, mode="w")

    # decode apk to temp folder
    decode_dir = configs.DECODED_DIR
    frame_dir = tempfile.mkdtemp()
    print("Extract APK at:", decode_dir, ". Frameworks:", frame_dir, file=output)
    if not os.path.exists(decode_dir):
        dec_ret = decode_apk(configs.APK_PATH, decode_dir, frame_dir, output=output)
        dec_ret = dec_ret.returncode
        shutil.rmtree(frame_dir)
        print("Frameworks removed!", file=output)
        if dec_ret != 0:
            if not configs.KEEP_DECODE:
                shutil.rmtree(decode_dir)
                print("Extracted APK resources removed!", file=output)
            if b_out2file:
                output.close()
            return -1, apk_name, msg
    api_level = apk_tool.get_api_version(configs.APK_PATH, decode_dir)

    gator_ret = invoke_gator_on_apk(
        apk_path=configs.APK_PATH,
        decode_dir=decode_dir,
        api_level=api_level,
        android_sdk_path=configs.SDK_ROOT,
        benchmark_name=apk_name,
        options=configs.OPTIONS,
        configs=configs,
        output=None,
        timeout=configs.TIMEOUT,
    )
    if isinstance(gator_ret, int):
        assert gator_ret == -50
        gator_ret = -2
    elif gator_ret.returncode != 0:
        gator_ret = -3
    else:
        gator_ret = gator_ret.returncode

    if not configs.KEEP_DECODE:
        shutil.rmtree(decode_dir)
        print("Extracted APK resources removed!", file=output)
    if b_out2file:
        output.close()
    return gator_ret, apk_name, msg

def main(apps, g_gator_root, g_sdk_dir, result_dir):
    print("app total size:", len(apps))
    output_dirs = ["output", "dot_output", "log_output"]
    for output_dir in output_dirs:
        output_dir = os.path.join(result_dir, output_dir)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    # skip settings
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

    # global g_lock
    # pool = mp.Pool(g_process_size)
    # g_lock = mp.Lock()
    for i in range(0, len(to_handle_apps)):
        app_path = apps[i]
        app = os.path.split(app_path)[1]
        decode_dir = os.path.join(result_dir, 'decode_dir', os.path.splitext(app)[0])
        configs = GlobalConfigs(g_gator_root, g_sdk_dir)
        configs.DECODED_DIR = decode_dir
        configs.APK_PATH = app_path
        fp_output = os.path.join(os.path.join(result_dir, "log_output"), app.replace(".apk", ".log"))
        msg = "{}/{}".format(i, len(apps))
        args = run_gator(configs, msg, fp_output)
        after_gator(args)
        # pool.apply_async(func=run_gator,
        #                  args=(configs, msg, fp_output, g_timeout),
        #                  callback=after_gator)

    # pool.close()
    # pool.join()


if __name__ == '__main__':
    apk_dir = '/mnt/e/WorkSpace/vscode/guibat/apks_sw'
    apps = basic_tool.getAllFiles(apk_dir, [], '.apk')
    g_gator_root = "app_behavior/gator"
    g_sdk_dir = '/mnt/e/Files/Sdk/platforms'
    result_dir = 'data'
    main(apps, g_gator_root, g_sdk_dir, result_dir)
