from typing import List
import igraph as ig
import networkx as nx
import numpy as np

from measures.measure import Measure
from .dataset_processor import get_probability_matrix
from ..utils import list_to_dict


class PolarizationIndex(Measure):

    def __init__(self, graph: nx.Graph, iggraph: ig.Graph, node_mapping: dict, left_part: List[int], right_part: List[int], dataset: str,
                 iterations: int = 500, cache: bool = True):
        super().__init__(graph, iggraph, node_mapping, left_part, right_part, dataset, cache)
        self.left_dict = list_to_dict(left_part)
        self.right_dict = list_to_dict(right_part)
        self.number_nodes = self.graph.number_of_nodes()
        self.iterations = iterations

    def calculate(self) -> float:
        s = np.zeros(self.graph.number_of_nodes())
        for n in self.left_part:
            try:
                s[n] = -1
            except:
                pass
        for n in self.right_part:
            try:
                s[n] = 1
            except:
                pass

        opinion_vector = np.copy(s)
        adj_dict_num_cache = {}
        for v in self.graph:
            adj_dict_num_cache[v] = len(list(self.graph.neighbors(v)))
        adj_dict = nx.to_dict_of_lists(self.graph)
        for its in range(self.iterations):
            prev_opinion_vector = opinion_vector
            for v in self.graph:
                sum_on = 0
                for n in adj_dict[v]:
                    sum_on = sum_on + prev_opinion_vector[n]
                opinion_vector[v] = (s[v] + sum_on) / (1 + adj_dict_num_cache[v])
        return (np.linalg.norm(opinion_vector) ** 2) / self.number_nodes

        # Q = get_probability_matrix(self.graph, self.dataset, self.iterations, self.number_nodes,
        #                            self.logger, self.cache)
        # return self.calc_result(Q, s)

    def calc_result(self, Q, s: np.ndarray) -> float:
        self.logger.info('Calculating opinion vector')
        z_rw = np.zeros(self.number_nodes)
        for i in range(self.number_nodes):
            row = Q[i]
            z_rw[i] = np.sum(row * s)
        return (np.linalg.norm(z_rw) ** 2) / self.number_nodes
