"""
Filter the combined filelist into CV- and OTS-only filelists

Zhenhao Ge, 2022-05-19
"""

import os

# os.chdir('/Users/zhge/PycharmProjects/speechbrain/tools')

def filter_filelist(filelist, dataset):
    lines2 = []
    lines = open(filelist, 'r').readlines()
    header = lines[0]
    lines = lines[1:]
    for line in lines:
        if dataset in line:
            lines2.append(line)
    lines2 = [header] + lines2
    path_wo_ext, ext = os.path.splitext(filelist)
    filelist_sel = '{}-{}{}'.format(path_wo_ext, dataset.lower(), ext)
    open(filelist_sel, 'w').writelines(lines2)
    print('wrote {} with {} files'.format(filelist_sel, len(lines2)-1))

# setup directories
dir_current = os.getcwd()
dir_output = os.path.abspath(os.path.join(dir_current, os.path.pardir,
        'templates', 'speech_recognition', 'data-test', 'filelists'))

# setup input file
filename = 'test.csv'
# filename = 'test_cv8.0_orig.csv'
filelist_input = os.path.join(dir_output, filename)

datasets = ['cv-corpus-8.0', 'FRF_ASR001', 'FRF_ASR002', 'FRF_ASR003']
for dataset in datasets:
    filter_filelist(filelist_input, dataset)


