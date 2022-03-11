# Process FRF_ASR001 dataset from raw data to the data usable in speechbrain
# i.e., easily to prepare the filelists with audio file, texts, and duration
#
# Zhenhao Ge, 2022-01-25

import os
import glob
import csv
from pathlib import Path

from tools.audio import audioread, audiowrite, wav_duration
# from tools.audio import soundsc

def remove_bracket(text):
    """remove contents in the brackets <>"""
    n = len(text)
    flag = True # copy or skip
    text2 = ''

    # loop over to copy or skip characters inside '<>'
    i = 0
    while i < n:
        if flag:
            if text[i] != '<':
                text2 += text[i]
            else:
                flag = False
        else:
            if text[i] == '>':
                flag = True
        i += 1

    # remove '(())'
    text2 = text2.replace('(())','')

    # remove redundant spaces
    text2 = ' '.join(text2.strip().split())
    return text2

def extract_segment(textfile):
    """get segments from text file"""

    lines = open(textfile, 'r').readlines()

    # remove beginning lines
    while lines[0][0] != '[':
        lines = lines[1:]
    # remove ending lines
    while lines[-1][0] != '[':
        lines = lines[:-1]
    nlines = len(lines)

    segments = []
    for i in range(0,nlines-2,2):
        start = float(lines[i].rstrip()[1:-1])
        text = lines[i+1].rstrip()
        text2 = remove_bracket(text)
        for letter in letters:
            text2 = text2.replace(letter, ' ')
        end = float(lines[i+2].rstrip()[1:-1])
        segments.append((start, end, text, text2))

    return segments

def tuple2csv(tuples, csvname='filename.csv', colname=[], encoding='utf-8', verbose=True):
    with open(csvname, 'w', newline='', encoding=encoding) as f:
        csv_out = csv.writer(f)
        if len(colname) != 0:
            header = colname
            csv_out.writerow(header)
        for i, tpl in enumerate(tuples):
            csv_out.writerow(list(tpl))
    if verbose:
        print('{} saved!'.format(csvname))

dataset = 'FRF_ASR001'
in_dir = "{}/Data/ots_french/{}/Audio".format(Path.home(), dataset)
out_dir = "{}/Data/ots_french/{}/Processed".format(Path.home(), dataset)
os.makedirs(out_dir, exist_ok=True)

audiofiles = sorted(glob.glob(os.path.join(in_dir, "**", "*.wav"), recursive=True))
naudiofiles = len(audiofiles)
print('{} of audio files in {}'.format(naudiofiles, in_dir))

nwords_min = 3 # min # of words for a valid segment
dur_max = 10 # max duration for utterance (longer utterance is not good for alignment)
# letters = ["_", "-", "'"]
letters = ["_", "-"] # decide not to replace "'" with space

for i, audiofile in enumerate(audiofiles):

    print('processing wav file {}/{}: {} ...'.format(i+1, naudiofiles, audiofile))

    # get text file
    textfile = audiofile.replace('Audio', 'Transcription').replace('.wav', '.txt')
    assert os.path.isfile(textfile), '{} does not exist!'

    # get segments
    segments = extract_segment(textfile)
    nsegments = len(segments)
    print('{} segments in {}'.format(nsegments, audiofile))

    # get call id
    cid = '-'.join(audiofile.split('-')[1:])
    cid = os.path.splitext(cid)[0]

    # create call dir
    calldir = os.path.join(out_dir, cid)
    os.makedirs(calldir, exist_ok=True)

    cnt = 0
    outpaths, txtpaths, txtpaths2 = [], [], []
    for j, segment in enumerate(segments):
        text, text2 = segment[2:]
        nwords = len(text2.split())
        starttime = segment[0]
        duration = float(format(segment[1]-segment[0], '.3f'))

        cond1 = nwords > nwords_min
        cond2 = duration <= dur_max
        cond3 = '*' not in text2
        if cond1 and cond2 and cond3:

            # read in audio segment
            data, params = audioread(audiofile, starttime, duration)

            # write out audio segment
            outfile = '{}_{:04d}.wav'.format(cid, cnt)
            outpath = os.path.join(calldir, outfile)
            audiowrite(outpath, data, params)
            outpaths.append(outpath)

            # write out the original text for the segment (as backup)
            txtfile = outfile.replace('.wav', '_orig.txt')
            txtpath = os.path.join(calldir, txtfile)
            open(txtpath, 'w').writelines(text)
            txtpaths.append(txtpath)

            # write out processed text for the segment
            txtfile2 = outfile.replace('.wav', '.txt')
            txtpath2 = os.path.join(calldir, txtfile2)
            open(txtpath2, 'w').writelines(text2.upper())
            txtpaths2.append(txtpath2)

            # increment counter
            cnt += 1

# write out original and processed texts in csv for comparison
txtpaths = sorted(glob.glob(os.path.join(out_dir, '**', '*_orig.txt'), recursive=True))
txtpaths2 = sorted(glob.glob(os.path.join(out_dir, '**', '*.txt'), recursive=True))
txtpaths2 = [path for path in txtpaths2 if '_orig' not in path]
assert len(txtpaths) == len(txtpaths2), '# of original & processed texts not match!'
tuple_list = []
for path in txtpaths:
    path2 = path.replace('_orig', '')
    text = open(path, 'r').readlines()[0].rstrip()
    text2 = open(path2, 'r').readlines()[0].rstrip()
    uttid = os.path.splitext(os.path.basename(path2))[0]
    tuple_list.append((uttid, text, text2))
header = ['uttid', 'original text', 'processed text']
tuple2csv(tuple_list, 'text_comp.csv', header)

# compare duration before and after processing
audiofiles_processed = sorted(glob.glob(os.path.join(out_dir, "**", "*.wav"), recursive=True))
naudiofiles_processed = len(audiofiles_processed)
durs = [wav_duration(f) for f in audiofiles]
durs_processed = [wav_duration(f) for f in audiofiles_processed]
print('duration: {:.3f} hrs. (raw), {:.3f} hrs. (processed)'.format(
    sum(durs)/3600, sum(durs_processed)/3600))
