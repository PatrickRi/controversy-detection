import glob
import os

import networkx as nx

from measures.utils import get_partitions

for file in glob.glob(os.path.join('../../partitioning/datasets/*_cc.gml')):
    g = nx.read_gml(os.path.join(file), label='id')
    name = str(os.path.basename(file).split('.')[0])
    left, right = get_partitions('metis', '../../partitioning', name)
    for i in left:
        g.nodes[i]['partition'] = 0
    for i in right:
        g.nodes[i]['partition'] = 1
    nx.write_gml(g, name + '_incl_partitions.gml')
