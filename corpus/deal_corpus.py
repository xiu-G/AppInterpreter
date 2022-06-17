def read_current_txt(dirs):
    files = basic_tool.getAllFiles(dirs, [], '.txt')
    api_lists = []
    for f in files:
        contents = basic_tool.readContentLists(f)
        class_name = ''
        for line in contents:
            line = line.strip()
            if line:
                words = line.split(' ')
                # print(words)
                if ('package' in words) and ('{' in words):
                    package_name = words[1]
                elif ('class' in words) and ('{' in words):
                    index = words.index('class') + 1
                    class_name = words[index]
                elif ('enum' in words) and ('{' in words):
                    index = words.index('enum') + 1
                    class_name = words[index]
                elif ('interface' in words) and ('{' in words):
                    index = words.index('interface') + 1
                    class_name = words[index]
                elif ('@interface' in words) and ('{' in words):
                    index = words.index('@interface') + 1
                    class_name = words[index]
                elif words[0] == 'method' or words[0]=='ctor':
                    method_items = line.strip().split()
                    new_items = []
                    marks = False
                    left = 0
                    for item in method_items:
                        if item.startswith('@'):
                            left += item.count('(')
                            left -= item.count(')')
                            marks = True
                            if left == 0:
                                marks = False
                            continue
                        # if (item.endswith('},') or 'permission' in item)and marks:
                        #     continue
                        if marks and left>0:
                            left += item.count('(')
                            left -= item.count(')')
                            if left == 0:
                                marks = False
                            continue
                        else:
                            marks = False
                            new_items.append(item)
                    line_new = ' '.join(new_items)
                    methed_info = line_new.split(')')[0]
                    method_name_info = methed_info.split('(')[0]
                    try:
                        method_param = methed_info.split('(')[1]
                    except Exception:
                        print('hereh')
                    info_split = method_name_info.split(' ')
                    return_type = info_split[-2]
                    if info_split[-3].endswith('>'):
                        return_type = ' '.join([info_split[-3], info_split[-2]])
                    method_name = info_split[-1]

                    method = method_name + '(' + method_param + ')'
                    save_data = '<' + package_name + '.' + class_name + ': ' + return_type + ' ' + method + '>'
                    # save_data = save_data.replace('@IntRange','int').replace('@FloatRange)','float')
                    pattern = re.compile(r'@[A-Za-z|.| ]*')
                    save_data = pattern.sub('', save_data)
                    api_lists.append(save_data)
                else:
                    continue
                while class_name.endswith(','):
                    class_name += words[index+1]
                    index += 1
    return api_lists