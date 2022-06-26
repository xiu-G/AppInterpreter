#!/usr/bin/env python3

import argparse
import glob
from ntpath import join
import os
import sys
import psycopg2
from subprocess import check_call, TimeoutExpired, CalledProcessError
from pygator.unpacker import decode_res_from_apk
from pygator.utils import remove_temp_dir, extract_target_api, extract_min_api, extract_max_api, is_requested_dangerous_permissions
from pygator import basic_tool
import multiprocessing as mp

gator_dir = os.path.dirname(os.path.realpath(__file__))


def pathExists(pathName):
    if os.access(pathName, os.F_OK):
        return True
    return False;

def extractLibsFromPath(pathName):
    if not pathExists(pathName):
        return ""
        pass
    fileList = glob.glob(pathName+"/*.jar")
    if len(fileList) == 0:
        return ""
    ret = ""
    for item in fileList:
        ret += ':' + item
    return ret;

def findBestGoogleAPI(sdkPath, apiLevel):
    googleAPILibDirs = glob.glob(sdkPath + "/add-ons/addon-google_apis-google-*")
    avaiLevels = []
    for item in googleAPILibDirs:
        id = item.rfind('-')
        digits = int(item[id+1:])
        avaiLevels.append(digits)
    avaiLevels.sort(reverse=True)
    if len(avaiLevels) == 0:
        return 0
    if apiLevel not in avaiLevels:
        apiLevel = avaiLevels[0]
    return sdkPath + "/add-ons/addon-google_apis-google-" + str(apiLevel)

def analyze(args, unknown):
    jar = os.path.join(gator_dir, 'sootandroid', 'build', 'libs', 'sootandroid-1.0-SNAPSHOT-all.jar')
    if not os.path.exists(jar):
        print('...... please build GATOR first.')
        exit(-1)
    apktool_dir = decode_res_from_apk(args.apkpath, args.apktoolDir)
    if args.apilevel != '-1':
        target_level = int(args.apilevel)
    else:
        target_level = extract_target_api(os.path.join(apktool_dir, 'apktool.yml'))
        if target_level == -1 or target_level >= 30:
            print('...... cannot determine the target API level for APK. Fallback to use 27.')
            target_level = 27
        elif target_level < 10:
            print('...... target API level is below 10. Force to use 10.')
            target_level = 10
        elif target_level > 100:
            return

    # is_requested_dangerous = is_requested_dangerous_permissions(os.path.join(apktool_dir, 'AndroidManifest.xml'))
    # if not is_requested_dangerous:
    #     print('NOT HAS DP:' + args.apkpath)
    #     remove_temp_dir(apktool_dir)
    #     return

    min_level = extract_min_api(os.path.join(apktool_dir, 'apktool.yml'))
    max_level = extract_max_api(os.path.join(apktool_dir, 'apktool.yml'))

    if not args.sdkpath:
        args.sdkpath = os.environ['ANDROID_SDK']
    print('...... resource decoded to %s' % apktool_dir)
    cmd = ['java', '-Xmx12G', '-cp', jar, 'presto.android.Main',
           '-sootandroidDir', os.path.join(gator_dir, 'sootandroid'),
           '-sdkDir', args.sdkpath,
           '-listenerSpecFile', os.path.join(gator_dir, 'sootandroid', 'listeners.xml'),
           '-wtgSpecFile', os.path.join(gator_dir, 'sootandroid', 'wtg.xml'),
           '-resourcePath', os.path.join(apktool_dir, 'res'),
           '-manifestFile', os.path.join(apktool_dir, 'AndroidManifest.xml'),
           '-project', args.apkpath,
           '-apiLevel', 'android-%s' % target_level,
           '-guiAnalysis',
           '-benchmarkName', args.apkpath.split('/')[-1],
           '-permissionMapFile', os.path.join(gator_dir, 'sootandroid', 'protected_apis.txt'),
           '-outputFile', args.outputFile,
           '-clientParam', 'printXml',
           "-flowgraphOutput", args.flowgraphOutput,
           #'-clientParam', 'noDumpSql',
           '-minSdkVersion', str(min_level),
           '-maxSdkVersion', str(max_level),
           '-targetSdkVersion', str(target_level),
           ]
    if args.google:
        GoogleAPIDir = findBestGoogleAPI(args.sdkpath, target_level)
        if GoogleAPIDir == 0 or (not pathExists(GoogleAPIDir)):
            print("Google API Level: " + str(target_level) + "Not installed!")
            sys.exit(-1)
        GoogleAPI = extractLibsFromPath(GoogleAPIDir + "/libs")
        androidJar =  os.path.join(args.sdkpath, 'platforms', 'android-%s' % target_level, 'android.jar')
        if len(GoogleAPI) != 0:
            androidJar = androidJar + ":" + GoogleAPI
        cmd.extend(['-android', androidJar])
        pass
    else:
        cmd.extend(['-android', os.path.join(args.sdkpath, 'platforms', 'android-%s' % target_level, 'android.jar')])
    if args.verbose:
        cmd.append('-verbose')
    cmd.extend(unknown)

    print('...... %s' % ' '.join(cmd))
    if args.debug:  # print out the command
        return
    if not args.logpath:
        try:
            check_call(cmd, timeout=int(args.timeout))

            remove_temp_dir(apktool_dir)
        except TimeoutExpired:
            #writeLogSql(args.apkpath.split('/')[-1], "Timeout!: " + args.apkpath)
            remove_temp_dir(apktool_dir)
            # sys.exit(-50)
        except CalledProcessError:
            remove_temp_dir(apktool_dir)
            # sys.exit(-50)

    else:
        with open(args.logpath, 'w') as outfile:
            check_call(cmd, timeout=int(args.timeout), stdout=outfile, stderr=outfile)
            print('...... log saved to %s' % outfile.name)
            remove_temp_dir(apktool_dir)

