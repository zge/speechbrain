import os

# Download + Unpacking test-clean of librispeech
import shutil
from speechbrain.utils.data_utils import download_file

# MINILIBRI_TEST_URL = "https://www.openslr.org/resources/12/test-clean.tar.gz"
# download_file(MINILIBRI_TEST_URL, 'content/test-clean.tar.gz')
# shutil.unpack_archive( 'content/test-clean.tar.gz', 'content/')

from speechbrain.pretrained import EncoderDecoderASR

# Uncomment for using another pre-trained model
asr_model = EncoderDecoderASR.from_hparams(
    source="speechbrain/asr-crdnn-rnnlm-librispeech",
    savedir="pretrained_models/asr-crdnn-rnnlm-librispeech",
    run_opts={"device":"cpu"})
#asr_model = EncoderDecoderASR.from_hparams(source="speechbrain/asr-crdnn-transformerlm-librispeech", savedir="pretrained_models/asr-crdnn-transformerlm-librispeech",  run_opts={"device":"cuda"})
# asr_model = EncoderDecoderASR.from_hparams(source="speechbrain/asr-transformer-transformerlm-librispeech", savedir="pretrained_models/asr-transformer-transformerlm-librispeech",  run_opts={"device":"cuda"})

import torch
import torchaudio

# load the first sentence
audio_1 = os.path.join(os.getcwd(),
     "content/LibriSpeech/test-clean/1089/134686/1089-134686-0030.flac")
assert os.path.isfile(audio_1), '{} does not exist!'.format(audio_1)

# decode the first sentence
asr_model.transcribe_file(audio_1)

# decode the first sentence as a batch with single sentence
snt_1, fs = torchaudio.load(audio_1)
wav_lens = torch.tensor([1.0])
asr_model.transcribe_batch(snt_1, wav_lens)

# load the second sentence
audio_2 = os.path.join(os.getcwd(),
    "content/LibriSpeech/test-clean/1089/134686/1089-134686-0007.flac")
assert os.path.isfile(audio_2), '{} does not exist!'.format(audio_2)

# decode the second sentence as a batch with single sentence
snt_2, fs = torchaudio.load(audio_2)
wav_lens=torch.tensor([1.0])
asr_model.transcribe_batch(snt_2, wav_lens)

# decode both sentence through padding
from torch.nn.utils.rnn import pad_sequence
batch = pad_sequence([snt_1.squeeze(), snt_2.squeeze()], batch_first=True, padding_value=0.0)
wav_lens = torch.tensor([snt_1.shape[1]/batch.shape[1], snt_2.shape[1]/batch.shape[1]])
asr_model.transcribe_batch(batch, wav_lens)

# set up a batch of 8 sentences
audio_files=[]
audio_files.append('content/LibriSpeech/test-clean/1089/134686/1089-134686-0030.flac')
audio_files.append('content/LibriSpeech/test-clean/1089/134686/1089-134686-0014.flac')
audio_files.append('content/LibriSpeech/test-clean/1089/134686/1089-134686-0007.flac')
audio_files.append('content/LibriSpeech/test-clean/1089/134691/1089-134691-0000.flac')
audio_files.append('content/LibriSpeech/test-clean/1089/134691/1089-134691-0003.flac')
audio_files.append('content/LibriSpeech/test-clean/1188/133604/1188-133604-0030.flac')
audio_files.append('content/LibriSpeech/test-clean/1089/134691/1089-134691-0019.flac')
audio_files.append('content/LibriSpeech/test-clean/1188/133604/1188-133604-0006.flac')

sigs, lens = [], []
for audio_file in audio_files:
    snt, fs = torchaudio.load(audio_file)
    sigs.append(snt.squeeze())
    lens.append(snt.shape[1])

batch = pad_sequence(sigs, batch_first=True, padding_value=0.0)
lens = torch.Tensor(lens) / batch.shape[1]
predicted_words, predicted_tokens = asr_model.transcribe_batch(batch, lens)

asr_model.tokenizer.encode_as_ids("HELLO")

hyps = predicted_tokens
refs = asr_model.tokenizer.encode_as_ids(transcriptions)
batch = [refs, hyps]

import collections
batches = [[[[1,2,3],[4,5,6]], [[1,2,4],[5,6]]],
            [[[7,8], [9]],     [[7,8],  [10]]]]
stats = collections.Counter()
for batch in batches:
    refs, hyps = batch
    stats = accumulatable_wer_stats(refs, hyps, stats)
print("%WER {WER:.2f}, {num_ref_tokens} ref tokens".format(**stats))