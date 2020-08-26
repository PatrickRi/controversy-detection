import glob
import os
import traceback
from datetime import datetime
from multiprocessing import Pool
from typing import List

import igraph as ig
import networkx as nx
import pandas as pd

from measures.BCC import BCC
from measures.EC import EmbeddingControversy
from measures.GMCK import BoundaryConnectivity
from measures.MBLB import MBLB
from measures.measure import Measure
from measures.modularity import Modularity
from measures.PI import PolarizationIndex
from measures.RWC import RWC
from measures.utils import get_config, get_logger, get_node_percentage, get_partitions, normalize_graph


def process_file(file):
    dataset_name = str(os.path.basename(file).split('.')[0])
    logger = get_logger('main')
    logger.info('Start processing %s', dataset_name)
    logger.info('start reading gml')
    graph_from_file = nx.read_gml(file, label='id')
    iggraph: ig.Graph = ig.read(file)
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
    percent = get_node_percentage(g.number_of_nodes())
    cache = config['cache']
    measures_list: List[Measure] = [
        # BCC('BCC', g, iggraph, node_mapping, left_part, right_part, dataset_name, cache=False),
        # BoundaryConnectivity('BC', g, iggraph, node_mapping, left_part, right_part, dataset_name),
        # ClusteringCoefficient(g, node_mapping, left_part, right_part, dataset_name),
        EmbeddingControversy('EC', g, iggraph, node_mapping, left_part, right_part, dataset_name, cache=False,
                             embedding='fa', plot=True),
        EmbeddingControversy('ECU', g, iggraph, node_mapping, left_part, right_part, dataset_name, cache=False,
                             embedding='umap', plot=True, n_neighbors=30),
        EmbeddingControversy('ECU(corr)', g, iggraph, node_mapping, left_part, right_part, dataset_name, cache=False,
                             embedding='umap', metric='correlation', plot=True),
        # PolarizationIndex('PI', g, iggraph, node_mapping, left_part, right_part, dataset_name, cache=False),
        # MBLB('MBLB', g, iggraph, node_mapping, left_part, right_part, dataset_name, percent=percent, cache=False),
        # Modularity('Modularity', g, iggraph, node_mapping, left_part, right_part, dataset_name),
        RWC('RWC', g, iggraph, node_mapping, left_part, right_part, dataset_name, percent=percent,
            iterations=1000),
    ]
    result_arr = []
    for m in measures_list:
        try:
            line = []
            line.append(dataset_name)
            logger.info('Calculating ' + m.name + ' for %s', dataset_name)
            start = datetime.now()
            result = m.calculate()
            duration = (datetime.now() - start).seconds
            line.append(m.name)
            line.append(result)
            line.append(duration)
            result_arr.append(line)
            logger.info('Result for ' + m.name + ' and dataset ' + dataset_name + ': ' + str(result))
        except BaseException as e:
            print('ERROR at', m.name, 'and dataset', dataset_name, str(e))
            traceback.print_tb(e.__traceback__)
    logger.info('RESULT:' + str(result_arr))
    return result_arr


if __name__ == '__main__':
    logger = get_logger('main')
    arr = []
    config = get_config(os.path.join(os.getcwd(), 'config.yaml'))
    files = glob.glob(os.path.join(config['dataset-path'], '*.gml'))


    # files = [f for f in files if 'NY_Teams_Twitter_cc.gml' in f]
    # files = [f for f in files if '_cc' in f and 'NY' not in f]
    # files = [f for f in files if 'karate' in f]
    def inList(f):
        ff = str(f).lower()
        # l = ['cruzeiro_atletico_twitter_cc', 'complete_graph_600', 'karate', 'connected_complete_graphs', 'gun_control_twitter_cc', 'facebook_friends_cc', 'ny_teams_twitter_cc', 'polblogs_cc']
        # l = ['cruzeiro_atletico_twitter_cc', 'complete_graph_600', 'karate', 'connected_complete_graphs', 'gun_control_twitter_cc', 'facebook_friends_cc', 'polblogs_cc']
        l = ['follow_ignore_cc', 'following_cc', 'ignoring_cc']
        # l = ['follow_ignore_cc']
        for ll in l:
            if ll in ff:
                return True
        return False


    files = [f for f in files if inList(f)]
    # for f in files:
    #     if 'NY_Teams' in f:
    #         files.remove(f)
    p = Pool(1)
    res = p.map(process_file, files)  # list(reversed(files))
    df = pd.DataFrame(data=[], columns=['dataset', 'measure', 'result', 'duration'])
    for l in res:
        for ll in l:
            df.loc[len(df)] = ll
    df.index.name = 'idx'
    df.to_csv(r'community_connection_' + datetime.now().strftime("%m-%d-%Y-%H%M%S") + '.csv')
    print(res)
