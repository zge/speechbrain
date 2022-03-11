# Process FRF_ASR003 dataset from raw data to the data usable in speechbrain
# i.e., easily to prepare the filelists with audio file, texts, and duration
#
# Zhenhao Ge, 2022-03-10

import os
import glob
from pathlib import Path
from shutil import copyfile

from tools.audio import wav_duration

def process_text(text):
    """ process text to remove symbols
     - remove symbols: '!'
    """
    letters = ['!', '-', '.', ':', '/', ';', '?']
    for letter in letters:
        text = text.replace(letter, '')
    return text

dataset = 'FRF_ASR003'
wav_dir = "{}/Data/ots_french/{}/wav".format(Path.home(), dataset)
txt_dir = "{}/Data/ots_french/{}/trl".format(Path.home(), dataset)
sel_dir = "{}/Data/ots_french/{}/sel".format(Path.home(), dataset)
os.makedirs(sel_dir, exist_ok=True)

audiofiles = sorted(glob.glob(os.path.join(wav_dir, '**', '*.wav'), recursive=True))
naudiofiles = len(audiofiles)
textfiles = sorted(glob.glob(os.path.join(txt_dir, '*.trl')))
ntextfiles = len(textfiles)
print('# of tesxt files: {}'.format(ntextfiles))

for i, textfile in enumerate(textfiles):

    print('processing text file {}/{}: {} ...'.format(i+1, ntextfiles, textfile))

    lines = open(textfile, 'r').readlines()
    spk_id = os.path.splitext(os.path.basename(textfile))[0]
    spk_id_num = spk_id[2:]
    lines = lines[1:]
    for j in range(0, len(lines), 2):
        utter_id = int(lines[j].split()[1][:-1])
        assert int(j/2) + 1 == utter_id, \
            'check utterance id {} in {}'.format(utter_id, textfile)
        text = lines[j+1].rstrip()
        utterfile = os.path.join(wav_dir, spk_id_num,
            '{}_{}.txt'.format(spk_id, utter_id))
        audiofile = utterfile.replace('.txt', '.wav')
        assert os.path.isfile(audiofile), 'check {}!'.format(audiofile)
        text = process_text(text)
        open(utterfile, 'w').writelines([text.upper()])


# sanity check (audio and text file match)
utterfiles = sorted(glob.glob(os.path.join(wav_dir, '**', '*.txt'), recursive=True))
nutterfiles = len(utterfiles)
assert naudiofiles == nutterfiles, 'audio and text files not match!'

# filter files by #words and max duration
nwords_min = 3
dur_max = 10
for i, audiofile in enumerate(audiofiles):

    print('processing wav file {}/{}: {} ...'.format(i+1, naudiofiles, audiofile))

    # get text file
    utterfile = audiofile.replace('.wav', '.txt')
    assert os.path.isfile(utterfile), '{} does not exist!'

    text = open(utterfile, 'r').readlines()[0].rstrip()
    nwords = len(text.split())
    duration = wav_duration(audiofile)

    cond1 = nwords > nwords_min
    cond2 = duration <= dur_max
    if cond1 and cond2:
        audiofile2 = audiofile.replace(wav_dir, sel_dir)
        audiodir = os.path.dirname(audiofile2)
        utterfile2 = utterfile.replace(wav_dir, sel_dir)
        os.makedirs(audiodir, exist_ok=True)
        copyfile(audiofile, audiofile2)
        copyfile(utterfile, utterfile2)

# compare duration before and after selection
audiofiles_sel = sorted(glob.glob(os.path.join(sel_dir, "**", "*.wav")))
naudiofiles_sel = len(audiofiles_sel)
durs = [wav_duration(f) for f in audiofiles]
durs_sel = [wav_duration(f) for f in audiofiles_sel]
print('duration: {:.3f} hrs. (raw), {:.3f} hrs. (processed)'.format(
    sum(durs)/3600, sum(durs_sel)/3600))
