from abc import ABCMeta, abstractmethod
import networkx as nx
from .utils import get_logger


class Measure(metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, graph: nx.Graph, node_mapping: dict, left_part: list, right_part: list, dataset: str):
        self.graph = graph
        self.node_mapping = node_mapping
        self.left_part = left_part
        self.right_part = right_part
        self.dataset = dataset
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    def calculate(self) -> float:
        raise NotImplementedError()
