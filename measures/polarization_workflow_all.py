import glob
import os
from multiprocessing import Pool
from typing import List
import pandas as pd
import numpy as np
import networkx as nx

from measures.PI import PolarizationIndex
from measures.BCC import BCC
from measures.EC import EmbeddingControversy
from measures.GMCK import BoundaryConnectivity
from measures.CC import ClusteringCoefficient
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

    if g.number_of_nodes() < 100:
        percent = 0.1
    elif g.number_of_nodes() < 1000:
        percent = 0.03
    elif g.number_of_nodes() < 10000:
        percent = 0.01
    else:
        percent = 0.001
    cache = config['cache']
    measures_list: List[Measure] = [
        BCC(g, node_mapping, left_part, right_part, dataset_name, cache=cache),
        BoundaryConnectivity(g, node_mapping, left_part, right_part, dataset_name),
        ClusteringCoefficient(g, node_mapping, left_part, right_part, dataset_name),
        EmbeddingControversy(g, node_mapping, left_part, right_part, dataset_name, cache=cache),
        PolarizationIndex(g, node_mapping, left_part, right_part, dataset_name, cache=cache),
        MBLB(g, node_mapping, left_part, right_part, dataset_name, percent=percent, cache=cache),
        Modularity(g, node_mapping, left_part, right_part, dataset_name),
        RWC(g, node_mapping, left_part, right_part, dataset_name, percent=percent)
    ]
    result_arr = []
    for m in measures_list:
        line = []
        line.append(dataset_name)
        logger.info('Calculating ' + m.__class__.__name__ + ' for %s', dataset_name)
        result = m.calculate()
        line.append(m.__class__.__name__)
        line.append(result)
        result_arr.append(line)
        logger.info('Result for ' + m.__class__.__name__ + ' and dataset ' + dataset_name + ': ' + str(result))
    logger.info('RESULT:' + str(result_arr))
    return result_arr


if __name__ == '__main__':
    logger = get_logger('main')
    arr = []
    config = get_config(os.path.join(os.getcwd(), 'config.yaml'))
    files = glob.glob(os.path.join(config['dataset-path'], '*.gml'))
    files = [f for f in files if 'NY_Teams' not in f]
    # for f in files:
    #     if 'NY_Teams' in f:
    #         files.remove(f)
    p = Pool(10)
    res = p.map(process_file, list(reversed(files)))
    df = pd.DataFrame(data=[], columns=['dataset', 'measure', 'result'])
    for l in res:
        for ll in l:
            df.loc[len(df)] = ll
    df.index.name = 'idx'
    df.to_csv(r'outputr.csv')
    print(res)

