from measures.Measure import Measure
import networkx as nx


class Modularity(Measure):

    def __init__(self, graph: nx.Graph, left_part: list, right_part: list, dataset: str):
        super().__init__(graph, left_part, right_part, dataset)

    def calculate(self) -> float:
        A = nx.adjacency_matrix(self.graph).todense()
        m = self.graph.number_of_edges() #TODO * 2 for undirected?
        K = 0
        N = self.graph.number_of_nodes()
        for i in range(1, N):
            for j in range(1, N):
                cd = int(self.__kronecker_delta(i, j))
                K = K + (A[i - 1, j - 1] - ((A[i - 1].sum() * A[j - 1].sum()) / (2 * m))) * cd

        print((1 / (2 * m)) * K)

    def __kronecker_delta(self, node_i, node_j):
        return (node_i in self.left_part and node_j in self.left_part) or (node_i in self.right_part and node_j in self.right_part)
