# Check the letters in the decoded text, to see if the accented letters
# are encoded in both single and two characters
#
# This script is a follow-up from `convert_accent_letter.py`,
# after finding all the mappings from two characters to single characters
# for the accented letters
#
# The goal is to remove all the two-characters version of the accented letters
# But before that, it is better to check if the two-character version exist
# in the decoded text
#
# Conclusion:
# There are 43 letters in the decoded text, plus ''' which will be converted to space
# since there is no ''' in the reference text
# If you want to preserve ''', then you need to re-process the CV data to preserve '''
#
# Zhenhao Ge, 2022-02-18

import os
import csv
from pathlib import Path

def get_char_dict(characters):
    char_dict = {}
    for c in characters:
        if c not in char_dict.keys():
            char_dict[c] = 1
        else:
            char_dict[c] += 1
    return char_dict

def write_dict_count(csvfile, dct, delimiter=',',
                     header = ['binary', 'letter', 'count', 'percent'], verbose=True):
    total_cnt = sum(dct.values())
    with open(csvfile, 'w', newline='') as f:
        csv_out = csv.writer(f, delimiter=delimiter)
        csv_out.writerow(header)
        keys = sorted(dct.keys())
        for i, k in enumerate(keys):
            cnt = dct[k]/total_cnt
            cnt_str = '{:.2f}'.format(cnt*100)
            #iso_code = ord(k.encode('iso-8859-1'))
            # row = [iso_code, k, dct[k], cnt_str]
            utf8_code = k.encode('utf-8')
            row = [utf8_code, k, dct[k], cnt_str]
            csv_out.writerow(row)
    if verbose:
        print('{} saved!'.format(csvfile))

dataset = 'cv-corpus-6.1-2020-12-11'
modeltype = 'CRDNN'
result_dir = os.path.join(Path.home(), 'OneDrive - Appen/results/20220202_ASR-Fr-Pretrained')
assert os.path.isdir(result_dir), 'result dir: {} does not exist!'.format(result_dir)
decoded_file = os.path.join(result_dir, dataset, modeltype,
                            'check_{}_{}.csv'.format(dataset, modeltype.lower()))
assert os.path.isfile(decoded_file), 'decoded file {} does not exist!'.format(decoded_file)

lines = open(decoded_file, 'r').readlines()
lines = lines[1:]
print('{} files in {}'.format(len(lines), os.path.basename(decoded_file)))

decoded_texts = [line.rstrip().split(',')[-1] for line in lines]
single_line_text = ' '.join(decoded_texts)
decoded_chars = single_line_text.replace(' ', '')
letters = sorted(set(decoded_chars))
nletters = len(letters)
print('{} chars in {}'.format(nletters, os.path.basename(decoded_file)))

char_dict = get_char_dict(decoded_chars)
char_count_file = os.path.join(result_dir, dataset, modeltype,
    'decoded_char_{}_{}.csv'.format(dataset, modeltype.lower()))
write_dict_count(char_count_file, char_dict, delimiter='\t')
print('wrote char dict to {}'.format(char_count_file))
