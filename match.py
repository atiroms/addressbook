
###############################################################################
# Libraries
###############################################################################
import numpy as np, pandas as pd
import os, difflib, re, datetime


###############################################################################
# Parameters
###############################################################################
l_clin_delete = [' ', 'メンタルクリニック', 'こころのクリニック','病院', 'クリニック', '医院', '診療所', '心療内科', '医療法人社団', '医療法人財団', '社団法人', '医療法人', '一般財団法人']
l_address_replace = [[' ', ''], ['ー', '-'], ['－', '-'], ['東京都', ''],  ['千葉県', ''], ['埼玉県', ''], ['神奈川県', ''],
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
# Load and clean data
###############################################################################
# Prepare list A dataframe
df_src_a = pd.read_csv(os.path.join(p_data, 'match', 'src', 'listA.csv'))
df_src_a.columns = ['id', 'send', 'name_corp', 'name_clinic', 'name_dr', 'pcode', 'address1', 'address2', 'alumnus', 'ref_history']

l_clin_a = []
l_clin_full_a = []
l_address_a = []
for idx_a, row_a in df_src_a.iterrows():
    name_clin_a = row_a['name_clinic']
    name_corp_a = row_a['name_corp']
    if type(name_corp_a) != float:
        name_clin_a = name_corp_a + name_clin_a
    l_clin_full_a.append(name_clin_a)
    name_clin_a = delete_clinic(name_clin_a, l_clin_delete)
    l_clin_a.append(name_clin_a)
    if type(row_a['address1']) != float:
        address_a = str(row_a['address1'])
        if type(row_a['address2']) != float:
            address_a += str(row_a['address2'])
        address_a = replace_address(address_a, l_address_replace)
    else:
        address_a = np.nan
    l_address_a.append(address_a)
df_src_a['clin_a'] = l_clin_a
df_src_a['clin_full_a'] = l_clin_full_a
df_src_a['address_a'] = l_address_a

l_idx_a_maybe_in_tokyo = []
for idx_a, row_a in df_src_a.iterrows():
    address1 = row_a['address1']
    if type(address1) == str:
        if address1.startswith('東京都'):
            l_idx_a_maybe_in_tokyo.append(idx_a)
    else:
        l_idx_a_maybe_in_tokyo.append(idx_a)
l_idx_a_not_in_tokyo = [idx for idx in df_src_a.index.tolist() if idx not in l_idx_a_maybe_in_tokyo]
df_a = df_src_a.loc[l_idx_a_maybe_in_tokyo,:]

# Prepare list B dataframe
df_src_b = pd.read_csv(os.path.join(p_data, 'match', 'src', 'listB.csv'))
df_src_b.columns = ['id', 'name_clinic', 'pcode', 'address', 'tel', 'misc']
df_src_b = df_src_b.loc[~np.isnan(df_src_b['id']), :]

l_clin_b = []
l_clin_full_b = []
l_address_b = []
for idx_b, row_b in df_src_b.iterrows():
    name_clin_b = row_b['name_clinic']
    l_clin_full_b.append(name_clin_b)
    name_clin_b = delete_clinic(name_clin_b, l_clin_delete)
    l_clin_b.append(name_clin_b)
    address_b = row_b['address']
    address_b = replace_address(address_b, l_address_replace)
    l_address_b.append(address_b)
df_src_b['clin_b'] = l_clin_b
df_src_b['clin_full_b'] = l_clin_full_b
df_src_b['address_b'] = l_address_b


###############################################################################
# Calculate similarity
###############################################################################
l_similarity_clin = []
for idx_a, row_a in df_a.iterrows():
    name_clin_a = row_a['clin_a']
    name_clin_full_a = row_a['clin_full_a']
    pcode_a = row_a['pcode']
    address_a = row_a['address_a']

    for idx_b, row_b in df_src_b.iterrows():
        name_clin_b = row_b['clin_b']
        name_clin_full_b = row_b['clin_full_b']
        pcode_b = row_b['pcode']
        address_b = row_b['address_b']
        similarity_clin =  difflib.SequenceMatcher(None, name_clin_a, name_clin_b).ratio()
        if type(pcode_a) == float or type(pcode_b) == float:
            similarity_pcode = np.nan
        else:
            similarity_pcode =  difflib.SequenceMatcher(None, pcode_a, pcode_b).ratio()
        if type(address_a) == float or type(address_b) == float:
            similarity_address = np.nan
        else:
            similarity_address =  difflib.SequenceMatcher(None, address_a, address_b).ratio()
        l_similarity_clin.append([idx_a, name_clin_full_a, pcode_a, address_a, idx_b, name_clin_full_b, pcode_b, address_b, similarity_clin, similarity_pcode, similarity_address])
df_similarity = pd.DataFrame(l_similarity_clin, columns = ['idx_a', 'name_clin_full_a', 'pcode_a', 'address_a', 'idx_b', 'name_clin_full_b', 'pcode_b', 'address_b', 'similarity_clin','similarity_pcode','similarity_address'])


###############################################################################
# Select Matching clinic
###############################################################################

df_similarity['similarity_clin_x_address'] = df_similarity['similarity_clin'] * df_similarity['similarity_address']

l_similarity_max_a = []
for idx_a in df_a.index:
    df_temp = df_similarity.loc[df_similarity['idx_a'] == idx_a, :]
    if np.isnan(df_temp['similarity_address'].idxmax()):
        df_temp = df_temp.loc[[df_temp['similarity_clin'].idxmax()], :]
    else:
        df_temp = df_temp.loc[[df_temp['similarity_clin_x_address'].idxmax()], :]
    l_similarity_max_a.append(df_temp)
df_similarity_max_a = pd.concat(l_similarity_max_a)

l_similarity_max_b = []
for idx_b in df_src_b.index:
    df_temp = df_similarity.loc[df_similarity['idx_b'] == idx_b, :]
    if np.isnan(df_temp['similarity_address'].idxmax()):
        df_temp = df_temp.loc[[df_temp['similarity_clin'].idxmax()], :]
    else:
        df_temp = df_temp.loc[[df_temp['similarity_clin_x_address'].idxmax()], :]
    l_similarity_max_b.append(df_temp)
df_similarity_max_b = pd.concat(l_similarity_max_b)


###############################################################################
# Save result
###############################################################################
df_similarity_max_a.to_csv(os.path.join(p_data, 'match', 'dst','listA_match.csv'),index = False)
df_similarity_max_b.to_csv(os.path.join(p_data, 'match', 'dst','listB_match.csv'),index = False)