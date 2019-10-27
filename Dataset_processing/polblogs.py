import networkx as nx

# polblogs contains multiple edges, which we will ignore
# add multigraph 1 in gml, then execute script
multigraph = nx.read_gml('./original_datasets/polblogs.gml', label='id')
g = nx.Graph(multigraph)
#for node in g:
#   del g.node[node]['value']
#   del g.node[node]['source']
#   del g.node[node]['label']
dict = {}
G_new = nx.to_networkx_graph(nx.adjacency_matrix(g).todense())
for i, node in enumerate(g.nodes()):
    dict[i] = node

nx.set_node_attributes(g, None, 'label')
nx.set_node_attributes(g, None, 'value')
nx.set_node_attributes(g, None, 'source')
nx.write_gml(G_new, './result/polblogs.gml')
