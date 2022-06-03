# Subset file list based on the letters
#
# The sub file lists filtered by letters are useful to
# check the utterances with that letters
#
# Some conclusions are drawn by observing the sub file list
#  - remove utterances with * (mispronunced words)
#  - replace ('_', ''', and '-') with ' ' (space)
#  - accented symbols appended from regular letter, become accented letter
#
# Zhenhao Ge, 2022-02-15

import os, sys
import json
import glob

# os.chdir('/Users/zhge/PycharmProjects/speechbrain/tools')
sys.path.append(os.getcwd())
from utils import concat_csv, csv2dict, dict2tuple, tuple2csv

# # option 1 (OTS dataset)
# dataset = 'ots_french/frf_asr002' # 'ots_french/frf_asr001', 'ots_french/frf_asr002', 'ots_french/frf_asr003'
# filetype = 'csv'

# option 2 (CV dataset)
# dataset = 'CommonVoice/cv-corpus-6.1-2020-12-11'
dataset = 'CommonVoice/cv-corpus-8.0-2022-01-19'
filetype = 'csv'

# set file list
filelist_path = '../templates/speech_recognition/filelists/{}'.format(dataset)
assert os.path.isdir(filelist_path), '{} does not exist!'.format(filelist_path)
sublist_path = os.path.join(filelist_path, 'subset_by_letter')
os.makedirs(sublist_path, exist_ok=True)
filelist_file = os.path.join(filelist_path, 'all.{}'.format(filetype))

# get the overall file list (if exist previous version, overwrite it to ensure the consistency)
csvfiles = glob.glob(os.path.join(filelist_path, '*.{}'.format(filetype)))
csvfiles = [f for f in csvfiles if 'all' not in f]
concat_csv(csvfiles, filelist_file, have_header=True)

# load entries from file list
if filetype == 'json':
    with open(filelist_file, 'r') as f:
        json_dict = json.load(f)
    tuple_list, keys = dict2tuple(json_dict)
elif filetype == 'csv':
    dict_list = csv2dict(filelist_file)
    keys = list(dict_list[0].keys())
    tuple_list = [tuple(dct.values()) for dct in dict_list]
idx_word = len(keys) - 1 # index of the words are always the last index

# get letter lists
# letters = ["*", "_", "-"] # these letters have been removed or converted
if filetype == 'json':
    words = [json_dict[k]['words'] for k in json_dict.keys()]
elif filetype == 'csv':
    words = [dct['wrd'] for dct in dict_list]
words = [word.rstrip() for word in words]
text = ' '.join(words)
letters = sorted(set(text.replace(' ', '')))
nletters = len(letters)
print('#letters: {}'.format(nletters))

# write out sub tuple list containing the letters as csv files
for i, letter in enumerate(letters):
    tuple_list_sel = [entry for entry in tuple_list if letter in entry[idx_word]]
    # iso_code = ord(letter.encode('iso-8859-1'))
    utf8_code = letter.encode('utf-8')
    csvfile = os.path.basename(filelist_file).replace('.{}'.format(filetype), \
        '_{:02d}_{}_{}.csv'.format(i, utf8_code, len(tuple_list_sel)))
    csvpath = os.path.join(sublist_path, csvfile)
    print('[{}/{}] writing subset with letter {} ({}) to {} ...'.format(i+1, nletters,
        letter, utf8_code, csvpath))
    tuple2csv(tuple_list_sel, csvpath, colname=keys)

# find the sub word list containing the letters
for i, letter in enumerate(letters):
    texts = [entry[-1] for entry in tuple_list if letter in entry[idx_word]]
    text = ' '.join(texts)
    words = text.split()
    words = sorted(set([w for w in words if letter in w]))
    utf8_code = letter.encode('utf-8')
    txtfile = os.path.basename(filelist_file).replace('.{}'.format(filetype), \
        '_{:02d}_{}_{}.txt'.format(i, utf8_code, len(words)))
    txtpath = os.path.join(sublist_path, txtfile)
    print('[{}/{}] writing word list with letter {} ({}) to {} ...'.format(i+1, nletters,
        letter, utf8_code, txtpath))
    open(txtpath, 'w').writelines('\n'.join(words))