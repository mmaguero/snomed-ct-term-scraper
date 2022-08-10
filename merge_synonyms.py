import pandas as pd
import sys

file_child = sys.argv[1] # file with childrens cleaned and uniques
file_syn = sys.argv[2] # file with synonyms

# read files
li =  []
df_child = pd.read_csv(file_child, sep='\t',encoding = 'utf8',lineterminator='\n', names=['id','term'] ,low_memory=False)
li.append(df_child)
df_syn = pd.read_csv(file_syn, sep='\t',encoding = 'utf8',lineterminator='\n', names=['id','term'] ,low_memory=False)
li.append(df_syn)

# concat frames
data = pd.concat(li, axis=0, ignore_index=True)

# clean
data['term']= data['term'].str.replace(r"\(general*\)","").str.strip()  #all in () r"\(.*\)"

# get uniques by id and term
data = data.drop_duplicates(subset=['id','term'])
data = data.sort_values(by=['id'])

# export tsv
data.to_csv(file_syn[:-4]+'_merged.tsv', sep='\t', index=False, encoding='utf-8', header=None)
