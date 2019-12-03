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