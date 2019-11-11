import os
from typing import List

import networkx as nx


def convert_into_directed(g):
    for edge in g.edges():
        node1 = edge[0]
        node2 = edge[1]
        g.add_edge(node2, node1)
    return g


def enrich_dataset_with_opinions(g: nx.Graph, left_part: List[int], right_part: List[int]) -> nx.Graph:
    return g


def get_dataset_with_opinions(g: nx.Graph, dataset: str, left_part: List[int], right_part: List[int],
                              cache: bool) -> nx.Graph:
    target_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'enriched_datasets',
                               dataset + '.gml')
    if os.path.exists(target_path) and cache:
        return nx.read_gml(target_path, label='id')
    else:
        new_graph = enrich_dataset_with_opinions(g, left_part, right_part)
        nx.write_gml(new_graph, target_path)
        return new_graph
