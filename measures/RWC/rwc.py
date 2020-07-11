from measures.measure import Measure
from typing import Dict, List
import math
import random
import networkx as nx
from .rwc_utils import get_nodes_with_highest_degree
from ..utils import list_to_dict
from tqdm import tqdm
import igraph as ig


class RWC(Measure):

    def __init__(self, name: str, graph: nx.Graph, iggraph: ig.Graph, node_mapping: dict, left_part: List[int], right_part: List[int], dataset: str,
                 percent: float = 0.10, iterations: int = 10000):
        super().__init__(name, graph, iggraph, node_mapping, left_part, right_part, dataset, True)
        self.percent = percent
        self.iterations = iterations

    def calculate(self) -> float:
        left_left = 0
        left_right = 0
        right_right = 0
        right_left = 0
        dict_left = list_to_dict(self.left_part)
        dict_right = list_to_dict(self.right_part)
        left_percent = math.ceil(self.percent * len(dict_left.keys()))
        right_percent = math.ceil(self.percent * len(dict_right.keys()))

        for j in tqdm(range(self.iterations)):
            left_nodes = get_nodes_with_highest_degree(self.graph, left_percent, dict_left)
            right_nodes = get_nodes_with_highest_degree(self.graph, right_percent, dict_right)
            # walks starting from left side
            nodes_left_list = list(left_nodes.keys())
            for i in range(len(nodes_left_list)):
                node = nodes_left_list[i]
                other_nodes = nodes_left_list[:i] + nodes_left_list[i + 1:]
                other_nodes_dict = list_to_dict(other_nodes)
                side = self.perform_random_walk(self.graph, node, other_nodes_dict, right_nodes)
                if side == "left":
                    left_left += 1
                elif side == "right":
                    left_right += 1
            # walks starting from right side
            nodes_right_list = list(right_nodes.keys())
            for i in range(len(nodes_right_list)):
                node = nodes_right_list[i]
                other_nodes = nodes_right_list[:i] + nodes_right_list[i + 1:]
                other_nodes_dict = list_to_dict(other_nodes)
                side = self.perform_random_walk(self.graph, node, left_nodes, other_nodes_dict)
                if side == "left":
                    right_left += 1
                elif side == "right":
                    right_right += 1
        print(left_left,right_right, left_right, right_left)
        e1 = left_left * 1.0 / (left_left + right_left)
        e2 = left_right * 1.0 / (left_right + right_right)
        e3 = right_left * 1.0 / (left_left + right_left)
        e4 = right_right * 1.0 / (left_right + right_right)

        return e1 * e4 - e2 * e3

    def perform_random_walk(self, g: nx.Graph, starting_node: int, user_nodes_side1: Dict[int, int],
                            user_nodes_side2: Dict[int, int]) -> str:
        dict_nodes = {}  # contains unique nodes seen till now
        step_count = 0
        side = ""
        while side == "":
            neighbors = list(g.neighbors(starting_node))
            random_num = random.randint(0, len(neighbors) - 1)
            starting_node = neighbors[random_num]
            dict_nodes[starting_node] = 1
            step_count += 1
            if starting_node in user_nodes_side1:
                side = "left"
            if starting_node in user_nodes_side2:
                side = "right"
        return side
