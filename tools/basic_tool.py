import os
import pickle
import subprocess
import sys
import codecs
import json
import random
import string
import glob
import numpy as np

def mkdir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def getAllFiles(dirPath, fileList, fileType):
    if not os.path.exists(dirPath):
        return []
    tmpDirs = os.listdir(dirPath)
    for tmpDir in tmpDirs:
        filePath = os.path.join(dirPath, tmpDir)
        if os.path.isdir(filePath):
            fileList = getAllFiles(filePath, fileList, fileType)
        else:
            if fileType == '':
                fileList.append(filePath)
            elif fileType != '' and filePath.endswith(fileType):
                fileList.append(filePath)
    return fileList

def readContentLists(filePath):
    if not os.path.exists(filePath):
        return []
    with codecs.open(filePath, "r", "utf8") as r:
        contents = r.readlines()
    return contents

def readContentText(filePath):
    with codecs.open(filePath, "r", "utf8") as r:
        contents = r.read()
    return contents

def readContentByte(filePath):
    with codecs.open(filePath, "rb") as r:
        contents = r.read()
    return str(contents)

def readContentByteList(filePath):
    with codecs.open(filePath, "rb") as r:
        contents = r.readlines()
    return contents

def writeContentLists(filePath, contents):
    new_contents = []
    for i, line in enumerate(contents):
        if not str(line).endswith('\n'):
            new_contents.append(str(contents[i]) + "\n")
        else:
            new_contents.append(str(contents[i]))
    with codecs.open(filePath, "w", "utf8") as w:
        w.writelines(new_contents)

def writeContentLists_mode(filePath, contents, mode):
    new_contents = []
    for i, line in enumerate(contents):
        if not line.endswith('\n'):
            new_contents.append(contents[i] + "\n")
        else:
            new_contents.append(contents[i])
    with codecs.open(filePath, mode, "utf8") as w:
        w.writelines(new_contents)

def writeContex_mode(filePath, text, mode):
    if not text.endswith('\n'):
        text += "\n"
    with codecs.open(filePath, mode, "utf8") as w:
        w.write(text)

def readContentLists_withoutbr(filePath):
    with codecs.open(filePath) as r:
        contents = r.readlines()
    for i, line in enumerate(contents):
        contents[i]=line.strip()
    return contents
'''
write json content to file
'''
def write_json_list(dic_list, file_path):
    with codecs.open(file_path, 'w', 'utf8') as f:
        for line in dic_list:
            f.write(json.dumps(line, cls=NpEncoder)+'\n')

'''
write json content to file
'''
def write_json(dic, file_path):
    with codecs.open(file_path, 'w', 'utf8') as f:
        f.write(json.dumps(dic, cls=NpEncoder)+'\n')

'''
get json content from file
'''
def read_json(content):
    if len(content.strip()) == 0:
        return {}
    js = json.loads(content.strip())
    return js

'''
get json content from file
'''
def read_json_list(content):
    data_list = []
    for line in content:
        js = json.loads(line.strip())
        data_list.append(js)
    return data_list

def read_json_dic(content):
    data_dic = {}
    for i, line in enumerate(content):
        js = json.loads(line.strip())
        if i == 0:
            data_dic= {js[0]:js[1]}
        else:
            data_dic[js[0]] = js[1]
    return data_dic

'''
get to run list
'''
def to_run_files(file_list1, file_list2):
    file1_name = {}
    file2_name = {}
    to_run_list = []
    for file1 in file_list1:
        file1_name[os.path.splitext(os.path.split(file1)[1])[0]] = file1
    for file2 in file_list2:
        file2_name[os.path.splitext(os.path.split(file2)[1])[0]] = file2
    for name in file1_name:
        if name not in file2_name:
            to_run_list.append(file1_name[name])
    return to_run_list

def random_string():
    num = random.randint(1,8)
    salt = ''.join(random.sample(string.ascii_letters, num))
    return salt.lower()

def extract_jar_libs(path_base):
    if not os.path.exists(path_base):
        return ""
    jars = glob.glob(path_base + "/*.jar")
    return ":" + ":".join(jars) if len(jars) > 0 else ""

def splitList(myList, n):
    resultList = []
    size = len(myList)
    if size < n:
        resultList.append(myList)
    else:
        quotient = int (size / n)
        remainder = size % n
        offset = 0
        myLen = 0
        if quotient > 0:
            myLen = n
        else:
            myLen = remainder
        start = 0
        end = 0
        tempList = None
        for i in range(0, myLen):
            if remainder != 0:
                remainder = remainder - 1
                offset = 1
            else:
                offset = 0
            end = start + quotient + offset
            tempList = myList[start:end]
            start = end
            resultList.append(tempList)
    return resultList



class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)

def run_cmd(time_out, cmd, output):
    if time_out == 0:
        return subprocess.run(cmd, stdout=output, stderr=output)
    else:
        try:
            return subprocess.run(cmd, stdout=output, stderr=output, timeout=time_out)
        except subprocess.TimeoutExpired:
            return -50

def save_pkl_data(path, data):
    """Save data in pkl format (save storage space).
    """
    with open(path, 'wb') as fo:
        pickle.dump(data, fo)


def load_pkl_data(path):
    """Load pkl data from given path.
    """
    with open(path, 'rb') as fi:
        data = pickle.load(fi)
    return data
