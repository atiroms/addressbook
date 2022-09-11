
###############################################################################
# Libraries
###############################################################################
import numpy as np, pandas as pd
import os, difflib, re, datetime


###############################################################################
# Parameters
###############################################################################
l_clin_delete = ['メンタルクリニック', 'こころのクリニック','病院' 'クリニック', '医院', '診療所', '医療法人社団', '医療法人財団']
l_address_replace = [[' ', ''], ['ー', '-'],  ['東京都', ''],  ['千葉県', ''], ['埼玉県', ''], ['神奈川県', ''],
                     ['０', '0'], ['１', '1'], ['２', '2'], ['３', '3'], ['４', '4'], ['５', '5'], ['６', '6'], ['７', '7'], ['８', '8'], ['９', '9']]

###############################################################################
# Script path
###############################################################################
p_root = None
for p_test in ['/home/atiroms/Documents','D:/atiro','D:/NICT_WS','/Users/smrt']:
    if os.path.isdir(p_test):
        p_root = p_test

if p_root is None:
    print('No root directory.')
else:
    p_script = os.path.join(p_root,'GitHub/addressbook')
    os.chdir(p_script)
    p_data = os.path.join(p_root, 'Dropbox/addressbook')

from helper import *


###############################################################################
# Functions
###############################################################################
def replace_address(str_src, l_address_replace):
    for address_replace in l_address_replace:
        str_src = str_src.replace(address_replace[0], address_replace[1])
    return str_src


###############################################################################
# Load and clean data
###############################################################################
df_src_a = pd.read_csv(os.path.join(p_data, 'src', 'listA.csv'))
df_src_a.columns = ['id', 'send', 'name_corp', 'name_clinic', 'name_dr', 'pcode', 'address1', 'address2', 'alumnus', 'ref_history']


df_src_b = pd.read_csv(os.path.join(p_data, 'src', 'listB.csv'))
df_src_b.columns = ['id', 'name_clinic', 'pcode', 'address', 'tel', 'misc']

df_src_b = df_src_b.loc[~np.isnan(df_src_b['id']), :]

#ll_idx_space = []
for idx, row in df_src_b.iterrows():
    name_clin_src = row['name_clinic']
    name_clin_dst = name_clin_src.replace(' ', '')
    df_src_b.loc[idx, 'name_clinic'] = name_clin_dst
    #l_idx_space = [m.start() for m in re.finditer(' ', name_clin_src)]
    #ll_idx_space.append(l_idx_space)

l_similarity_clin = []
for idx_a, row_a in df_src_a.iterrows():
    name_clin_a = row_a['name_clinic']
    name_corp_a = row_a['name_corp']
    if type(name_corp_a) != float:
        name_clin_a = name_corp_a + name_clin_a
    pcode_a = row_a['pcode']

    if type(row_a['address1']) != float:
        address_a = str(row_a['address1'])
        if type(row_a['address2']) != float:
            address_a += str(row_a['address2'])
        address_a = replace_address(address_a, l_address_replace)
    else:
        address_a = np.nan

    for idx_b, row_b in df_src_b.iterrows():
        name_clin_b = row_b['name_clinic']
        pcode_b = row_b['pcode']
        address_b = row_b['address']
        address_b = replace_address(address_b, l_address_replace)
        similarity_clin =  difflib.SequenceMatcher(None, name_clin_a, name_clin_b).ratio()
        if type(pcode_a) == float or type(pcode_b) == float:
            similarity_pcode = np.nan
        else:
            similarity_pcode =  difflib.SequenceMatcher(None, pcode_a, pcode_b).ratio()
        if type(address_a) == float or type(address_b) == float:
            similarity_address = np.nan
        else:
            similarity_address =  difflib.SequenceMatcher(None, address_a, address_b).ratio()
        l_similarity_clin.append([idx_a, name_clin_a, pcode_a, address_a, idx_b, name_clin_b, pcode_b, address_b, similarity_clin, similarity_pcode, similarity_address])
df_similarity = pd.DataFrame(l_similarity_clin, columns = ['idx_a', 'name_clin_a', 'pcode_a', 'address_a', 'idx_b', 'name_clin_b', 'pcode_b', 'address_b', 'similarity_clin','similarity_pcode','similarity_address'])

l_similarity_max_clin_a = []
for idx_a in df_src_a.index:
    df_temp = df_similarity.loc[df_similarity['idx_a'] == idx_a, :]
    df_temp = df_temp.loc[[df_temp['similarity'].idxmax()], :]
    l_similarity_max_clin_a.append(df_temp)
df_similarity_max_clin_a = pd.concat(l_similarity_max_clin_a)