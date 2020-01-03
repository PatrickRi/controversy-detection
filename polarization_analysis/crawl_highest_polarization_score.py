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
from polarization_analysis.utils import postings_df_to_graph, partition, normalize, fetch_sql, write_name_file, \
    calc_measures_n_times, calc_measures_n_times_async
from polarization_analysis.pol_workflow_utils import calc_polarization

pd.set_option('display.max_colwidth', -1)
pd.set_option('display.max_columns', None)

if __name__ == '__main__':
    template = Template("""SELECT p.ID_Posting, ID_Posting_Parent, p.ID_CommunityIdentity
            from Content c
                INNER JOIN Postings p ON p.ID_GodotObject=c.ID_GodotObject
            where c.ID_GodotObject='$docid'""")
    measures_list = [
        "BCC", "BoundaryConnectivity", "EmbeddingControversy", "MBLB", "Modularity", "PolarizationIndex", "RWC"
    ]
    df_posting_count = pd.read_csv('postings_per_article.csv', sep=';', names=['docid', 'cnt', 'title'], index_col='docid')
    for (docid,cnt) in df_posting_count['cnt'].iteritems():
        query = template.substitute(docid=docid)
        df_stats_flattened = calc_polarization(str(docid), query, 'ID_Posting', 'postings', measures=measures_list)
        for m in measures_list:
            a = df_stats_flattened.loc[(df_stats_flattened['level_1'] == 'mean' ) & (df_stats_flattened['measure'] == m)]
            a['level_0'] = str(docid)
            print(a.to_string(index=False, header=False))
