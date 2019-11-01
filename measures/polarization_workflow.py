import networkx as nx

from measures.BCC import BCC
from measures.MBLB import MBLB
from measures.GMCK import BoundaryConnectivity
from measures.EC import EmbeddingControversy
from measures.measure import Measure
from measures.utils import normalize_graph, get_config, get_partitions
from measures.modularity import Modularity
from measures.RWC import RWC
from typing import List
import os

config = get_config(os.path.join(os.getcwd(), 'config.yaml'))

dataset_name = config['dataset-name']
graph_from_file = nx.read_gml(os.path.join(config['dataset-path'], dataset_name + '.gml'), label='id')
# partitions are normalized too, therefore necessary to achieve matching
g, node_mapping = normalize_graph(graph_from_file)

# partitioner = get_partitioner(config['partition'])
# left_part, right_part = partitioner.partition(g, node_mapping)
left_part, right_part = get_partitions(config['partition'], config['partitions-path'], dataset_name)

measures_list: List[Measure] = [
    #BCC(g, node_mapping, left_part, right_part, dataset_name),
    BoundaryConnectivity(g, node_mapping, left_part, right_part, dataset_name),
    EmbeddingControversy(g, node_mapping, left_part, right_part, dataset_name),
    MBLB(g, node_mapping, left_part, right_part, dataset_name),
    Modularity(g, node_mapping, left_part, right_part, dataset_name),
    RWC(g, node_mapping, left_part, right_part, dataset_name, percent=0.05)

]
for m in measures_list:
    print(m.__class__.__name__, m.calculate())
