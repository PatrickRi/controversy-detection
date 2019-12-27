import os
from collections import namedtuple
from typing import Dict

import igraph as ig
import networkx as nx

Edge = namedtuple("Edge", ["source", "target"])


def read_betweenness_file(path: str) -> Dict[Edge, float]:
    with open(path, 'r') as f:
        lines = f.readlines()
        dict_edge_betweenness: Dict[Edge, float] = {}

        for line in lines:
            line = line.strip()
            line_split = line.split(",")
            dict_edge_betweenness[Edge(int(line_split[0]), int(line_split[1]))] = float(line_split[2])
    return dict_edge_betweenness


def create_file(g, iggraph, target_path, dataset) -> Dict[Edge, float]:
    # networkx too slow, and sampling is not working as excepted (see dedicated branch)
    # https://stackoverflow.com/questions/32465503/networkx-never-finishes-calculating-betweenness-centrality-for-2-mil-nodes
    # scores = nx.edge_betweenness_centrality(g, seed=42)
    ig_g_btwn = iggraph.edge_betweenness(False)
    scl_igg = rescale_e(ig_g_btwn, len(g), True, g.is_directed())  # rescale like networkx
    if not g.is_directed():
        scores = [x * 2 for x in scl_igg]  # values of networkx are twice as high
    else:
        scores = scl_igg
    dict_edge_betweenness: Dict[Edge, float] = {}
    for t, v in zip(iggraph.get_edgelist(), scores):
        dict_edge_betweenness[Edge(t[0], t[1])] = v
    with open(target_path, 'w') as f:
        for key, value in dict_edge_betweenness.items():
            f.write(str(key.source) + "," + str(key.target) + "," + str(value) + "\n")
    return dict_edge_betweenness


def rescale_e(betweenness, n, normalized, directed=False, k=None):
    if normalized:
        if n <= 1:
            scale = None  # no normalization b=0 for all nodes
        else:
            scale = 1 / (n * (n - 1))
    else:  # rescale by 2 for undirected graphs
        if not directed:
            scale = 0.5
        else:
            scale = None
    if scale is not None:
        if k is not None:
            scale = scale * n / k
        result = []
        for v in betweenness:
            result.append(v * scale)
        return result
    return betweenness


def get_centralities(g: nx.Graph, iggraph: ig.Graph, dataset: str, cache) -> Dict[Edge, float]:
    target_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'edge_betweenness', dataset + '.txt')
    if os.path.exists(target_path) and cache:
        return read_betweenness_file(target_path)
    else:
        return create_file(g, iggraph, target_path, dataset)
