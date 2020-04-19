import glob
import os

import networkx as nx

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
    #nx.write_gml(G, './result/' + str(dataset) + '.gml')

    # additionally generate a second dataset, containing only the connected component
    print(dataset)
    print("nodes: ", G.number_of_nodes())
    print("edges: ", G.number_of_edges())
    ccs = list(nx.connected_components(G))
    if len(ccs) > 1:
        lengths = [len(c) for c in sorted(ccs, key=len, reverse=True)]
        print('Creating second dataset for', str(dataset), 'containing only the largest CC')
        print('Largest CC has size', lengths[0], 'which is ' + str((lengths[0] / G.number_of_nodes()) * 100),
              '% of the dataset')
        largest_cc = max(ccs, key=len)
        S = G.subgraph(largest_cc).copy()
        #nx.write_gml(S, './result/' + str(dataset) + '_cc.gml')
