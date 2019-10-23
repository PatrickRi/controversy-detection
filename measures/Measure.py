from abc import ABCMeta, abstractmethod
import networkx as nx


class Measure(metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, graph: nx.Graph, left_part: list, right_part: list, dataset: str):
        self.graph = graph
        self.left_part = left_part
        self.right_part = right_part
        self.dataset = dataset

    @abstractmethod
    def calculate(self) -> float:
        raise NotImplementedError()
