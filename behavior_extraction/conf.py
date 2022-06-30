
import argparse


def set_args():
    parser = argparse.ArgumentParser(
        description='behavior extraction')
        # add_argument('--path_app', type=str, required=True)
    parser.add_argument('--filters_words', default=[], type=list)
    parser.add_argument('--third_libs', default=[], type=list)
    parser.add_argument('--api_to_name_file', default='', type=str)
    parser.add_argument('--result_dir_root', default='data', type=str)
    parser.add_argument('--filters_behaviors_dir', default='', type=str)
    
    parser.add_argument('-a', '--apk_file', dest='apk_file', default='', type=str)
    parser.add_argument('--app_name', default='', type=str)
    parser.add_argument('--app_result_dir', default='', type=str)
    parser.add_argument('--important_api_path', default='', type=str)
    return parser
    
    