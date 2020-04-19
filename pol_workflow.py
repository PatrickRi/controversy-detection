import pandas as pd
import os
import networkx as nx
import pyodbc
import numpy as np
from string import Template
import pymetis
from partitioning.create_partitions import metis_to_nodelist, to_adjacency_list, write_nodelist_file
from measures.BCC import BCC
from measures.CC import ClusteringCoefficient
from measures.EC import EmbeddingControversy
from measures.GMCK import BoundaryConnectivity
from measures.MBLB import MBLB
from measures.measure import Measure
from measures.modularity import Modularity
from measures.PI import PolarizationIndex
from measures.RWC import RWC
from measures.utils import get_config, get_logger, get_partitions, normalize_graph

# msg found 0 files is from create_partitions main method
logger = get_logger('main')
docid = '2000022399507'# '2000073253280'
target_path = os.path.join('.', 'cache', docid)
if not os.path.exists(target_path):
    os.makedirs(target_path)
### fetch data

query = Template("""SELECT p.ID_Posting, ID_Posting_Parent, p.ID_CommunityIdentity
from Content c
    INNER JOIN Postings p ON p.ID_GodotObject=c.ID_GodotObject
where c.ID_GodotObject='$docid'""")
query = query.substitute(docid=docid)

sql_conn = pyodbc.connect(
    'DRIVER={SQL Server Native Client 11.0};SERVER=si;DATABASE=Standard-Export-06062019;Trusted_Connection=yes')
df = pd.read_sql(query, sql_conn, index_col='ID_Posting', coerce_float=False)
logger.info('Fetched ' + str(len(df)) + ' rows')
df.to_csv(os.path.join(target_path, 'sql_result.csv'))
### parse data into network_cc

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
ccs = list(nx.weakly_connected_components(graph))
if len(ccs) > 1:
    lengths = [len(c) for c in sorted(ccs, key=len, reverse=True)]
    logger.info('Largest CC has size ' + str(lengths[0]) + ' which is ' + str(
        (lengths[0] / graph.number_of_nodes()) * 100) + '% of the dataset')
    largest_cc = max(ccs, key=len)
    graph = graph.subgraph(largest_cc).copy()
nx.write_gml(graph, os.path.join(target_path, docid + '.gml'))
### partition
g = nx.Graph(graph)
g = nx.convert_node_labels_to_integers(g)
(edgecuts, parts) = pymetis.part_graph(2, adjacency=to_adjacency_list(g))
left, right = metis_to_nodelist(parts)
write_nodelist_file(os.path.join(target_path, 'left'), docid, left)
write_nodelist_file(os.path.join(target_path, 'right'), docid, right)

# run metrics on it
if not g.has_node(0):
    g, node_mapping = normalize_graph(g)
else:
    g: nx.Graph = g
    node_mapping = {}
    for n in range(g.number_of_nodes()):
        node_mapping[n] = n
logger.info('finished normalizing')
left_part = [int(x) for x in left]
right_part = [int(x) for x in right]
if g.number_of_nodes() < 100:
    percent = 0.1
elif g.number_of_nodes() < 1000:
    percent = 0.03
elif g.number_of_nodes() < 10000:
    percent = 0.01
else:
    percent = 0.001

measures_list = [
    BCC(g, node_mapping, left_part, right_part, docid, os.path.join(target_path, docid + '.gml'), cache=False),
    BoundaryConnectivity(g, node_mapping, left_part, right_part, docid),
    ClusteringCoefficient(g, node_mapping, left_part, right_part, docid),
    EmbeddingControversy(g, node_mapping, left_part, right_part, docid),
    MBLB(g, node_mapping, left_part, right_part, docid, percent=percent),
    Modularity(g, node_mapping, left_part, right_part, docid, os.path.join(target_path, docid + '.gml')),
    PolarizationIndex(g, node_mapping, left_part, right_part, docid, cache=False),
    RWC(g, node_mapping, left_part, right_part, docid, percent=percent)
]
arr = []
for m in measures_list:
    logger.info('Start calculating %s', m.__class__.__name__)
    result = m.__class__.__name__, m.calculate()
    print(result)
    arr.append(result)
print(arr)
print(np.mean(np.array([x[1] for x in arr])))
print(np.std(np.array([x[1] for x in arr])))
