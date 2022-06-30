from read_graph_file import graph_set
'''
construct a graph from gml file
'''
 
def constructGragh(contents):
    g = graph_set.graph()
    for line in contents:
        if line.strip().startswith('<node id="'):
            node = line.split('<node id="')[1].split('"')[0]
            node = node.replace('&amp;', '&').replace('&lt;', '<', ).replace('&gt;','>').replace('&quot;','"').replace('&#39;',"'")
            g.add_node(node)
        if line.strip().startswith('<edge id="'):
            src = line.strip().split('source="')[1].split('"')[0]
            src = src.replace('&amp;', '&').replace('&lt;', '<', ).replace('&gt;','>').replace('&quot;','"').replace('&#39;',"'")
            tar = line.strip().split('target="')[1].split('"')[0]
            tar = tar.replace('&amp;', '&').replace('&lt;', '<', ).replace('&gt;','>').replace('&quot;','"').replace('&#39;',"'")
            g.add_edge(src, tar)
    return g