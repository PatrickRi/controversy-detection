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

if __name__ == '__main__':
    logger = get_logger('main')
    docid = '2000073253280'#UngarnFlüchtigline: '2000022399507'  # '2000073253280'
    target_path = os.path.join('cache', 'postings', docid)
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    ### fetch data
    # noinspection SqlNoDataSourceInspection
    query = Template("""SELECT p.ID_Posting, ID_Posting_Parent, p.ID_CommunityIdentity
    from Content c
        INNER JOIN Postings p ON p.ID_GodotObject=c.ID_GodotObject
    where c.ID_GodotObject='$docid'""")
    query = query.substitute(docid=docid)
    df = fetch_sql(query, docid, 'ID_Posting', logger, target_path)
    ### parse data into network_cc

    graph = postings_df_to_graph(df, logger)
    gml_target = os.path.join(target_path, docid + '.gml')
    nx.write_gml(graph, gml_target)
    iggraph: ig.Graph = ig.read(gml_target)
    ### partition
    g, node_mapping = normalize(graph)
    left_part, right_part = partition(g, target_path, docid)

    # run metrics on it
    percent = get_node_percentage(g.number_of_nodes())
    measures_list = [
        BCC(g, iggraph, node_mapping, left_part, right_part, docid, cache=False),
        BoundaryConnectivity(g, iggraph, node_mapping, left_part, right_part, docid),
        #ClusteringCoefficient(g, iggraph, node_mapping, left_part, right_part, docid),
        EmbeddingControversy(g, iggraph, node_mapping, left_part, right_part, docid),
        MBLB(g, iggraph, node_mapping, left_part, right_part, docid, percent=percent),
        Modularity(g, iggraph, node_mapping, left_part, right_part, docid),
        PolarizationIndex(g, iggraph, node_mapping, left_part, right_part, docid, cache=False),
        RWC(g, iggraph, node_mapping, left_part, right_part, docid, percent=percent)
    ]
    df = calc_measures_n_times_async(measures_list, 5, logger)
    df.to_csv(os.path.join(target_path, 'output' + datetime.now().strftime("%m-%d-%Y-%H%M%S") + '.csv'))
    print(df)
    df_stats = df[['measure', 'result']].groupby('measure').describe()
    df_stats.to_csv(os.path.join(target_path, 'stats' + datetime.now().strftime("%m-%d-%Y-%H%M%S") + '.csv'))
    print(df_stats)