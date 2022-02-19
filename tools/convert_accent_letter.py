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
#  - for letters[58] (`)
#     + (letters[0] + letters[58], letters[26]) # accented A
#     + (letters[4] + letters[58], letters[34]) # accented E
#     + (letters[20] + letters[58], letters[50]) # accented U
#  - for letters[59] ('́)
#     + (letters[14] + letters[59], letters[45]) # accented O
#     + (letters[4] + letters[59], letters[35]) # accented E
#  - for letters[60] (^)
#     + (letters[0] + letters[60], letters[28]) # accented A
#     + (letters[4] + letters[60], letters[36]) # accented E
#     + (letters[8] + letters[60], letters[40]) # accented I
#     + (letters[14] + letters[60], letters[46]) # accented O
#     + (letters[20] + letters[60], letters[52]) # accented U
#  - for letters[61] (̧')
#     + (letters[2] + letters[61], letters[76]) # accented C
#
# Pre-requisites:
#  - run `count_word.py` to generate `chars.csv` for cv-corpus-6.1-2020-12-11
#  - run `subset_by_letter.py` to generate `all_*.csv` for all letters
#
# Zhenhao Ge, 2022-02-16

import os
import glob

dataset = 'cv-corpus-6.1-2020-12-11'
filetype = 'csv'
letter_file = '../templates/speech_recognition/LM/data/{}/chars.{}'.format(dataset, filetype)
assert os.path.isfile(letter_file), '{} does not exist!'.format(letter_file)
filelist_dir = '../templates/speech_recognition/filelists/CommonVoice/cv-corpus-6.1-2020-12-11'
sublist_files = sorted(glob.glob(os.path.join(filelist_dir, 'subset_by_letter', '*.{}'.format(filetype))))
idx_range = [58,62]
sublist_files_sel = sublist_files[idx_range[0]:idx_range[1]]
print('\n'.join([os.path.basename(f) for f in sublist_files_sel]))

lines = open(letter_file, 'r').readlines()
lines = lines[1:]
tuple_list = [line.rstrip().split('\t') for line in lines]
letters = [entry[1] for entry in tuple_list]
letters_accent = letters[idx_range[0]:idx_range[1]]

# show the accented letters with their indices
print([(i, letter) for i, letter in enumerate(letters)][idx_range[0]:idx_range[1]])

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
                output = ('line {}'.format(j), 'word {}'.format(k), 'index {}'.format(l),
                          subword, word, text)
                print(', '.join(output))
                tuple_list.append(tpl)
    subwords = sorted(set([tpl[3] for tpl in tuple_list]))
    print('subwords: {}'.format(subwords))
