import os
import yaml
from measures.utils import get_config
import networkx as nx
from os import walk
import glob
from measures.partition import get_partitioner, Partition



config = get_config(os.path.join(os.getcwd(), 'config.yaml'))

files = glob.glob('../Datasets/*.gml')
for file in files:
    try:
        g = nx.read_gml(file, label='id')
        left, right = get_partitioner('metis').partition(g, None)
        with open(os.path.join('../Partitions', 'metis', 'left', os.path.basename(file).split('.')[0]+'.txt'), 'w') as f:
            for item in left:
                f.write("%s\n" % item)

    except:
        print("wtf")



config['partition']

config['dataset-path']
