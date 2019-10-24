import networkx as nx
from measures.utils import normalize_graph, get_config
from measures.modularity import Modularity
from measures.partition import get_partitioner, Partition
from .measure import Measure
import os
import yaml

config = get_config(os.path.join(os.getcwd(), 'config.yaml'))

graph_from_file = nx.read_gml(os.path.join(config['dataset-path'], config['dataset-name']), label='id')
g, node_mapping = normalize_graph(graph_from_file)

partitioner = get_partitioner(config['partition'])
left_part, right_part = partitioner.partition(g, node_mapping)

m = Modularity(g, node_mapping, left_part, right_part, config['dataset-name'])
score = m.calculate()
print(score)