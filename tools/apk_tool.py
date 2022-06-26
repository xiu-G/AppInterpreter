import glob
import os
import subprocess

from tools.basic_tool import extract_jar_libs

def decode_apk(apk_path, decode_path, frame_path="", output=None):
    if frame_path=="":
        cmd =["java", "-jar", "apktool.jar", "d", apk_path, "-o", decode_path, "-f"]
    else:
        cmd = ["java", "-jar", "apktool.jar", "d", apk_path,
            "--frame-path", frame_path,
            "-o", decode_path, "-f"]
    print(' '.join(cmd))
    return subprocess.run(cmd, stdout=output, stderr=None)

def extract_target_api(yml_path, name):
    if not os.path.exists(yml_path):
        return -1
    with open(yml_path, 'r') as fd:
        for line in fd.readlines():
            if name in line:
                return extract_number(line)
    return -1

def extract_target_api_from_aapt(apk):
    output = os.popen("aapt dump badging %s" % apk).read()
    lines = output.splitlines()
    minSdkVersion, targetSdkSdkVersion, platformBuildVersionName = 0, 0, 0
    sdk_min_version = 8
    sdk_max_version = 30
    sdk_default_version = 18
    for line in lines:
        if "sdkVersion" in line:
            minSdkVersion = int(line.split(':')[-1].strip()[1:-1])
        elif "targetSdkVersion" in line:
            try:
                targetSdkSdkVersion = int(line.split(':')[-1].strip()[1:-1])
                break
            except Exception:
                pass
            break
        elif "platformBuildVersionName" in line:
            tmp = line.split('=')[-1].strip()[1:-1]
            try:
                if tmp != "":
                    platformBuildVersionName = int(tmp)
                # break
            except ValueError:
                continue
    if targetSdkSdkVersion >= sdk_min_version and targetSdkSdkVersion <= sdk_max_version:
        return targetSdkSdkVersion
    elif platformBuildVersionName >= sdk_min_version and platformBuildVersionName <= sdk_max_version:
        return platformBuildVersionName
    elif minSdkVersion <= sdk_min_version:
        return sdk_min_version
    else:
        return sdk_default_version

def get_api_version(apk, decode_dir="", api_level=-1):
    if api_level != '-1':
        target_level = int(api_level)
    if decode_dir != "":
        target_level = extract_target_api(os.path.join(decode_dir, 'apktool.yml'), "targetSdkVersion")
    if target_level == -1:
        target_level = extract_target_api_from_aapt(apk)
    if target_level == -1 or target_level >= 30:
        print('...... cannot determine the target API level for APK. Fallback to use 27.')
        target_level = 27
    elif target_level < 10:
        print('...... target API level is below 10. Force to use 10.')
        target_level = 10
    elif target_level > 100:
        return -1


def extract_number(cur_line):
    firstCom = cur_line.find("'")
    secondCom = cur_line.find("'", firstCom + 1)
    levelStr = cur_line[firstCom + 1: secondCom]
    return int(levelStr)


def find_best_google_api(sdk_path, api_level):
    google_api_lib_dirs = glob.glob(sdk_path + "/add-ons/addon-google_apis-google-*")
    available_levels = []
    for item in google_api_lib_dirs:
        id = item.rfind('-')
        digits = int(item[id + 1:])
        available_levels.append(digits)
    available_levels.sort(reverse=True)
    if len(available_levels) == 0:
        return 0
    if api_level not in available_levels:
        api_level = available_levels[0]
    return sdk_path + "/add-ons/addon-google_apis-google-" + str(api_level)

def add_google(sdkpath, apk_level, android_jar):
    google_api_dir = find_best_google_api(sdkpath, apk_level)
    if google_api_dir == 0 or not os.path.exists(google_api_dir):
        print(">>>>>> Google API Level: %d not installed, try to install with sdkmanager..." % apk_level)
        sub_cmd = [os.path.join(sdkpath, 'tools', 'bin', 'sdkmanager'),
                    'add-ons;addon-google_apis-google-%s' % apk_level]
        # print('>>>>>> %s' % ' '.join(sub_cmd))
        if subprocess.call(sub_cmd) != 0:
            sub_cmd = [os.path.join(sdkpath, 'tools', 'bin', 'sdkmanager'),
                        'add-ons;addon-google_apis-google-24']
            # print('>>>>>> %s' % ' '.join(sub_cmd))
            subprocess.call(sub_cmd)
        google_api_dir = find_best_google_api(sdkpath, apk_level)
    google_api = extract_jar_libs(google_api_dir + "/libs")
    if len(google_api) != 0:
        android_jar = android_jar + google_api
    return android_jar