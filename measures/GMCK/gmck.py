from measures.measure import Measure
from typing import List
import networkx as nx


class BoundaryConnectivity(Measure):

    def __init__(self, graph: nx.Graph, node_mapping: dict, left_part: List[int], right_part: List[int], dataset: str):
        super().__init__(graph, node_mapping, left_part, right_part, dataset)

    def calculate(self) -> float:
        cut_nodes1 = {}
        cut_nodes = {}

        for i in self.left_part:
            for j in self.right_part:
                if self.graph.has_edge(i, j):
                    cut_nodes1[i] = 1
                    cut_nodes1[j] = 1

        dict_across = {}  # num. edges across the cut
        dict_internal = {}  # num. edges internal to the cut

        # remove nodes from the cut that don't satisfy condition 2 - Guerra et al. p5
        for key in list(cut_nodes1.keys()):
            if self.satisfy_condition_2(self.graph, key, cut_nodes1):
                cut_nodes[key] = 1

        for edge in self.graph.edges():
            node1 = edge[0]
            node2 = edge[1]
            if node1 not in cut_nodes and (node2 not in cut_nodes):  # only consider edges involved in the cut
                continue
            if node1 in cut_nodes and node2 in cut_nodes:  # if both nodes are on the cut and both are on the same side, ignore
                if node1 in self.left_part and node2 in self.left_part:
                    continue
                if node1 in self.right_part and node2 in self.right_part:
                    continue
            if node1 in cut_nodes:
                if node1 in self.left_part:
                    if node2 in self.left_part and node2 not in cut_nodes1:
                        if node1 in dict_internal:
                            dict_internal[node1] += 1
                        else:
                            dict_internal[node1] = 1
                    elif node2 in self.right_part and node2 in cut_nodes:
                        if node1 in dict_across:
                            dict_across[node1] += 1
                        else:
                            dict_across[node1] = 1
                elif node1 in self.right_part:
                    if node2 in self.left_part and node2 in cut_nodes:
                        if node1 in dict_across:
                            dict_across[node1] += 1
                        else:
                            dict_across[node1] = 1
                    elif node2 in self.right_part and node2 not in cut_nodes1:
                        if node1 in dict_internal:
                            dict_internal[node1] += 1
                        else:
                            dict_internal[node1] = 1
            if node2 in cut_nodes:
                if node2 in self.left_part:
                    if node1 in self.left_part and node1 not in cut_nodes1:
                        if node2 in dict_internal:
                            dict_internal[node2] += 1
                        else:
                            dict_internal[node2] = 1
                    elif node1 in self.right_part and node1 in cut_nodes:
                        if node2 in dict_across:
                            dict_across[node2] += 1
                        else:
                            dict_across[node2] = 1
                elif node2 in self.right_part:
                    if node1 in self.left_part and node1 in cut_nodes:
                        if node2 in dict_across:
                            dict_across[node2] += 1
                        else:
                            dict_across[node2] = 1
                    elif node1 in self.right_part and node1 not in cut_nodes1:
                        if node2 in dict_internal:
                            dict_internal[node2] += 1
                        else:
                            dict_internal[node2] = 1

        polarization_score = 0.0
        for keys in list(cut_nodes.keys()):
            if keys not in dict_internal or keys not in dict_across:  # for singleton nodes from the cut
                continue
            if dict_across[keys] == 0 and dict_internal[keys] == 0:  # there's some problem
                raise Exception("Whoops!")
            polarization_score += (dict_internal[keys] * 1.0 / (dict_internal[keys] + dict_across[keys]) - 0.5)

        polarization_score = polarization_score / len(list(cut_nodes.keys()))
        return polarization_score

    def satisfy_condition_2(self, g: nx.Graph, node: int,
                            cut_nodes):  # A node v \in G_i has at least one edge connecting to a member of G_i which is not connected to G_j.
        neighbors = list(g.neighbors(node))
        for n in neighbors:
            if node in self.left_part and n in self.right_part:  # only consider neighbors belonging to G_i
                continue
            if node in self.right_part and n in self.left_part:  # only consider neighbors belonging to G_i
                continue
            if n not in cut_nodes:
                return True
        return False
