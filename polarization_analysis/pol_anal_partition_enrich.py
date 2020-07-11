import glob
import os

import networkx as nx

from measures.utils import get_partitions, __read_partition_file
name = '2000050349977'
# for file in glob.glob(os.path.join('.', 'cache', 'postings_top', '2000036209341')):
g = nx.read_gml(os.path.join('.', 'cache', 'postings_top', name, name+'_postings_top.gml'), label='id')

left_path = glob.glob(os.path.join('.', 'cache', 'postings_top', name, 'left', '*.txt'))[0]
right_path = glob.glob(os.path.join('.', 'cache', 'postings_top', name, 'right', '*.txt'))[0]
left_part = __read_partition_file(left_path)
right_part = __read_partition_file(right_path)
for i in left_part:
    g.nodes[i]['partition'] = 0
    comments = ''
    for x in g[i]:
        comments = comments + '---' + g[i][x]['comment']
    g.nodes[i]['comments'] = comments
for i in right_part:
    g.nodes[i]['partition'] = 1
    comments = ''
    for x in g[i]:
        comments = comments + '---' + g[i][x]['comment']
    g.nodes[i]['comments'] = comments
nx.write_gml(g, os.path.join('.', 'cache', 'postings_top', name, name + '_incl_partitions.gml'))
