from measures.measure import Measure
import networkx as nx
from typing import List
from ..utils import list_to_dict
import igraph as ig


class ClusteringCoefficient(Measure):

    def __init__(self, name: str, graph: nx.Graph, iggraph: ig.Graph, node_mapping: dict, left_part: List[int], right_part: List[int], dataset: str):
        super().__init__(name, graph, iggraph, node_mapping, left_part, right_part, dataset, True)
        self.left_dict = list_to_dict(left_part)
        self.right_dict = list_to_dict(right_part)

    def calculate(self) -> float:
        # Note that igraph would be 4 times faster, but it only takes a few seconds + we get the individual coefficients
        # Note that normalization using a Null model is useless, as with a constant probability of drawing edges, the
        # expected clustering coefficient stays almost the same, regardless the size of the network
        #return self.calc_networkx()
        return self.calc_inter_cluster()


    def calc_inter_cluster(self):
        cl = nx.average_clustering(self.graph, nodes=self.left_part)
        cr = nx.average_clustering(self.graph, nodes=self.left_part)
        return (cr+cl)/2


    def calc_networkx(self):
        # extracted from nx.average_clustering
        count_zeros = True
        self.logger.info('Calculate local cluster coefficients (transitivity)')
        c = nx.clustering(self.graph).values()
        if not count_zeros:
            c = [v for v in c if v > 0]
        self.logger.info('Calculate mean')
        return sum(c) / len(c)


    def calc_igraph(self):
        self.logger.info('Start reading gml')
        ig_g: ig.Graph = ig.read('../partitioning/datasets/' + self.dataset + '.gml')
        self.logger.info('Calculate transitivity')
        igcc = ig_g.transitivity_avglocal_undirected(mode='zero')
        return igcc