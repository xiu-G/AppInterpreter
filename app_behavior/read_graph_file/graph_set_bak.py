
from copy import deepcopy

from func_timeout import func_set_timeout
import func_timeout
# import func_timeout
# from func_timeout import func_set_timeout
print_log = open('a.txt','a')

time_limit = 2*60
class GraphError(Exception):
    pass

class graph:
    def __init__(self,gdict=None, apk=''):
        if gdict is None:
            gdict = {}
        self.gdict = gdict
        self.in_gdict = {}
        self.stack = []
        self.name = apk
        self.exist_libs = {}
    
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
    # def get_subgraph(self, node_start, path_list, i=0, j=0):
    #     out_edges = self.find_out_edges(node_start)
    #     i += 1
    #     if out_edges == []:
    #         self.stack.pop()
    #     else:
    #         for index, out_edge in enumerate(out_edges):
    #             j = index+1
    #             # print(i, j, len(out_edges), node_start, file = print_log)
    #             if out_edge in self.stack:
    #                 path_temp = []
    #                 path_temp.append(out_edge)
    #                 path_list.append(path_temp)
    #             else:
    #                 path_temp = []
    #                 path_temp.append(out_edge)
    #                 self.stack.append(out_edge)
    #                 self.get_subgraph(out_edge, path_temp, i, j)
    #                 path_list.append(path_temp)
    #         self.stack.pop()
    
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
    
    # def get_paths(self, thirdlibs=[]):
    #     path_list = []
    #     path_total = []
    #     node_list = self.get_start_node()
    #     for i, node_start in enumerate(node_list):
    #         if len(thirdlibs)>0:
    #             if self.is_third_lib(node_start, thirdlibs):
    #                 continue
    #         path_temp = []
    #         self.stack.append(node_start)
    #         path_temp.append(node_start)
    #         try:
    #             self.get_subgraph(node_start, path_temp, 0, 0)
    #         except func_timeout.exceptions.FunctionTimedOut:
    #             print_log = open('time_out_api_sequence.txt','a')
    #             print('time out')
    #             print_log.write(self.name+'\n')
    #             print_log.close()
    #             continue
    #         path_list.append(path_temp)
    #     return path_list
        
    # @func_set_timeout(time_limit)
    def get_xml(self, function, ui_info):
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
            # views = node['views']
            # for view in views:
            #     handlers = view['handlers']
            #     for handler in handlers:
            #         methods = handler['handlers']
            #         if function in methods:
            #             if layout not in xml_list:
            #                 xml_list.append(layout)
        return xml_list
    
    def get_widget(self, function, ui_info):
        # print(type(function))
        widget_list = []
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
                            if '|' in widget_id and ('ImageButton' in widget_id or 'ImageView' in widget_id or 'TextView' in widget_id):
                                widget_id = widget_id.split('|')[1].split(']')[0]

                                widget_list.append(widget_id)
                        # sys.exit()


            # views = node['views']
            # for view in views:
            #     handlers = view['handlers']
            #     for handler in handlers:
            #         methods = handler['handlers']
            #         if function in methods:
            #             if layout not in xml_list:
            #                 xml_list.append(layout)
        return widget_list

    
    @func_set_timeout(time_limit)
    def get_subgraph_with_ui(self, node_start, path_list, ui_info, i=0, j=0):
        out_edges = self.find_out_edges(node_start)
        i += 1
        if out_edges == []:
            self.stack.pop()
        else:
            for index, out_edge in enumerate(out_edges):
                j = index+1
                print(i, j, len(out_edges), node_start, file = print_log)
                xml_name = self.get_xml(out_edge, ui_info)
                widgets = self.get_widget(out_edge, ui_info)
                # if len(xml_name) > 0:
                #     print(out_edge, xml_name)
                    # sys.exit()
                if out_edge in self.stack:
                    path_temp = []
                    # print(out_edge)
                    path_temp.append([out_edge, widgets, xml_name])
                    path_list.append(path_temp)
                else:
                    path_temp = []
                    self.stack.append(out_edge)
                    # print(out_edge)
                    path_temp.append([out_edge, widgets, xml_name])
                    self.get_subgraph_with_ui(out_edge, path_temp, ui_info, i, j)
                    path_list.append(path_temp)
            self.stack.pop()

    def get_paths_with_ui(self, ui_info, thirdlibs=[]):
        path_list = []
        path_total = []
        node_list = self.get_start_node()
        for i, node_start in enumerate(node_list):
            if len(thirdlibs)>0:
                if self.is_third_lib(node_start, thirdlibs):
                    continue
            path_temp = []
            print("==============="+node_start, file = print_log)
            self.stack.append(node_start)
            xml_name = self.get_xml(node_start, ui_info)
            widgets = self.get_widget(node_start, ui_info)
            path_temp.append([node_start, widgets, xml_name])
            try:
                self.get_subgraph_with_ui(node_start, path_temp, ui_info, 0, 0)
            except:  # func_timeout.exceptions.FunctionTimedOut:
                # print_log = open('time_out_api_sequence.txt','a')
                # print('time out')
                # print_log.write(self.name+'\n')
                # print_log.close()
                continue
            path_list.append(path_temp)
        return path_list

    def get_subgraph(self, node_start, path_list, ui_info, i=0, j=0):
        out_edges = self.find_out_edges(node_start)
        i += 1
        if out_edges == []:
            self.stack.pop()
        else:
            for index, out_edge in enumerate(out_edges):
                j = index+1
                # print(i, j, len(out_edges), node_start, file = print_log)
                xml_name = self.get_xml(out_edge, ui_info)
                widgets = self.get_widget(out_edge, ui_info)
                # if len(xml_name) > 0:
                #     print(out_edge, xml_name)
                    # sys.exit()
                if out_edge in self.stack:
                    path_temp = []
                    # print(out_edge)
                    path_temp.append([out_edge, widgets, xml_name])
                    path_list.append(path_temp)
                else:
                    path_temp = []
                    self.stack.append(out_edge)
                    # print(out_edge)
                    path_temp.append([out_edge, widgets, xml_name])
                    self.get_subgraph(out_edge, path_temp, ui_info, i, j)
                    path_list.append(path_temp)
            self.stack.pop()
    
    
    def get_paths(self, ui_info):
        path_list = []
        path_total = []
        node_list = self.get_start_node()
        for i, node_start in enumerate(node_list):
            # print(i, len(node_list))
            # print(node_start)
            # sys.exit()
            path_temp = []

            self.stack.append(node_start)
            # print(node_start)
            xml_name = self.get_xml(node_start, ui_info)
            widgets = self.get_widget(node_start, ui_info)
            # if len(xml_name) > 0:
            #      print(node_start, xml_name)
            #      sys.exit()
            path_temp.append([node_start, widgets, xml_name])
            try:
                self.get_subgraph(node_start, path_temp, ui_info, 0, 0)
            except func_timeout.exceptions.FunctionTimedOut:
                print_log = open('time_out_api_sequence.txt','a')
                print('time out')
                print_log.write(self.name+'\n')
                print_log.write(node_start + '\n')
                print_log.close()
                continue
            path_list.append(path_temp)
        return path_list

