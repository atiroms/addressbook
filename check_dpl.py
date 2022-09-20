###############################################################################
# Libraries
###############################################################################
import numpy as np, pandas as pd
import os, difflib, re, datetime


###############################################################################
# Parameters
###############################################################################
l_clin_delete = [' ']
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
# Prepare list A match dataframe
df_match_a = pd.read_csv(os.path.join(p_data, 'merge', 'src', 'listA_match.csv'))
df_match_a.loc[df_match_a['match'] != False, 'match'] = True


###############################################################################
# Check duplicate
###############################################################################
l_df_duplicate = []
for idx_b in sorted(list(set(df_match_a['idx_b'].to_list()))):
    df_tmp = df_match_a.loc[df_match_a['idx_b'] == idx_b, :]
    if len(df_tmp) > 1:
        l_df_duplicate.append(df_tmp)
df_duplicate = pd.concat(l_df_duplicate)

df_duplicate.to_csv(os.path.join(p_data, 'check_dpl', 'dst','listA_duplicate.csv'),index = False)


###############################################################################
# Load manually checked duplicate data
###############################################################################
# Prepare list A match dataframe
df_match_a_check1 = pd.read_csv(os.path.join(p_data, 'check_dpl', 'src', 'listA_match_check1.csv'))
df_match_a_check1 = df_match_a_check1.astype({'idx_a': int}, errors = 'raise') 

# Prepare list A match duplicate check dataframe
df_match_a_dpl = pd.read_csv(os.path.join(p_data, 'check_dpl', 'dst', 'listA_duplicate_check.csv'))
df_match_a_dpl = df_match_a_dpl[['idx_a', 'duplicate', 'match2', 'ocr_error']]

df_match_a_merge = pd.merge(df_match_a_check1, df_match_a_dpl, on = 'idx_a', how = 'left')


df_match_a_merge.to_csv(os.path.join(p_data, 'check_dpl', 'dst','list_match_check2.csv'),index = False)
