from typing import List

import networkx as nx
import numpy as np
from scipy.stats import entropy
from sklearn.neighbors import KernelDensity

from measures.measure import Measure
from .dataset_processor import get_centralities
from ..utils import list_to_dict


class BCC(Measure):

    def __init__(self, graph: nx.Graph, node_mapping: dict, left_part: List[int], right_part: List[int], dataset: str,
                 cache: bool = True, bandwidth: float = 0.0000001):
        super().__init__(graph, node_mapping, left_part, right_part, dataset, cache)
        self.bandwidth = bandwidth
        self.left_dict = list_to_dict(self.left_part)
        self.right_dict = list_to_dict(self.right_part)

    def calculate(self) -> float:
        self.logger.info('Retrieve centralities')
        dict_edge_betweenness = get_centralities(self.graph, self.dataset, self.cache)

        self.logger.info('Split lists')
        eb_list = []
        for s, t in self.graph.edges:
            if (s in self.left_part and t in self.right_part) or (s in self.right_part and t in self.left_part):
                if (s, t) in dict_edge_betweenness:
                    edge_betweenness = dict_edge_betweenness[(s, t)]
                    eb_list.append(edge_betweenness)
                else:
                    edge_betweenness = dict_edge_betweenness[(t, s)]
                    eb_list.append(edge_betweenness)
        eb_list_all = self.replace_with_small(list(dict_edge_betweenness.values()))
        eb_list = self.replace_with_small(eb_list)
        self.logger.info('Calculate entropy')
        entr = entropy(self.sample_from_kde(np.array(eb_list)), self.sample_from_kde(np.array(eb_list_all)))
        return 1 - np.exp(-1.0 * entr)[0]

    def replace_with_small(self, arr):
        result = []
        for x in arr:
            if x < 0.000001:
                result.append(0.000001)
            else:
                result.append(x)
        return result

    def sample_from_kde(self, values: np.ndarray):
        kde_fitted = KernelDensity(bandwidth=self.bandwidth).fit(values.reshape(-1, 1))
        return kde_fitted.sample(10000)
