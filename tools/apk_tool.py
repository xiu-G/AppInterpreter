import os

def get_api_version(apk):
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

def extract_number(cur_line):
    firstCom = cur_line.find("'")
    secondCom = cur_line.find("'", firstCom + 1)
    levelStr = cur_line[firstCom + 1: secondCom]
    return int(levelStr)

def extract_sdk_api(yml_path, name):
    if not os.path.exists(yml_path):
        return 1000
    with open(yml_path, 'r') as fd:
        for line in fd.readlines():
            if name in line:
                return extract_number(line)
    return -1