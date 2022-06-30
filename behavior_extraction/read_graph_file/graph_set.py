
from copy import deepcopy
import subprocess
import time
# import func_timeout
# from func_timeout import func_set_timeout


# print_log = open('a.txt','a')
# time_limit2 = 2*60
class GraphError(Exception):
    pass


class graph:
    def __init__(self,gdict=None, apk='', packages=''):
        if gdict is None:
            gdict = {}
        self.gdict = gdict
        self.in_gdict = {}
        self.stack = []
        self.name = apk
        self.path_mem = {}
        self.android_lib_mem = {}
        self.exist_libs = {}
        self.semantics = []
        self.packages = packages
        self.goon = True
        self.start_time = time.time()
        self.time_limit = 3000
        # self.time_limit = 1000
        self.android_length_limit = 15000
        # self.android_length_limit = 1500000
        self.depth = 0
        self.android_length = 0
        self.path_length = 0
    
    def set_name(self, name):
        self.name = name

    def count_number(self):
        node_number = 0
        edge_number = 0
        for node in self.gdict:
            node_number += 1
            edge_number += len(self.gdict[node])
        print("node_number:"+str(node_number))
        print("edge_number:"+str(edge_number))
        return node_number, edge_number

    def edges(self, node):
        return self.find_out_edges(node)
    
    def add_node(self, node):
        if node not in self.gdict:
            self.gdict[node] = []
    
    def del_node(self, node):
        if node not in self.gdict:
            return

        edges = self.find_out_edges(node)
        self.gdict.pop(node)
        for edge in edges:
            self.in_gdict[edge].remove(node)

        if node in self.in_gdict:
            in_nodes = deepcopy(self.in_gdict[node])

            for in_node in in_nodes:
                self.gdict[in_node].remove(node)
                self.in_gdict[node].remove(in_node)
        
    def add_edge(self, vrtx1, vrtx2):
        if vrtx1 in self.gdict:
            if vrtx2 not in self.gdict[vrtx1]:
                self.gdict[vrtx1].append(vrtx2)
        else:
            self.gdict[vrtx1] = [vrtx2]

        if vrtx2 in self.in_gdict:
            if vrtx1 not in self.in_gdict[vrtx2]:
                self.in_gdict[vrtx2].append(vrtx1)
        else:
            self.in_gdict[vrtx2] = [vrtx1]


    def find_out_edges(self, node):
        return self.gdict[node]
    
    def get_out_degrees(self, node):
        outDegree = len(self.gdict.get(node, []))
        return outDegree

    def get_in_degrees(self, node):
        inDegree = len(self.in_gdict.get(node, []))
        return inDegree

    def get_start_node(self):
        node_list = []
        for i, node in enumerate(self.gdict):
            if self.get_in_degrees(node) == 0:
                node_list.append(node)
            elif self.get_in_degrees(node) == 1:  # in node is self
                if node in self.find_out_edges(node):
                    node_list.append(node)
        return node_list
    
    # @func_set_timeout(time_limit)
    def get_xml(self, function, ui_info, xml_name):
        # print(type(function))
        xml_list = []
        for node in ui_info:
            if '|' not in node['name']:
                continue
            layout = node['name'].split('|')[-1].split(']')[0].split('layout_')[-1]+'.xml'
            class_name = node['name'].split(']')[0].split('[')[1]
            function_class = function.split(':')[0].replace('<','')
            if function_class == class_name:
                if layout not in xml_list:
                    xml_list.append(layout)
        if xml_list == []:
            return xml_name
        return xml_list
    
    def get_widget_texts(self, widget_id, widget_infos, xml_names):
        widget_information = []
        for widget_info in widget_infos:
            # print(widget_info)
            # sys.exit()
            xml_name = widget_info[1][0]
            if xml_name in xml_names:
                widget_id_tmp = widget_info[0][1][0]
                if widget_id == widget_id_tmp:
                    widget_information.append(widget_info)
        return widget_information
    
    def get_widget_texts2(self, widget_infos, xml_names):
        widget_information = []
        for widget_info in widget_infos:
            # print(widget_info)
            # sys.exit()
            xml_name = widget_info[1][0]
            if xml_name in xml_names:
                widget_information.append(widget_info)
        return widget_information

    def set_semantics(self, widget_infos):
        widget_information = []
        for widget_info in widget_infos:
            widget_information.append(widget_info)
        self.semantics = widget_information
  
    def get_widget(self, function, ui_info, widget_info, xml_name):
        # print(type(function))
        widget_list = []
        find_flag = False
        for node in ui_info:
            if '|' not in node['name']:
                continue
            views = node['views']
            for view in views:
                handlers = view['handlers']
                for handler_list in handlers:
                    for handler in handler_list['handlers']:
                        if function == handler:
                            # print(function)
                            # print(handler)
                            widget_id = view['name']
                            if '|' in widget_id and 'widget' in widget_id and 'Layout' not in widget_id: 
                                widget_id = widget_id.split('|')[1].split(']')[0]
                                widget_information = self.get_widget_texts(widget_id, widget_info, xml_name)
                                widget_list.append([widget_id, widget_information])
                                find_flag = True
                        # sys.exit()
        if find_flag == False:
            widget_information = self.get_widget_texts2(widget_info, xml_name)
            if widget_information == []:
                widget_information = self.semantics
            widget_list.append(['', widget_information])


            # views = node['views']
            # for view in views:
            #     handlers = view['handlers']
            #     for handler in handlers:
            #         methods = handler['handlers']
            #         if function in methods:
            #             if layout not in xml_list:
            #                 xml_list.append(layout)
        return widget_list


    def get_subgraph(self, node_start, path_list, android_path_list, ui_info, widget_info, xml_name, lib_num, android_depth, i=0, j=0):
        if '<net.lepeng.batterydoctor.IgnoreListActivity: void onCreate(android.os.Bundle)>' in node_start:
            print()
        self.depth += 1
        if self.goon == False:
            return
        if time.time()-self.start_time > self.time_limit or self.android_length > self.android_length_limit :
            self.goon = False
            return
        out_edges = self.find_out_edges(node_start)
        if len(out_edges) > 100 and ('click' in self.stack[-1].lower() or 'start(' in self.stack[-1].lower() or 'schedule' in self.stack[-1].lower() or 'asynctask execute' in self.stack[-1].lower() or 'sendmessage(' in self.stack[-1].lower()):
            stack_dics = {}
            new_out_edges = []
            stacks = self.stack
            for stack in stacks:
                stack_dics[stack.split(':')[0].split('$')[0].strip()]=""
            for out_edge in out_edges:
                if 'click' not in out_edge.lower() and 'task' not in out_edge.lower() and 'schedule' not in out_edge.lower() and 'execute(' not in out_edge.lower() and 'handleMessage(' not in out_edge.lower() and 'run(' not in out_edge.lower() and 'doinbackground' not in out_edge.lower():
                    print(out_edge)
                    new_out_edges.append(out_edge)
                elif out_edge.split(':')[0].split('$')[0].strip() in stack_dics:
                    new_out_edges.append(out_edge)
                else:
                    # print(out_edge)
                    pass
            out_edges = new_out_edges
            print(new_out_edges)
        elif len(out_edges)>100:
            print(self.stack[-1].lower())

        i += 1
        if out_edges == []:
            self.stack.pop()
        elif lib_num == android_depth:
            self.stack.pop()
        else:
            ori_xml = xml_name
            for index, out_edge in enumerate(out_edges):
                j = index+1
                if out_edge in self.path_mem.keys():
                    path_list.append(self.path_mem[out_edge])
                    if self.is_android_lib(out_edge):
                        android_path_list.append(self.android_lib_mem[out_edge])
                        self.android_length += len(self.android_lib_mem[out_edge])
                else:
                    # print(i, j, len(out_edges), node_start)
                    # print(i, j, len(out_edges), node_start, file = print_log)
                    xml_name = self.get_xml(out_edge, ui_info, ori_xml)
                    widgets = self.get_widget(out_edge, ui_info, widget_info, xml_name)
                    # if len(xml_name) > 0:
                    #     print(out_edge, xml_name)
                        # sys.exit()
                    if out_edge in self.stack:
                        path_temp = []
                        # print(out_edge)
                        path_temp.append([out_edge, widgets, xml_name])
                        path_list.append(path_temp)
                        if self.is_android_lib(out_edge):
                            android_path_list.append(path_temp)
                            self.android_length += len(path_temp)
                    else:
                        path_temp = []
                        android_path_temp = []
                        self.stack.append(out_edge)
                        # print(out_edge)
                        path_temp.append([out_edge, widgets, xml_name])
                        if self.is_android_lib(out_edge):
                            android_path_temp.append([out_edge, widgets, xml_name])
                            self.get_subgraph(out_edge, path_temp, android_path_temp, ui_info, widget_info, xml_name, lib_num+1, android_depth, i, j)
                        else:
                            self.get_subgraph(out_edge, path_temp, android_path_temp, ui_info, widget_info, xml_name, 0, android_depth, i, j)
                        path_list.append(path_temp)
                        if len(android_path_temp) != 0:
                            android_path_list.append(android_path_temp)
                            self.android_length += len(android_path_temp)

            self.path_mem[node_start] = path_list
            if self.is_android_lib(node_start):
                self.android_lib_mem[node_start] = android_path_list
            self.stack.pop()
    
    def is_third_lib(self, node, libs):
        class_name = node[1:-1]
        items = class_name.split('.')
        matchItems = class_name
        if len(items) > 3:
            matchItems = items[0]+"."+items[1]+"."+items[2]+"."
        if matchItems in self.exist_libs:
            return self.exist_libs[matchItems]
        for lib in libs:
            if lib.startswith('L'):
                lib = lib.replace('/','.')[1:]
            if class_name.startswith(lib):
                self.exist_libs[matchItems] = True
                return True
        self.exist_libs[matchItems] = False
        return False

    def is_android_lib(self, node):
        android_libs = ['androidx','android','java','javax','com.android','dalvik','kotlin','sun']
        if_api = False
        for android in android_libs:
            if node[1:].startswith(android):
                if_api = True
                break
        return if_api

    # @func_set_timeout(time_limit2)
    def get_paths(self, ui_info, widget_info, thirdlibs, android_depth=5):
        path_list = []
        android_path_list = []
        node_list = self.get_start_node()
        start_time = time.time()
        for i, node_start in enumerate(node_list):
            # print(i, len(node_start), len(node_list))
            if not node_start.startswith('<'+self.packages):
                # if len(thirdlibs)>0:
                #     if self.is_third_lib(node_start, thirdlibs):
                #         continue
                # if self.is_android_lib(node_start):
                #     continue
                continue
            elif node_start.startswith('<'+self.packages+'.R$'):
                continue
            elif node_start.startswith('<'+self.packages+'.R:'):
                continue
            elif node_start.startswith('<'+self.packages+'.BuildConfig:'):
                continue
            self.path_length += 1
            if node_start in self.path_mem.keys():
                path_list.append(self.path_mem[node_start])
            else:
                path_temp = []
                android_path_temp = []
                self.stack.append(node_start)
                # print(node_start)
                xml_name = self.get_xml(node_start, ui_info, [])
                widgets = self.get_widget(node_start, ui_info, widget_info, xml_name)
                # if len(xml_name) > 0:
                #      print(node_start, xml_name)
                #      sys.exit()
                path_temp.append([node_start, widgets, xml_name])
                if self.is_android_lib(node_start):
                    lib_num = 1
                else:
                    lib_num = 0
                
                    self.goon = True
                    self.start_time = time.time()
                    self.android_length = 0
                    self.depth = 1
                    self.get_subgraph(node_start, path_temp, android_path_temp, ui_info, widget_info, xml_name, lib_num, android_depth, 0, 0)
                    path_list.append(path_temp)
                    android_path_list.append(android_path_temp)
                    
                    if self.goon == False:
                        return [], [] 
        return path_list, android_path_list



if __name__ == "__main__":
    dot_path = "/home/data/xiu/code-translation/code/DeepIntent/data/dot_output/com.wkow.android.weather/com.wkow.android.weather.dot"
    #"/home/data/xiu/code-translation/code/DeepIntent/data/dot_output/5cb8e0edb98794792346304a5065b69e/5cb8e0edb98794792346304a5065b69e.dot"
    apk_json_path = "/home/data/xiu/code-translation/code/DeepIntent/data/output/com.wkow.android.weather.apk.json"
    from tools import basic_tool
    from read_graph_file import read_dot
    third_libs_file = '/home/data/xiu/code-translation/code/CodeComment/source_data/liteRadar_3rdLibs'
    third_libs = basic_tool.readContentLists_withoutbr(third_libs_file)
    contents = basic_tool.readContentLists(dot_path)
    graph = read_dot.construct_graph_without_dummyMainMethod(contents, dot_path)
    ui_info = {}
    path_list = graph.get_paths(ui_info, third_libs)
    key = {'path':path_list}
    basic_tool.write_json(key, 'a1.json')

   