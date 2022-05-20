"""
Combine CV and OTS data to form new file lists

Zhenhao Ge, 2022-03-11
"""

import os
import random

# os.chdir('/Users/zhge/PycharmProjects/speechbrain/tools')

def replace_path(filelist_file, path1, path2):
    lines = open(filelist_file, 'r').readlines()
    lines2 = [line.replace(path1, path2) for line in lines]
    return lines2

def combine_filelist_files(infiles, outfile, seed=1234):

    filelist_cv, filelist_ots1, filelist_ots2, filelist_ots3 = infiles

    path1 = 'data/'
    path2 = '$data_root/'
    lines_cv = replace_path(filelist_cv, path1, path2)
    header = lines_cv[0].rstrip().split(',')
    lines_cv = lines_cv[1:] # remove the header
    print('#files in {}: {}'.format(filelist_cv, len(lines_cv)))

    # get updated lines in ots1
    path1 = '$data_root/'
    path2 = '$data_root/ots_french/FRF_ASR001/Resampled/'
    lines_ots1 = replace_path(filelist_ots1, path1, path2)
    lines_ots1 = lines_ots1[1:] # remove the header
    print('#files in {}: {}'.format(filelist_ots1, len(lines_ots1)))

    # get updated lines in ots2
    path1 = '$data_root/'
    path2 = '$data_root/ots_french/FRF_ASR002/Resampled/'
    lines_ots2 = replace_path(filelist_ots2, path1, path2)
    lines_ots2 = lines_ots2[1:]  # remove the header
    print('#files in {}: {}'.format(filelist_ots2, len(lines_ots2)))

    # get updated lines in ots3
    path1 = '$data_root/'
    path2 = '$data_root/ots_french/FRF_ASR003/wav/'
    lines_ots3 = replace_path(filelist_ots3, path1, path2)
    lines_ots3 = lines_ots3[1:]
    print('#files in {}: {}'.format(filelist_ots3, len(lines_ots3)))

    # combined lines from multiple files randomly
    lines_combined = lines_cv + lines_ots1 + lines_ots2 + lines_ots3
    random.seed(seed)
    random.shuffle(lines_combined)
    print('#files in {}: {}'.format(outfile, len(lines_combined)))

    # write combined lines into output file
    lines_combined = [','.join(header) + '\n'] + lines_combined
    open(outfile, 'w').writelines(lines_combined)


# set the file list dirs
root_dir = '../templates/speech_recognition/filelists/'
filelist_dir_cv = os.path.join(root_dir, 'CommonVoice/cv-corpus-8.0-2022-01-19')
filelist_dir_ots1 = os.path.join(root_dir, 'ots_french/frf_asr001')
filelist_dir_ots2 = os.path.join(root_dir, 'ots_french/frf_asr002')
filelist_dir_ots3 = os.path.join(root_dir, 'ots_french/frf_asr003')

# make dir for the combined file lists
filelist_dir_combined = os.path.join(root_dir, 'cv_with_ots')
os.makedirs(filelist_dir_combined, exist_ok=True)

### prepare the combined training file list ###

# set the input file lists for training
filelist_train_cv = os.path.join(filelist_dir_cv, 'train.csv')
filelist_train_ots1 = os.path.join(filelist_dir_ots1, 'train.csv')
filelist_train_ots2 = os.path.join(filelist_dir_ots2, 'train.csv')
filelist_train_ots3 = os.path.join(filelist_dir_ots3, 'train.csv')

# set the output combined file list for training
filelist_train = os.path.join(filelist_dir_combined, 'train.csv')

# combine file lists for training
combine_filelist_files([filelist_train_cv, filelist_train_ots1, filelist_train_ots2,
                        filelist_train_ots3], filelist_train, seed=1234)

### prepare the combined validation file list ###

# set the input file lists for validation
filelist_valid_cv = os.path.join(filelist_dir_cv, 'dev.csv')
filelist_valid_ots1 = os.path.join(filelist_dir_ots1, 'valid.csv')
filelist_valid_ots2 = os.path.join(filelist_dir_ots2, 'valid.csv')
filelist_valid_ots3 = os.path.join(filelist_dir_ots3, 'valid.csv')

# set the output combined file list for validation
filelist_valid = os.path.join(filelist_dir_combined, 'valid.csv')

# combine file lists for validation
combine_filelist_files([filelist_valid_cv, filelist_valid_ots1, filelist_valid_ots2,
                        filelist_valid_ots3], filelist_valid, seed=1234)

### prepare the combined test file list ###

# set the input file lists for testing
filelist_test_cv = os.path.join(filelist_dir_cv, 'test.csv')
filelist_test_ots1 = os.path.join(filelist_dir_ots1, 'test.csv')
filelist_test_ots2 = os.path.join(filelist_dir_ots2, 'test.csv')
filelist_test_ots3 = os.path.join(filelist_dir_ots3, 'test.csv')

# set the output combined file list for testing
filelist_test = os.path.join(filelist_dir_combined, 'test.csv')

# combine file lists for testing
combine_filelist_files([filelist_test_cv, filelist_test_ots1, filelist_test_ots2,
                        filelist_test_ots3], filelist_test, seed=1234)

# sanity check: find the alphabet size in the filelist
filelist_checks = [filelist_train_cv, filelist_train_ots1,
                   filelist_train_ots2, filelist_train_ots3]
for filelist_check in filelist_checks:
    lines = open(filelist_check, 'r').readlines()
    lines = lines[1:]
    texts = [line.rstrip().split(',')[-1] for line in lines]
    single_line = ' '.join(texts)
    letters = sorted(set(single_line.replace(' ', '')))
    # for i, letter in enumerate(letters):
    #     print('{}: {}'.format(i, letter))
    print('#letters in {}: {}'.format(filelist_check, len(letters)))