def construct_graph_without_dummyMainMethod(contents, dot_path):
    g = graph(apk=dot_path)
    if 'digraph "callgraph" {' in contents[0]:
        for line in contents:
            if "->" in line:
                items = line.split("->")
                src = items[0].strip().split('"')[1]
                if src.startswith("<dummyMainClass:"):
                    continue
                tar = items[1].strip().split('"')[1]
                g.add_node(src)
                g.add_node(tar)
                g.add_edge(src, tar)
            elif line.strip().startswith('"<'):
                src = line.strip().split('"')[1]
                if src.startswith("<dummyMainClass:"):
                    continue
                g.add_node(src)
    else:
        node_dic = {}
        for line in contents:
            # print(line)
            if "->" in line:
                items = line.split("->")
                src = items[0].strip()
                tar = items[1].strip()[:-1]
                if src not in node_dic:
                    continue
                # if '<dummyMainClass:' in node_dic[src]:
                #     continue
                # print(src, tar)
                g.add_edge(node_dic[src], node_dic[tar])
                # print("add edge")
            elif 'label="' in line.strip():
                label = line.strip().split('"')[1]
                if '<dummyMainClass:' in label:
                    continue
                node = line.split('[')[0].strip()
                node_dic[node] = label
                g.add_node(label)
    return g

if __name__ == "__main__":
    dot_path = "/home/data/xiu/code-translation/code/DeepIntent/data/dot_output/net.chanel.weather.forecast.accu/net.chanel.weather.forecast.accu.dot"
    #"/home/data/xiu/code-translation/code/DeepIntent/data/dot_output/5cb8e0edb98794792346304a5065b69e/5cb8e0edb98794792346304a5065b69e.dot"
    apk_json_path = "/home/data/xiu/code-translation/code/DeepIntent/data/output/net.chanel.weather.forecast.accu.apk.json"
    # "/home/data/xiu/code-translation/code/DeepIntent/data/output_bak/5cb8e0edb98794792346304a5065b69e.apk.json"
    from tools import basic_tool
    from read_graph_file import read_dot

    contents = basic_tool.readContentLists(dot_path)
    graph = construct_graph_without_dummyMainMethod(contents, dot_path)
    # ui_info = basic_tool.read_json(basic_tool.readContentText(apk_json_path))
    ui_info = {}

    path_list = graph.get_paths_with_ui(ui_info)
    print(path_list[0])