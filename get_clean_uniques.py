import pandas as pd
import sys

# file argument
fileN = sys.argv[1] # file to get uniques / clean

# load data
data = pd.read_csv(fileN, sep='\t', names=['id','desc'], header=None)

# new data frame with split value columns 
new = data['desc'].str.split("|", n = 1, expand = True) 
# making separate first column from new data frame 
data['term']= new[1]#.str.replace(r"(general)","").str.strip() # all in () r"\(.*\)"
# replace startswith with otros
#data['term'] = data['term'].apply(lambda x: x.replace('otros','') if x.strip().startswith('otros') else x)
# Dropping old columns 
data.drop(columns =["desc"], inplace = True) 

# get uniques terms
data = data.groupby(['id']).agg({
                                 'term':'first',
                                 }).reset_index()

# export tsv
data.to_csv(fileN[:-4]+'_uniques_clean.tsv', sep='\t', index=False, encoding='utf-8', header=None)

