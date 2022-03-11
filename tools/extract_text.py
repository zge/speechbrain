"""
Extract texts from filelist files
The format of filelist can be either json or csv

Zhenhao Ge, 2022-01-26
"""


import os

# example 1
dataset = 'frf_asr003'
cats = ['train', 'valid', 'test']
flist_dir = os.path.join('../templates/speech_recognition/filelists/ots_french', dataset)
text_dir = os.path.join('../templates/speech_recognition/LM/data', dataset)
filetype = 'csv' # 'json' or 'csv'

# # example 2
# cats = ['train', 'dev', 'test']
# # flist_dir = '../templates/speech_recognition/filelists/CommonVoice/cv-corpus-6.1-2020-12-11'
# # text_dir = '../templates/speech_recognition/LM/data/cv-corpus-6.1-2020-12-11'
# flist_dir = '../templates/speech_recognition/filelists/CommonVoice/cv-corpus-8.0-2022-01-19'
# text_dir = '../templates/speech_recognition/LM/data/cv-corpus-8.0-2022-01-19'
# os.makedirs(text_dir, exist_ok=True)
# filetype = 'csv'

def convert_symbol(text, l1, l2, quote='"'):
  """convert symbol l1 to l2 if inside quote"""
  text2 = ''
  inside = False
  for c in text:
    if c == quote:
      inside = not inside
    elif c == l1:
      if inside:
        text2 += l2
      else:
        text2 += l1
    else:
       text2 += c
  return text2

def csv2dict(csvname, delimiter=',', encoding='utf-8'):
  """extract rows in csv file to a dictionary list"""
  lines = open(csvname, 'r', encoding=encoding).readlines()
  header = lines[0].rstrip().split(delimiter)
  lines = lines[1:]
  nlines = len(lines)

  dict_list = [{} for _ in range(nlines)]
  for i, line in enumerate(lines):
    line2 = convert_symbol(line.rstrip(), delimiter, '|')
    items = line2.split(delimiter)
    items = [s.replace('|', delimiter) for s in items]
    dict_list[i] = {k:items[j] for j,k in enumerate(header)}

  return dict_list

def read_text(annotation_file, filetype):

    if filetype == 'json':

        import json
        # read text from json file
        with open(annotation_file, 'r') as f:
            json_dict = json.load(f)
        lines = [json_dict[key]['words'] for key in json_dict.keys()]

    elif filetype == 'csv':

        import csv
        # read text from csv file
        dict_list = csv2dict(annotation_file)
        lines = [d['wrd'] for d in dict_list]

    return lines

# write out 3 files
for cat in cats:
    flistfile = os.path.join(flist_dir, '{}.{}'.format(cat,filetype))
    assert os.path.isfile(flistfile), 'filelist file {} does not exist!'.format(flistfile)
    lines = read_text(flistfile, filetype)
    textfile = os.path.join(text_dir, '{}.txt'.format(cat))
    textdir = os.path.dirname(textfile)
    os.makedirs(textdir, exist_ok=True)
    open(textfile, 'w').writelines('\n'.join(lines))
    print('wrote to {}'.format(textfile))

# concatenate 3 files together
infiles = [os.path.join(text_dir, '{}.txt'.format(cat)) for cat in cats]
outfile = os.path.join(text_dir, 'all.txt')
with open(outfile, 'w') as outf:
    for infile in infiles:
        with open(infile, 'r') as inf:
            outf.write(inf.read())
print('wrote to {}'.format(outfile))

# sanity check: find the alphabet size in outfile
lines = open(outfile, 'r').readlines()
single_line = ' '.join([line.rstrip() for line in lines])
letters = sorted(set(single_line.replace(' ', '')))
for i, letter in enumerate(letters):
    print('{}: {}'.format(i, letter))
assert len(letters) == 39, "# of letters should be 39!"
