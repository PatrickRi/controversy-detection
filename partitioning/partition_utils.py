import os

import networkx as nx


def to_adjacency_list(g):
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
