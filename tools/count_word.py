"""
Count #words and #characters from text file or json file

Prerequisites
  - run `extract_text.py` to obtain all.txt for the dataset

Function structure
  - get_word_char
    - get_word_dict
    - get_char_dict

Zhenhao Ge, 2022-01-26
"""

import os
import json
import csv

def get_word_char(filepath, type='text'):

    # read text lines
    if type == 'text':
        lines = open(filepath, 'r').readlines()
    elif type== 'csv':
        lines = open(filepath, 'r').readlines()
        lines = [line.split(',')[-1] for line in lines[1:]]
    elif type == 'json':
        with open(filepath, 'r') as f:
            json_dict = json.load(f)
        lines = [json_dict[key]['words'] for key in json_dict.keys()]

    lines = [line.rstrip() for line in lines]
    nutters = len(lines)

    # concatenate lines into a single long line
    single_line = ' '.join(lines)
    word_dict = get_word_dict(single_line.upper())

    # count #words
    words = single_line.split()
    nwords = len(words)

    # count #characters
    characters = single_line.replace(' ', '')
    ncharacters = len(characters)
    char_dict = get_char_dict(characters.upper())

    # count #letters (unique characters)
    letters = sorted(char_dict.keys())
    nletters = len(letters)

    # count the utterance with each char, i.e., #utters_with_letter_a
    char2nutter_dict = {}
    for i, letter in enumerate(letters):
        # print('checking {}-th/{} letter {} in {} lines ...'.format(
        #     i, nletters, letter, len(lines)))
        for line in lines:
            if letter in line:
                if letter in char2nutter_dict.keys():
                    char2nutter_dict[letter] += 1
                else:
                    char2nutter_dict[letter] = 1

    return word_dict, char_dict, char2nutter_dict, nwords, ncharacters, nutters

def get_word_dict(string):
    words = string.split()
    word_dict = {}
    for word in words:
        if word not in word_dict.keys():
            word_dict[word] = 1
        else:
            word_dict[word] += 1
    return word_dict

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

# specify dataset, e.g.
#  - LM/data/mini-librispeech,
#  - LM/data/frf_asr001,
#  - LM/data/cv-corpus-6.1-2020-12-11,
#  - filelists/ots_frnch/frf_asr001,
#  - filelists/CommonVoice/cv-corpus-6.1-2020-12-11, etc.)

# specify the dataset
# dataset = 'cv-corpus-8.0-2022-01-19' # 'cv-corpus-6.1-2020-12-11', 'cv-corpus-8.0-2022-01-19'
dataset = 'frf_asr002' # 'frf_asr001', 'frf_asr002', 'frf_asr003'
# specify file type (txt, csv, or json)
filetype = 'txt'

# count for text files in LM dir (originally from librispeech)
if dataset == 'mini-librispeech' and filetype == 'txt':
    for filename in ['train.txt', 'valid.txt', 'test.txt']:
        textfile = os.path.join('templates/speech_recognition/LM/data/mini-librispeech', filename)
        nwords, ncharacters = get_word_char(textfile, type='text')[-2:]
        print('{}: {} words, {} characters'.format(textfile, nwords, ncharacters))

# count for json files in mini-librispeech
if dataset == 'mini-librispeech' and filetype == 'json':
    for filename in ['train.json', 'valid.json', 'test.json']:
        jsonfile = os.path.join('templates/speech_recognition/filelists/mini-librispeech', filename)
        nwords, ncharacters = get_word_char(jsonfile, type='json')[-2:]
        print('{}: {} words, {} characters'.format(jsonfile, nwords, ncharacters))

# count for json files in frf_asr001
if dataset == 'frf_asr001' and filetype == 'json':
    for filename in ['train.json', 'valid.json', 'test.json']:
        jsonfile = os.path.join('templates/speech_recognition/filelists/ots_french/frf_asr001', filename)
        nwords, ncharacters = get_word_char(jsonfile, type='json')[-2:]
        print('{}: {} words, {} characters'.format(jsonfile, nwords, ncharacters))

# count for txt files in frf_asr001
if dataset == 'frf_asr001' and filetype == 'txt':
    for filename in ['train.txt', 'valid.txt', 'test.txt']:
        textfile = os.path.join('templates/speech_recognition/LM/data/frf_asr001', filename)
        word_dict, char_dict, char2nutter_dict, nwords, ncharacters, nutters = get_word_char(textfile, type='text')
        print('{}: alphabet size: {}'.format(textfile, len(char_dict.keys())))
        print('{}: {} words, {} characters'.format(textfile, nwords, ncharacters))

# count for txt files in frf_asr002
if dataset == 'frf_asr002' and filetype == 'txt':
    for filename in ['train.txt', 'valid.txt', 'test.txt']:
        textfile = os.path.join('templates/speech_recognition/LM/data/frf_asr002', filename)
        word_dict, char_dict, char2nutter_dict, nwords, ncharacters, nutters = get_word_char(textfile, type='text')
        print('{}: alphabet size: {}'.format(textfile, len(char_dict.keys())))
        print('{}: {} words, {} characters'.format(textfile, nwords, ncharacters))

# count for txt files in frf_asr003
if dataset == 'frf_asr003' and filetype == 'txt':
    for filename in ['train.txt', 'valid.txt', 'test.txt']:
        textfile = os.path.join('templates/speech_recognition/LM/data/frf_asr003', filename)
        word_dict, char_dict, char2nutter_dict, nwords, ncharacters, nutters = get_word_char(textfile, type='text')
        print('{}: alphabet size: {}'.format(textfile, len(char_dict.keys())))
        print('{}: {} words, {} characters'.format(textfile, nwords, ncharacters))

