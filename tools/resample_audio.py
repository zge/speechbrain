# Resample audio files
# dataset: ots_french/FRF_ASR001
#
# Zhenhao Ge, 2022-02-23

import os
import glob
from subprocess import PIPE, run

# os.chdir('/Users/zhge/PycharmProjects/speechbrain/tools')

dataset = 'FRF_ASR002' # 'FRF_ASR001', 'FRF_ASR002'
data_root = '../templates/speech_recognition/data/ots_french/{}'.format(dataset)
data_processed = os.path.join(data_root, 'Processed')
assert os.path.isdir(data_root), 'dir {} does not exist!'.format(data_processed)
data_resampled = os.path.join(data_root, 'Resampled')
# listfile = '../templates/speech_recognition/filelists/ots_french/{}/all.json'.format(dataset)
# assert os.path.isfile(listfile), 'file {} does not exist!'.format(listfile)

# set the resampling rate
sr = 16000

# get all input audio files
audio_files = glob.glob(os.path.join(data_processed, '**', '*.wav'), recursive=True)
nfiles = len(audio_files)
print('{} files in {}'.format(nfiles, data_processed))

for i, audio_file in enumerate(audio_files):
    if i % 100 == 0:
        print('processing uttid {} ~ {} ({}) ...'.format(i, min(i+100, nfiles), nfiles))
    audio_file2 = audio_file.replace(data_processed, data_resampled)
    audio_dir = os.path.dirname(audio_file2)
    os.makedirs(audio_dir, exist_ok=True)
    if not os.path.isfile(audio_file2):
        cmd = 'sox {} -r {} {}'.format(audio_file, sr, audio_file2)
        output = run(cmd, shell=True, stdout=PIPE, stderr=PIPE).stdout
