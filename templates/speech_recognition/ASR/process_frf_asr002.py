# Process FRF_ASR002 dataset from raw data to the data usable in speechbrain
# i.e., easily to prepare the filelists with audio file, texts, and duration
#
# Zhenhao Ge, 2022-03-10

import os
import glob
import csv
from pathlib import Path

from tools.audio import audioread, audiowrite, wav_duration
# from tools.audio import soundsc

def process_text(text):
    """ process text to remove symbols
     - remove tags: {spk}, {noise}, {click}, {beep},
       <caller>, </caller>, <recipient>, </recipient>
     - invalid if contains: <bmusic>, <bnoise>, <bspeech>, <foreign>, [utx],
       +WORD, WOR-, -ORD, ~ WORD, (()), ((Word Word))
     - conversion: %ah, %um, %hmm -> ah, um, hmm
    """

    # return empty string if invalid tags present
    invalid_tags = ['<bmusic>', '<bnoise>', '<bspeech>', '<foreign>',
                    '<nospeech>', '</error>',
                    '[utx]', ' +', '- ', ' -', ' ~ ', '((', '))']
    for tag in invalid_tags:
        if tag in text:
            return ''

    text2 = text[:]

    # remove removable tags
    remove_tags = ['{spk}', '{noise}', '{click}', '{beep}',
            '<caller>', '</caller>', '<recipient>', '</recipient>']
    for tag in remove_tags:
        text2 = text2.replace(tag, '')

    # convert tags by removing '%' in the front
    convert_tags = ['%ah', '%um', '%hmm']
    for tag in convert_tags:
        if tag in text2:
            text2 = text2.replace(tag, tag[1:])

    # remove redundant spaces
    text2 = ' '.join(text2.strip().split())

    # remove text with "+" inside
    if '+' in text2:
        text2 = ''

    # sanity check (should not contain following symbols)
    symbols = ['{', '}', '[', ']', '<', '>', '(', ')', '~', '/', '%']
    for symbol in symbols:
        if symbol in text2:
            raise Exception('{} in {}'.format(symbol, text2))

    return text2

def get_ts_lines(lines):
    idxs = [i for i, line in enumerate(lines) if line[0] == '[' and line[-2:] == ']\n']
    return idxs

def remove_line(lines, idx):
    return lines[:idx] + lines[idx+1:]

def extract_segment(textfile):
    """get segments from text file"""

    lines = open(textfile, 'r').readlines()

    # remove beginning lines
    while lines[0][0] != '[':
        lines = lines[1:]
    # remove ending lines
    while lines[-1][0] != '[':
        lines = lines[:-1]

    # remove redundant timestamps
    extra_ts = True
    while extra_ts:
        idxs = get_ts_lines(lines)
        ii_odd = [i for i,odd in enumerate([idx%2 for idx in idxs]) if odd==1]
        if len(ii_odd) > 0:
            idx_first_odd = idxs[ii_odd[0]]
            idx_before_first_odd = idxs[ii_odd[0] - 1]
            if idx_first_odd - idx_before_first_odd == 1:
                lines = remove_line(lines, idx_before_first_odd)
            else:
                raise Exception('check lines of timestamp in {}'.format(textfile))
        else:
           extra_ts = False

    nlines = len(lines)

    letter_count_all = {l: 0 for l in letters}
    segments = []
    for i in range(0,nlines-2,2):
        start = float(lines[i].rstrip()[1:-1])
        text = lines[i+1].rstrip()
        text2 = process_text(text)

        letter_count = {}
        for letter in letters:
            letter_count[letter] = sum([1 if letter in text2 else 0 for c in text2])
            letter_count_all[letter] += letter_count[letter]

        for letter in letters:
            text2 = text2.replace(letter, ' ')
        end = float(lines[i+2].rstrip()[1:-1])
        segments.append((start, end, text, text2))

    return segments, letter_count_all

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

dataset = 'FRF_ASR002'
in_dir = "{}/Data/ots_french/{}/Audio".format(Path.home(), dataset)
out_dir = "{}/Data/ots_french/{}/Processed".format(Path.home(), dataset)
os.makedirs(out_dir, exist_ok=True)

audiofiles = sorted(glob.glob(os.path.join(in_dir, "**", "*.wav"), recursive=True))
naudiofiles = len(audiofiles)
print('{} of audio files in {}'.format(naudiofiles, in_dir))

nwords_min = 3 # min # of words for a valid segment
dur_max = 10 # max duration for utterance (longer utterance is not good for alignment)
letters = ["_", "-", "’", "'"] # decide to replace "'" and "’" with space

# # take a look all text files at once
# textfiles = sorted(glob.glob(os.path.join(in_dir, '**', '*.txt'), recursive=True))
# for textfile in textfiles:
#     lines = open(textfile, 'r').readlines()
#     lines = lines[1:][1:-1:2]

for i, audiofile in enumerate(audiofiles):

    print('processing wav file {}/{}: {} ...'.format(i+1, naudiofiles, audiofile))

    # get text file
    textfile = audiofile.replace('.wav', '.txt')
    assert os.path.isfile(textfile), '{} does not exist!'

    # get segments
    segments, letter_count = extract_segment(textfile)
    nsegments = len(segments)
    print('{} replacement in {}'.format(letter_count, audiofile))
    print('{} segments in {}'.format(nsegments, audiofile))

    # get audio name
    audioname = os.path.splitext(os.path.basename(audiofile))[0]

    # create call dir
    calldir = os.path.dirname(audiofile.replace(in_dir, out_dir))
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
        if cond1 and cond2:

            # read in audio segment
            data, params = audioread(audiofile, starttime, duration)

            # write out audio segment
            outfile = '{}_{:03d}.wav'.format(audioname, cnt)
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

# compare original and processed texts in csv
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
tuple2csv(tuple_list, 'text_comp_{}.csv'.format(dataset.lower()), header)

# compare duration before and after processing
audiofiles_processed = sorted(glob.glob(os.path.join(out_dir, "**", "*.wav"), recursive=True))
naudiofiles_processed = len(audiofiles_processed)
durs = [wav_duration(f) for f in audiofiles]
durs_processed = [wav_duration(f) for f in audiofiles_processed]
print('duration: {:.3f} hrs. (raw), {:.3f} hrs. (processed)'.format(
    sum(durs)/3600, sum(durs_processed)/3600))
