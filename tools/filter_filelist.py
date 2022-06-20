# Filter filelist by letter
# Filter out the utterances with uncommon letters
#
# Zhenhao Ge, 2022-03-04

import os
import csv
import shutil

# os.chdir('/Users/zhge/PycharmProjects/speechbrain/tools')

def get_letter(char_file):
    lines = open(char_file, 'r').readlines()
    lines = lines[1:]
    letters = [line.rstrip().split('\t')[1] for line in lines]
    return letters

def tuple2csv(tuples, csvname='filename.csv', colname=[], verbose=True):
    with open(csvname, 'w', newline='') as f:
        csv_out = csv.writer(f)
        if len(colname) != 0:
            header = colname
            csv_out.writerow(header)
        for i, tpl in enumerate(tuples):
            csv_out.writerow(list(tpl))
    if verbose:
        print('{} saved!'.format(csvname))

def concat_csv(infiles, outfile, have_header=True, verbose=True):

    if have_header:
        header = open(infiles[0], 'r').readline().rstrip().split(',')
    else:
        header = None
    with open(outfile, 'w', newline='') as f:
        csv_out = csv.writer(f)
        if have_header:
            csv_out.writerow(header)
        for infile in infiles:
            lines = open(infile, 'r').readlines()
            if have_header:
                lines = lines[1:]
            for line in lines:
                row = line.rstrip().split(',')
                csv_out.writerow(row)
    if verbose:
        print('{} saved!'.format(outfile))

dataset_standard = 'frf_asr001'
char_file_standard = os.path.join('../templates/speech_recognition/LM/data',
                           dataset_standard, 'chars.csv')
assert os.path.isfile(char_file_standard), '{} does not exist'.format(char_file_standard)

# get letter files
# dataset_extra = 'cv-corpus-8.0-2022-01-19'
# dataset_extra = 'frf_asr002'
dataset_extra = 'frf_asr003'
char_file_extra = os.path.join('../templates/speech_recognition/LM/data',
                           dataset_extra, 'chars.csv')
assert os.path.isfile(char_file_extra), '{} does not exsit'.format(char_file_extra)

# set filelist dir
# filelist_dir = '../recipes/CommonVoice/exp/CommonVoice/{}/'.format(dataset_extra)
filelist_dir = '../templates/speech_recognition/filelists/ots_french/{}/'.format(dataset_extra)
assert os.path.isdir(filelist_dir), '{} does not exist!'.format(filelist_dir)

letters_extra = get_letter(char_file_extra)
letters_standard = get_letter(char_file_standard)
print('#letters in the dataset with extra letters {}: {}'.format(
    os.path.basename(char_file_extra), len(letters_extra)))
print('#letters in the dataset with standard letters {}: {}'.format(
    os.path.basename(char_file_standard), len(letters_standard)))

# find common letters in both standard and extra
letters_common = [l for l in letters_standard if l in letters_extra]
print('#letters in both standard and extra: {}'.format(len(letters_common)))

# find letters in extra but not in standard
letters_extra_not_standard = [l for l in letters_extra if l not in letters_standard]
print('#letters in extra but not in standard: {}'.format(len(letters_extra_not_standard)))

# csv_files = ['train.csv', 'dev.csv', 'test.csv']
csv_files = ['train.csv', 'valid.csv', 'test.csv']
for csv_file in csv_files:

    # get header and entries from the csv file
    csv_path = os.path.join(filelist_dir, csv_file)
    lines = open(csv_path, 'r').readlines()
    header = lines[0].rstrip().split(',')
    lines = lines[1:]
    entries = [line.rstrip().split(',') for line in lines]
    nutters = len(entries)
    durations = [float(entry[1]) for entry in entries]
    dur_total = sum(durations)

    entries2, cnt, durations_rm = [], 0, []
    for entry in entries:
        duration, text = float(entry[1]), entry[-1]
        letters_sel = [l for l in text if l in letters_extra_not_standard]
        if len(letters_sel) == 0:
            entries2.append(entry)
        else:
            durations_rm.append(duration)
            cnt += 1
    dur_rm = sum(durations_rm)
    print('removed {}/{} utterances ({:.3f} hrs. / {:.3f} hrs.) in {}'.format(
        cnt, nutters, dur_rm/3600, dur_total/3600, csv_file))

    csv_path_old = csv_path.replace('.csv', '_old.csv')
    shutil.move(csv_path, csv_path_old)
    tuple2csv(entries2, csv_path, colname=header)

infiles = [os.path.join(filelist_dir, csv_file) for csv_file in csv_files]
outfile = os.path.join(filelist_dir, 'all.csv')
concat_csv(infiles, outfile)