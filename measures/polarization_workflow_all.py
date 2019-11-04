import glob
import os
from typing import List

import networkx as nx
import pandas as pd

from measures.EC import EmbeddingControversy
from measures.GMCK import BoundaryConnectivity
from measures.MBLB import MBLB
from measures.measure import Measure
from measures.modularity import Modularity
from measures.RWC import RWC
from measures.utils import get_config, get_logger, get_partitions, normalize_graph

logger = get_logger('main')
arr = []
config = get_config(os.path.join(os.getcwd(), 'config.yaml'))
files = glob.glob(os.path.join(config['dataset-path'], '*.gml'))
for file in files:
    dataset_name = os.path.basename(file).split('.')[0]
    logger.info('Start processing %s', dataset_name)
    graph_from_file = nx.read_gml(file, label='id')
    # partitions are normalized too, therefore necessary to achieve matching
    g, node_mapping = normalize_graph(graph_from_file)

    # partitioner = get_partitioner(config['partition'])
    # left_part, right_part = partitioner.partition(g, node_mapping)
    left_part, right_part = get_partitions(config['partition'], config['partitions-path'], dataset_name)

    measures_list: List[Measure] = [
        # BCC(g, node_mapping, left_part, right_part, dataset_name),
        BoundaryConnectivity(g, node_mapping, left_part, right_part, dataset_name),
        EmbeddingControversy(g, node_mapping, left_part, right_part, dataset_name),
        MBLB(g, node_mapping, left_part, right_part, dataset_name),
        Modularity(g, node_mapping, left_part, right_part, dataset_name),
        RWC(g, node_mapping, left_part, right_part, dataset_name, percent=0.05)
    ]
    line = []
    line.append(dataset_name)
    for m in measures_list:
        logger.info('Calculating ' + m.__class__.__name__ + ' for %s', dataset_name)
        result = m.calculate()
        line.append(result)
        logger.info('Result:: %s', result)
    arr.append(line)
dfcsv = pd.DataFrame(data=arr, columns=['dataset', 'GMCK', 'EC', 'MBLB', 'Modularity', 'RWC'])
dfcsv.to_csv(r'output.csv')
