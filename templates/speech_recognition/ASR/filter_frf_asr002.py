# Remove processed files with noise
# First get the statistics about #files with different noise tag
# Then, determine if files in certain noise category need to be removed
#
# Zhenhao Ge, 2022-06-07

import os
import glob
from pathlib import Path
from shutil import rmtree

from tools.audio import audioread, audiowrite, wav_duration
# from tools.audio import soundsc

dataset = 'FRF_ASR002'
data_dir = '{}/Data/ots_french/{}/Processed'.format(Path.home(), dataset)
filtered_dir = os.path.join(data_dir, 'Filtered')
os.makedirs(filtered_dir, exist_ok=True)

audiofiles = sorted(glob.glob(os.path.join(data_dir, '**', '*.wav'), recursive=True))
naudiofiles = len(audiofiles)
print('{} of audio files in {}'.format(naudiofiles, data_dir))

tags = ['{spk}', '<bmusic>', '<bnoise>', '<bspeech>', '{noise}', '{click}', '{beep}', '<foreign>',
        '[utx]', '%ah', '%um', '%hmm', '+', '-', '- ', ' -', '~', '((', '))', '<caller>', '<recipient>']
tags_removed = ['<bmusic>', '<bnoise>', '<bspeech>', '{noise}', '<foreign>', '[utx]',
                '+', '~', ' -', '- ', '((', '))', '<caller>', '<recipient>']
tags_kept = ['{spk}', '{click}', '{beep}', '%ah', '%um', '%hmm', '-', ]
# tags_removed = ['(())', '<cough>', '<foreign>', '<int>', '<laugh>', '<ring>', '*']
# tags_kept = ['<ah>', '<breath>', '<click>', '<dtmf>', '<euh>', '<hmm>', '<lipsmack>']
assert len(tags) == len(tags_removed) + len(tags_kept), 'check tags!'

# loop over audio and text files
tag2file = {tag:[] for tag in tags}
spkids = []
audiofiles_withtag = []
audiofiles_removed = []
for i, audiofile in enumerate(audiofiles):

    spkid = os.path.basename(os.path.dirname(os.path.dirname(audiofile)))
    if spkid not in spkids:
        spkids.append(spkid)
        print('processing {}/{} audiofile with speaker ID: {}'.format(
            i+1, naudiofiles, spkid))

    # read text
    textfile = audiofile.replace('.wav', '_orig.txt')
    textname = os.path.basename(textfile)
    lines = open(textfile, 'r').readlines()
    text_orig = lines[0]

    # data, para = audioread(audiofile)
    # soundsc(data, para)

    for tag in tags:
        # # obtain #files in each tag category
        if tag in text_orig:
            tag2file[tag].append((audiofile.replace(data_dir, ''), text_orig))
            audiofiles_withtag.append(audiofile)
            # collect audiofiles need to be removed based on tags to be removed
            if tag in tags_removed:
                audiofiles_removed.append(audiofile)

tag2file = {k:sorted(set(v)) for k,v in tag2file.items()}
tag2num = {k:len(v) for k,v in tag2file.items()}
audiofiles_withtag = sorted(set(audiofiles_withtag))
audiofiles_removed = sorted(set(audiofiles_removed))
print('There are {} speakers in dataset {}'.format(len(spkids), dataset))
print('There are {}/{} audio files with tag'.format(
    len(audiofiles_withtag), naudiofiles))
print('There are {}/{} audio files to be filtered'.format(
    len(audiofiles_removed), naudiofiles))

# filter out the selected audio files and their associated text files
for i, audiofile in enumerate(audiofiles_removed):
    filename = os.path.basename(audiofile)
    sessionid = os.path.basename(os.path.dirname(audiofile))
    spkid = os.path.basename(os.path.dirname(os.path.dirname(audiofile)))
    output_dir = os.path.join(filtered_dir, spkid, sessionid)
    os.makedirs(output_dir, exist_ok=True)
    audiofile_out = os.path.join(output_dir, filename)
    textfile = audiofile.replace('.wav', '.txt')
    textfile_out = os.path.join(output_dir, filename.replace('.wav', '.txt'))
    textfile_orig = audiofile.replace('.wav', '_orig.txt')
    textfile_orig_out = os.path.join(output_dir, filename.replace('.wav', '_orig.txt'))
    assert os.path.isfile(textfile), 'file: {} does not exist!'.format(textfile)
    assert os.path.isfile(textfile_orig), 'file: {} does not exist!'.format(textfile_orig)
    os.rename(audiofile, audiofile_out)
    os.rename(textfile, textfile_out)
    os.rename(textfile_orig, textfile_orig_out)
    print('{}/{}: move {} --> {}'.format(i+1, len(audiofiles_removed),
        os.path.splitext(audiofile.replace(data_dir, ''))[0],
        os.path.splitext(audiofile_out.replace(data_dir, ''))[0]))

