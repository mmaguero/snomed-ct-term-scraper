import requests
import json
import sys
import pandas as pd
from time import sleep
import ssl 

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# console args
fileN = sys.argv[1] # file name without extension if "child" else file+extension
write_mode = sys.argv[2] # a (append) or w (truncate)
operation = sys.argv[3] # child=children or syn=synomym
parent_id = sys.argv[4] # if operation=child the snomed-id, ocupations: 14679004 | ETHNIC: 372148003 else -1
# E.G.: python get_snomedct.py ethnic w child 372148003

# functions
# construct url
def set_url(base_url_extended, target_a, parent_id, target_b=str()):
    return base_url_extended+target_a+parent_id+target_b
    
# make request
def get_data(url, params, headers):
    sleep(5) # https://stackoverflow.com/questions/23013220/max-retries-exceeded-with-url-in-requests
    response = requests.get(url, params=params, headers=headers, verify = False) # verified=False but https://stackoverflow.com/questions/51925384/unable-to-get-local-issuer-certificate-when-using-requests-in-python/57466119#57466119
    #json_response = response.json()
    #print(f'Text matches: {json_response}')
    binary = response.content
    data = json.loads(binary)
    return data     

# get childrens    
def recursiveData(input_, file_):
    for d in input_:
        try:
            '''if d['conceptId'] in downloaded_.iloc[-1].id:
               print('already exists...', str(d['conceptId']))
               continue'''
            print (d['conceptId'], '\t', d['fsn']['term'], '|', d['pt']['term'])
            file_.write(d['conceptId'] + '\t' + d['fsn']['term'] + '|' + d['pt']['term'] + '\n')
            url = set_url(base_url+edition+version, target_a, str(d['conceptId']), target_b)
            newInput = get_data(url, params, headers) # child
            if newInput and len(newInput)>0:
                input_ += newInput
        except Exception as e:
            print(e)
    return recursiveData(input_, file_)
    
# get synonyms
def get_synonyms(fr_, fw_):
    for line in fr_:
        line = line.split('\t')
        concept_id = line[0].strip()
        term = line[1].strip()
        url = set_url(base_url+edition+version, target_a, str(concept_id))
        data = get_data(url, str(), headers) # parent
        for d in data['descriptions']:
            if (d['lang'] == 'en' and d['type'] == 'SYNONYM' and d['term'] != term):
                print (d['conceptId'] + '\t' + d['term'] + '\n')
                fw_.write(d['conceptId'] + '\t' + d['term'] + '\n')

# base URL extended
base_url = 'https://browser.ihtsdotools.org/snowstorm/snomed-ct/browser/'
edition = 'MAIN/' #SNOMEDCT-ES
version = '2022-07-31/' #'2019-10-31/'
# specific URL
target_a = 'concepts/'
parent_id = str(parent_id)
target_b = '/children'
# URL
url = set_url(base_url+edition+version, target_a, parent_id, target_b)
# params
params = {'form': 'inferred'}
# headers
headers = {
    'Host': 'browser.ihtsdotools.org',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'es,en',
    'Accept-Encoding': 'gzip, deflate, br',
    'X-Requested-With': 'XMLHttpRequest',
    'Connection': 'keep-alive',
    'Referer': 'https://browser.ihtsdotools.org/?perspective=full&conceptId1=372148003&edition=MAIN/2022-07-31&release=&languages=es,en',
    #'Cookie': '_ga=GA1.2.2125387514.1587470275; _gid=GA1.2.1370184987.1587992362; licenseCookie=true; _gat=1',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    }

# "main"
try:
    if operation == 'child':
        # for check if exist ID
        '''if write_mode == 'a':
            downloaded = pd.read_csv(fileN,sep='\t',names=["id","term"])
        else:
            downloaded = pd.DataFrame(columns=["id","term"])'''
        f = open(fileN+'_'+operation+'.tsv', write_mode)
        data = get_data(url, params, headers) # parent
        returnData = recursiveData(data, f)
        f.close() 
    elif operation == 'syn': 
        fr = open(fileN, 'r') # without duplicates (use before get_clean_uniques.py)
        fw = open(fileN[:-4]+'_'+operation+'.tsv', write_mode)
        returnData = get_synonyms(fr,fw)
        fw.close() 
        fr.close() 
    
except Exception as e:
    print(e)  
'''finally:
    f.close() '''
        
