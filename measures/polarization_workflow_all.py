import glob
import os
from multiprocessing import Pool
from typing import List

import networkx as nx

from measures.BCC import BCC
from measures.EC import EmbeddingControversy
from measures.GMCK import BoundaryConnectivity
from measures.MBLB import MBLB
from measures.measure import Measure
from measures.modularity import Modularity
from measures.RWC import RWC
from measures.utils import get_config, get_logger, get_partitions, normalize_graph


def process_file(file):
    dataset_name = str(os.path.basename(file).split('.')[0])
    logger = get_logger('main')
    logger.info('Start processing %s', dataset_name)
    logger.info('start reading gml')
    graph_from_file = nx.read_gml(file, label='id')
    logger.info('finished reading gml')
    # partitions are normalized too, therefore necessary to achieve matching
    config = get_config(os.path.join(os.getcwd(), 'config.yaml'))
    if config['normalize']:
        g, node_mapping = normalize_graph(graph_from_file)
    else:
        g: nx.Graph = graph_from_file
        node_mapping = {}
        for n in range(g.number_of_nodes()):
            node_mapping[n] = n
    logger.info('finished normalizing')

    left_part, right_part = get_partitions(config['partition'], config['partitions-path'], dataset_name)
    logger.info('finished loading partitions')

    measures_list: List[Measure] = [
        #BCC(g, node_mapping, left_part, right_part, dataset_name),
        BoundaryConnectivity(g, node_mapping, left_part, right_part, dataset_name),
        EmbeddingControversy(g, node_mapping, left_part, right_part, dataset_name),
        #MBLB(g, node_mapping, left_part, right_part, dataset_name),
        Modularity(g, node_mapping, left_part, right_part, dataset_name),
        RWC(g, node_mapping, left_part, right_part, dataset_name, percent=0.05)
    ]
    line = []
    line.append(dataset_name)
    for m in measures_list:
        logger.info('Calculating ' + m.__class__.__name__ + ' for %s', dataset_name)
        result = m.calculate()
        line.append(result)
        logger.info('Result for ' + m.__class__.__name__ + ' and dataset ' + dataset_name + ': ' + str(result))
    return line


if __name__ == '__main__':
    logger = get_logger('main')
    arr = []
    config = get_config(os.path.join(os.getcwd(), 'config.yaml'))
    files = glob.glob(os.path.join(config['dataset-path'], '*.gml'))
    p = Pool(10)
    res = p.map(process_file, files)
    print(res)
    # dfcsv = pd.DataFrame(data=arr, columns=['dataset', 'GMCK', 'EC', 'MBLB', 'Modularity', 'RWC'])
    # dfcsv.to_csv(r'output.csv')
