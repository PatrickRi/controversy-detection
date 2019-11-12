import os
import random

import networkx as nx
import numpy as np
from tqdm import tqdm


def construct_H(g: nx.Graph, number_nodes: int, logger) -> nx.Graph:
    logger.info('Constructing H')
    X = nx.Graph()
    nodes_offset = number_nodes
    logger.info('Adding nodes to H')
    for n in g:
        X.add_node(n + nodes_offset)
    H = nx.compose(g, X)
    H = nx.DiGraph(H)
    logger.info('Adding edges to H')
    for n in g:
        H.add_edge(n, n + nodes_offset)
    return H


def perform_random_walk(starting_node: int, adj) -> int:
    while True:
        neighbors = list(adj[starting_node])
        if len(neighbors) == 0:
            return starting_node
        random_num = random.randint(0, len(neighbors) - 1)
        starting_node = neighbors[random_num]


def random_walk_Q(H: nx.Graph, g: nx.Graph, iterations: int, logger) -> np.ndarray:
    logger.info('Performing random walks')
    hnn = H.number_of_nodes()
    Q = np.zeros((hnn, hnn))
    adj_map = H.adj  # faster for degree
    for i in tqdm(range(iterations)):
        Q_curr = np.zeros((hnn, hnn))
        for n in g:
            node_itrs = len(adj_map[n]) * 2
            for itr in range(node_itrs):
                end = perform_random_walk(n, adj_map)
                Q_curr[n, end] = Q_curr[n, end] + 1 / node_itrs
        Q = Q + Q_curr / iterations
    return Q


def get_probability_matrix(g: nx.Graph, dataset: str, iterations: int, number_nodes: int, logger,
                           cache: bool) -> np.ndarray:
    target_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'matrices',
                               dataset + '_' + str(iterations) + '.npy')
    if os.path.exists(target_path) and cache:
        return np.load(target_path)
    else:
        H = construct_H(g, number_nodes, logger)
        Q = random_walk_Q(H, g, iterations, logger)
        np.save(target_path, Q)
        return Q
