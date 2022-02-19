# Check the subwords in the tokenizer, so we know which letters can be the output
#
# Zhenhao Ge, 2022-02-18

import torch
import csv

def get_char_dict(characters):
    char_dict = {}
    for c in characters:
        if c not in char_dict.keys():
            char_dict[c] = 1
        else:
            char_dict[c] += 1
    return char_dict

def write_dict_count(csvfile, dct, delimiter=',',
                     header = ['binary', 'letter', 'count', 'percent'], verbose=True):
    total_cnt = sum(dct.values())
    with open(csvfile, 'w', newline='') as f:
        csv_out = csv.writer(f, delimiter=delimiter)
        csv_out.writerow(header)
        keys = sorted(dct.keys())
        for i, k in enumerate(keys):
            cnt = dct[k]/total_cnt
            cnt_str = '{:.2f}'.format(cnt*100)
            #iso_code = ord(k.encode('iso-8859-1'))
            # row = [iso_code, k, dct[k], cnt_str]
            utf8_code = k.encode('utf-8')
            row = [utf8_code, k, dct[k], cnt_str]
            csv_out.writerow(row)
    if verbose:
        print('{} saved!'.format(csvfile))

from speechbrain.pretrained import EncoderDecoderASR
if torch.cuda.is_available():
    print('using GPU ...')
    device = 'cuda'
else:
    print('using CPU ...')
    device = 'cpu'
asr_model = EncoderDecoderASR.from_hparams(
    source="speechbrain/asr-crdnn-commonvoice-fr",
    savedir="pretrained_models/asr-crdnn-commonvoice-fr",
    run_opts={"device":device})

vocab_size = asr_model.tokenizer.vocab_size()
tuple_list = []
for i in range(vocab_size):
    token = asr_model.tokenizer.decode_ids([i])
    tuple_list.append([i,token])

tokens = [entry[-1] for entry in tuple_list]
chars = ''.join(tokens)
letters = sorted(set(chars))

# show tokens with '''
[token for token in tokens if "'" in token]

char_dict = get_char_dict(chars)
char_count_file = 'token_char_crdnn.csv'
write_dict_count(char_count_file, char_dict, delimiter='\t')
print('wrote char dict to {}'.format(char_count_file))

