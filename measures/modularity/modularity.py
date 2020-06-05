from measures.measure import Measure
import networkx as nx
import numpy as np
from typing import List
from ..utils import list_to_dict
import igraph as ig
import os


class Modularity(Measure):

    def __init__(self, graph: nx.Graph, iggraph: ig.Graph, node_mapping: dict, left_part: List[int], right_part: List[int], dataset: str,
                 algorithm: str = "newman"):
        super().__init__(graph, iggraph, node_mapping, left_part, right_part, dataset, True)
        self.algorithm = algorithm
        self.left_dict = list_to_dict(left_part)
        self.right_dict = list_to_dict(right_part)

    def calculate(self) -> float:
        if self.algorithm == "newman_slow": # traditional self-implementation
            return self.newman()
        elif self.algorithm == 'newman':
            return self.newman_igraph()
        else:
            raise Exception("Algorithm " + self.algorithm + " not supported yet")

    def newman_igraph(self) -> float:
        self.logger.info('Start building membership')
        arr = np.zeros(self.graph.number_of_nodes())
        for n in self.right_part:
            try:
                arr[n] = 1
            except:
                pass
        self.logger.info('Start reading gml')
        self.logger.info('Start calc Modularity')
        r = self.iggraph.modularity(membership=arr)
        self.logger.info('Finished calc Modularity')
        return r

    def newman(self) -> float:
        """
        Calculates the modularity score according to 1/2m * Sij(Aij - (kikj)/2m)d(cicj)
        :return:
        Modularity score according to Newman
        """
        self.logger.info('Start with A and m')
        A = nx.adjacency_matrix(self.graph).todense()
        m = self.graph.number_of_edges()  # TODO * 2 for undirected?
        K = 0
        N = self.graph.number_of_nodes()
        for i in range(0, N):
            if i / N > 0.5:
                print('50%')
            elif i / N > 0.25:
                print('25%')
            for j in range(0, N):
                kd = int(self.__kronecker_delta(i, j))
                K = K + (A[i, j] - ((A[i].sum() * A[j].sum()) / (2 * m))) * kd
        self.logger.info('Done calculating')
        return (1 / (2 * m)) * K

    def __kronecker_delta(self, node_i, node_j):
        return (node_i in self.left_dict and node_j in self.left_dict) or (
                    node_i in self.right_dict and node_j in self.right_dict)
