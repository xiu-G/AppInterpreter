import argparse
import os
from tools import basic_tool
IMAGE2WIDGET_ROOT = 'app_behavior/ImageToWidgetAnalyzer'
TIME_OUT = 3600


def loadFile(dirPath):
	files = basic_tool.getAllFiles(dirPath, [], '')
	for i in range(len(files)):
		if ".apk" in files[i]:
			getNames(str(files[i]))

def getNames(fileName):
    fileName = os.path.splitext(os.path.split(fileName)[1])[0]
    if os.path.exists('selectedAPK.txt'):
        contents = basic_tool.readContentLists_withoutbr("selectedAPK.txt")
        if fileName not in contents:
            f = open("selectedAPK.txt", "a")
            f.write(fileName + "\n")
            f.close()
    else:
        f = open("selectedAPK.txt", "w")
        f.write(fileName + "\n")
        f.close()
                    
def set_args():
    parser = argparse.ArgumentParser(
        description='ImageToWidgetAnalyzer: map to a csv file.')
    parser.add_argument('-r', '--image2widget_root',
                        dest='image2widget_root',
                        default=IMAGE2WIDGET_ROOT,
                        help='path to root dir')

    parser.add_argument('-o', '--output_dir',
                        dest='output_dir',
                        required=True,
                        default='',
                        help='dir to output result')

    parser.add_argument('-go', '--gator_output_dir',
                        dest='gator_output_dir',
                        required=True,
                        default='',
                        help='dir of gator output result')

    parser.add_argument('--log',
                        dest='log_path',
                        metavar='LOG_FILE',
                        default='',
                        required=False,
                        help='save log to disk')
    
    parser.add_argument('-t', '--timeout',
                        dest='time_out',
                        metavar='TIMEOUT',
                        default=TIME_OUT,
                        required=False,
                        help='timeout in seconds')
    return parser

def run_img2widget(apk_dir, result_dir):
    loadFile(apk_dir)
    log = os.path.join(result_dir, "img2widget_log.txt")
    img2widgets = os.path.join(result_dir, "img2widgets")
    basic_tool.mkdir(img2widgets)
    parser = set_args()
    args = [
        '-o', img2widgets,
        '--log', log,
        '-go', os.path.join(result_dir, "output"),
    ]
    args, unknown = parser.parse_known_args(args)
    cp_jars = basic_tool.extract_jar_libs(os.path.join(args.image2widget_root, "lib"))
    cp_jars = ":" + os.path.join(args.image2widget_root, "bin") + cp_jars
    cmd = [
        "java","-Xmx12G",
        "-classpath", cp_jars,
        "ImageToWidgetsAnalyzer",
        args.gator_output_dir,
        args.gator_output_dir,
        args.output_dir,
        os.path.realpath('selectedAPK.txt')
    ]
    log = open(args.log_path, mode="w")
    basic_tool.run_cmd(args.time_out, cmd, log)
    log.close()



if __name__ == '__main__':
    apk_dirs = ['/home/data/xiu/code-translation/code/guibat/apk']
    # apk_dirs = ['/home/data/yuec/DeepIntent/data/example/benign', '/home/data/yuec/DeepIntent/data/example/malicious']
    result_dir = 'data'
    for apk_dir in apk_dirs:
        run_img2widget(apk_dir, result_dir)