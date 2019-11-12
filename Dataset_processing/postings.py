import glob
import os
import pandas as pd
import networkx as nx
import csv

graph = nx.DiGraph()

# dictionary of postings and their authors
posting_dictionary = {} # Posting -> CommunityIdentity
# dictionary of parent postings
parent_dictionary = {} # Posting -> Parent

with open(os.path.join('..', 'Datasets', 'derstandard', 'Postings.csv'), encoding="utf8") as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    # skip header
    next(reader, None)

    for row in reader:
        posting_id = row[2]
        posting_dictionary[posting_id] = row[0]
        posting_parent_id = row[3]
        if posting_parent_id != 'NULL':
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

nx.write_gml(graph, './derstandard/' + 'postings.gml') # max 197 weight :D

# check if necessary
#
#     # additionally generate a second dataset, containing only the connected component
#     ccs = list(nx.connected_components(v))
#     if len(ccs) > 1:
#         lengths = [len(c) for c in sorted(ccs, key=len, reverse=True)]
#         print('Creating second dataset for', k, 'containing only the largest CC')
#         print('Largest CC has size', lengths[0], 'which is ' + str((lengths[0] / v.number_of_nodes()) * 100),
#               '% of the dataset')
#         largest_cc = max(ccs, key=len)
#         S = v.subgraph(largest_cc).copy()
#         nx.write_gml(S, './derstandard/' + k + '_cc.gml')
