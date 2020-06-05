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
from polarization_analysis.pol_workflow_utils import calc_polarization
pd.set_option('display.max_colwidth', -1)
pd.set_option('display.max_columns', None)

if __name__ == '__main__':
    docid = '2000010118013'
    query = Template("""SELECT v.ID_CommunityIdentity, v.ID_Posting, ID_Posting_Parent
        from Content c
            INNER JOIN Postings p ON p.ID_GodotObject=c.ID_GodotObject
	        INNER JOIN Votes v ON v.ID_Posting=p.ID_Posting
        where c.ID_GodotObject='$docid'""")
    query = query.substitute(docid=docid)
    calc_polarization(docid, query, None, 'votes')