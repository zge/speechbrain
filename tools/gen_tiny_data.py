"""
Generate a tiny dataset from the filelists with randomly selected subsets

Zhenhao Ge, 2022-04-06
"""

import os
from pathlib import Path
from shutil import copyfile
import glob

root_dir = '../templates/speech_recognition/filelists/'
filelist_dir_combined = os.path.join(root_dir, 'cv_with_ots')

data_root = os.path.join(Path.home(), 'Data')
data_root_tiny = os.path.join(data_root, 'tiny')
os.makedirs(data_root_tiny, exist_ok=True)

# copy files
cats = ['train', 'valid', 'test']
nwavs = {}
ncopied = 0
for cat in cats:
    filelist = os.path.join(filelist_dir_combined, '{}_tiny.csv'.format(cat))
    lines = open(filelist, 'r').readlines()
    wavs = [line.split(',')[2] for line in lines[1:]]
    for wav in wavs:
        path = wav.replace('$data_root', data_root)
        path_tiny = path.replace(data_root, data_root_tiny)
        dir_tiny = os.path.dirname(path_tiny)
        os.makedirs(dir_tiny, exist_ok=True)
        copyfile(path, path_tiny)
        if os.path.isfile(path_tiny):
            ncopied += 1
        else:
            raise Exception('check {}!'.format(path_tiny))
    nwavs[cat] = len(wavs)
    print('{} files in {}'.format(nwavs[cat], filelist))
print('{} files in filelists'.format(sum(nwavs.values())))

# sanity check
wavs_mp3 = glob.glob(os.path.join(data_root_tiny, '**', '*.mp3'), recursive=True)
wavs_wav = glob.glob(os.path.join(data_root_tiny, '**', '*.wav'), recursive=True)
wavs_all = wavs_mp3 + wavs_wav
print('{} files copied'.format(len(wavs_all)))
