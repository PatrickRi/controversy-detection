from measures.Measure import Measure
import networkx as nx


class Modularity(Measure):

    def __init__(self, graph: nx.Graph, left_part: list, right_part: list, dataset: str):
        super().__init__(graph, left_part, right_part, dataset)

    def calculate(self) -> float:
        A = nx.adjacency_matrix(self.graph)
        m = len(list(self.graph.edges()))

