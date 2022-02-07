import os
import json
from pathlib import Path

root_dir = 'templates/speech_recognition/filelists'
dataset = 'mini-librispeech'
dataset = 'frf_asr001'


def get_duration_hr(json_file):

    with open(json_file, 'r') as json_f:
        json_dict = json.load(json_f)

    durations = [entry['length'] for entry in json_dict.values()]
    duration_hr = sum(durations)/3600

    return duration_hr


json_train = os.path.join(root_dir, dataset, 'train.json')
json_valid = os.path.join(root_dir, dataset, 'valid.json')
json_test = os.path.join(root_dir, dataset, 'test.json')

duration_hr_train = get_duration_hr(json_train)
duration_hr_valid = get_duration_hr(json_valid)
duration_hr_test = get_duration_hr(json_test)

print('duration (hr) for dataset {}: {:.2f} / {:.2f} / {:.2f}'.format(
    dataset, duration_hr_train, duration_hr_valid, duration_hr_test))