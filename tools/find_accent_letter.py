# These script is used to find out the mapping from
#  a) the regular letter appended accent symbol, to
#  b) the accented letter, e.g., 'E' (letter 4) + '`' -> 'È'
# in the CommonVoice dataset (e.g., cv-corpus-6.1-2020-12-11).
#
# The accented letters focusing on in this script (index [58, 62)):
# [["b'\\xcc\\x80'", '̀'],
#  ["b'\\xcc\\x81'", '́'],
#  ["b'\\xcc\\x82'", '̂'],
#  ["b'\\xcc\\xa7'", '̧']]
#
# Once find all the mappings, these combined letters will be
# replaced by their corresponding single letter
#
# Mapping rules learned
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
#     + (letters[3] + letters[62], letters[77]) # accented C
#
# Pre-requisites:
#  - run `extract_text.py` to generate `{train,dev,test}.txt`
#  - run `count_word.py` to generate `chars.csv` for `all.txt` of cv-corpus-6.1-2020-12-11
#  - run `subset_by_letter.py` to generate `all_*.csv` for all letters
#
# Zhenhao Ge, 2022-02-16

import os, sys
import glob
sys.path.append(os.getcwd())
from utils import tuple2csv

# dataset = 'cv-corpus-6.1-2020-12-11'
dataset = 'cv-corpus-8.0-2022-01-19'
filetype = 'csv'
letter_file = '../templates/speech_recognition/LM/data/{}/chars.{}'.format(dataset, filetype)
assert os.path.isfile(letter_file), '{} does not exist!'.format(letter_file)
print('letter file: {}'.format(letter_file))
filelist_dir = '../templates/speech_recognition/filelists/CommonVoice/{}'.format(dataset)
sublist_files = sorted(glob.glob(os.path.join(filelist_dir, 'subset_by_letter', 'v1', '*.{}'.format(filetype))))
sublist_files = [f for f in sublist_files if 'tuple' not in f]
print('# of sublist files: {}'.format(len(sublist_files)))

idx_range = [58,62]
sublist_files_sel = sublist_files[idx_range[0]:idx_range[1]]
print('selected sublist files:')
print('\n'.join([' - {}'.format(os.path.basename(f)) for f in sublist_files_sel]))

# get accented letters
lines = open(letter_file, 'r').readlines()
lines = lines[1:]
tuple_list = [line.rstrip().split('\t') for line in lines]
letters = [entry[1] for entry in tuple_list]
nletters = len(letters)
print('# of letters: {}'.format(nletters))

# show the accented letters with their indices
print([(i, letter) for i, letter in enumerate(letters)][idx_range[0]:idx_range[1]])

letters_accent = letters[idx_range[0]:idx_range[1]]
for i,f in enumerate(sublist_files_sel):
    tuple_list = []
    print('processing {} with letter {} (index {}) ...'.format(
        os.path.basename(f), letters_accent[i], idx_range[0]+i))
    lines = open(f, 'r').readlines()
    lines = lines[1:]
    print('{} lines in {}'.format(len(lines), os.path.basename(f)))
    for j,line in enumerate(lines):
        entry = line.rstrip().split(',')
        text = entry[-1]
        words = text.split()
        for k, word in enumerate(words):
            if letters_accent[i] in word:
                l = word.index(letters_accent[i])
                if l > 0:
                    subword = word[l-1:l+1]
                else:
                    subword = 'na'
                tpl = (j, k, l, subword, word, text)
                # output = ('line {}'.format(j), 'word {}'.format(k), 'index {}'.format(l),
                #           subword, word, text)
                # print(', '.join(output))
                tuple_list.append(tpl)
    csvpath = f.replace('.csv', '_tuple.csv')
    header = ['line-idx', 'word-idx', 'letter-idx', 'subword', 'word', 'text']
    tuple2csv(tuple_list, csvpath, colname=header)
    subwords = sorted(set([tpl[3] for tpl in tuple_list]))
    print('subwords: {}'.format(subwords))
