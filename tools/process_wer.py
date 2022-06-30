"""
Process test_wer.txt

Zhenhao Ge, 2022-05-27
"""

import os
import csv

# os.chdir('/Users/zhge/PycharmProjects/speechbrain/tools')
dir_current = os.getcwd()
dir_result = os.path.abspath(os.path.join(dir_current, os.path.pardir, 'results'))

def dict2tuple(dct, key='ID'):

    # verify the 2nd-layer keys are the same
    # (i.e., the keys of dict of dict are the same)
    subkeys = [list(dct[k].keys()) for k in dct.keys()]
    result = all(element == subkeys[0] for element in subkeys)
    assert result, 'sub-keys are not the same for sub-dictionaries'

    keys = [key, *subkeys[0]]
    tuple_list = []
    for k in dct.keys():
        elements = [dct[k][kk] for kk in subkeys[0]]
        tuple_list.append((k, *elements))
    return tuple_list, keys

def tuple2csv(tuples, csvname='filename.csv', colname=[], verbose=True):
    with open(csvname, 'w', newline='') as f:
        csv_out = csv.writer(f)
        if len(colname) != 0:
            header = colname
            csv_out.writerow(header)
        for i, tpl in enumerate(tuples):
            csv_out.writerow(list(tpl))
    if verbose:
        print('{} saved!'.format(csvname))

file_wer = os.path.join(dir_result, 'wer_test_cv_with_ots_20220624.txt')
assert os.path.isfile(file_wer), 'file {} does not exist!'.format(file_wer)

# extract the lines with wers
lines = open(file_wer, 'r').readlines()
lines2 = []
for i, line in enumerate(lines):
    if line[:10] == '==========':
        lines2.append(lines[i+1].rstrip())
lines2 = lines2[1:]

# obtain the dictionary list
dct_list = []
for line in lines2:
    parts = line.split()
    filename = parts[0][:-1]
    wer = float(parts[2])
    num_errs = int(parts[4])
    num_words = int(parts[6][:-1])
    num_ins = int(parts[7])
    num_del = int(parts[9])
    num_sub = int(parts[11])
    dct = {'filename': filename, 'wer': wer, 'num_errs': num_errs, \
           'num_words': num_words, 'num_ins': num_ins, 'num_del': num_del, \
           'num_sub': num_sub}
    if 'common_voice' in filename:
        dct['dataset'] = 'cv'
    elif 'inLine' in filename or 'outLine' in filename:
        dct['dataset'] = 'frf_asr001'
    elif len(filename.split('_')) == 2:
        dct['dataset'] = 'frf_asr003'
    else:
        dct['dataset'] = 'frf_asr002'
    dct_list.append(dct)

# write individual wer file
header = ['dataset', 'filename', 'wer', 'num_errs', 'num_words', 'num_ins', 'num_del', 'num_sub']
file_wer_utt = file_wer.replace('.txt', '.csv')
with open(file_wer_utt, 'w', newline='') as f:
    csv_out = csv.writer(f)
    csv_out.writerow(header)
    for i, dct in enumerate(dct_list):
        tpl = [dct[k] for k in header]
        csv_out.writerow(tpl)

# write summary file
datasets = ['cv', 'frf_asr001', 'frf_asr002', 'frf_asr003']
summary = {dataset: {} for dataset in datasets}
for dataset in datasets:
    for k in header[3:]:
        summary[dataset][k]= sum([dct[k] for dct in dct_list if dct['dataset'].lower()==dataset])
    summary[dataset]['wer'] = summary[dataset]['num_errs'] / summary[dataset]['num_words']

file_summary = file_wer.replace('.txt', '_summary.csv')
tuple_list, keys = dict2tuple(summary, key='dataset')
tuple2csv(tuple_list, csvname=file_summary, colname=keys)