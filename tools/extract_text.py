"""
Extract text from json file list

Zhenhao Ge, 2022-01-26
"""

import json
import os

json_dir = 'templates/speech_recognition/filelists/frf_asr001'
text_dir = 'templates/speech_recognition/LM/data/frf_asr001'

for cat in ['train', 'valid', 'test']:
    jsonfile = os.path.join(json_dir, '{}.json'.format(cat))
    textfile = os.path.join(text_dir, '{}.txt'.format(cat))

    with open(jsonfile, 'r') as f:
        json_dict = json.load(f)

    lines = [json_dict[key]['words'] for key in json_dict.keys()]
    open(textfile, 'w').writelines('\n'.join(lines))
