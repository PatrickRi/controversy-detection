from abc import ABCMeta, abstractmethod
from typing import Tuple

import networkx as nx


class Partition(metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, graph: nx.Graph, node_mapping: dict):
        self.graph = graph
        self.node_mapping = node_mapping

    @abstractmethod
    def partition(self) -> Tuple[list, list]:
        raise NotImplementedError()
