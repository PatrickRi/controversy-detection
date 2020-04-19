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
from measures.utils import get_config, get_logger, get_partitions, normalize_graph

logger = get_logger('main')

config = get_config(os.path.join(os.getcwd(), 'config.yaml'))

# dataset_name = config['dataset-name']
dataset_name = 'connected_complete_graphs'#'gun_control_Twitter_cc'#'connected_complete_graphs'#'Facebook_Friends_cc' #NY_Teams_Twitter_cc #'NY_Teams_Twitter_cc'  # 'Cruzeiro_Atletico_Twitter_cc'
logger.info('start reading gml')
graph_from_file: nx.Graph = nx.read_gml(os.path.join(config['dataset-path'], dataset_name + '.gml'), label='id')
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
nn=g.number_of_nodes()
percent = 0.02
if nn >= 10000:
    percent_n = 2000 * 0.02 + 8000 * 0.01 + (nn - 10000) * 0.005
    percent = percent_n / nn
elif nn >= 2000:
    percent_n = 2000 * 0.02 + (nn-2000) * 0.01
    percent = percent_n/nn

measures_list: List[Measure] = [
    BCC(g, node_mapping, left_part, right_part, dataset_name, cache=False),
    BCC(g, node_mapping, left_part, right_part, dataset_name, cache=False),
    BCC(g, node_mapping, left_part, right_part, dataset_name, cache=False),
    BCC(g, node_mapping, left_part, right_part, dataset_name, cache=False),
    #BoundaryConnectivity(g, node_mapping, left_part, right_part, dataset_name),
    #ClusteringCoefficient(g, node_mapping, left_part, right_part, dataset_name),
    #EmbeddingControversy(g, node_mapping, left_part, right_part, dataset_name, embedding='umap', cache=False, plot=True),
    #MBLB(g, node_mapping, left_part, right_part, dataset_name, percent=percent),
    #Modularity(g, node_mapping, left_part, right_part, dataset_name),
    #PolarizationIndex(g, node_mapping, left_part, right_part, dataset_name, cache=False),
    #RWC(g, node_mapping, left_part, right_part, dataset_name, percent=percent)

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
