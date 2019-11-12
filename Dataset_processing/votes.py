import glob
import os
import pandas as pd
import networkx as nx
import csv

g_weighted_pos = nx.DiGraph()
g_weighted_neg = nx.DiGraph()
g_weighted = nx.DiGraph()

# dictionary of postings and their authors
posting_dictionary = {} # Posting -> CommunityIdentity
# dictionary of parent postings
parent_dictionary = {} # Posting -> Parent

with open(os.path.join('..', 'Datasets', 'derstandard', 'postings_votes_join.csv'), encoding="utf8") as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    # skip header
    next(reader, None)

    for row in reader:
        posting_id = row[0]
        posting_author = row[3]
        voter_ci = row[4]
        pos_vote = int(row[5])
        neg_vote = int(row[6])
        if pos_vote > 0:
            if g_weighted_pos.has_edge(voter_ci, posting_author):
                g_weighted_pos[voter_ci][posting_author]['weight'] = g_weighted_pos[voter_ci][posting_author]['weight'] + 1
            else:
                g_weighted_pos.add_edge(voter_ci, posting_author, weight=1)
        if neg_vote > 0:
            if g_weighted_neg.has_edge(voter_ci, posting_author):
                g_weighted_neg[voter_ci][posting_author]['weight'] = g_weighted_neg[voter_ci][posting_author]['weight'] + 1
            else:
                g_weighted_neg.add_edge(voter_ci, posting_author, weight=1)
        change = pos_vote - neg_vote
        if g_weighted.has_edge(voter_ci, posting_author):
            g_weighted[voter_ci][posting_author]['weight'] = g_weighted[voter_ci][posting_author]['weight'] + change
        else:
            g_weighted.add_edge(voter_ci, posting_author, weight=change)

graphs = {'positive_votes': g_weighted_pos,
          'negative_votes': g_weighted_neg,
          'votes': g_weighted}
for k, v in graphs.items():
    nx.write_gml(v, './derstandard/' + k + '.gml')

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
