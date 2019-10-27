import networkx as nx
import os
import glob


files = glob.glob('./original_datasets/polarizacao_datasets/*.arestas')
for file in files:
    txtfile = open(file)
    lines = txtfile.readlines()
    dict_left = {}
    G = nx.Graph()
    for line in lines:
        line = line.strip()
        elements = line.split(',')
        G.add_edge(elements[0], elements[1])
    dataset = os.path.basename(file).split('.')[0]
    nx.write_gml(G, './result/' + str(dataset) + '.gml')
