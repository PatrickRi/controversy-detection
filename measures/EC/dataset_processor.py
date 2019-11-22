import os
from datetime import datetime
from typing import Dict, List

import matplotlib.pyplot as plt
import networkx as nx
import seaborn as sns

from .force_atlas import force_atlas_fa2
from .umap_ec import umap_ec


def read_positions_file(path: str) -> Dict[int, List[float]]:
    with open(path, 'r') as f:
        lines = f.readlines()
        dict_positions = {}
        for i in range(len(lines)):
            line1 = lines[i].strip()
            line1_split = line1.split("\t")
            node = int(line1_split[0])
            [x, y] = [float(line1_split[1].split(",")[0]), float(line1_split[1].split(",")[1])]
            dict_positions[node] = [x, y]
    return dict_positions


def create_file(g, target_path, embedding, partition, dataset, plot) -> Dict[int, List[float]]:
    print('start partitioning')
    start = datetime.now()
    if embedding == 'fa':
        positions = force_atlas_fa2(g, 100)
    else:
        positions = umap_ec(g, partition)
    if plot:
        embeddinga = []
        embeddingb = []
        for i in list(positions.values()):
            embeddinga.append(i[0])
            embeddingb.append(i[1])
        plt.scatter(embeddinga, embeddingb, c=[sns.color_palette()[x] for x in partition])
        plt.savefig(dataset + '_' + embedding + '.png')
    print('end partitioning', 'took:', (datetime.now() - start).seconds, 'seconds')
    with open(target_path, 'w') as f:
        for keys in positions.keys():
            f.write(str(keys) + "\t" + str(positions[keys][0]) + "," + str(positions[keys][1]) + "\n")
    return positions


def get_positions(g: nx.Graph, dataset: str, cache: bool, embedding: str, partition, plot: bool) -> Dict[
    int, List[float]]:
    target_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'positions',
                               dataset + '_positions_ ' + embedding + '.txt')
    if os.path.exists(target_path) and cache:
        return read_positions_file(target_path)
    else:
        return create_file(g, target_path, embedding, partition, dataset, plot)
