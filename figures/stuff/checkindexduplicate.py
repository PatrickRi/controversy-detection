import os
from ast import literal_eval
import codecs

i_dict={}
with codecs.open("merged_results_gc_check_index_duplicate.csv", "r", encoding="utf8") as f:
    f.readline()
    for line in f:
        idx = int(line.split(",")[0])
        if idx in i_dict:
            print("ducplicate found: ", idx)
        i_dict[idx] = 1

