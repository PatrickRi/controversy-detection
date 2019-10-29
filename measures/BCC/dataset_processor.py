import os
from collections import namedtuple
from typing import Dict

import networkx as nx

Edge = namedtuple("Edge", ["source", "target"])


def read_betweenness_file(path: str) -> Dict[Edge, float]:
    with open(path, 'r') as f:
        lines = f.readlines()
        dict_edge_betweenness: Dict[Edge, float] = {}

        for line in lines:
            line = line.strip()
            line_split = line.split(",")
            dict_edge_betweenness[Edge(line_split[0], line_split[1])] = float(line_split[2])
    return dict_edge_betweenness


def create_file(g, target_path) -> Dict[Edge, float]:
    scores = nx.edge_betweenness_centrality(g, seed=42)
    with open(target_path, 'w') as f:
        for key, value in scores.items():
            f.write(str(key[0]) + "," + str(key[1]) + "," + str(value) + "\n")
    return scores


def get_centralities(g: nx.Graph, dataset: str) -> Dict[Edge, float]:
    target_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'edge_betweenness', dataset + '.txt')
    if os.path.exists(target_path):
        return read_betweenness_file(target_path)
    else:
        return create_file(g, target_path)
