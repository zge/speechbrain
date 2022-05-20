"""
Get data from filelist, e.g. get testing data only from the test filelist

Zhenhao Ge, 2022-05-19
"""

import os
from shutil import copyfile

# os.chdir('/Users/zhge/PycharmProjects/speechbrain/tools')
dir_current = os.getcwd()

def replace_path(filelist_file, path1, path2):
    lines = open(filelist_file, 'r').readlines()
    lines2 = [line.replace(path1, path2) for line in lines]
    return lines2

# specify filelist
filelist = '../templates/speech_recognition/filelists/cv_with_ots/test.csv'
assert os.path.exists(filelist), 'filelist {} does not exist!'.format(filelist)

# set path replacement pair
path1 = '$data_root'
path2 = os.path.abspath(os.path.join(dir_current, os.path.pardir,
        'templates', 'speech_recognition', 'data'))
assert os.path.isdir(path2), 'path {} does not exist!'.format(path2)

# setup output dir
dir_output = path2.replace('/data', '/data-test')
os.makedirs(dir_output, exist_ok=True)

# get lines from filelist
lines = replace_path(filelist, path1, path2)
header = lines[0].rstrip().split(',')
lines = lines[1:]  # remove the header
nlines = len(lines)
print('#files in {}: {}'.format(filelist, nlines))

# copy data in the filelist
itvl = 1000
for i, line in enumerate(lines):
    if i % itvl == 0:
        print('copying files: {} ~ {} (total {}) ...'.format(
            i, min(i+itvl, nlines), nlines))
    filename = line.split(',')[2]
    dirname = os.path.dirname(filename)
    dirname2 = dirname.replace(path2, dir_output)
    filename2 = filename.replace(path2, dir_output)
    os.makedirs(dirname2, exist_ok=True)
    copyfile(filename, filename2)

# copy filelist over for backup
filelist_copy = os.path.join(dir_output, os.path.basename(filelist))
copyfile(filelist, filelist_copy)
print('copy file: {} -> {}'.format(filelist, filelist_copy))