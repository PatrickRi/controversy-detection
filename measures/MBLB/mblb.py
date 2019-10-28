from measures.measure import Measure
from typing import Dict, List
import networkx as nx
import numpy as np
import scipy.sparse as sp
import time
from .dataset_processor import get_dataset_with_ideologies


class MBLB(Measure):

    def __init__(self, graph: nx.Graph, node_mapping: dict, left_part: List[int], right_part: List[int], dataset: str):
        super().__init__(graph, node_mapping, left_part, right_part, dataset)

    def calculate(self) -> float:
        g = get_dataset_with_ideologies(self.graph, self.dataset, self.left_part, self.right_part)
        ideologies = nx.get_node_attributes(g, 'ideo')
        corenode = []
        for key in list(ideologies.keys()):
            if ideologies[key] == 1 or ideologies[key] == -1:
                corenode.append(key)

        v_current = self.model(g, corenode)

        return self.calculate_polarization_index(v_current)

    def model(self, g: nx.Graph, corenode: List[int], tol=10 ** -5):
        """
        :param g: Graph to calculate opinions. The nodes have an attribute "ideo" with their ideology, set to 0 for all listeners, 1 and -1 for the elite.
        :param corenode: Nodes that belong to the seed (Identifiers from the Graph G)
        :param tol: threshold for convergence. It will evaluate the difference between opinions at time t and t+1
        :return: array
        """
        N = g.number_of_nodes()

        # Build the adjacency matrix
        Aij = sp.lil_matrix((N, N))
        print("Adjacency matrix shape: " + str(Aij.shape))
        for o, d in g.edges():
            Aij[o, d] = 1
            Aij[d, o] = 1
        # Build the vectors with users opinions
        v_current = []
        v_new = []
        # dict_nodes = {} # for what are labels needed???
        for nodo in list(g.nodes()):
            # dict_nodes[G.node[nodo]['label']] = G.node[nodo]['ideo']
            v_current.append(g.nodes[nodo]['ideo'])
            v_new.append(0.0)

        v_current = 1. * np.array(v_current)
        v_new = 1. * np.array(v_new)
        notconverged = len(v_current)
        times = 0

        # Do as many times as required for convergence
        while notconverged > 0:
            times = times + 1
            t = time.time()

            # for all nodes apart from corenode, calculate opinion as average of neighbors
            for j in np.setdiff1d(list(range(len(v_current))), corenode):
                nodosin = Aij.getrow(j).nonzero()[1]
                if len(nodosin) > 0:
                    v_new[j] = np.mean(v_current[nodosin])
                else:
                    v_new[j] = v_current[j]
            #            nodos_changed[j]=nodos_changed[j] or (v_new[j]!=v_current[j])

            # update opinion
            for j in corenode:
                v_new[j] = v_current[j]

            diff = np.abs(v_current - v_new)
            notconverged = len(diff[diff > tol])
            v_current = v_new.copy()
        return v_current

    def calculate_polarization_index(self, ideos):
        # Input: Vector with individuals Xi
        # Output: Polarization index, Area Difference, Normalized Pole Distance
        D = []  # POLE DISTANCE
        AP = []  # POSSITIVE AREA
        AN = []  # NEGATIVE AREA
        cgp = []  # POSSITIVE GRAVITY CENTER
        cgn = []  # NEGATIVE GRAVITY CENTER

        ideos.sort()
        hist, edg = np.histogram(ideos, np.linspace(-1, 1.1, 50))
        edg = edg[:len(edg) - 1]
        AP = sum(hist[edg > 0])
        AN = sum(hist[edg < 0])
        AP0 = 1. * AP / (AP + AN)
        AN0 = 1. * AN / (AP + AN)
        cgp = sum(hist[edg > 0] * edg[edg > 0]) / sum(hist[edg > 0])
        cgn = sum(hist[edg < 0] * edg[edg < 0]) / sum(hist[edg < 0])
        D = cgp - cgn
        p1 = 0.5 * D * (1. - 1. * abs(AP0 - AN0))  # polarization index
        DA = 1. * abs(AP0 - AN0) / (AP0 + AN0)  # Areas Difference
        D = 0.5 * D  # Normalized Pole Distance
        # it seems: 1 = 4 = 6 and 2 = 5
        # e.g. for karate_easley:
        # 0.6969187675070029 0.05882352941176472 0.7404761904761905 0.6969187675070029 0.058823529411764705 0.6969187675070029
        print(p1, DA, D, (1 - DA) * D, abs((AP - AN) / (AP + AN)), (1 - abs((AP - AN) / (AP + AN))) * D)
        return p1