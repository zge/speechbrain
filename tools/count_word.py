"""
Count #words and #characters from text file or json file

Zhenhao Ge, 2022-01-26
"""

import os
import json

def get_word_char(filepath, type='text'):

    # read text lines
    if type == 'text':
        lines = open(textfile, 'r').readlines()
    elif type == 'json':
        with open(jsonfile, 'r') as f:
            json_dict = json.load(f)
        lines = [json_dict[key]['words'] for key in json_dict.keys()]

    # concatenate lines into a single long line
    single_line = ' '.join(lines)

    # count #words
    words = single_line.split()
    nwords = len(words)

    # count #characters
    characters = single_line.replace(' ', '')
    ncharacters = len(characters)

    return nwords, ncharacters

# count for text files in LM dir (originally from librispeech)
for filename in ['train.txt', 'valid.txt', 'test.txt']:
    textfile = os.path.join('templates/speech_recognition/LM/data', filename)
    nwords, ncharacters = get_word_char(textfile, type='text')
    print('{}: {} words, {} characters'.format(textfile, nwords, ncharacters))

# count for json files in mini-librispeech
for filename in ['train.json', 'valid.json', 'test.json']:
    jsonfile = os.path.join('templates/speech_recognition/filelists/mini-librispeech', filename)
    nwords, ncharacters = get_word_char(jsonfile, type='json')
    print('{}: {} words, {} characters'.format(jsonfile, nwords, ncharacters))

# count for json files in frf_asr001
for filename in ['train.json', 'valid.json', 'test.json']:
    jsonfile = os.path.join('templates/speech_recognition/filelists/frf_asr001', filename)
    nwords, ncharacters = get_word_char(jsonfile, type='json')
    print('{}: {} words, {} characters'.format(jsonfile, nwords, ncharacters))