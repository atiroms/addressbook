###############################################################################
# Libraries
###############################################################################
import numpy as np, pandas as pd
import os, difflib, re, datetime


###############################################################################
# Parameters
###############################################################################
l_clin_delete = [' ']
#l_address_replace = [[' ', ''], ['ー', '-'], ['－', '-'], ['東京都', ''],  ['千葉県', ''], ['埼玉県', ''], ['神奈川県', ''],
l_address_replace = [[' ', ''], ['－', '-'], ['東京都', ''],  ['千葉県', ''], ['埼玉県', ''], ['神奈川県', ''],
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
# Prepare list A match dataframe
df_match_a = pd.read_csv(os.path.join(p_data, 'check_dpl', 'dst', 'listA_match_check3.csv'))
df_match_a = df_match_a[~np.isnan(df_match_a['idx_a'])]
# Idx of list A to be deleted
l_idx_a_delete = df_match_a.loc[df_match_a['delete'] == True, 'idx_a'].to_list()
# Dataframe of matched clinics
df_match_checked = df_match_a[(df_match_a['match'] != False) & (df_match_a['delete'] != True)]
# Idx of list A with match in list B
l_idx_a_match = df_match_a[(df_match_a['match'] != False) & (df_match_a['delete'] != True)]['idx_a'].tolist()
# Idx of list B with match in list B
l_idx_b_match = df_match_a[(df_match_a['match'] != False) & (df_match_a['delete'] != True)]['idx_b'].tolist()

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
#df_a = df_src_a.loc[l_idx_a_maybe_in_tokyo,:]

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
# Merge data
###############################################################################
# A and B
df_a_and_b = df_match_checked
df_a_and_b['source'] = 'A_and_B'
df_a_and_b = df_a_and_b[['source','idx_a','idx_b']]
df_tmp_a = df_src_a
df_tmp_a['idx_a'] = df_tmp_a.index
df_tmp_a = df_tmp_a[['idx_a', 'clin_full_a', 'pcode', 'address_a','name_dr','alumnus','ref_history','send']]
df_tmp_a.columns = ['idx_a', 'a_clinic', 'a_pcode', 'a_address', 'a_name_dr', 'a_alumnus', 'a_refhist', 'a_send']
df_tmp_b = df_src_b
df_tmp_b['idx_b'] = df_tmp_b.index
df_tmp_b = df_tmp_b[['idx_b', 'clin_full_b', 'pcode', 'address_b','tel']]
df_tmp_b.columns = ['idx_b', 'b_clinic', 'pcode', 'address_b','tel']
df_a_and_b = pd.merge(df_a_and_b, df_tmp_a, how = 'left', on = 'idx_a')
df_a_and_b = pd.merge(df_a_and_b, df_tmp_b, how = 'left', on = 'idx_b')

# A not B
l_idx_a_not_b = df_src_a.index.tolist()
l_idx_a_not_b = [idx_a for idx_a in l_idx_a_not_b if idx_a not in l_idx_a_match]
l_idx_a_not_b = [idx_a for idx_a in l_idx_a_not_b if idx_a not in l_idx_a_delete]
df_a_not_b = df_src_a
df_a_not_b['source'] = 'A_not_B'
df_a_not_b['idx_a'] = df_a_not_b.index
df_a_not_b = df_a_not_b.loc[df_a_not_b['idx_a'].isin(l_idx_a_not_b),['source','idx_a', 'clin_full_a', 'pcode', 'address_a','name_dr','alumnus','ref_history','send']]
df_a_not_b.columns = ['source','idx_a', 'a_clinic', 'a_pcode', 'a_address', 'a_name_dr', 'a_alumnus', 'a_refhist', 'a_send']

# B not A
l_idx_b_not_a = df_src_b.index.tolist()
l_idx_b_not_a = [idx_b for idx_b in l_idx_b_not_a if idx_b not in l_idx_b_match]
df_b_not_a = df_src_b
df_b_not_a['source'] = 'B_not_A'
df_b_not_a['idx_b'] = df_b_not_a.index
df_b_not_a = df_b_not_a.loc[df_b_not_a['idx_b'].isin(l_idx_b_not_a),['source','idx_b', 'clin_full_b', 'pcode', 'address_b','tel']]
df_b_not_a.columns = ['source','idx_b', 'b_clinic', 'pcode', 'address_b','tel']

# Concat
df_concat = pd.concat([df_a_and_b, df_a_not_b, df_b_not_a], axis = 0)
df_concat.index = [i for i in range(len(df_concat))]


###############################################################################
# Save data
###############################################################################
df_a_and_b.to_csv(os.path.join(p_data, 'merge', 'dst','result_A_and_B.csv'),index = False)
df_a_not_b.to_csv(os.path.join(p_data, 'merge', 'dst','result_A_not_B.csv'),index = False)
df_b_not_a.to_csv(os.path.join(p_data, 'merge', 'dst','result_B_not_A.csv'),index = False)
df_concat.to_csv(os.path.join(p_data, 'merge', 'dst','result_concat.csv'),index = False)
