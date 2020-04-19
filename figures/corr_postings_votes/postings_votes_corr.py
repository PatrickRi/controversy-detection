import pandas as pd
import os
pd.set_option('display.max_colwidth', -1)
pd.set_option('display.max_columns', None)
postings = pd.read_csv('postings_per_article.csv', comment='#', delimiter=';')
votes = pd.read_csv('votes_per_article.csv', comment='#', delimiter=';')
votes['votes'] = votes['cnt']
postings['postings'] = postings['cnt']
votes = votes[['ID_GodotObject', 'votes']]
postings = postings[['ID_GodotObject', 'postings']]
df = votes.set_index('ID_GodotObject').join(postings.set_index('ID_GodotObject'))
print(df.head(100))
for s in ['pearson', 'kendall', 'spearman']:
    print('Correlation for', s)
    print(df.corr(s))
    print(df.corr(s)['votes']['postings'])