# scoring given decoding results and reference
#  - the audio files in the reference does not necessarily to match the files in
#    decoding results, but should include all the files in the decoding list
#  - hyp and ref files are matched by their unique utterance ID, so the whole file
#    path is not necessarily to be matched
#
# Zhenhao Ge, 2021-06-28

import os
import argparse
import torch
from speechbrain.pretrained import EncoderDecoderASR
import collections
from speechbrain.utils.edit_distance import accumulatable_wer_stats
from speechbrain.utils.edit_distance import wer_details_by_utterance

def read_hyp(hyp_list):
    # read hyp list into json dict with utterance IDs as keys
    lines = open(hyp_list, 'r').readlines()
    header = lines[0].rstrip().split(',')
    lines = lines[1:]
    json_dict = {}
    for line in lines:
        audiofile, dur, predicted_words, predicted_tokens = line.rstrip().split(',')
        uttid = os.path.splitext(os.path.basename(audiofile))[0]
        dur = float(dur)
        predicted_tokens = [int(e) for e in predicted_tokens.split()]
        json_dict[uttid] = {'source': audiofile, 'duration': dur,
                            'predicted-words': predicted_words, 'predicted-tokens': predicted_tokens}
    return json_dict

def read_ref(ref_list):
    # read ref list into json dict with utterance IDs as keys
    lines = open(ref_list, 'r').readlines()
    lines = lines[1:]
    json_dict = {}
    for line in lines:
        uttid, dur, audiofile, _, referenced_words = line.rstrip().split(',')
        json_dict[uttid] = {'source': audiofile, 'duration': float(dur),
                       'referenced-words': referenced_words}
    return json_dict

def parse_args():
    usage = 'usage: scoring to get WER'
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument('--source-dir', type=str,
                        help='asr source model dir')
    parser.add_argument('--save-dir', type=str, default=None,
                        help='asr local model dir')
    parser.add_argument('--out-dir', type=str, default='inference_output',
                        help='dir to save inference results')
    parser.add_argument('--hyp-list', type=str,
                        help='decoding result csv file')
    parser.add_argument('--ref-list', type=str,
                        help='file list with reference transcription')
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
    # args.out_dir = 'inference_output'
    # args.hyp_list = 'inference_output/cv8.0_with_ots_fr_seq2seq_ctc_attention_now2v_nosmooth_sb_15files_72.25secs.csv'
    # args.ref_list = '../filelists/cv_with_ots/valid.csv'
    # args.batch_size = 3

    source_name = os.path.basename(args.source_dir)
    if args.save_dir == None:
        args.save_dir = os.path.join('pretrained_models', source_name)

    source_dir = args.source_dir
    save_dir = args.save_dir
    out_dir = args.out_dir
    hyp_list = args.hyp_list
    ref_list = args.ref_list
    batch_size = args.batch_size

    print('ASR model source dir: {}'.format(source_dir))
    print('ASR model local dir: {}'.format(save_dir))
    print('Output dir: {}'.format(out_dir))
    print('Hypothesis list file: {}'.format(hyp_list))
    print('Reference list file: {}'.format(ref_list))
    print('Batch size: {}'.format(batch_size))

    # check or make dirs
    assert os.path.isdir(source_dir), 'source dir does not exist!'.format(source_dir)
    os.makedirs(save_dir, exist_ok=True)
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

    # read predicted words and tokens from hyp list
    json_dict_hyp = read_hyp(hyp_list)

    # read reference words from ref list
    json_dict_ref = read_ref(ref_list)

    # # debugging: get the duration from hyp and ref lists
    # tuple_list = []
    # for uttid in json_dict_hyp.keys():
    #     dur_hyp = json_dict_hyp[uttid]['duration']
    #     dur_ref = json_dict_ref[uttid]['duration']
    #     tuple_list.append((uttid, dur_hyp, dur_ref))

    # get details by utterance
    ref_dict, hyp_dict = {}, {}
    for uttid in json_dict_hyp.keys():
        hyp_dict[uttid] = json_dict_hyp[uttid]['predicted-tokens']
        referenced_words = json_dict_ref[uttid]['referenced-words']
        ref_dict[uttid] = asr_model.tokenizer.encode_as_ids(referenced_words)
    details_by_utterance = wer_details_by_utterance(ref_dict, hyp_dict)
    detail_dict = {}
    for d in details_by_utterance:
        detail_dict[d['key']] = {'num_edits': d['num_edits'], 'num_ref_tokens': d['num_ref_tokens'],
                                 'WER': d['WER'], 'insertions': d['insertions'],
                                 'deletions': d['deletions'], 'substitutions': d['substitutions']}

    # compute WER
    uttids = sorted(json_dict_hyp.keys())
    num_files = len(uttids)
    stats = collections.Counter()
    for i in range(0,num_files, batch_size):
        idx_end = min(num_files, i + batch_size)
        uttids_batch = uttids[i:idx_end]
        refs = [ref_dict[uttid] for uttid in uttids_batch]
        hyps = [hyp_dict[uttid] for uttid in uttids_batch]
        stats = accumulatable_wer_stats(refs, hyps, stats)
    print("%WER {WER:.2f}, {num_ref_tokens} ref tokens".format(**stats))
