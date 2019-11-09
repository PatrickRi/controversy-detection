import math
import os
from operator import itemgetter
from typing import Dict, List

import networkx as nx

from ..utils import list_to_dict


def convert_into_directed(g):
    for edge in g.edges():
        node1 = edge[0]
        node2 = edge[1]
        g.add_edge(node2, node1)
    return g


# first take the nodes with the highest degree, then take the top $k$
def get_nodes_with_highest_degree(g: nx.Graph, k: int, partition: Dict[int, int]):
    random_nodes = {}
    dict_degrees = {}
    for node in g.nodes():
        dict_degrees[node] = g.degree[node]
    sorted_dict = sorted(dict_degrees.items(), key=itemgetter(1), reverse=True)  # sorts nodes by degrees
    count = 0
    for i in sorted_dict:
        if count > k:
            break
        if i[0] not in partition:
            continue
        random_nodes[i[0]] = i[1]
        count += 1
    return random_nodes


def enrich_dataset_with_ideologies(g: nx.Graph, left_part: List[int], right_part: List[int],
                                   percent: float) -> nx.Graph:
    g = convert_into_directed(g)
    dict_left = list_to_dict(left_part)
    dict_right = list_to_dict(right_part)
    left_percent = math.ceil(percent * len(dict_left.keys()))
    right_percent = math.ceil(percent * len(dict_right.keys()))

    left_seed_nodes = get_nodes_with_highest_degree(g, left_percent, dict_left)
    right_seed_nodes = get_nodes_with_highest_degree(g, right_percent, dict_right)

    dict_ideos = {}

    for node in g.nodes():
        if node in left_seed_nodes:
            dict_ideos[node] = 1
        elif node in right_seed_nodes:
            dict_ideos[node] = -1
        else:
            dict_ideos[node] = 0

    for node in g.nodes():
        node_ideo = dict_ideos[node]
        g.add_node(node, ideo=node_ideo)
    return g


def get_dataset_with_ideologies(g: nx.Graph, dataset: str, left_part: List[int], right_part: List[int],
                                percent: float, cache: bool) -> nx.Graph:
    target_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'enriched_datasets',
                               dataset + '_' + str(percent * 100) + '.gml')
    if os.path.exists(target_path) and cache:
        return nx.read_gml(target_path, label='id')
    else:
        new_graph = enrich_dataset_with_ideologies(g, left_part, right_part, percent)
        nx.write_gml(new_graph, target_path)
        return new_graph