def build(args, unknown):
    cmd = [os.path.join(gator_dir, 'gradlew'), ':sootandroid:shadowJar']
    check_call(cmd)


def set_args():
    parser = argparse.ArgumentParser(
        description='GATOR: Program Analysis Toolkit For Android.')

    subparsers = parser.add_subparsers(dest='command',
                                       metavar='COMMAND')
    subparsers.required = True

    ####################################
    ####################################
    parser_compile = subparsers.add_parser('build',
                                           aliases=['b'],
                                           help='build GATOR')
    parser_compile.set_defaults(func=build)

    ####################################
    ####################################
    parser_analyze = subparsers.add_parser('analyze',
                                           aliases=['a'],
                                           help='analyze APK')
    parser_analyze.set_defaults(func=analyze)

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

    parser_analyze.add_argument('-p', '--apk',
                                dest='apkpath',
                                metavar='APK',
                                required=True,
                                help='path to the APK')

    parser_analyze.add_argument('-o', '--outputFile',
                            dest='outputFile',
                            metavar='outputFile',
                            required=True,
                            help='path to the output location')

    parser_analyze.add_argument('-apktoolDir', '--apktoolDir',
                        dest='apktoolDir',
                        metavar='apktoolDir',
                        required=False,
                        default='',
                        help='path to the output apktoolapktoolDir')

    parser_analyze.add_argument('-flowgraphOutput', '--flowgraphOutput',
                        dest='flowgraphOutput',
                        metavar='flowgraphOutput',
                        required=False,
                        default='',
                        help='path to the output flowgraphOutput')
    return parser

def run(i, files, tmp_dir, result_dir):
    parser = set_args()
    for index, f in enumerate(files):
        if '5cb8e0edb98794792346304a5065b69e' not in f:
            continue
        name = os.path.split(f)[1].split('.apk')[0]
        print(str(i)+'---'+str(index)+'---'+str(len(files))+'---'+name)
        apk_result_dir = os.path.join(result_dir, name)
        if os.path.exists(os.path.join(apk_result_dir, name+'.dot')):
            continue
        basic_tool.mkdir(apk_result_dir)
        args = [
            'a',
            '-p', f,
            '-client', 'GUIHierarchyPrinterClient',
            # '-client', 'WTGDemoClient',
            '-o', os.path.join(apk_result_dir, ''),
            '-apktoolDir', os.path.join(tmp_dir, name),
            '-flowgraphOutput', os.path.join(apk_result_dir, name+'.dot'),
            '--log', os.path.join(apk_result_dir, name+'.log'),
        ]
        args, unknown = parser.parse_known_args(args)
        args.func(args, unknown)


def main():
    AMD_dir = '/home/data/xiu/apks/old_malware/AMD'
    # AMD_dir = '/home/data/xiu/code-translation/code/guibat/apk'
    files = basic_tool.getAllFiles(AMD_dir, [], '.apk')
    # tmp_dir = '/home/data/xiu/code-translation/code/guibat/data/tmp'
    # result_dir = '/home/data/xiu/code-translation/code/guibat/data/gator_result'
    result_dir = '/home/data/xiu/code-translation/code/guibat/sw_data'
    # files = ["/home/data/xiu/apks/old_malware/AMD/Airpush/variety1/5cb8e0edb98794792346304a5065b69e.apk"]
    run(0, files, "", result_dir)
    # dirs_lists = basic_tool.splitList(files, 8)
    # p = mp.Pool()
    # for i in range(len(dirs_lists)):
    #     p.apply_async(run, args=(i, dirs_lists[i], tmp_dir, result_dir, ))
    # p.close()
    # p.join()
    # args = ['b']
    # ./gator a -p abc.apk -client GUIHierarchyPrinterClient -cp print2stdout


if __name__ == '__main__':
    main()
