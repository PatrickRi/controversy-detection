import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from multiprocessing import Pool
import os
from datetime import datetime
import igraph as ig
import networkx as nx
import pyodbc
import numpy as np
from string import Template
from measures.BCC import BCC
from measures.CC import ClusteringCoefficient
from measures.EC import EmbeddingControversy
from measures.GMCK import BoundaryConnectivity
from measures.MBLB import MBLB
from measures.modularity import Modularity
from measures.PI import PolarizationIndex
from measures.RWC import RWC
from measures.utils import get_config, get_logger, get_partitions, normalize_graph, get_node_percentage
from polarization_analysis.utils import postings_df_to_graph, partition, normalize, fetch_sql, write_name_file, calc_measures_n_times, calc_measures_n_times_async
pd.set_option('display.max_colwidth', -1)
pd.set_option('display.max_columns', None)

def calc_polarization(doc_id, query, id_col, type, measures=None):
    logger = get_logger('main')
    target_path = os.path.join('cache', type, doc_id)
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    ### fetch data
    # noinspection SqlNoDataSourceInspection
    df = fetch_sql(query, doc_id, id_col, logger, target_path)
    ### parse data into network_cc

    graph = postings_df_to_graph(df, logger)
    gml_target = os.path.join(target_path, doc_id + '.gml')
    nx.write_gml(graph, gml_target)
    iggraph: ig.Graph = ig.read(gml_target)
    ### partition
    g, node_mapping = normalize(graph)
    left_part, right_part = partition(g, target_path, doc_id)

    # run metrics on it
    percent = get_node_percentage(g.number_of_nodes())
    measures_dict = {
        "BCC": BCC(g, iggraph, node_mapping, left_part, right_part, doc_id, cache=False),
        "BoundaryConnectivity": BoundaryConnectivity(g, iggraph, node_mapping, left_part, right_part, doc_id),
        # ClusteringCoefficient(g, iggraph, node_mapping, left_part, right_part, doc_id),
        "EmbeddingControversy": EmbeddingControversy(g, iggraph, node_mapping, left_part, right_part, doc_id),
        "MBLB": MBLB(g, iggraph, node_mapping, left_part, right_part, doc_id, percent=percent),
        "Modularity": Modularity(g, iggraph, node_mapping, left_part, right_part, doc_id),
        "PolarizationIndex": PolarizationIndex(g, iggraph, node_mapping, left_part, right_part, doc_id, cache=False),
        "RWC": RWC(g, iggraph, node_mapping, left_part, right_part, doc_id, percent=percent)
    }
    if measures is None:
        measures_list = measures_dict.values()
    else:
        measures_list = [measures_dict[m] for m in measures]
    df = calc_measures_n_times_async(measures_list, 10, logger)
    df.to_csv(os.path.join(target_path, 'output_' + datetime.now().strftime("%m-%d-%Y-%H%M%S") + '.csv'))
    #print(df)
    df_stats = df[['measure', 'result']].groupby('measure').describe()
    df_stats.to_csv(os.path.join(target_path, 'stats_' + datetime.now().strftime("%m-%d-%Y-%H%M%S") + '.csv'))
    df_stats_flattened = df[['measure', 'result']].groupby('measure').describe().unstack().reset_index()
    df_stats_flattened.to_csv(os.path.join(target_path, 'stats_flattended_' + datetime.now().strftime("%m-%d-%Y-%H%M%S") + '.csv'))
    #print(df_stats)
    return df_stats_flattened