from abc import ABCMeta, abstractmethod
from typing import Tuple

import networkx as nx


class Partition(metaclass=ABCMeta):

    @abstractmethod
    def partition(self, graph: nx.Graph, node_mapping: dict) -> Tuple[list, list]:
        raise NotImplementedError()
