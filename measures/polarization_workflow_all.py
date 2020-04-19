import glob
import os
from multiprocessing import Pool
from typing import List
import pandas as pd
from datetime import datetime
import numpy as np
import networkx as nx
import traceback
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
    if config['normalize'] or not graph_from_file.has_node(0):
        g, node_mapping = normalize_graph(graph_from_file)
    else:
        g: nx.Graph = graph_from_file
        node_mapping = {}
        for n in range(g.number_of_nodes()):
            node_mapping[n] = n
    logger.info('finished normalizing')

    left_part, right_part = get_partitions(config['partition'], config['partitions-path'], dataset_name)
    logger.info('finished loading partitions')
    nn = g.number_of_nodes()
    percent = 0.02
    iterations = 500
    if nn >= 10000:
        percent_n = 2000 * 0.02 + 8000 * 0.01 + (nn - 10000) * 0.005
        percent = percent_n / nn
        iterations = 10000
    elif nn >= 2000:
        percent_n = 2000 * 0.02 + (nn-2000) * 0.01
        percent = percent_n/nn
        iterations = 2000
    cache = config['cache']
    measures_list: List[Measure] = [
        #BCC(g, node_mapping, left_part, right_part, dataset_name, cache=False),
        #BoundaryConnectivity(g, node_mapping, left_part, right_part, dataset_name),
        #ClusteringCoefficient(g, node_mapping, left_part, right_part, dataset_name),
        EmbeddingControversy(g, node_mapping, left_part, right_part, dataset_name, cache=False, embedding='fa', plot=True),
        EmbeddingControversy(g, node_mapping, left_part, right_part, dataset_name, cache=False, embedding='umap', plot=True),
        EmbeddingControversy(g, node_mapping, left_part, right_part, dataset_name, cache=False, embedding='umap', metric='correlation', plot=True),
        #PolarizationIndex(g, node_mapping, left_part, right_part, dataset_name, cache=False),
        #MBLB(g, node_mapping, left_part, right_part, dataset_name, percent=percent, cache=False),
        #Modularity(g, node_mapping, left_part, right_part, dataset_name),
        #RWC(g, node_mapping, left_part, right_part, dataset_name, percent=percent, iterations=iterations),
    ]
    result_arr = []
    for m in measures_list:
        try:
            line = []
            line.append(dataset_name)
            logger.info('Calculating ' + m.__class__.__name__ + ' for %s', dataset_name)
            start = datetime.now()
            result = m.calculate()
            duration = (datetime.now() - start).seconds
            line.append(m.__class__.__name__)
            line.append(result)
            line.append(duration)
            result_arr.append(line)
            logger.info('Result for ' + m.__class__.__name__ + ' and dataset ' + dataset_name + ': ' + str(result))
        except BaseException as e:
            print('ERROR at', m.__class__.__name__, 'and dataset', dataset_name, str(e))
            traceback.print_tb(e.__traceback__)
    logger.info('RESULT:' + str(result_arr))
    return result_arr


if __name__ == '__main__':
    logger = get_logger('main')
    arr = []
    config = get_config(os.path.join(os.getcwd(), 'config.yaml'))
    files = glob.glob(os.path.join(config['dataset-path'], '*.gml'))
    #files = [f for f in files if 'NY_Teams_Twitter_cc.gml' in f]
    #files = [f for f in files if '_cc' in f and 'NY' not in f]
    #files = [f for f in files if 'karate' in f]
    def inList(f):
        ff = str(f).lower()
        #l = ['cruzeiro_atletico_twitter_cc', 'complete_graph_600', 'karate', 'connected_complete_graphs', 'gun_control_twitter_cc', 'facebook_friends_cc', 'ny_teams_twitter_cc', 'polblogs_cc']
        l = ['cruzeiro_atletico_twitter_cc', 'complete_graph_600', 'karate', 'connected_complete_graphs', 'gun_control_twitter_cc', 'facebook_friends_cc', 'polblogs_cc']
        for ll in l:
            if ll in ff:
                return True
        return False
    files = [f for f in files if inList(f)]
    # for f in files:
    #     if 'NY_Teams' in f:
    #         files.remove(f)
    p = Pool(4)
    res = p.map(process_file, files) #list(reversed(files))
    df = pd.DataFrame(data=[], columns=['dataset', 'measure', 'result', 'duration'])
    for l in res:
        for ll in l:
            df.loc[len(df)] = ll
    df.index.name = 'idx'
    df.to_csv(r'output_performanceForStripplot_' + datetime.now().strftime("%m-%d-%Y-%H%M%S") + '.csv')
    print(res)

