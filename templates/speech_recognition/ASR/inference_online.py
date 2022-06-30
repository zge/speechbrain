# Inference samples with trained model
#
# Zhenhao Ge, 2022-02-01

import os
import torch
import torchaudio
from subprocess import PIPE, run

# os.chdir('templates/speech_recognition/ASR')

# specify model path
# # option 1: model hosted on Huggingface
# # (path is interpreted as a Huggingface model ID when the path is not exist)
# asr_model_source = "speechbrain/asr-crdnn-commonvoice-fr"
# # option 2: model downloaded from Huggingface
# asr_model_source = "../../../pretrained_models/asr-crdnn-commonvoice-fr"
# option 3: model locally trained
asr_model_source = os.path.join('../../../recipes/CommonVoice/results',
    'speech_dev_dl_pytorch2', 'cv8.0_fr_seq2seq_ctc_attention_now2v_nosmooth_sb_16k')

# save model locally
# asr_model_savedir = "pretrained_models/asr-crdnn-commonvoice-fr"
asr_model_savedir = "pretrained_models/cv8.0_fr_seq2seq_ctc_attention_now2v_nosmooth_sb_16k"
os.makedirs(asr_model_savedir, exist_ok=True)

from speechbrain.pretrained import EncoderDecoderASR

if torch.cuda.is_available():
    print('using GPU ...')
    device = 'cuda'
else:
    print('using CPU ...')
    device = 'cpu'

# load model
asr_model = EncoderDecoderASR.from_hparams(
    source=asr_model_source,
    savedir=asr_model_savedir,
    run_opts={"device":device})

sr = 16000
data_output = 'inference_output'
os.makedirs(data_output, exist_ok=True)

# specify audiofile
# example:
#  - audiofile: 'fr/clips/common_voice_fr_19645489.mp3'
#  - hyp: "IL TÂCHA D'ATTRIBUER DES LOGEMENTS AUX SANS ABRIS AYANT PERDU LEUR HABITATION DANS LES BOMBESEMENTS"
dataset = '../data/CommonVoice/cv-corpus-6.1-2020-12-11'
audiofile = os.path.join(dataset, 'fr/clips/common_voice_fr_19645489.mp3')
assert os.path.isfile(audiofile), '{} does not exist!'.format(audiofile)

snt, fs = torchaudio.load(audiofile)
if fs != sr:
    audioname, ext = os.path.splitext(os.path.basename(audiofile))
    audiofile_resampled = os.path.join(data_output, '{}_{}{}'.format(audioname, sr, ext))
    cmd = 'sox {} -r {} {}'.format(audiofile, sr, audiofile_resampled)
    output = run(cmd, shell=True, stdout=PIPE, stderr=PIPE).stdout
    snt, fs = torchaudio.load(audiofile_resampled)
else:
    audiofile_resampled = audiofile

# via transcribe_batch (get both predicted words and tokens)
wav_lens = torch.tensor([1.0])
predicted_words, predicted_tokens = asr_model.transcribe_batch(snt, wav_lens)

# via transcribe_file (get predicted words only)
predicted_words = asr_model.transcribe_file(audiofile_resampled)
