# Process FRF_ASR001 dataset from raw data to the data usable in speechbrain
# i.e., easily to prepare the filelists with audio file, texts, and duration
#
# Zhenhao Ge, 2022-01-25

import os
import glob
from pathlib import Path

from tools.audio import audioread, audiowrite
# from tools.audio import soundsc

def remove_bracket(text):
    """remove contents in the brackets <>"""
    n = len(text)
    flag = True # copy or skip
    text2 = ''

    # loop over to copy or skip characters
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
        end = float(lines[i+2].rstrip()[1:-1])
        segments.append((start, end, text2))

    return segments

in_dir = "{}/Data/ots_french/FRF_ASR001/Audio".format(Path.home())
out_dir = "{}/Data/ots_french/FRF_ASR001/Processed".format(Path.home())
os.makedirs(out_dir, exist_ok=True)

audiofiles = sorted(glob.glob(os.path.join(in_dir, "*.wav")))
naudiofiles = len(audiofiles)
print('{} of audio files in {}'.format(naudiofiles, in_dir))

nwords_min = 3 # min # of words for a valid segment

for i, audiofile in enumerate(audiofiles):

    print('processing wav file {}/{}: {} ...'.format(i+1, naudiofiles, audiofile))

    # get call id
    cid = '-'.join(audiofile.split('-')[1:])
    cid = os.path.splitext(cid)[0]

    # create call dir
    calldir = os.path.join(out_dir, cid)
    os.makedirs(calldir, exist_ok=True)

    # get segments
    textfile = audiofile.replace('Audio', 'Transcription').replace('.wav', '.txt')
    segments = extract_segment(textfile)
    nsegments = len(segments)
    print('{} segments in {}'.format(nsegments, audiofile))

    cnt = 0
    outpaths, txtpaths = [], []
    for j, segment in enumerate(segments):
        text = segment[2]
        nwords = len(text.split())

        if nwords > nwords_min:

            # read in audio segment
            starttime = segment[0]
            duration = segment[1] - segment[0]
            data, params = audioread(audiofile, starttime, duration)

            # write out audio segment
            outfile = '{}_{:04d}.wav'.format(cid, cnt)
            outpath = os.path.join(calldir, outfile)
            audiowrite(outpath, data, params)
            outpaths.append(outpath)

            # write out text file for the segment
            txtfile = outfile.replace('.wav', '.txt')
            txtpath = os.path.join(calldir, txtfile)
            open(txtpath, 'w').writelines(text)
            txtpaths.append(txtpath)

            # increment counter
            cnt += 1
