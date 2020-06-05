from typing import List
import igraph as ig
import networkx as nx
import numpy as np
import scipy.sparse as sp

from measures.measure import Measure
from .dataset_processor import get_dataset_with_ideologies


class MBLB(Measure):

    def __init__(self, graph: nx.Graph, iggraph: ig.Graph, node_mapping: dict, left_part: List[int], right_part: List[int], dataset: str,
                 percent: float = 0.05, cache: bool = True):
        super().__init__(graph, iggraph, node_mapping, left_part, right_part, dataset, cache)
        self.percent = percent

    def calculate(self) -> float:
        g = get_dataset_with_ideologies(self.graph, self.dataset, self.left_part, self.right_part, self.percent,
                                        self.cache)
        self.logger.info('Retrieved datasets with ideologies')
        ideologies = nx.get_node_attributes(g, 'ideo')
        corenode = []
        for key in list(ideologies.keys()):
            if ideologies[key] == 1 or ideologies[key] == -1:
                corenode.append(key)
        self.logger.info('Creating model')
        v_current = self.model(g, corenode)
        self.logger.info('Calculating Polarization')
        return self.calculate_polarization_index(v_current)

    def model(self, g: nx.Graph, corenodes: List[int], tol=10 ** -4):
        """
        :param g: Graph to calculate opinions. The nodes have an attribute "ideo" with their ideology, set to 0 for all listeners, 1 and -1 for the elite.
        :param corenodes: Nodes that belong to the seed (Identifiers from the Graph G)
        :param tol: threshold for convergence. It will evaluate the difference between opinions at time t and t+1
        :return: array
        """
        N = g.number_of_nodes()

        # Build the adjacency matrix
        Aij = sp.lil_matrix((N, N))
        self.logger.info("Adjacency matrix shape: %s", str(Aij.shape))
        for o, d in g.edges():
            Aij[o, d] = 1
            Aij[d, o] = 1
        # Build the vectors with users opinions
        v_current = []
        v_new = []
        for nodo in list(g.nodes()):
            v_current.append(g.nodes[nodo]['ideo'])
            v_new.append(0.0)

        v_current = 1. * np.array(v_current)
        v_new = 1. * np.array(v_new)
        notconverged = len(v_current)
        times = 0
        self.logger.info('Starting to converge...')
        # Do as many times as required for convergence
        not_converged_tracker = []
        while notconverged > 0:
            times = times + 1

            # for all nodes apart from corenode, calculate opinion as average of neighbors
            iter_nodes = np.setdiff1d(list(range(len(v_current))), corenodes)
            for j in iter_nodes:
                nodosin = Aij.getrow(j).nonzero()[1]
                if len(nodosin) > 0:
                    v_new[j] = np.mean(v_current[nodosin])
                else:
                    v_new[j] = v_current[j]

            # update opinion
            for j in corenodes:
                v_new[j] = v_current[j]

            diff = np.abs(v_current - v_new)
            notconverged = len(diff[diff > tol])
            if times % 5 == 0:
                self.logger.info('Unconverged: %s after %s times', str(notconverged), times)
                not_converged_tracker.append(notconverged)
                if len(not_converged_tracker) > 100 and np.mean(not_converged_tracker[-3:]) == notconverged:
                    self.logger.info('No change in 500 iterations, stopping')
                    notconverged = 0
            v_current = v_new.copy()
        return v_current

    def calculate_polarization_index(self, ideos):
        # Input: Vector with individuals Xi
        # Output: Polarization index, Area Difference, Normalized Pole Distance
        D = []  # POLE DISTANCE
        AP = []  # POSITIVE AREA
        AN = []  # NEGATIVE AREA
        cgp = []  # POSITIVE GRAVITY CENTER
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
        # 1 = 4 = 6 and 2 = 5
        # e.g. for karate_easley:
        # 0.6969187675070029 0.05882352941176472 0.7404761904761905 0.6969187675070029 0.058823529411764705 0.6969187675070029
        # polblogs_cc:
        # 0.6657809037580392 0.09656301145662849 0.736942268471308 0.6657809037580392 0.09656301145662848 0.6657809037580392
        # print(p1, DA, D, (1 - DA) * D, abs((AP - AN) / (AP + AN)), (1 - abs((AP - AN) / (AP + AN))) * D)
        return p1
