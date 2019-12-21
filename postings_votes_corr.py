import pandas as pd
import os
pd.set_option('display.max_colwidth', -1)
pd.set_option('display.max_columns', None)
postings = pd.read_csv('C:\\Users\\Priemer\\Desktop\\postings_per_article.csv', comment='#', delimiter=';')
votes = pd.read_csv('C:\\Users\\Priemer\\Desktop\\votes_per_article.csv', comment='#', delimiter=';')
postings['votes'] = votes['cnt']
postings['postings'] = postings['cnt']
for s in ['pearson', 'kendall', 'spearman']:
    print('Correlation for', s)
    print(postings.corr(s))
    print(postings.corr(s)['votes']['postings'])