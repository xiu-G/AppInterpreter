import argparse
import csv
import subprocess
import getAPKNames
import basic_tool
import gator
import os
import add_xml_android_onclick
def parse_args(args_list):
    parser = argparse.ArgumentParser(args_list)
    ## Required parameters
    parser.add_argument("--apk_dir", default=None, type=str,
                        help="apps'dir")
    parser.add_argument("--android_sdk", default=None, type=str,
                        help="android sdk dir" )
    parser.add_argument("--result_dir", default=os.path.realpath("data"), type=str,
                        help="DeepIntent all result dir" )
    parser.add_argument("--gator_root", default=os.path.realpath('gator-IconIntent'), type=str,
                        help="The path of gator-IconIntent")
    parser.add_argument("--image2widget_root", default=os.path.realpath('ImageToWidgetAnalyzer'), type=str,
                        help="The path of image2widget")
    parser.add_argument("--wid_root", default=os.path.realpath('WidImageResolver'), type=str,
                        help="The path of WidImageResolver.")
    parser.add_argument("--callgraph_root", default=os.path.realpath('APKCallGraph'), type=str,
                        help="The path of APKCallGraph.")
    parser.add_argument("--apkname_path", default=os.path.realpath('selectedAPK.txt'), type=str,
                        help="The path of selectedAPK names file.")
    parser.add_argument("--jellybean", default=os.path.realpath('jellybean_allmappings.txt'), type=str,
                        help="The path of jellybean_allmappings file.")
    parser.add_argument("--RetargetedApp_jar", default=os.path.realpath('ic3/RetargetedApp.jar'), type=str,
                        help="The path of RetargetedApp.jar")
    parser.add_argument("--ic3_jar", default=os.path.realpath('ic3/ic3-0.2.0-full.jar'), type=str,
                        help="The path of ic3.jar")
    parser.add_argument("--cc_properties", default=os.path.realpath('ic3/cc.properties'), type=str,
                        help="The path of cc properties")
    parser.add_argument("--time_out", default=30*60, type=float,
                        help="The max time of every step.")
    args = parser.parse_args(args_list)
    return args

def run_cmd(time_out, cmd, output):
    print(' '.join(cmd))
    if time_out == 0:
        return subprocess.run(cmd, stdout=output, stderr=output)
    else:
        try:
            return subprocess.run(cmd, stdout=output, stderr=output, timeout=time_out)
        except subprocess.TimeoutExpired:
            return -50

def run_wid(apk_dir, root_path, result_dir, time_out):
    cp_jars = basic_tool.extract_jar_libs(os.path.join(root_path, "lib"))
    cp_jars = ":" + os.path.join(root_path, "bin") + cp_jars
    cp_jars = ":" + os.path.join(root_path, "resourses") + cp_jars
    cmd = [
        "java","-Xmx12G",
        "-classpath", cp_jars,
        "edu.cwru.android.ui.WidgetIDIconMappingMain",
        apk_dir,
    ]
    log = os.path.join(result_dir, "wid_log.txt")
    log = open(log, mode="w")
    run_cmd(time_out, cmd, log)
    log.close()

def run_img2widget(image2widget_root, result_dir, time_out, out_put, img2widgets, apkname_path):
    root_path = image2widget_root
    cp_jars = basic_tool.extract_jar_libs(os.path.join(root_path, "lib"))
    cp_jars = ":" + os.path.join(root_path, "bin") + cp_jars
    cmd = [
        "java","-Xmx12G",
        "-classpath", cp_jars,
        "ImageToWidgetsAnalyzer",
        out_put,
        out_put,
        img2widgets,
        apkname_path
    ]
    log = os.path.join(result_dir, "img2widget_log.txt")
    log = open(log, mode="w")
    run_cmd(time_out, cmd, log)
    log.close()

def insert_outputmapping(jellybean):
    tmp_dic = {}
    file_content = basic_tool.readContentLists(jellybean)
    for item in file_content:
        if item.startswith("Permission"):
            permission = item.split("Permission:")[1].strip()
            if permission not in tmp_dic:
                tmp_dic[permission] = []
        elif item.startswith("<"):
            tmp = item.split('>')[-1]
            function = item.replace(tmp,"").strip()
            tmp_dic[permission].append(function)
    for permission in tmp_dic:
        for function in tmp_dic[permission]:
            insert = "mysql -ucodecomment -ptest123456 -e 'use cc;INSERT INTO outputmapping (Permission, Method) VALUES (\"{}\", \"{}\");'".format(permission, function)
            # print(insert)
            os.system(insert)

