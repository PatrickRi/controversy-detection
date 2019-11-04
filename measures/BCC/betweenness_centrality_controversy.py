from typing import List

import networkx as nx
import numpy as np
from scipy.stats import entropy
from sklearn.neighbors import KernelDensity

from measures.measure import Measure
from .dataset_processor import get_centralities


class BCC(Measure):

    def __init__(self, graph: nx.Graph, node_mapping: dict, left_part: List[int], right_part: List[int], dataset: str,
                 bandwidth: float = 0.0000001):
        super().__init__(graph, node_mapping, left_part, right_part, dataset)
        self.bandwidth = bandwidth

    def calculate(self) -> float:
        self.logger.info('Retrieve centralities')
        dict_edge_betweenness = get_centralities(self.graph, self.dataset)

        self.logger.info('Split lists')
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
        self.logger.info('Calculate entropy')
        entr = entropy(self.sample_from_kde(np.array(eb_list)), self.sample_from_kde(np.array(eb_list_all)))
        return 1 - np.exp(-1.0 * entr)

    def sample_from_kde(self, values: np.ndarray):
        kde_fitted = KernelDensity(bandwidth=self.bandwidth).fit(values.reshape(-1, 1))
        return kde_fitted.sample(10000)