# # undo filtering (for debugging use)
# # step 1: move back files
# for i, audiofile in enumerate(audiofiles_removed):
#     filename = os.path.basename(audiofile)
#     sessionid = os.path.basename(os.path.dirname(audiofile))
#     spkid = os.path.basename(os.path.dirname(os.path.dirname(audiofile)))
#     output_dir = os.path.join(filtered_dir, spkid, sessionid)
#     assert os.path.isdir(output_dir), 'dir: {} does not exist!'.format(output_dir)
#     audiofile_out = os.path.join(output_dir, filename)
#     textfile = audiofile.replace('.wav', '.txt')
#     textfile_out = os.path.join(output_dir, filename.replace('.wav', '.txt'))
#     textfile_orig = audiofile.replace('.wav', '_orig.txt')
#     textfile_orig_out = os.path.join(output_dir, filename.replace('.wav', '_orig.txt'))
#     if os.path.isfile(audiofile_out):
#         os.rename(audiofile_out, audiofile)
#         os.rename(textfile_out, textfile)
#         os.rename(textfile_orig_out, textfile_orig)
#         print('{}/{}: move back {} --> {}'.format(i+1, len(audiofiles_removed),
#             os.path.splitext(audiofile_out.replace(data_dir, ''))[0],
#             os.path.splitext(audiofile.replace(data_dir, ''))[0]))
#     elif os.path.isfile(audiofile):
#         print('{}/{}: already move back {} --> {}'.format(i+1, len(audiofiles_removed),
#             os.path.splitext(audiofile_out.replace(data_dir, ''))[0],
#             os.path.splitext(audiofile.replace(data_dir, ''))[0]))
#     else:
#         raise Exception('missing both {} and {}!'.format(
#             os.path.splitext(audiofile.replace(data_dir, ''))[0],
#             os.path.splitext(audiofile_out.replace(data_dir, ''))[0]))
# # step 2: delete sub dirs in filtered dir
# audiofiles_checked = sorted(glob.glob(os.path.join(filtered_dir, '**', '*.wav'), recursive=True))
# assert len(audiofiles_checked) == 0, 'still files left in the filtered dir!'
# subdirs = glob.glob(os.path.join(filtered_dir, '*'))
# for subdir in subdirs:
#     rmtree(subdir)

# sanity check
audiofiles_checked = sorted(glob.glob(os.path.join(filtered_dir, '**', '*.wav'), recursive=True))
assert len(audiofiles_checked) == len(audiofiles_removed), 'missing removed files!'
audiofiles_all = sorted(glob.glob(os.path.join(data_dir, '**', '*.wav'), recursive=True))
assert len(audiofiles_all) == len(audiofiles), '#audiofiles changed after move!'

# compare duration before and after processing
audiofiles_processed_new = sorted(glob.glob(os.path.join(data_dir, "**", "*.wav"), recursive=True))
audiofiles_remained = sorted([f for f in audiofiles_processed_new if 'Filtered' not in f])
naudiofiles_processed_new = len(audiofiles_processed_new)
naudiofiles_remained = len(audiofiles_remained)
print('There are {}/{} audio files remained after filtering'.format(
    naudiofiles_remained, naudiofiles_processed_new))
durs_processed_new = [wav_duration(f) for f in audiofiles_processed_new]
durs_remained = [wav_duration(f) for f in audiofiles_remained]
print('duration: {:.3f} hrs. (processed), {:.3f} hrs. (remained)'.format(
    sum(durs_processed_new)/3600, sum(durs_remained)/3600))