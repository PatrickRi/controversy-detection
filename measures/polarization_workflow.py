import networkx as nx

from measures.BCC import BCC
from measures.MBLB import MBLB
from measures.GMCK import BoundaryConnectivity
from measures.EC import EmbeddingControversy
from measures.measure import Measure
from measures.utils import normalize_graph, get_config, get_partitions, get_logger
from measures.modularity import Modularity
from measures.RWC import RWC
from typing import List
import os

logger = get_logger('main')

config = get_config(os.path.join(os.getcwd(), 'config.yaml'))

dataset_name = config['dataset-name']
logger.info('start reading gml')
graph_from_file = nx.read_gml(os.path.join(config['dataset-path'], dataset_name + '.gml'), label='id')
logger.info('finished reading gml')
# partitions are normalized too, therefore necessary to achieve matching
# only necessary if input doesn't start from 0
if config['normalize']:
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

measures_list: List[Measure] = [
    BCC(g, node_mapping, left_part, right_part, dataset_name),
    #BoundaryConnectivity(g, node_mapping, left_part, right_part, dataset_name),
    #EmbeddingControversy(g, node_mapping, left_part, right_part, dataset_name),
    #MBLB(g, node_mapping, left_part, right_part, dataset_name, 0.01),
    #Modularity(g, node_mapping, left_part, right_part, dataset_name, algorithm='newman'),
    #RWC(g, node_mapping, left_part, right_part, dataset_name, percent=0.05)

]
for m in measures_list:
    logger.info('Start calculating %s', m.__class__.__name__)
    print(m.__class__.__name__, m.calculate())
