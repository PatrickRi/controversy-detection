import glob
import os
import pandas as pd
import networkx as nx
import csv

following = nx.DiGraph()
ignoring = nx.DiGraph()
follow_ignore = nx.DiGraph()

with open(os.path.join('..', 'Datasets', 'derstandard', 'CommunityConnection.csv'), encoding="utf8") as csvfile:
    reader = csv.reader(csvfile, delimiter=';')

    # skip header
    next(reader, None)

    for row in reader:
        ci = row[0]
        ci_to = row[1]
        conn_type = row[2]
        if conn_type == '1':
            following.add_edge(ci, ci_to)
        else:
            ignoring.add_edge(ci, ci_to)
        follow_ignore.add_edge(ci, ci_to, weight=1 if conn_type == '1' else -1)

graphs = {'following': following,
          'ignoring': ignoring,
          'follow_ignore': follow_ignore}
for k, v in graphs.items():
    print(k, 'contains',len(list(nx.selfloop_edges(v))), 'selfloop edges')
    v.remove_edges_from(nx.selfloop_edges(v))
    nx.write_gml(v, './derstandard/' + k + '.gml')

# check if necessary
#

#     # additionally generate a second dataset, containing only the connected component
for k, g in graphs.items():
    ccs = list(nx.weakly_connected_components(g))
    if len(ccs) > 1:
        lengths = [len(c) for c in sorted(ccs, key=len, reverse=True)]
        print('Creating second dataset for', k, 'containing only the largest CC')
        print('Number of edges',len(list(g.edges)))
        print('Largest CC has size', lengths[0], 'which is ' + str((lengths[0] / g.number_of_nodes()) * 100),
              '% of the dataset')
        print('Second largest CC has size', lengths[1], 'which is ' + str((lengths[1] / g.number_of_nodes()) * 100),
              '% of the dataset')
        largest_cc = max(ccs, key=len)
        S = g.subgraph(largest_cc).copy()
        nx.write_gml(S, './derstandard/' + k + '_cc.gml')
