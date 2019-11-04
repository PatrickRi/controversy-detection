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
        eb_list_all, eb_list = get_centralities(self.graph, self.dataset, self.left_part, self.right_part)
        eb_list_all = self.replace_with_small(eb_list_all)
        eb_list = self.replace_with_small(eb_list)
        self.logger.info('Calculate entropy')
        entr = entropy(self.sample_from_kde(np.array(eb_list)), self.sample_from_kde(np.array(eb_list_all)))
        return 1 - np.exp(-1.0 * entr)[0]


    def replace_with_small(self, arr):
        result = []
        for x in arr:
            if x == 0:
                result.append(0.000001)
            else:
                result.append(x)
        return result

    def sample_from_kde(self, values: np.ndarray):
        kde_fitted = KernelDensity(bandwidth=self.bandwidth).fit(values.reshape(-1, 1))
        return kde_fitted.sample(10000)
