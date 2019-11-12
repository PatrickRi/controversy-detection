from typing import List

import networkx as nx
import numpy as np

from measures.measure import Measure
from .dataset_processor import get_probability_matrix
from ..utils import list_to_dict


class PolarizationIndex(Measure):

    def __init__(self, graph: nx.Graph, node_mapping: dict, left_part: List[int], right_part: List[int], dataset: str,
                 iterations: int = 5, cache: bool = True):
        super().__init__(graph, node_mapping, left_part, right_part, dataset, cache)
        self.left_dict = list_to_dict(left_part)
        self.right_dict = list_to_dict(right_part)
        self.number_nodes = self.graph.number_of_nodes()
        self.iterations = iterations

    def calculate(self) -> float:
        s = np.zeros(self.graph.number_of_nodes())
        for n in self.left_part:
            s[n] = -1
        for n in self.right_part:
            s[n] = 1
        Q = get_probability_matrix(self.graph, self.dataset, self.iterations, self.number_nodes,
                                   self.logger, self.cache)
        return self.calc_result(Q, s)

    def calc_result(self, Q: np.ndarray, s: np.ndarray) -> float:
        self.logger.info('Calculating opinion vector')
        z_rw = np.zeros(self.number_nodes)
        for i in range(self.number_nodes):
            row = Q[i]
            psum = 0
            for j in range(self.number_nodes):
                p = row[j + self.number_nodes]
                si = s[j]
                psum = psum + p * si
            z_rw[i] = psum
        return (np.linalg.norm(z_rw) ** 2) / self.number_nodes