def run_ic3(result_dir, jellybean, apps, android_sdk, RetargetedApp_jar, ic3_jar, cc_properties, time_out):
    output = os.path.join(result_dir, "ic3_log.txt")
    output = open(output, mode="w")
    # mysql_1 = "mysql -ucodecomment -ptest123456 -e 'drop database if exists cc; create database cc'"
    # os.system(mysql_1)
    # mysql_2 = "mysql -ucodecomment -ptest123456 cc < schema"
    # os.system(mysql_2)
    insert_outputmapping(jellybean)
    android_platform = os.path.join(android_sdk, 'platforms')
    # mysql -uroot -pjiaozhuys05311 cc < schema
    for app in apps:
        output.write("----------------------------------------------------------------\n")
        output.write(app+":\n")
        api_level = basic_tool.get_api_version(app)
        if api_level>=30:
            api_level = 29
        # forceAndroidJar=android_platform+"/android-"+api_level+"/android.jar"
        forceAndroidJar=os.path.join(android_platform, 'android-'+str(api_level), 'android.jar')
        app_name = os.path.splitext(os.path.split(app)[1])[0]
        retargetedPath = os.path.join(os.path.join(result_dir, "testspace"), app_name+'.apk')
        ic3_app_path = os.path.join(result_dir, "ic3_output", app_name)
        if os.path.exists(ic3_app_path):
            continue
        os.makedirs(ic3_app_path)
        cmd1 = "timeout 1800 java -Xmx24000m -jar {0} {1} {2} {3}".format(RetargetedApp_jar, forceAndroidJar, app, retargetedPath)
        run_cmd(time_out, cmd1.split(), output)
        cmd2 = "timeout 1800 java -Xmx24000m -jar {0} -apkormanifest {1} -input {2} -cp {3} -db {4} -dbname cc -protobuf {5}".format(ic3_jar, app, retargetedPath, forceAndroidJar, cc_properties, ic3_app_path)
        run_cmd(time_out, cmd2.split(), output)
    output.close()

def run_callgraph(i, apps, root_path, result_dir, apk_dir, sdk_dir, time_out=0):
    cp_jars = basic_tool.extract_jar_libs(os.path.join(root_path, "lib"))
    cp_jars = ":" + os.path.join(root_path, "bin") + cp_jars
    output = os.path.join(result_dir, "callgraph_log.txt"+str(i))
    output = open(output, mode="w")
    android_sdk_platforms = os.path.join(sdk_dir, 'platforms')
    for index, app in enumerate(apps):
        path, name = os.path.split(app)
        name,ext = os.path.splitext(name)
        print(i, index, len(apps))
        if os.path.exists(os.path.join(result_dir, 'dot_output', name, name+'.dot')):
            continue

        output.write("-----------------------------------------\n")
        output.write(app+"\n")
        api_level = basic_tool.get_api_version(app)
        # java -jar APKCallGraph.jar $app  /Your apk folder/ /DeepIntent/IconWidgetAnalysis/Static_Analysis/img2widgets/ /DeepIntent/IconWidgetAnalysis/Static_Analysis/permission_output/ /DeepIntent/IconWidgetAnalysis/Static_Analysis/ic3/output/
        cmd = [
            "java","-Xmx12G",
            "-classpath", cp_jars,
            "APKCallGraph",
            app,
            apk_dir,
            os.path.join(result_dir,"img2widgets/"),
            os.path.join(result_dir,"permission_output/"),
            os.path.join(result_dir,"ic3_output/"),
            str(api_level),
            android_sdk_platforms,
        ]
        run_cmd(time_out, cmd, output)

def run_combine(dirPath, result_dir):
    filepath = os.path.join(result_dir, "permissions.csv")
    output = open(filepath, "w")
    header = ["APK", "Image", "WID", "WID Name", "Layout", "Handler", "Method", "Permissions"]
    writer = csv.DictWriter(output, fieldnames = header)
    writer.writeheader()
    files = os.listdir(dirPath)
    for i in range(len(files)):
        if ".csv" in files[i]:
            print(files[i])
            f = open(os.path.join(dirPath,files[i]), "r")
            reader = csv.reader(f, delimiter = "\t")
            rowNum = 0
            for row in reader:
                if (rowNum == 0):
                    rowNum += 1
                    continue;
                else:
                    writer.writerow({"APK": row[0], "Image": row[1], "WID": row[2], "WID Name": row[3], "Layout": row[4], "Handler": row[5], "Method": row[6], "Permissions": row[7]})
            rowNum += 1

