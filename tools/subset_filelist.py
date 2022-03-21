# Randomly subset filelist to get a small one
#
# Zhenhao Ge, 2022-03-20

import os

root_dir = '../templates/speech_recognition/filelists/'
filelist_dir_combined = os.path.join(root_dir, 'cv_with_ots')
assert os.path.isdir(filelist_dir_combined), \
    "dir {} doesn't exist".format(filelist_dir_combined)

percent = 0.01

cats = ['train', 'valid', 'test']
for cat in cats:
    filelist = os.path.join(filelist_dir_combined, '{}.csv'.format(cat))
    lines = open(filelist, 'r').readlines()
    nfiles = len(lines) - 1
    nfiles_sel = int(nfiles * percent)
    filelist_sel = os.path.join(filelist_dir_combined, '{}_tiny.csv'.format(cat))
    open(filelist_sel, 'w').writelines(lines[:nfiles_sel+1])
