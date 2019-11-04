import os
import networkx as nx
import glob
import pymetis
import faulthandler


def to_adjacency_list(G):
    adjacency_list = []
    for n in g.nodes():
        adjacency_list.append(list(nx.neighbors(g, n)))
    return adjacency_list


def metis_to_nodelist(parts):
    left = []
    right = []
    for i, p in enumerate(parts):
        if p == 0:
            left.append(i)
        else:
            right.append(i)
    return left, right


def write_nodelist_file(directory_path, dataset, nodes):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    target_path = os.path.join(directory_path, dataset + '.txt')
    with open(target_path, 'w') as f:
        for item in nodes:
            f.write("%s\n" % item)
    print(str(target_path) + " written")


faulthandler.enable()
files = glob.glob('./datasets/*.gml')
print("found", len(files), "files")
for file in files:
    try:
        print("processing", file)
        dataset = os.path.basename(file).split('.')[0]
        g = nx.read_gml(file, label='id')
        g = nx.convert_node_labels_to_integers(g)
        (edgecuts, parts) = pymetis.part_graph(2, adjacency=to_adjacency_list(g))
        # print("RESULT:", parts)
        left, right = metis_to_nodelist(parts)
        write_nodelist_file(os.path.join('./partitioning', 'metis', 'left'), dataset, left)
        write_nodelist_file(os.path.join('./partitioning', 'metis', 'right'), dataset, right)

    except BaseException as e:
        print(str(type(e)) + ":" + str(e))
