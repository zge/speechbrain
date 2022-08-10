# inference with batch
#
# Zhenhao Ge, 2021-06-21

import os
import argparse
import csv
import torch
import torchaudio
from subprocess import PIPE, run
from shutil import copyfile
from torch.nn.utils.rnn import pad_sequence
from hyperpyyaml import load_hyperpyyaml
from speechbrain.pretrained import EncoderDecoderASR

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

def write_csv(csvfile, lines, header=None):
    # write the result csv
    with open(csvfile, 'w', newline = '') as f:
        write = csv.writer(f)
        if header:
            write.writerow(header)
        write.writerows(lines)
    print('wrote lines in {}'.format(csvfile))

def parse_args():
    usage = 'usage: inference with batch'
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument('--source-dir', type=str,
                        help='asr source model dir')
    parser.add_argument('--save-dir', type=str, default=None,
                        help='asr local model dir')
    parser.add_argument('--tmp-dir', type=str, default='tmp_dir',
                        help='dir to save resampled audio if needed')
    parser.add_argument('--out-dir', type=str, default='inference_output',
                        help='dir to save inference results')
    parser.add_argument('--filelist', type=str,
                        help='text file with a list of audio files')
    parser.add_argument('--data-root', type=str, default=None,
                        help='data root dir')
    parser.add_argument('--num-files', type=int, default=float('Inf'),
                        help='number of audiofiles to be inferenced')
    parser.add_argument('--batch-size', type=int, default=10,
                        help='number of audio files in one batch')
    return parser.parse_args()

if __name__ == '__main__':

    # runtime mode
    args = parse_args()

    # # interactive mode
    # # os.chdir('templates/speech_recognition/ASR')
    # args = argparse.ArgumentParser()
    # args.source_dir = os.path.join('../../../recipes/CommonVoice/results',
    # 'speech_dev_dl_pytorch2', 'cv8.0_with_ots_fr_seq2seq_ctc_attention_now2v_nosmooth_sb')
    # args.save_dir = None
    # args.tmp_dir = 'tmp_dir'
    # args.out_dir = 'inference_output'
    # args.filelist = '../filelists/cv_with_ots/valid.lst'
    # args.data_root = '/Users/zhge/Data'
    # args.num_files = 15
    # args.batch_size = 3

    source_name = os.path.basename(args.source_dir)
    if args.save_dir == None:
        args.save_dir = os.path.join('pretrained_models', source_name)

    source_dir = args.source_dir
    save_dir = args.save_dir
    tmp_dir = args.tmp_dir
    out_dir = args.out_dir
    filelist = args.filelist
    data_root = args.data_root
    num_files = args.num_files
    batch_size = args.batch_size

    print('ASR model source dir: {}'.format(source_dir))
    print('ASR model local dir: {}'.format(save_dir))
    print('Temp dir for saving resampled audio: {}'.format(tmp_dir))
    print('Output dir: {}'.format(out_dir))
    print('Audio file list: {}'.format(filelist))
    print('Data root dir: {}'.format(data_root))
    print('Num of audio files to be inferenced: {}'.format(num_files))
    print('Batch size: {}'.format(batch_size))

    # check or make dirs
    assert os.path.isdir(source_dir), 'source dir does not exist!'.format(source_dir)
    os.makedirs(save_dir, exist_ok=True)
    os.makedirs(tmp_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)

    # load ASR model
    if torch.cuda.is_available():
        print('using GPU ...')
        device = 'cuda'
    else:
        print('using CPU ...')
        device = 'cpu'
    asr_model = EncoderDecoderASR.from_hparams(source=source_dir, savedir=save_dir,
        run_opts={"device": device})
    print('loaded asr model: {} -> {}'.format(source_dir, save_dir))

    # read hyperparameters
    hparams_file = os.path.join(save_dir, 'hyperparams.yaml')
    assert os.path.isfile(hparams_file), 'file: {} does not exist!'.format(hparams_file)
    with open(hparams_file) as fin:
        hparams = load_hyperpyyaml(fin)
    sr = hparams['sample_rate']
    print('asr model was trained with data at {} sampling rate'.format(sr))

    # read selected audio files
    lines = open(filelist, 'r').readlines()
    if '.' not in lines[0]:
        lines = lines[1:]
    lines_sel = lines[:num_files]
    audiofiles_sel = [l.replace('$data_root', data_root).rstrip() for l in lines_sel]
    print('selected first {} audio files for inference'.format(num_files))

    # convert selected audio files
    json_dict = {}
    audiofiles_resampled = []
    for audiofile in audiofiles_sel:
        snt, fs = torchaudio.load(audiofile)
        dur = snt.shape[1]/fs
        uttid, ext = os.path.splitext(os.path.basename(audiofile))
        audiofile_resampled = os.path.join(tmp_dir, '{}_{}{}'.format(uttid, sr, ext))
        # convert/copy audio file from its source dir to the tmp dir
        if fs != sr:
            cmd = 'sox {} -r {} {}'.format(audiofile, sr, audiofile_resampled)
            output = run(cmd, shell=True, stdout=PIPE, stderr=PIPE).stdout
        else:
            if not os.path.isfile(audiofile_resampled):
                copyfile(audiofile, audiofile_resampled)
        audiofiles_resampled.append(audiofile_resampled)
        json_dict[uttid] = {'source': audiofile, 'resampled': audiofile_resampled,
                                'duration': dur}

    # # generate filelist for converted audio files
    # tmp_flist = [f.replace(tmp_dir, '$data_root') for f in audiofiles_resampled]
    # open('demo_100.lst', 'w').writelines('\n'.join(tmp_flist))

    # get the pairs of utterance ID and duration
    uttid_dur_pairs = [(k, json_dict[k]['duration']) for k in sorted(json_dict.keys())]
    uttid_dur_pairs_sorted = sorted(uttid_dur_pairs, key = lambda pair: pair[1], reverse=True)

    # decode in batch
    predicted_words_all = [[] for _ in range(num_files)]
    predicted_tokens_all = [[] for _ in range(num_files)]
    for i in range(0, num_files, batch_size):

        idx_end = min(num_files, i + batch_size)
        print('decoding file {} - {} (total {}) ...'.format(i, idx_end, num_files))

        # get audio files in a batch
        audio_files = [json_dict[uttid]['resampled'] \
                       for uttid, dur in uttid_dur_pairs_sorted[i:idx_end]]

        # batch decode
        predicted_words, predicted_tokens = batch_docode(audio_files)
        predicted_words_all[i:idx_end] = predicted_words
        predicted_tokens_all[i:idx_end] = predicted_tokens

    # collect predicted words and tokens in json dict (prepare to write out decoding results)
    for i in range(num_files):
        uttid = uttid_dur_pairs_sorted[i][0]
        json_dict[uttid]['predicted-words'] = predicted_words_all[i]
        json_dict[uttid]['predicted-tokens'] = predicted_tokens_all[i]

    # get the data to be writen out
    header = ['source', 'duration', 'predicted-words', 'predicted-tokens']
    lines = []
    for audiofile in audiofiles_sel:
        uttid, ext = os.path.splitext(os.path.basename(audiofile))
        line = [json_dict[uttid][c] for c in header]
        line[3] = ' '.join([str(e) for e in line[3]])
        lines.append(line)

    # write out decoding results
    dur_total = sum([json_dict[k]['duration'] for k in json_dict.keys()])
    output_csv = os.path.join(out_dir, '{}_{}files_{:.2f}secs.csv'.format(
        source_name, num_files, dur_total))
    write_csv(output_csv, lines, header)
