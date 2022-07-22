# This script is used to replace the double-char encoding of accented letter
# with single-char encoding version
#
# This is a follow-up, after finding the mappings using `tools/convert_accent_letter.py`
#
# Mapping rules learned from `tools/convert_accent_letter.py`
#  - for letters[59] (`)
#     + (letters[1] + letters[59], letters[27]) # accented A
#     + (letters[5] + letters[59], letters[35]) # accented E
#     + (letters[21] + letters[59], letters[51]) # accented U
#  - for letters[60] ('́)
#     + (letters[15] + letters[60], letters[46]) # accented O
#     + (letters[5] + letters[60], letters[36]) # accented E
#  - for letters[61] (^)
#     + (letters[1] + letters[61], letters[29]) # accented A
#     + (letters[5] + letters[61], letters[37]) # accented E
#     + (letters[9] + letters[61], letters[41]) # accented I
#     + (letters[15] + letters[61], letters[47]) # accented O
#     + (letters[21] + letters[61], letters[53]) # accented U
#  - for letters[62] (̧')
#     + (letters[3] + letters[62], letters[82]) # accented C
#
# Zhenhao Ge, 2022-02-18

import os
import csv
import shutil
import numpy as np

def get_text(csv_path):
    lines = open(csv_path, 'r').readlines()
    lines = lines[1:]
    texts = [line.split(',')[-1].rstrip() for line in lines]
    return texts

def get_char_dict(characters):
    char_dict = {}
    for c in characters:
        if c not in char_dict.keys():
            char_dict[c] = 1
        else:
            char_dict[c] += 1
    return char_dict

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

# os.chdir('recipes/CommonVoice/')

# data_dir = 'exp/CommonVoice/cv-corpus-6.1-2020-12-11/'
data_dir = 'exp/CommonVoice/cv-corpus-8.0-2022-01-19/'
# data_dir = '../../templates/speech_recognition/filelists/ots_french/frf_asr001/'
assert os.path.isdir(data_dir), '{} does not exist!'.format(data_dir)

# get all texts
texts_all = []
csv_files = ['train.csv', 'dev.csv', 'test.csv']
for csv_file in csv_files:
    csv_path = os.path.join(data_dir, csv_file)
    texts = get_text(csv_path)
    texts_all += texts

# check current alphabet
single_line = ' '.join(texts_all)
words = single_line.split()
characters = single_line.replace(' ', '')
ncharacters = len(characters)
char_dict = get_char_dict(characters)

# find the indices of accent letters (59,60,61,62)
letters = sorted(set(characters))
print('\n'.join(['{}, {}'.format(i, letter) for (i,letter) in enumerate(letters)]))


# setup the replacement tuples
replacement_tuples = []
replacement_tuples.append((letters[0] + letters[58], letters[26]))
replacement_tuples.append((letters[4] + letters[58], letters[34]))
replacement_tuples.append((letters[20] + letters[58], letters[50]))
replacement_tuples.append((letters[14] + letters[59], letters[45]))
replacement_tuples.append((letters[4] + letters[59], letters[35]))
replacement_tuples.append((letters[0] + letters[60], letters[28]))
replacement_tuples.append((letters[4] + letters[60], letters[36]))
replacement_tuples.append((letters[8] + letters[60], letters[40]))
replacement_tuples.append((letters[14] + letters[60], letters[46]))
replacement_tuples.append((letters[20] + letters[60], letters[52]))
# replacement_tuples.append((letters[3] + letters[62], letters[77]))
replacement_tuples.append((letters[2] + letters[61], letters[81]))

replacement_valid_tuples = []
for tpl in replacement_tuples:
    double, single = tpl
    words_double = sorted(set([word for word in words if double in word]))
    words_single = [word.replace(double, single) for word in words_double]
    words_exist = np.mean([1 if word in words else 0 for word in words_single])
    replacement_valid_tuples.append((double, single, words_exist))

for csv_file in csv_files:

    # get header and entries from the csv file
    csv_path = os.path.join(data_dir, csv_file)
    lines = open(csv_path, 'r').readlines()
    header = lines[0].rstrip().split(',')
    lines = lines[1:]
    entries = [line.rstrip().split(',') for line in lines]

    # process the entries with accented letters replacement
    print('processing {} with {} entries ...'.format(csv_path, len(entries)))
    for tpl in replacement_tuples:
        for entry in entries:
            double, single = tpl
            entry[-1] = entry[-1].replace(double, single)

    # backup the original csv file and write the new file with the same filename
    csv_path_old = csv_path.replace('.csv', '_old.csv')
    shutil.move(csv_path, csv_path_old)
    tuple2csv(entries, csv_path, colname=header)

# sanity check after processing (to make sure no double-char encoded accented letters)
# just rerun the beginning part of this script below

# get all texts
texts_all = []
csv_files = ['train.csv', 'dev.csv', 'test.csv']
for csv_file in csv_files:
    csv_path = os.path.join(data_dir, csv_file)
    texts = get_text(csv_path)
    texts_all += texts

# check current alphabet
single_line = ' '.join(texts_all)
words = single_line.split()
characters = single_line.replace(' ', '')
ncharacters = len(characters)
char_dict = get_char_dict(characters)
print('#letters in {} in dir {}: {}'.format(csv_files, data_dir, len(char_dict)))

# find the indices of accent letters (now there is no accent letters)
letters = sorted(set(characters))
print('\n'.join(['{}, {}'.format(i, letter) for (i,letter) in enumerate(letters)]))