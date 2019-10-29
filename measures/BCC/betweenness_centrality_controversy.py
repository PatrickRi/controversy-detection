from typing import List

import networkx as nx
from scipy.stats import entropy

from measures.measure import Measure
from .dataset_processor import get_centralities


class BCC(Measure):

    def __init__(self, graph: nx.Graph, node_mapping: dict, left_part: List[int], right_part: List[int], dataset: str):
        super().__init__(graph, node_mapping, left_part, right_part, dataset)

    def calculate(self) -> float:
        dict_edge_betweenness = get_centralities(self.graph, self.dataset)

        eb_list = []
        for left_node in self.left_part:
            for right_node in self.right_part:
                if self.graph.has_edge(left_node, right_node):
                    if (left_node, right_node) in dict_edge_betweenness:
                        edge_betweenness = dict_edge_betweenness[(left_node, right_node)]
                        eb_list.append(edge_betweenness)
                    else:
                        edge_betweenness = dict_edge_betweenness[(right_node, left_node)]
                        eb_list.append(edge_betweenness)
        eb_list_all = [x for x in dict_edge_betweenness.values()]

        return entropy(eb_list, eb_list_all)
