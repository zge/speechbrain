# Inference samples with trained model
#
# Zhenhao Ge, 2022-02-01

import os
import json
import random
import torch
import torchaudio
import csv
from subprocess import PIPE, run
from shutil import copyfile
from torch.nn.utils.rnn import pad_sequence
import collections
from speechbrain.utils.edit_distance import accumulatable_wer_stats
from speechbrain.utils.edit_distance import wer_details_by_utterance

# os.chdir('templates/speech_recognition/ASR')

listfile = '../filelists/frf_asr001/all.json'
assert os.path.isfile(listfile), '{} does not exist!'.format(listfile)
data_root = '../data/ots_french/FRF_ASR001/Processed'
data_resampled = '../data/ots_french/FRF_ASR001/Resampled'
data_output = 'data'
dur_lim = [5, 10] # select audio files with duration between 5 and 10 secs.
seed = 1234
num_sel = 100
sr = 16000
batch_size = 10

# make the dir for resampled audio files
os.makedirs(data_resampled, exist_ok=True)
os.makedirs(data_output, exist_ok=True)

from speechbrain.pretrained import EncoderDecoderASR
asr_model = EncoderDecoderASR.from_hparams(
    source="speechbrain/asr-crdnn-commonvoice-fr",
    savedir="pretrained_models/asr-crdnn-commonvoice-fr",
    run_opts={"device":"cpu"})

def batch_docode(audio_files):
    # find the signals and the corresponding lengths
    sigs, lens = [], []
    for audio_file in audio_files:
        snt, fs = torchaudio.load(audio_file)
        sigs.append(snt.squeeze())
        lens.append(snt.shape[1])

    # batch decoding
    batch = pad_sequence(sigs, batch_first=True, padding_value=0.0)
    lens = torch.Tensor(lens) / batch.shape[1]
    predicted_words, predicted_tokens = asr_model.transcribe_batch(batch, lens)

    return predicted_words, predicted_tokens

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

# read json list file
with open(listfile, 'r') as f:
    json_dict = json.load(f)

# update the paths (placeholder to real path)
for k in json_dict.keys():
    json_dict[k]['wav'] = json_dict[k]['wav'].replace('{data_root}', data_root)

# # check the wav paths
# wavs = [json_dict[k]['wav'] for k in json_dict.keys()]

# # check the duration distribution
# import matplotlib.pyplot as plt
# durs = [json_dict[k]['length'] for k in json_dict.keys()]
# plt.hist(durs, bins='auto')

# select files within the duration range
json_dict_sel = {}
for k in json_dict.keys():
    dur = json_dict[k]['length']
    if dur >= dur_lim[0] and dur <= dur_lim[1]:
        json_dict_sel[k] = json_dict[k]

# randomly select a subset of utterance IDs for inference
uttids = sorted(json_dict_sel.keys())
random.seed(seed)
random.shuffle(uttids)
uttids_sel = sorted(uttids[:num_sel])

# sort utterance IDs based on their corresponding utterance length
durs_sel = [json_dict[uttid]['length'] for uttid in uttids_sel]
uttid_dur_pairs = [(uttid, dur) for uttid, dur in zip(uttids_sel, durs_sel)]
uttid_dur_pairs_sorted = sorted(uttid_dur_pairs, key = lambda pair: pair[1], reverse=True)

# convert selected utterance file from 8K to 16K (model is trained with 16K data)
for i, (uttid, dur) in enumerate(uttid_dur_pairs_sorted):
    if i % 100 == 0:
        print('processing uttid {} ~ {} ...'.format(i, i+100))
    infile = json_dict_sel[uttid]['wav']
    outfile = infile.replace(data_root, data_resampled)
    if not os.path.isfile(outfile):
        outdir = os.path.dirname(outfile)
        os.makedirs(outdir, exist_ok=True)
        cmd = 'sox {} -r {} {}'.format(infile, sr, outfile)
        output = run(cmd, shell=True, stdout=PIPE, stderr=PIPE).stdout

# decode in batch
batches = []
ref_dict, hyp_dict = {}, {}
for i in range(0, num_sel, batch_size):

    print('decoding file {} - {} ...'.format(i, i+batch_size))

    # get audio files in a batch
    audio_files = [json_dict_sel[uttid]['wav'].replace(data_root, data_resampled) \
                   for uttid,dur in uttid_dur_pairs_sorted[i:i+batch_size]]

    uttids_batch = [os.path.splitext(os.path.basename(f))[0] for f in audio_files]

    predicted_words, predicted_tokens = batch_docode(audio_files)

    transcriptions = [json_dict_sel[uttid]['words'].upper() \
                      for uttid,dur in uttid_dur_pairs_sorted[i:i+batch_size]]
    refs = [asr_model.tokenizer.encode_as_ids(transcriptions[i]) for i in range(batch_size)]
    hyps = predicted_tokens

    batches.append([refs, hyps])

    for j, uttid in enumerate(uttids_batch):
        ref_dict[uttid] = refs[j]
        hyp_dict[uttid] = hyps[j]

# get details by utterance
details_by_utterance = wer_details_by_utterance(ref_dict, hyp_dict)
detail_dict = {}
for d in details_by_utterance:
    detail_dict[d['key']] = {'num_edits': d['num_edits'], 'num_ref_tokens': d['num_ref_tokens'],
                             'WER': d['WER'], 'insertions': d['insertions'],
                             'deletions': d['deletions'], 'substitutions': d['substitutions']}

# compute WER
stats = collections.Counter()
for batch in batches:
    refs, hyps = batch
    stats = accumulatable_wer_stats(refs, hyps, stats)
print("%WER {WER:.2f}, {num_ref_tokens} ref tokens".format(**stats))

# output refs, hyps for manual check
tuple_list = []
for i in range(len(batches)):
    batch = batches[i]
    refs, hyps = batch
    for j, (ref, hyp) in enumerate(zip(refs, hyps)):
        ref_text = asr_model.tokenizer.decode_ids(ref)
        hyp_text = asr_model.tokenizer.decode_ids(hyp)
        uttid = uttid_dur_pairs_sorted[i*batch_size+j][0]
        audio_file = json_dict_sel[uttid]['wav'].replace(data_root, data_resampled)
        audio_file2 = os.path.join(data_output, os.path.basename(audio_file))
        copyfile(audio_file, audio_file2)
        details = [detail_dict[uttid]['num_edits'],
                   detail_dict[uttid]['num_ref_tokens'],
                   detail_dict[uttid]['WER'],
                   detail_dict[uttid]['insertions'],
                   detail_dict[uttid]['deletions'],
                   detail_dict[uttid]['substitutions']]
        tuple_list.append([uttid, *details, audio_file2, ref_text, hyp_text])

# write out tuple list as csv file
header = ['uttid', 'num_edits', 'num_ref_tokens', 'WER', 'insertions', 'deletions',
          'substitutions', 'audio path', 'reference', 'hypothesis']
tuple2csv(tuple_list, 'check2.csv', header)