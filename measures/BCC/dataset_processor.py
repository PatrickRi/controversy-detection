import os
from typing import List, Tuple

import igraph as ig
import networkx as nx


def read_betweenness_file(path: str) -> List[float]:
    with open(path, 'r') as f:
        lines = f.readlines()
        edge_betweennesses: List[float] = []

        for line in lines:
            line = line.strip()
            edge_betweennesses.append(float(line))
    return edge_betweennesses


def create_file(g, dataset, target_path) -> List[float]:
    # limit the number of nodes, as runtime grows exponentially (limits runtime to around 10mins)
    # k = g.number_of_nodes()
    # if g.number_of_nodes() > 2000:
    #    k = 2000
    # scores = nx.edge_betweenness_centrality(g, k=k, seed=42)
    # still too slow, use igraph instead:
    ig_g: ig.Graph = ig.read('../partitioning/datasets/' + dataset + '.gml')
    ig_g_btwn = ig_g.edge_betweenness(False)
    scl_igg = rescale_e(ig_g_btwn, len(g), True, g.is_directed())  # rescale like networkx
    if not g.is_directed():
        scores = [x * 2 for x in scl_igg]  # values of networkx are twice as high
    else:
        scores = scl_igg
    with open(target_path, 'w') as f:
        for value in scores:
            f.write(str(value) + "\n")
    return scores


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


def create_cuts_file(g, target_path, left_part: List[int], right_part: List[int]) -> List[float]:
    cut_nodes = []
    cut_nodes_tuples = []
    for left_node in left_part:
        for right_node in right_part:
            if g.has_edge(left_node, right_node):
                cut_nodes.append(left_node)
                cut_nodes.append(right_node)
                cut_nodes_tuples.append((left_node, right_node))
                cut_nodes_tuples.append((right_node, left_node))
    scores = calc_edge_betweenness_centrality(g, cut_nodes)
    filtered_scores = []
    for k, v in scores.items():
        if k in cut_nodes_tuples:
            filtered_scores.append(v)
    with open(target_path, 'w') as f:
        for value in filtered_scores:
            f.write(str(value) + "\n")
    return filtered_scores


# excerpt from networkx, to calculate only for selcted nodes (to save time)
def calc_edge_betweenness_centrality(g: nx.Graph, cut_nodes: List[int]):
    betweenness = dict.fromkeys(g, 0.0)  # b[v]=0 for v in G
    # b[e]=0 for e in G.edges()
    betweenness.update(dict.fromkeys(g.edges(), 0.0))
    for s in cut_nodes:
        # single source shortest paths
        S, P, sigma = nx.betweenness._single_source_shortest_path_basic(g, s)
        # accumulation
        betweenness = nx.betweenness._accumulate_edges(betweenness, S, P, sigma, s)
    # rescaling
    for n in g:  # remove nodes to only return edges
        del betweenness[n]
    betweenness = nx.betweenness._rescale_e(betweenness, len(g), normalized=True,
                                            directed=g.is_directed())
    return betweenness


def get_centralities(g: nx.Graph, dataset: str, left_part: List[int], right_part: List[int]) -> Tuple[
    List[float], List[float]]:
    target_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'edge_betweenness', dataset + '.txt')
    target_path_cut = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'edge_betweenness', dataset + '_cut.txt')
    if os.path.exists(target_path):
        return (read_betweenness_file(target_path), read_betweenness_file(target_path_cut))
    else:
        return (create_file(g, dataset, target_path), create_cuts_file(g, target_path_cut, left_part, right_part))
