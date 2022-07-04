from behavior_extraction.read_graph_file import graph_set
'''
construct a graph from gml file
'''
def constructGragh(contents):
    g = graph_set.graph()
    if 'digraph "callgraph" {' in contents[0]:
        for line in contents:
            if "->" in line:
                items = line.split("->")
                src = items[0].strip().split('"')[1]
                tar = items[1].strip().split('"')[1]
                g.add_node(src)
                g.add_node(tar)
                g.add_edge(src, tar)
            elif line.strip().startswith('"<'):
                src = line.strip().split('"')[1]
                g.add_node(src)
    else:
        node_dic = {}
        for line in contents:
            if "->" in line:
                items = line.split("->")
                src = items[0].strip()
                tar = items[1].strip()[:-1]
                g.add_edge(node_dic[src], node_dic[tar])
            elif 'label="<' in line.strip():
                label = line.strip().split('"')[1]
                node = line.split('[')[0].strip()
                node_dic[node] = label
                g.add_node(label)
    return g
 
def construct_graph_without_dummyMainMethod(contents, dot_path, packages=""):
    g = graph_set.graph(apk=dot_path, packages=packages)
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
        dummy_methods = []
        for line in contents:
            # print(line)
            if "->" in line:
                items = line.split("->")
                src = items[0].strip()
                tar = items[1].strip()[:-1]
                if src not in node_dic:
                    continue
                g.add_edge(node_dic[src], node_dic[tar])
            elif 'label="' in line.strip():
                label = line.strip().split('"')[1]
                if '<dummyMainClass:' in label:
                    continue
                node = line.split('[')[0].strip()
                node_dic[node] = label
                g.add_node(label)
    return g


def del_init(g):
    g.del_node('<java.lang.Object: void <init>()>')
    g.del_node('<java.lang.RuntimeException: void <init>(java.lang.String)>')
    g.del_node('<java.lang.Exception: void <init>()>')
    g.del_node('<java.lang.Throwable: void <init>()>')

def read_deepintent_dot_without_dummyMainMethod(contents):
    g = graph_set.graph()
    node_dic = {}
    dummy_node = ''
    for content in contents:
        if 'label=' in content:
            number = content.split(' [ ')[0].strip()
            node = content.split('label="')[1].split('" ];')[0].strip()
            if node.startswith("<dummyMainClass:"):
                dummy_node = number
                continue
            g.add_node(node)
            node_dic[number] = node
        elif ' -- ' in content:
            src = content.split(' -- ')[0].strip()
            tar = content.split(' -- ')[1].split(';')[0].strip()
            if src==dummy_node or node_dic[src].startswith("<dummyMainClass:"):
                continue
            g.add_edge(node_dic[src], node_dic[tar])
    return g
