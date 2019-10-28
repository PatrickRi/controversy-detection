from typing import Tuple, Dict, List
import yaml
import os

import networkx as nx


# Nodes have arbitrary names, which might be difficult later on, 0:n is much simpler, but dictionary might be needed
def normalize_graph(g: nx.Graph) -> Tuple[nx.Graph, Dict]:
    mapping = {}
    g_new = nx.to_networkx_graph(nx.adjacency_matrix(g).todense())
    for i, node in enumerate(g.nodes()):
        mapping[i] = node
    return g_new, mapping


def adjacency_matrix(g: nx.Graph):
    return nx.adjacency_matrix(g).todense()


def get_config(config_path: str, overwrites: str = None) -> Dict[str, any]:
    with open(config_path, 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

    if overwrites is not None and overwrites != "":
        over_parts = [yaml.load(x) for x in overwrites.split(",")]

        for d in over_parts:
            for key, value in d.items():
                cfg[key] = value
    return cfg


def get_partitions(method: str, directory: str, dataset: str) -> Tuple[List[int], List[int]]:
    left_target_path = os.path.join(directory, method, 'left', dataset + '.txt')
    right_target_path = os.path.join(directory, method, 'right', dataset + '.txt')
    return __read_partition_file(left_target_path), __read_partition_file(right_target_path)


def __read_partition_file(path: str) -> List[int]:
    file = open(path)
    lines = file.readlines()
    nodes = []
    for line in lines:
        line = int(line.strip())
        nodes.append(line)
    return nodes
