"""
Replace the ground-truth reference in the filelist

e.g. replace the processed reference with the original reference

Zhenhao Ge, 2022-05-19
"""

import os
import csv

# os.chdir('/Users/zhge/PycharmProjects/speechbrain/tools')

def get_file2ref(filelist_lookup):
    lines = open(filelist_lookup, 'r').readlines()
    lines = lines[1:] # remove the head
    dct = {}
    for line in lines:
        parts = line.split(',')
        filename = os.path.basename(parts[2])
        reference = parts[4].rstrip()
        dct[filename] = reference
    return dct

dataset = 'cv-corpus-8.0-2022-01-19'

# setup directories
dir_current = os.getcwd()
dir_output = os.path.abspath(os.path.join(dir_current, os.path.pardir,
        'templates', 'speech_recognition', 'data-test'))

# setup input files
filelist_input = os.path.join(dir_output, 'test.csv')
assert os.path.isfile(filelist_input), 'filelist {} does not exist!'.format(filelist_input)
filelist_lookup = os.path.abspath(os.path.join(dir_current, os.path.pardir,
        'recipes', 'CommonVoice', 'exp', 'CommonVoice', 'cv-corpus-8.0-2022-01-19',
        'old', 'test0.csv'))

# setup output files
filelist_output = filelist_input.replace('test.csv', 'test_cv8.0_orig.csv')
assert os.path.isfile(filelist_lookup), 'filelist {} does not exist!'.format(filelist_lookup)
file_compare = os.path.join(dir_output, 'cv8.0_ref_original_vs_processed.csv')

# get dict to map filename to the original reference
f2r = get_file2ref(filelist_lookup)

# get lines from filelist
lines = open(filelist_input, 'r').readlines()
header = lines[0].rstrip().split(',')
lines = lines[1:]  # remove the header
nlines = len(lines)
print('#files in {}: {}'.format(filelist_input, nlines))

lines2 = []
ref_pairs = []
tuple_list = []
for i, line in enumerate(lines):
    parts = line.split(',')
    uttid, duration, relative_path, spk_id = parts[:-1]
    ref_proc = parts[4].rstrip()
    if dataset in line: # lines in the select dataset (need to use the original reference)
        filename = os.path.basename(parts[2])
        ref_orig = f2r[filename]
        tuple_list.append((uttid, duration, relative_path, spk_id, ref_orig))
        if ref_orig != ref_proc:
            ref_pairs.append((uttid, duration, relative_path, ref_orig, ref_proc))
    else: # lines in other datasets (use the processed reference, no replacement needed)
        tuple_list.append((uttid, duration, relative_path, spk_id, ref_proc))

# write out the filelist with cv trans replaced by the original
with open(filelist_output, 'w', newline='') as f:
    csv_out = csv.writer(f)
    csv_out.writerow(header)
    for i, tpl in enumerate(tuple_list):
        csv_out.writerow(list(tpl))
    print('wrote file: {}'.format(filelist_output))

# write out the file for original/processed transcriptions comparison
header = ['ID', 'duration', 'wav', 'wrd-original', 'wrd-processed']
with open(file_compare, 'w', newline='') as f:
    csv_out = csv.writer(f)
    csv_out.writerow(header)
    for i,tpl in enumerate(ref_pairs):
        csv_out.writerow(list(tpl))
    print('wrote file: {}'.format(file_compare))



