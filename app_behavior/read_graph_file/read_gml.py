from read_graph_file import graph_set
'''
construct a graph from gml file
'''
def constructGragh(contents):
    inNode, inEdge = False, False
    label_dic = {}
    # g_list = []
    g = graph_set.graph()
    for line in contents:
        # TODO
        # add if multigraph bigger than 1
        # if line.strip().startswith("multigraph"):
        #     number = int(line.split()[1])
        #     for n in number:
        #         g_list.append(graph_set.graph())
        if line.strip() == "node [":
            inNode = True
        elif line.strip().startswith("id"):
            node = line.strip().split()[1]
        elif line.strip().startswith("label"):
            label = " ".join(line.strip().split()[2:]).split("@")[0].split('"')[0].strip()
            g.add_node(label)
            label_dic[node] = label
        elif line.strip().startswith("external"):
            ifExternal = line.strip().split()[1]
        elif line.strip() == "edge [":
            inEdge = True
        elif line.strip().startswith("source"):
            source = line.strip().split()[1]
        elif line.strip().startswith("target"):
            target = line.strip().split()[1]
            g.add_edge(label_dic[source], label_dic[target])
        elif line.strip().startswith("]"):
            inNode = False
            inEdge = False
    return g
 
