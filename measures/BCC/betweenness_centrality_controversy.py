from typing import List
import igraph as ig
import networkx as nx
import numpy as np
from scipy.stats import entropy
from sklearn.neighbors import KernelDensity

from measures.measure import Measure
from .dataset_processor import get_centralities
from ..utils import list_to_dict


class BCC(Measure):

    def __init__(self, graph: nx.Graph, iggraph: ig.Graph, node_mapping: dict, left_part: List[int],
                 right_part: List[int], dataset: str, cache: bool = True, bandwidth: float = 0.0000001):
        super().__init__(graph, iggraph, node_mapping, left_part, right_part, dataset, cache)
        self.bandwidth = bandwidth
        self.left_dict = list_to_dict(self.left_part)
        self.right_dict = list_to_dict(self.right_part)

    def calculate(self) -> float:
        self.logger.info('Retrieve centralities')
        dict_edge_betweenness = get_centralities(self.graph, self.iggraph, self.dataset, self.cache)

        self.logger.info('Split lists')
        eb_list = []
        for s, t in self.graph.edges:
            if (s in self.left_part and t in self.right_part) or (s in self.right_part and t in self.left_part):
                if (s, t) in dict_edge_betweenness:
                    edge_betweenness = dict_edge_betweenness[(s, t)]
                    eb_list.append(edge_betweenness)
                else:
                    edge_betweenness = dict_edge_betweenness[(t, s)]
                    eb_list.append(edge_betweenness)
        eb_list_all = self.replace_with_small(list(dict_edge_betweenness.values()))
        eb_list = self.replace_with_small(eb_list)
        self.logger.info('Calculate entropy')

        # eb_list_np = np.zeros(5)
        # for i in range(5):
        #     eb_list_np[i] = self.sample_from_kde(np.array(eb_list)).mean()
        # eb_list_all_np = np.zeros(5)
        # for i in range(5):
        #     eb_list_all_np[i] = self.sample_from_kde(np.array(eb_list_all)).mean()
        # print('{:.15f}'.format(eb_list_np.mean()))
        # print('{:.15f}'.format(eb_list_np.std()))
        # print('{:.15f}'.format(eb_list_all_np.mean()))
        # print('{:.15f}'.format(eb_list_all_np.std()))
        #
        # entr = entropy(self.sample_from_kde(np.array(eb_list)), self.sample_from_kde(np.array(eb_list_all)))
        # print('{:.15f}'.format(entr[0]))
        # print('{:.15f}'.format(entropy(self.sample_from_kde(np.array(eb_list_all)), self.sample_from_kde(np.array(eb_list)))[0]))
        # print('{:.15f}'.format(
        #     entropy(self.sample_from_kde(np.array(eb_list) * 10000000),
        #             self.sample_from_kde(np.array(eb_list_all) * 10000000))[0]))
        # print('{:.15f}'.format(
        #     entropy(self.sample_from_kde(np.array(eb_list_all)*10000000), self.sample_from_kde(np.array(eb_list)*10000000))[0]))
        # return 1 - np.exp(-1.0 * entr)[0]
        entropies = np.zeros(1)
        for i in range(1):
            # np.savetxt('karate_eb_list.txt', eb_list, fmt='%f')
            # np.savetxt('karate_eb_list_all.txt', eb_list_all, fmt='%f')
            eb_list_all_sampled = self.sample_from_kde(np.array(eb_list_all) * 10000)
            eb_list_sampled = self.sample_from_kde(np.array(eb_list) * 10000)
            entr = entropy(eb_list_all_sampled, eb_list_sampled)
            # print(self.dataset, "  - Entropy:", entr, "Means:", eb_list_all_sampled.mean(), eb_list_sampled.mean())
            entropies[i] = 1 - np.exp(-1.0 * entr)[0]
        # print(self.dataset, " - alt Entropy:", 1 - np.exp(-1.0 * entropy(eb_list_sampled, eb_list_all_sampled))[0])
        # print(self.dataset, " - alt exp Entropy:", 1 - np.exp(-1.0 * entropy(np.exp(eb_list_sampled), np.exp(eb_list_all_sampled)))[0])
        return entropies.mean()

    def replace_with_small(self, arr):
        result = []
        for x in arr:
            if x < 0.000000001:
                result.append(0.000000001)
            else:
                result.append(x)
        return result

    def sample_from_kde(self, values: np.ndarray):
        kde_fitted = KernelDensity(bandwidth=self.bandwidth).fit(values.reshape(-1, 1))
        return kde_fitted.sample(10000)
