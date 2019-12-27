import os
import networkx as nx
import glob
import pymetis
import faulthandler
from .partition_utils import to_adjacency_list, metis_to_nodelist, write_nodelist_file

faulthandler.enable()
files = glob.glob('./datasets/*.gml')
print("found", len(files), "files")
for file in files:
    try:
        print("processing", file)
        dataset = os.path.basename(file).split('.')[0]
        g = nx.read_gml(file, label='id')
        g = nx.Graph(g)
        g = nx.convert_node_labels_to_integers(g)
        (edgecuts, parts) = pymetis.part_graph(2, adjacency=to_adjacency_list(g))
        # print("RESULT:", parts)
        left, right = metis_to_nodelist(parts)
        write_nodelist_file(os.path.join('./partitioning', 'metis', 'left'), dataset, left)
        write_nodelist_file(os.path.join('./partitioning', 'metis', 'right'), dataset, right)

    except BaseException as e:
        print(str(type(e)) + ":" + str(e))
