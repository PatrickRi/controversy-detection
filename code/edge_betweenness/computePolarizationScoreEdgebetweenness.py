# script to get the edges on a cut. Very informal implementation using n^2 computations. Can be done better, but this suits our case

# first run metis to get the 2 communities

import sys
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import random
import math
from sklearn.neighbors import KernelDensity

#filename = sys.argv[1]
filename = './edge_betweenness/political_blogs.txt' #TODO remove
#filename = './edge_betweenness/karate_club.txt' #TODO remove
#file2 = sys.argv[2]
file2 = 'political_blogs' #TODO remove
#file2 = 'karate_club' #TODO remove

G = nx.read_weighted_edgelist(filename, delimiter=",")

f3 = open("edge_betweenness/" + file2 + ".txt")
# f3 = open("edge_betweenness_follower_network/" + file2 + ".txt") 
lines3 = f3.readlines()
dict_edgebetweenness = {}

for line in lines3:
    line = line.strip()
    line_split = line.split(",")
    dict_edgebetweenness[line_split[0] + "," + line_split[1]] = float(line_split[2])

f1 = open("../../polblogs_left.txt")
#f1 = open("../../karate_left.txt")
# f1 = open("../communities_follow_networks/community1_" + file2 + ".txt") 
lines1 = f1.readlines()

f2 = open("../../polblogs_right.txt")
#f2 = open("../../karate_right.txt")
# f2 = open("../communities_follow_networks/community2_" + file2 + ".txt") 
lines2 = f2.readlines()

cut_edges = {}
eb_list = []

for i in range(len(lines1)):
    name1 = lines1[i].strip()
    for j in range(len(lines2)):
        name2 = lines2[j].strip()
        if (G.has_edge(name1, name2)):
            if (name1 + "," + name2) in dict_edgebetweenness:
                edge_betweenness = dict_edgebetweenness[name1 + "," + name2]
                eb_list.append(edge_betweenness)
            else:
                edge_betweenness = dict_edgebetweenness[name2 + "," + name1]
                eb_list.append(edge_betweenness)

print("********************" + file2 + "*********************")
print("length of cut", len(eb_list))
print("length of cut/num edges", len(eb_list)*1.0/len(G.edges()))
eb_list1 = np.asarray(eb_list)
eb_list2 = []
variance = np.var(eb_list1)
mean = np.mean(eb_list1)
# print variance, mean 
print("SPID", variance/mean)

f = open("edge_betweenness/" + file2 + ".txt")
# f = open("edge_betweenness_follower_network/"+file2+".txt") 
lines = f.readlines()

eb_list_all = []

for line in lines:
    line = line.strip()
    line_split = line.split(",")
    eb_list_all.append(float(line_split[2]))

eb_list_all1 = np.asarray(eb_list_all)
#"""
num_bins = 20
# the histogram of the data
plt.hist(eb_list_all, num_bins, color='green', alpha=0.5, label='All edges')
plt.hist(eb_list, num_bins, color='red', alpha=0.5, label='Edges on the cut')
plt.savefig(file2 + '_eb.png')
#"""
#np.savetxt('list_all.txt', np.array(eb_list_all), fmt='%f')
#np.savetxt('list.txt', np.array(eb_list), fmt='%f')

entropies = []
#for i in range(0, 10000):
#    comparison = random.sample(eb_list_all, len(eb_list))
#    entropies.append(stats.entropy(eb_list, comparison))
#entropy = sum(entropies) / len(entropies)
#print("Entropy: " + str(entropy))
#print("BCC therefore: " + str(1 - math.exp(-1.0*entropy)))

#kde_sample = KernelDensity().fit(np.array(eb_list).reshape(-1, 1))
#listsamples = kde_sample.sample(10000, 43)
#kde_allsamples = KernelDensity().fit(np.array(eb_list_all).reshape(-1, 1))
#listallsamples = kde_allsamples.sample(10000, 43)
#entropy = stats.entropy(listsamples, listallsamples)
#print("KDE Entropy: " + str(entropy))
#print("BCC therefore: " + str(1 - math.exp(-1.0*entropy)))
#"""
num_bins = 20
# the histogram of the data
#plt.hist(listsamples, num_bins, color='red', alpha=0.5, label='Edges on the cut')
#plt.savefig(file2 + '_kde.png')
#plt.hist(listallsamples, num_bins, color='green', alpha=0.5, label='All edges')
#plt.savefig(file2 + '_kde_all.png')
#"""

#print(stats.entropy(eb_list, eb_list_all)) #TODO must be same size but how?
print("Ratio of edge betweenness", np.median(eb_list1) / np.median(eb_list_all1))
for eb in eb_list:
    eb_list2.append(eb / np.max(eb_list1))

eb_list3 = np.asarray(eb_list2)
print("Mean edge betweenness on the cut", np.mean(eb_list3), "Median", np.median(eb_list3), "\n")
