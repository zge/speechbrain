# -*- coding: utf-8 -*-
"""
Compare alphabet difference in CV, OTS French data and the ASR tokenizer

Zhenhao Ge, 2022-02-18
"""

import os, sys
from pathlib import Path

sys.path.append(os.getcwd())
from utils import csv2dict

def get_letter(char_file):
    lines = open(char_file, 'r').readlines()
    lines = lines[1:]
    letters = [line.rstrip().split('\t')[1] for line in lines]
    return letters


def find_sel(csv_file, letters):
    dict_list = csv2dict(csv_file)
    durations = [float(entry['duration']) for entry in dict_list]
    nutters = len(durations)
    dur_total = sum(durations)

    cnt = 0
    durations_sel = []
    for i, entry in enumerate(dict_list):
        letters_sel = [l for l in entry['wrd'] if l in letters]
        if len(letters_sel) > 0:
            # print('entry {}: {} ({})'.format(i, letters_sel, entry['wrd']))
            durations_sel.append(float(entry['duration']))
            cnt += 1
    dur_sel = sum(durations_sel)

    return nutters, cnt, dur_total, dur_sel

dataset = 'cv-corpus-6.1-2020-12-11'
result_folder = '20220202_ASR-Fr-Pretrained'
result_dir = os.path.join(Path.home(), 'OneDrive - Appen/results', result_folder)
assert os.path.isdir(result_dir), '{} does not exist'.format(result_dir)
char_file_asr = os.path.join(result_dir, dataset, 'CRDNN', 'alphabets', 'token_char_crdnn.csv')

result_folder = '20220209_Ref-Hyp_TextInspection'
result_dir = os.path.join(Path.home(), 'OneDrive - Appen/results', result_folder)
assert os.path.isdir(result_dir), '{} does not exist'.format(result_dir)
char_file_cv = os.path.join(result_dir, 'chars_corpus_6.1-2020-12-11.csv')
char_file_ots = os.path.join(result_dir, 'chars_frf_asr001.csv')

letters_asr = get_letter(char_file_asr)
letters_cv = get_letter(char_file_cv)
letters_ots = get_letter(char_file_ots)
print('#letters in {}: {}'.format(os.path.basename(char_file_asr), len(letters_asr)))
print('#letters in {}: {}'.format(os.path.basename(char_file_cv), len(letters_cv)))
print('#letters in {}: {}'.format(os.path.basename(char_file_ots), len(letters_ots)))

# find common letters in both OTS and CV
letters_cv_ots = [l for l in letters_ots if l in letters_cv]
print('#letters in both ots and cv: {}'.format(len(letters_cv_ots)))

# find letters in CV but not in OTS
letters_cv_not_ots = [l for l in letters_cv if l not in letters_ots]
print('#letters in cv but not in ots: {}'.format(len(letters_cv_not_ots)))

# find common letters in both CV and ASR tokenizer
letters_cv_asr = [l for l in letters_cv if l in letters_asr]
print('#letters in both cv and asr: {}'.format(len(letters_cv_asr)))

# find letters in ASR tokenizer but not in CV
letters_asr_not_cv = [l for l in letters_asr if l not in letters_cv]
print('#letters in asr but not in CV: {}'.format(len(letters_asr_not_cv)))

# find letters in CV but not in ASR tokenizer
letters_cv_not_asr = [l for l in letters_cv if l not in letters_asr]
print('#letters in cv but not in asr: {}'.format(len(letters_cv_not_asr)))

# find out the total duration of utterances contains letters_cv_not_ots
for cat in ['train', 'dev', 'test']:
    csv_file = '../recipes/CommonVoice/exp/CommonVoice/{}/{}.csv'.format(dataset, cat)
    nutters, nutters_sel, dur, dur_sel = find_sel(csv_file, letters_cv_not_ots)
    print('{}/{} utterances ({:.3f} hr. /{:.3f} hr.) in {} with uncommon letters'.format(
        nutters_sel, nutters, dur_sel/3600, dur/3600, os.path.basename(csv_file)))
