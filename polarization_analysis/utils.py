from string import Template
from multiprocessing import Pool
import base64
import re
from urllib.parse import urlencode
import pyodbc
import networkx as nx
import pandas as pd
from typing import List
import numpy as np
from measures.utils import normalize_graph
from measures.measure import Measure
from partitioning.partition_utils import metis_to_nodelist, to_adjacency_list, write_nodelist_file
import pymetis
import os


def postings_df_to_graph(df: pd.DataFrame, logger, min_weight):
    graph = nx.DiGraph()
    # dictionary of postings and their authors
    posting_dictionary = {}  # Posting -> CommunityIdentity
    # dictionary of parent postings
    parent_dictionary = {}  # Posting -> Parent

    for row in df.iterrows():
        posting_id = row[0]
        posting_dictionary[posting_id] = row[1][1]
        posting_parent_id = row[1][0]
        if not np.isnan(posting_parent_id):
            parent_dictionary[posting_id] = posting_parent_id

    def get_parent_community(posting_id):
        if posting_id not in parent_dictionary:
            return posting_id
        else:
            return get_parent_community(parent_dictionary[posting_id])

    for posting_id, comm_ident in posting_dictionary.items():
        if posting_id not in parent_dictionary:
            pass
        else:
            parent = get_parent_community(posting_id)
            parent_ci = posting_dictionary[parent]
            if graph.has_edge(comm_ident, parent_ci):
                graph[comm_ident][parent_ci]['weight'] = graph[comm_ident][parent_ci]['weight'] + 1
            else:
                graph.add_edge(comm_ident, parent_ci, weight=1)
    to_be_removed=[]
    for edge in graph.edges:
        if graph[edge[0]][edge[1]]['weight'] < min_weight:
            to_be_removed.append(edge)
    logger.info('Number of to be removed edges ' + str(len(to_be_removed)) + ' which is ' + str(
        (len(to_be_removed) / graph.number_of_edges()) * 100) + '% of all edges')
    for edge in to_be_removed:
        graph.remove_edge(edge[0], edge[1])
    ccs = list(nx.weakly_connected_components(graph))
    if len(ccs) > 1:
        lengths = [len(c) for c in sorted(ccs, key=len, reverse=True)]
        logger.info('Largest CC has size ' + str(lengths[0]) + ' which is ' + str(
            (lengths[0] / graph.number_of_nodes()) * 100) + '% of the dataset')
        largest_cc = max(ccs, key=len)
        graph = graph.subgraph(largest_cc).copy()
    return graph


def partition(g, target_path, docid):
    (edgecuts, parts) = pymetis.part_graph(2, adjacency=to_adjacency_list(g))
    left, right = metis_to_nodelist(parts)
    write_nodelist_file(os.path.join(target_path, 'left'), docid, left)
    write_nodelist_file(os.path.join(target_path, 'right'), docid, right)
    return [int(x) for x in left], [int(x) for x in right]


def normalize(graph):
    g = nx.Graph(graph)
    g = nx.convert_node_labels_to_integers(g)
    if not g.has_node(0):
        g, node_mapping = normalize_graph(g)
    else:
        g: nx.Graph = g
        node_mapping = {}
        for n in range(g.number_of_nodes()):
            node_mapping[n] = n
    return g, node_mapping


def fetch_sql(query, docid, index_col, logger, target_path, sql_cache):
    target = os.path.join(target_path, 'sql_result.pkl')
    if os.path.exists(target) and sql_cache:
        logger.info('Reading query from cache')
        return pd.read_pickle(target)
    else:
        sql_conn = pyodbc.connect(
            'DRIVER={SQL Server Native Client 11.0};SERVER=si;DATABASE=Standard-Export-06062019;Trusted_Connection=yes')
        df = pd.read_sql(query, sql_conn, index_col=index_col, coerce_float=False)
        logger.info('Fetched ' + str(len(df)) + ' rows')
        df.to_csv(os.path.join(target_path, 'sql_result.csv'))
        df.to_pickle(target)
        write_name_file(docid, target_path)
        return df


def write_name_file(docid, target_path):
    sql_conn = pyodbc.connect(
        'DRIVER={SQL Server Native Client 11.0};SERVER=si;DATABASE=Standard-Export-06062019;Trusted_Connection=yes')
    cursor = sql_conn.cursor()
    query = Template("""select titletext from Content where ID_GodotObject = '$docid'""")
    query = query.substitute(docid=docid)
    cursor.execute(query)
    row = cursor.fetchone()
    if row:
        title = re.sub(r'(?u)[^-\w.]', '', str(row[0]).strip().replace(' ', '_'))
        title = title.replace('.', '_')
        open(os.path.join(target_path, title + '.txt'), 'a').close()


def calc_measures(measures_list: List[Measure], logger):
    arr =[]
    for m in measures_list:
        try:
            line=[]
            logger.info('Calculating ' + m.name)
            result = m.calculate()
            line.append(m.name)
            line.append(result)
            arr.append(line)
            logger.info('Result for ' + m.name + ': ' + str(result))
        except Exception as e:
            print('ERROR at', m.name)
    return arr

def calc_measures_n_times(measures_list, times, logger):
    df = pd.DataFrame(data=[], columns=['measure', 'result'])
    for i in range(times):
        arr = calc_measures(measures_list, logger)
        for l in arr:
            df.loc[len(df)] = l
    df.index.name = 'idx'
    return df

def calc_measures_n_times_async(measures_list, times, logger):
    p = Pool(times)
    args = []
    for i in range(times):
        args.append((measures_list, logger))
    #res = p.map(calc_measures, args)
    #res = p.starmap(calc_measures, [[measures_list] * times, [logger] * times])
    res = p.starmap(calc_measures, args)
    df = pd.DataFrame(data=[], columns=['measure', 'result'])
    i = 00
    for arr in res:
        for l in arr:
            df.loc[len(df)] = l
    df.index.name = 'idx'
    return df

