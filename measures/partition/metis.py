import sys, os, os.path
from typing import Tuple

os.environ['METIS_DLL'] = 'C:\\Users\\Patrick\\Documents\\TU\\2019S\\Thesis_Code\\metis-5.1.0\\build\\windows\\libmetis\\Release\\metis.dll'
import networkx as nx
import metis
from .partition import Partition


class MetisPartitioner(Partition):

    def partition(self, graph: nx.Graph, node_mapping: dict) -> Tuple[list, list]:
        (edgecuts, parts) = metis.part_graph(graph, 2)
        left = []
        right = []
        for i, p in enumerate(parts):
            if p == 0:
                left.append(i)
            else:
                right.append(i)
        return left, right
