import os

import deal_corpus
from tools import basic_tool

# 词组形式

def save_database(source_dir, api_result):
    api_lists = read_current_txt(source_dir)
    print(len(api_lists))
    api_lists = list(set(api_lists))
    print(len(api_lists))
    basic_tool.writeContentLists(api_result, api_lists)


if __name__ == '__main__':
    source_base_dir = 'data/source_words/database/android/f_base'
    api_references = 'data/source_words/database/android/api_reference'
    api_result = 'data/source_words/database/android_api_list.txt'
    # if not os.path.exists(api_result):
    save_database(source_dir, api_result)
    