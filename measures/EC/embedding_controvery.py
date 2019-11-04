import math
from typing import Dict, List

import networkx as nx

from measures.measure import Measure
from .dataset_processor import get_positions


class EmbeddingControversy(Measure):

    def __init__(self, graph: nx.Graph, node_mapping: dict, left_part: List[int], right_part: List[int], dataset: str):
        super().__init__(graph, node_mapping, left_part, right_part, dataset)

    def calculate(self) -> float:
        self.logger.info('Fetch positions')
        dict_positions = get_positions(self.graph, self.dataset)
        # calculate dx and dy and dxy
        self.logger.info('Calculate distance left-left')
        avg_left_left = self.calc_avg_distance(self.left_part, self.left_part, dict_positions)
        self.logger.info('Calculate distance right-right')
        avg_right_right = self.calc_avg_distance(self.right_part, self.right_part, dict_positions)
        self.logger.info('Calculate distance left-right')
        avg_both = self.calc_avg_distance(self.left_part, self.right_part, dict_positions)

        return 1 - ((avg_left_left + avg_right_right) / (2 * avg_both))

    def calc_avg_distance(self, partition1: List[int], partition2: List[int],
                          dict_positions: Dict[int, List[float]]) -> float:
        total = 0.0
        count = 0.0

        for i in range(len(partition1)):
            node1 = partition1[i]
            for j in range(i + 1, len(partition2)):
                node2 = partition2[j]
                dist = self.calc_distance(dict_positions[node1], dict_positions[node2])
                total += dist
                count += 1.0
        return total / count

    def calc_distance(self, point1, point2) -> float:
        x1 = point1[0]
        y1 = point1[1]
        x2 = point2[0]
        y2 = point2[1]
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
