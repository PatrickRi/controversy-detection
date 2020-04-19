import networkx as nx
import os
# polblogs contains multiple edges, which we will ignore
# add multigraph 1 in gml, then execute script
multigraph = nx.read_gml('./original_datasets/polblogs.gml', label='id')
g = nx.Graph(multigraph)
# for node in g:
#   del g.node[node]['value']
#   del g.node[node]['source']
#   del g.node[node]['label']
dict = {}
part1 = []
part2 = []
G_new = nx.to_networkx_graph(nx.adjacency_matrix(g).todense())
for i, node in enumerate(g.nodes()):
    dict[i] = node
for node in g:
    if g.nodes[node]['value'] == 0:
        part1.append(node-1)
    else:
        part2.append(node - 1)
def write_nodelist_file(directory_path, dataset, nodes):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    target_path = os.path.join(directory_path, dataset + '.txt')
    with open(target_path, 'w') as f:
        for item in nodes:
            f.write("%s\n" % item)
    print(str(target_path) + " written")
write_nodelist_file(os.path.join('.'), 'polblogs_org1', part1)
write_nodelist_file(os.path.join('.'), 'polblogs_org2', part2)

nx.set_node_attributes(g, None, 'label')
nx.set_node_attributes(g, None, 'value')
nx.set_node_attributes(g, None, 'source')
nx.write_gml(G_new, './result/polblogs.gml')

print("nodes: ", g.number_of_nodes())
print("edges: ", g.number_of_edges())
ccs = list(nx.connected_components(g))
if len(ccs) > 1:
    lengths = [len(c) for c in sorted(ccs, key=len, reverse=True)]
    print('Largest CC has size', lengths[0], 'which is ' + str((lengths[0] / g.number_of_nodes()) * 100),
          '% of the dataset')
    largest_cc = max(ccs, key=len)
    S = g.subgraph(largest_cc).copy()
    nx.write_gml(S, './result/polblogs_cc.gml')


