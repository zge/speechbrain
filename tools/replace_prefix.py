"""
Replace the prefix in the filelist

e.g. replace '/gpfsscratch/rech/kxg/uyk21ll/cv-corpus-6.1-2020-12-11/fr//clips'
to 'data/CommonVoice/cv-corpus-6.1-2020-12-11/fr/clips'


Zhenhao Ge, 2022-05-25
"""

import os

# os.chdir('/Users/zhge/PycharmProjects/speechbrain/tools')

dataset = 'cv-corpus-6.1-2020-12-11'
str1 = '/gpfsscratch/rech/kxg/uyk21ll/cv-corpus-6.1-2020-12-11/fr//clips'
str2 = 'data/CommonVoice/cv-corpus-6.1-2020-12-11/fr/clips'

# setup directories
dir_current = os.getcwd()
dir_filelist = os.path.abspath(os.path.join(dir_current, os.path.pardir,
    'recipes', 'CommonVoice', 'exp', 'CommonVoice', dataset))
assert os.path.isdir(dir_filelist), 'dir {} does not exist!'.format(dir_filelist)

filename = 'train_sb.csv' # '{train, dev, test}_sb.csv'
file_input = os.path.join(dir_filelist, filename)
basename, ext = os.path.splitext(filename)
assert os.path.isfile(file_input), 'file {} does not exist!'.format(file_input)
file_output = os.path.join(dir_filelist, '{}_new{}'.format(basename, ext))

lines = open(file_input, 'r').readlines()
print('{} -> {}: {} -> {}'.format(os.path.basename(file_input),
                                  os.path.basename(file_output), str1, str2))
lines_new = []
for line in lines:
    if str1 in line:
        line_new  = line.replace(str1, str2)
    else:
        line_new = line
    lines_new.append(line_new)
print('writing {} ...'.format(file_output))
open(file_output, 'w').writelines(lines_new)
