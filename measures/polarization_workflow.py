import os
from typing import List
import numpy as np
import networkx as nx

from measures.BCC import BCC
from measures.CC import ClusteringCoefficient
from measures.EC import EmbeddingControversy
from measures.GMCK import BoundaryConnectivity
from measures.MBLB import MBLB
from measures.measure import Measure
from measures.modularity import Modularity
from measures.PI import PolarizationIndex
from measures.RWC import RWC
import igraph as ig
from measures.utils import get_config, get_logger, get_partitions, normalize_graph, get_node_percentage

logger = get_logger('main')

config = get_config(os.path.join(os.getcwd(), 'config.yaml'))

# dataset_name = config['dataset-name']
dataset_name = 'karate'#'gun_control_Twitter_cc'#'connected_complete_graphs'#'Facebook_Friends_cc' #NY_Teams_Twitter_cc #'NY_Teams_Twitter_cc'  # 'Cruzeiro_Atletico_Twitter_cc'
logger.info('start reading gml')
graph_from_file: nx.Graph = nx.read_gml(os.path.join(config['dataset-path'], dataset_name + '.gml'), label='id')
iggraph: ig.Graph = ig.read(os.path.join(config['dataset-path'], dataset_name + '.gml'))
logger.info('finished reading gml')
# partitions are normalized too, therefore necessary to achieve matching
# only necessary if input doesn't start from 0
if config['normalize'] or not graph_from_file.has_node(0):
    g, node_mapping = normalize_graph(graph_from_file)
else:
    g: nx.Graph = graph_from_file
    node_mapping = {}
    for n in range(g.number_of_nodes()):
        node_mapping[n] = n
logger.info('finished normalizing')

# partitioner = get_partitioner(config['partition'])
# left_part, right_part = partitioner.partition(g, node_mapping)
left_part, right_part = get_partitions(config['partition'], config['partitions-path'], dataset_name)
logger.info('finished loading partitions')
arr = []
percent = get_node_percentage(g.number_of_nodes())

measures_list: List[Measure] = [
    BCC(g, iggraph, node_mapping, left_part, right_part, dataset_name, cache=False),
    # BCC(g, iggraph, node_mapping, left_part, right_part, dataset_name, cache=False),
    # BCC(g, iggraph, node_mapping, left_part, right_part, dataset_name, cache=False),
    # BCC(g, iggraph, node_mapping, left_part, right_part, dataset_name, cache=False),
    BoundaryConnectivity(g, iggraph, node_mapping, left_part, right_part, dataset_name),
    ClusteringCoefficient(g, iggraph, node_mapping, left_part, right_part, dataset_name),
    EmbeddingControversy(g, iggraph, node_mapping, left_part, right_part, dataset_name, embedding='umap', cache=False, plot=False),
    MBLB(g, iggraph, node_mapping, left_part, right_part, dataset_name, percent=percent),
    Modularity(g, iggraph, node_mapping, left_part, right_part, dataset_name),
    PolarizationIndex(g, iggraph, node_mapping, left_part, right_part, dataset_name, cache=False),
    RWC(g, iggraph, node_mapping, left_part, right_part, dataset_name, percent=percent)
]
for i in range(1):
    for m in measures_list:

        logger.info('Start calculating %s', m.__class__.__name__)
        result = m.__class__.__name__, m.calculate()
        arr.append(result)
        print(result)
print(arr)
print(np.mean(np.array([x[1] for x in arr])))
print(np.std(np.array([x[1] for x in arr])))
