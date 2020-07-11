from abc import ABCMeta, abstractmethod
import networkx as nx
from .utils import get_logger
import igraph as ig


class Measure(metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, name: str, graph: nx.Graph, iggraph: ig.Graph, node_mapping: dict, left_part: list, right_part: list, dataset: str,
                 cache: bool = True):
        self.name = name
        self.graph = graph
        self.iggraph = iggraph
        self.node_mapping = node_mapping
        self.left_part = left_part
        self.right_part = right_part
        self.dataset = dataset
        self.cache = cache
        self.logger = get_logger(self.__class__.__name__ + '-' + dataset)

    @abstractmethod
    def calculate(self) -> float:
        raise NotImplementedError()
