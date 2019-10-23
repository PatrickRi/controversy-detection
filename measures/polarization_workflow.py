import networkx as nx
from measures.utils import normalize_graph
from measures.modularity import Modularity

graph_from_file = nx.read_gml("../Datasets/karate.gml", label='id')
g, node_mapping = normalize_graph(graph_from_file)



Modularity(g, node_mapping, left_part, right_part, "karate.gml")