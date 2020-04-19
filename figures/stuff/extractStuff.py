import os
from ast import literal_eval
import codecs

with codecs.open("asdf2.txt", "r", encoding="utf8") as f:
    for line in f:
        if "RESULT" in line:
            arr = literal_eval(line.split("RESULT:")[1])
            for e in arr:
                print("1,1,"+str(e[0])+","+str(e[1])+","+str(e[2])+","+str(e[3]))
