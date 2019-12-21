import os
import networkx as nx
import glob
from measures.utils import get_partitions

g = nx.read_gml(os.path.join('../../partitioning/datasets/following_cc.gml'), label='id')
left, right = get_partitions('metis', '../../partitioning', 'following_cc')
for i in left:
    g.nodes[i]['partition'] = 0
for i in right:
    g.nodes[i]['partition'] = 1
nx.write_gml(g, 'following.gml')

g = nx.read_gml(os.path.join('../../partitioning/datasets/ignoring_cc.gml'), label='id')
left, right = get_partitions('metis', '../../partitioning', 'ignoring_cc')
for i in left:
    g.nodes[i]['partition'] = 0
for i in right:
    g.nodes[i]['partition'] = 1
nx.write_gml(g, 'ignoring.gml')

g = nx.read_gml(os.path.join('../../partitioning/datasets/follow_ignore_cc.gml'), label='id')
left, right = get_partitions('metis', '../../partitioning', 'follow_ignore_cc')
for i in left:
    g.nodes[i]['partition'] = 0
for i in right:
    g.nodes[i]['partition'] = 1
for s, t in g.edges:
    if int(g[s][t]['weight']) < 0:
        g[s][t]['nonnegweight'] = 0
    else:
        g[s][t]['nonnegweight'] = 1
nx.write_gml(g, 'follow_ignore.gml')