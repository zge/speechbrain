import os
import json
import glob
from pathlib import Path
from subprocess import PIPE, run

root_dir = '../templates/speech_recognition/filelists'
# dataset = 'mini-librispeech'
# dataset = 'ots_french/frf_asr001'
dataset = 'ots_french/frf_asr003'
# dataset = 'CommonVoice/cv-corpus-8.0-2022-01-19'

datadir = os.path.join(Path.home(), 'Data', dataset)
assert os.path.isdir(datadir), 'dir {} does not exist!'.format(datadir)

def get_dur_from_dir(datadir):
    durations = []
    audiofiles = glob.glob(os.path.join(datadir, 'fr', 'clips', '*.mp3'))
    naudiofiles = len(audiofiles)
    for i, audiofile in enumerate(audiofiles):
        if i % 1000 == 0:
            print('getting durations for {} - {} ...'.format(
                i+1, min(i+1000, naudiofiles)))
        cmd = 'soxi -d {}'.format(audiofile)
        output = run(cmd, shell=True, stdout=PIPE).stdout
        hms = output.rstrip().decode('ascii')
        hh, mm, ss = hms.split(':')
        dur = float(hh)*3600 + float(mm)*60 + float(ss)
        durations.append(dur)

        duration_hr = sum(durations)/3600

    return duration_hr

def get_dur_from_list(listfile):

    ext = os.path.splitext(listfile)[1]

    if ext == '.json':
        with open(listfile, 'r') as json_f:
            json_dict = json.load(json_f)
        durations = [entry['length'] for entry in json_dict.values()]
    elif ext == '.csv':
        with open(listfile, 'r') as csv_f:
            lines = csv_f.readlines()
        lines = lines[1:]
        durations = [float(line.split(',')[1]) for line in lines]

    duration_hr = sum(durations)/3600

    return duration_hr


# json_train = os.path.join(root_dir, dataset, 'train.json')
# json_valid = os.path.join(root_dir, dataset, 'valid.json')
# json_test = os.path.join(root_dir, dataset, 'test.json')
# duration_hr_train = get_duration_hr(json_train)
# duration_hr_valid = get_duration_hr(json_valid)
# duration_hr_test = get_duration_hr(json_test)

csv_train = os.path.join(root_dir, dataset, 'train.csv')
csv_valid = os.path.join(root_dir, dataset, 'valid.csv')
csv_test = os.path.join(root_dir, dataset, 'test.csv')
duration_hr_train = get_dur_from_list(csv_train)
duration_hr_valid = get_dur_from_list(csv_valid)
duration_hr_test = get_dur_from_list(csv_test)
duration_hr = duration_hr_train + duration_hr_valid + duration_hr_test

print('duration (hr) for dataset {}: {:.3f} / {:.3f} / {:.3f}'.format(
    dataset, duration_hr_train, duration_hr_valid, duration_hr_test))
print('total duration (hr) for {}: {:.3f}'.format(dataset, duration_hr))