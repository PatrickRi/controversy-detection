import random
from typing import List

import networkx as nx
import numpy as np
from tqdm import tqdm
from measures.measure import Measure
from ..utils import list_to_dict


class PolarizationIndex(Measure):

    def __init__(self, graph: nx.Graph, node_mapping: dict, left_part: List[int], right_part: List[int], dataset: str, iterations: int=50):
        super().__init__(graph, node_mapping, left_part, right_part, dataset, True)
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
        H = self.construct_H()
        Q = self.random_walk_Q(H)
        return self.calc_result(Q, s)

    def construct_H(self) -> nx.Graph:
        self.logger.info('Constructing H')
        X = nx.Graph()
        nodes_offset = self.number_nodes
        self.logger.info('Adding nodes to H')
        for n in self.graph:
            X.add_node(n + nodes_offset)
        H = nx.compose(self.graph, X)
        H = nx.DiGraph(H)
        self.logger.info('Adding edges to H')
        for n in self.graph:
            H.add_edge(n, n + nodes_offset)
        return H

    def perform_random_walk(self, starting_node: int, H: nx.Graph) -> int:
        while True:
            neighbors = list(H.neighbors(starting_node))
            if len(neighbors) == 0:
                return starting_node
            random_num = random.randint(0, len(neighbors) - 1)
            starting_node = neighbors[random_num]

    def random_walk_Q(self, H: nx.Graph) -> np.ndarray:
        self.logger.info('Performing random walks')
        hnn = H.number_of_nodes()
        Q = np.zeros((hnn, hnn))
        for i in tqdm(range(self.iterations)):
            Q_curr = np.zeros((hnn, hnn))
            for n in self.graph:
                for itr in range(self.iterations):
                    end = self.perform_random_walk(n, H)
                    Q_curr[n, end] = Q_curr[n, end] + 1 / self.iterations
            Q = Q + Q_curr / self.iterations
        return Q

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
