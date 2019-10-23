from measures.measure import Measure
import networkx as nx


class Modularity(Measure):

    def __init__(self, graph: nx.Graph, node_mapping: dict, left_part: list, right_part: list, dataset: str,
                 algorithm: str = "newman"):
        super().__init__(graph, node_mapping, left_part, right_part, dataset)
        self.algorithm = algorithm

    def calculate(self) -> float:
        if self.algorithm == "newman":
            return self.newman()
        else:
            raise Exception("Algorithm " + self.algorithm + " not supported yet")

    def newman(self) -> float:
        """
        Calculates the modularity score according to 1/2m * Sij(Aij - (kikj)/2m)d(cicj)
        :return:
        Modularity score according to Newman
        """
        A = nx.adjacency_matrix(self.graph).todense()
        m = self.graph.number_of_edges()  # TODO * 2 for undirected?
        K = 0
        N = self.graph.number_of_nodes()
        for i in range(0, N):
            for j in range(0, N):
                kd = int(self.__kronecker_delta(i, j))
                K = K + (A[i, j] - ((A[i].sum() * A[j].sum()) / (2 * m))) * kd

        return (1 / (2 * m)) * K

    def __kronecker_delta(self, node_i, node_j):
        return (node_i in self.left_part and node_j in self.left_part) or (
                    node_i in self.right_part and node_j in self.right_part)