def run_map1tomore(result_dir):
    inputf = os.path.join(result_dir, "permissions.csv")
    inputf2 = "1tomore.txt"
    outputf = os.path.join(result_dir, "outputP.csv")
    methods = dict()
    count = 0
    fin = csv.reader(open(inputf, "r"))
    fin2 = open(inputf2, "r")
    fout = csv.writer(open(outputf, "w"))

    for line in fin2.readlines():
        line = line.strip("\n").rstrip("\t").split("\t")
        temp = list()
        for i in range(1, len(line)):
            temp.append(str(line[i]))
        methods[str(line[0])] = temp

    for line in fin:
        count += 1
        print(count)
        if str(line[6]) in methods.keys():
            line[7] = methods[line[6]]
            print("yes")
            fout.writerow(line)
        else:
            print("no")
            fout.writerow(line)

def run_add_xml_android_onclick(result_dir, output, apps):
    # gator_files = basic_tool.getAllFiles(output, [], '.apk.json')
    for i, app in enumerate(apps):
        print(i, len(apps))
        path, name = os.path.split(app)
        f = os.path.join(output, name+'.json')
        if not os.path.exists(f):
            continue
        apk_name = os.path.splitext(name)[0]
        decode_dir = os.path.join(result_dir, 'decode_dir', apk_name)
        gator_result = f
        wid_result = os.path.join(output, apk_name+'.json')
        add_xml_android_onclick.main(decode_dir, gator_result, wid_result)

def main(args_list):
    args = parse_args(args_list)
    apps = basic_tool.getAllFiles(args.apk_dir, [], ".apk")
    # getAPKNames.main(args.apk_dir)
    # out_put = os.path.join(args.result_dir, "output")
    # gator.main(apps, args.gator_root, args.result_dir, args.android_sdk)
    # ## add xml android:onclick
    # run_add_xml_android_onclick(args.result_dir, out_put)
    ## once
    # run_wid(args.apk_dir, args.wid_root, args.result_dir, args.time_out)
    # basic_tool.mkdir(os.path.join(args.result_dir, "testspace"))
    # basic_tool.mkdir(os.path.join(args.result_dir, "ic3_output"))
    run_ic3(args.result_dir, args.jellybean, apps, args.android_sdk, args.RetargetedApp_jar, args.ic3_jar, args.cc_properties, args.time_out)
    ## once
    img2widgets = os.path.join(args.result_dir, "img2widgets")
    basic_tool.mkdir(os.path.join(img2widgets))

    run_img2widget(args.image2widget_root, args.result_dir, args.time_out, out_put, img2widgets, args.apkname_path)
    run_callgraph(apps, args.callgraph_root, args.result_dir, args.apk_dir, args.android_sdk,)
    # permissions = os.path.join(args.result_dir, "permission_output")
    run_combine(permissions, args.result_dir)
    # # # # python3 map1tomore.py #change the input and output file names and paths at line 4, 5, and 6.
    # run_map1tomore(args.result_dir)



if __name__ == "__main__":
    # apk_dir = os.path.realpath("../../data/text_example/total/apk")
    apk_dir = '/home/data/xiu/apks/test'
    # apk_dirs = ['/home/data/xiu/apks/old_malware','/home/data/xiu/apks/benign']
    # apk_dir = '/home/data/xiu/apks/test'
    # apk_dir = '/home/data/xiu/code-translation/code/guibat/apk'
    android_sdk = "/home/data/xiu/android-sdk"
    # apk_dir = '/mnt/e/WorkSpace/vscode/DeepIntent/data/text_example/total/apk'
    # android_sdk = "/mnt/e/Files/Sdk"
    time_out = 30*60
    args_list = [
                "--apk_dir", apk_dir,
                "--android_sdk", android_sdk
            ]
    main(args_list)
    # for apk_dir in apk_dirs:
    #     args_list = [
    #             "--apk_dir", apk_dir,
    #             "--android_sdk", android_sdk
    #         ]
    #     main(args_list)