# count for txt file in cv-corpus-6.1-2020-12-11
if dataset == 'cv-corpus-6.1-2020-12-11' and filetype == 'txt':
    for filename in ['train.txt', 'dev.txt', 'test.txt']:
        textfile = os.path.join('templates/speech_recognition/LM/data/cv-corpus-6.1-2020-12-11', filename)
        word_dict, char_dict, char2nutter_dict, nwords, ncharacters, nutters = get_word_char(textfile, type='text')
        print('{}: alphabet size: {}'.format(textfile, len(char_dict.keys())))
        print('{}: {} words, {} characters'.format(textfile, nwords, ncharacters))

# count for csv file in cv-corpus-6.1-2020-12-11
if dataset == 'cv-corpus-6.1-2020-12-11' and filetype == 'csv':
    for filename in ['train.csv', 'dev.csv', 'test.csv']:
        textfile = os.path.join('recipes/CommonVoice/exp/CommonVoice/cv-corpus-6.1-2020-12-11', filename)
        word_dict, char_dict, char2nutter_dict, nwords, ncharacters, nutters = get_word_char(textfile, type='csv')
        print('{}: alphabet size: {}'.format(textfile, len(char_dict.keys())))
        print('{}: {} words, {} characters'.format(textfile, nwords, ncharacters))

# count for txt file in cv-corpus-8.0-2022-01-19
if dataset == 'cv-corpus-8.0-2022-01-19' and filetype == 'txt':
    for filename in ['train.txt', 'dev.txt', 'test.txt']:
        textfile = os.path.join('templates/speech_recognition/LM/data/cv-corpus-8.0-2022-01-19', filename)
        word_dict, char_dict, char2nutter_dict, nwords, ncharacters, nutters = get_word_char(textfile, type='text')
        print('{}: alphabet size: {}'.format(textfile, len(char_dict.keys())))
        print('{}: {} words, {} characters'.format(textfile, nwords, ncharacters))

# count for csv file in cv-corpus-8.0-2022-01-19
if dataset == 'cv-corpus-8.0-2022-01-19' and filetype == 'csv':
    for filename in ['train.csv', 'dev.csv', 'test.csv']:
        textfile = os.path.join('recipes/CommonVoice/exp/CommonVoice/cv-corpus-8.0-2022-01-19', filename)
        word_dict, char_dict, char2nutter_dict, nwords, ncharacters, nutters = get_word_char(textfile, type='csv')
        print('{}: alphabet size: {}'.format(textfile, len(char_dict.keys())))
        print('{}: {} words, {} characters'.format(textfile, nwords, ncharacters))

# generate 'words.csv' and 'chars.csv' from 'all.txt' for OTS dataset
# pre-requisite 'all.txt' is generated from extract_text.py
textfile = os.path.join('templates/speech_recognition/LM/data/{}'.format(dataset), 'all.txt')
assert os.path.isfile(textfile), '{} does not exist'.format(textfile)
word_dict, char_dict, char2nutter_dict, nwords, ncharacters, nutters = get_word_char(textfile, type='text')
print('{}: {} words, {} characters, {} utterances'.format(textfile, nwords, ncharacters, nutters))
word_count_file = os.path.join('templates/speech_recognition/LM/data/{}'.format(dataset), 'words.csv')
write_dict_count(word_count_file, word_dict)
print('#words: {}'.format(len(word_dict.keys())))
print('wrote word dict to {}'.format(word_count_file))
char_count_file = os.path.join('templates/speech_recognition/LM/data/{}'.format(dataset), 'chars.csv')
write_dict_count(char_count_file, char_dict, delimiter='\t')
print('#letters: {}'.format(len(char_dict.keys())))
print('wrote char dict to {}'.format(char_count_file))
char2nutter_count_file = os.path.join('templates/speech_recognition/LM/data/{}'.format(dataset), 'char2nutter.csv')
write_dict_count(char2nutter_count_file, char2nutter_dict, delimiter='\t')
print('#letters: {}'.format(len(char_dict.keys())))
print('wrote char2nutter dict to {}'.format(char2nutter_count_file))

# generate 'words.csv' and 'chars.csv' from 'all.txt' for CV dataset
# pre-requisite 'all.txt' is generated from extract_text.py
textfile = os.path.join('templates/speech_recognition/LM/data/{}'.format(dataset), 'all.txt')
assert os.path.isfile(textfile), '{} does not exist'.format(textfile)
word_dict, char_dict, char2nutter_dict, nwords, ncharacters, nutters = get_word_char(textfile, type='text')
print('{}: {} words, {} characters, {} utterances'.format(textfile, nwords, ncharacters, nutters))
word_count_file = os.path.join('templates/speech_recognition/LM/data/{}'.format(dataset), 'words.csv')
write_dict_count(word_count_file, word_dict)
print('#words: {}'.format(len(word_dict.keys())))
print('wrote word dict to {}'.format(word_count_file))
char_count_file = os.path.join('templates/speech_recognition/LM/data/{}'.format(dataset), 'chars.csv')
write_dict_count(char_count_file, char_dict, delimiter='\t')
print('#letters: {}'.format(len(char_dict.keys())))
print('wrote char dict to {}'.format(char_count_file))
char2nutter_count_file = os.path.join('templates/speech_recognition/LM/data/{}'.format(dataset), 'char2nutter.csv')
write_dict_count(char2nutter_count_file, char2nutter_dict, delimiter='\t')
print('#letters: {}'.format(len(char_dict.keys())))
print('wrote char2nutter dict to {}'.format(char2nutter_count_file))
