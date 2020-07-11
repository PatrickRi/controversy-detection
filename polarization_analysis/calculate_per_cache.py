import glob
import os
from datetime import datetime
from multiprocessing import Pool

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
from measures.utils import __read_partition_file, get_logger, get_node_percentage
from polarization_analysis.utils import normalize

pd.set_option('display.max_colwidth', -1)
pd.set_option('display.max_columns', None)


def create_measures(all, g, iggraph, node_mapping, left_part, right_part, doc_id, percent, plot, target_path):
    if all:
        measures_dict = {
            "BCC": BCC('BCC', g, iggraph, node_mapping, left_part, right_part, doc_id, cache=False),
            "BC": BoundaryConnectivity('BC', g, iggraph, node_mapping, left_part, right_part, doc_id),
            "EC": EmbeddingControversy('EC', g, iggraph, node_mapping, left_part, right_part, doc_id, cache=False,
                                       plot=plot, plot_target_path=target_path),
            "ECU(corr)": EmbeddingControversy('ECU(corr)', g, iggraph, node_mapping, left_part, right_part, doc_id,
                                              'umap',
                                              15, 'correlation', cache=False, plot=plot, plot_target_path=target_path),
            "ECU(n30)": EmbeddingControversy('ECU(n30)', g, iggraph, node_mapping, left_part, right_part, doc_id,
                                             'umap',
                                             30, cache=False, plot=plot, plot_target_path=target_path),
            "MBLB": MBLB('MBLB', g, iggraph, node_mapping, left_part, right_part, doc_id, percent=percent, cache=False),
            "Modularity": Modularity('Modularity', g, iggraph, node_mapping, left_part, right_part, doc_id),
            "PolarizationIndex": PolarizationIndex('PI', g, iggraph, node_mapping, left_part, right_part, doc_id,
                                                   cache=False),
            "RWC": RWC('RWC', g, iggraph, node_mapping, left_part, right_part, doc_id, percent=percent, iterations=1000)
        }
    else:
        measures_dict = {
            "BCC": BCC('BCC', g, iggraph, node_mapping, left_part, right_part, doc_id, cache=False),
            "EC": EmbeddingControversy('EC', g, iggraph, node_mapping, left_part, right_part, doc_id, cache=False,
                                       plot=plot, plot_target_path=target_path),
            "ECU(corr)": EmbeddingControversy('ECU(corr)', g, iggraph, node_mapping, left_part, right_part, doc_id,
                                              'umap',
                                              15, 'correlation', cache=False, plot=plot, plot_target_path=target_path),
            "ECU(n30)": EmbeddingControversy('ECU(n30)', g, iggraph, node_mapping, left_part, right_part, doc_id,
                                             'umap',
                                             30, cache=False, plot=plot, plot_target_path=target_path),
            "RWC": RWC('RWC', g, iggraph, node_mapping, left_part, right_part, doc_id, percent=percent, iterations=1000)
        }
    return list(measures_dict.values())


def calculate(m: Measure):
    try:
        line = []
        res = m.calculate()
        line.append(m.name)
        del m
        line.append(res)
        return line
    except Exception as e:
        print('ERROR at', m.name)
    return []


if __name__ == '__main__':
    logger = get_logger('main')
    posting_dirs = glob.glob('./cache/postings_top')
    found = False
    for posting_dir in posting_dirs:
        articles = glob.glob(os.path.join('.', posting_dir, '*'))
        for article in articles:
            doc_id = article.split(os.sep)[-1]
            # if doc_id == '2000054017662':
            #     found = True
            # if not found:
            #     continue
            logger.info('curr doc id: ' + doc_id)
            gml_path = glob.glob(os.path.join('.', article, '*.gml'))[0]
            graph = nx.read_gml(gml_path, label='id')
            iggraph: ig.Graph = ig.read(gml_path)
            g, node_mapping = normalize(graph)
            left_path = glob.glob(os.path.join('.', article, 'left', '*.txt'))[0]
            right_path = glob.glob(os.path.join('.', article, 'right', '*.txt'))[0]
            left_part = __read_partition_file(left_path)
            right_part = __read_partition_file(right_path)
            percent = get_node_percentage(g.number_of_nodes())
            df = pd.DataFrame(data=[], columns=['measure', 'result'])
            for i in range(5):
                arr = []
                plot = i == 0
                measures = create_measures(plot, g, iggraph, node_mapping, left_part, right_part, doc_id, percent, plot,
                                           article)
                p = Pool(9)
                res = p.map(calculate, measures)
                arr.append(res)
                for l in res:
                    df.loc[len(df)] = l
                p.terminate()
            df.index.name = 'idx'
            df.to_csv(os.path.join(article,
                                   'scores_' + datetime.now().strftime("%m-%d-%Y-%H%M%S") + '.csv'))
