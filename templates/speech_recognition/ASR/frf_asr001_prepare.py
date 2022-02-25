"""
Prepare manifest files for speech recognition with OTS FRF_ASR001 dataset.

Author:
  * Zhenhao Ge, 2022-01-24
"""

import os
import json
import csv
import logging
import random
from pathlib import Path
from speechbrain.utils.data_utils import get_all_files
from speechbrain.dataio.dataio import read_audio

logger = logging.getLogger(__name__)
SAMPLERATE = 8000
SEED = 1234
RATIO = '8:1:1'


def prepare_frf_asr001(
    data_folder, ext, save_train, save_valid, save_test):

    wav_list = sorted(get_all_files(data_folder, match_and=[".wav"]))
    trans_list = sorted(get_all_files(data_folder, match_and=[".txt"]))
    trans_list = [f for f in trans_list if '_orig' not in f]
    assert len(wav_list) == len(trans_list), "audio and text does not match!"

    # randomize wav list
    random.seed(SEED)
    random.shuffle(wav_list)

    # get percentage from ratio
    ratio = [int(r) for r in RATIO.split(':')]
    percent = {}
    percent['train'] = float(ratio[0]) / sum(ratio)
    percent['valid'] = float(ratio[1]) / sum(ratio)
    percent['test'] = float(ratio[2]) / sum(ratio)

    # get the split wav lists
    nwavs = len(wav_list)
    wav_list_train = sorted(wav_list[:int(nwavs*percent['train'])])
    wav_list_valid = sorted(wav_list[int(nwavs*percent['train']):int(nwavs*(percent['train']+percent['valid']))])
    wav_list_test = sorted(wav_list[int(nwavs*(percent['train']+percent['valid'])):])


    if ext == 'json':

        # create the json files 3 datasets
        create_json(wav_list_train, save_train)
        create_json(wav_list_valid, save_valid)
        create_json(wav_list_test, save_test)

        # create the json file for all datasets together
        save_all = save_train.replace('train', 'all')
        create_json(sorted(wav_list), save_all)

    elif ext == 'csv':

        # create the csv files for 3 datasets
        create_csv(wav_list_train, save_train)
        create_csv(wav_list_valid, save_valid)
        create_csv(wav_list_test, save_test)

        # create the csv file for all datasets together
        save_all = save_train.replace('train', 'all')
        create_csv(sorted(wav_list), save_all)


def create_json(wav_list, json_file):

    json_dict = {}
    for wav_file in wav_list:

        # Reading the signal (to retrieve duration in seconds)
        signal = read_audio(wav_file)
        duration = signal.shape[0] / SAMPLERATE

        # Reading the transcription
        trans_file = wav_file.replace(".wav", ".txt")
        assert os.path.isfile(trans_file), "{} not exist".format(trans_file)
        trans = open(trans_file).readlines()[0]

        # Manipulate path to get relative path and uttid
        path_parts = wav_file.split(os.path.sep)
        uttid, _ = os.path.splitext(path_parts[-1])
        relative_path = os.path.join("{data_root}", *path_parts[-2:])

        # Create entry for this utterance
        json_dict[uttid] = {
            "wav": relative_path,
            "length": duration,
            "words": trans,
        }

    # Writing the dictionary to the json file
    with open(json_file, mode="w") as json_f:
        json.dump(json_dict, json_f, ensure_ascii=False, indent=2)

    logger.info(f"{json_file} successfully created!")

def create_csv(wav_list, csv_file):

    header = ['ID', 'duration', 'wav', 'spk_id', 'wrd']

    tuple_list = []
    for wav_file in wav_list:

        # Reading the signal (to retrieve duration in seconds)
        signal = read_audio(wav_file)
        duration = signal.shape[0] / SAMPLERATE

        # Reading the transcription
        trans_file = wav_file.replace(".wav", ".txt")
        assert os.path.isfile(trans_file), "{} not exist".format(trans_file)
        trans = open(trans_file).readlines()[0]

        # Manipulate path to get relative path and uttid
        path_parts = wav_file.split(os.path.sep)
        uttid, _ = os.path.splitext(path_parts[-1])
        spk_id = '_'.join(uttid.split('_')[:-1])
        relative_path = os.path.join("$data_root", *path_parts[-2:])

        # Create entry for this utterance
        tuple_list.append((uttid, str(duration), relative_path, spk_id, trans))

    # Writing the tuple list to the csv file
    with open(csv_file, 'w', newline='') as f:
        csv_out = csv.writer(f)
        csv_out.writerow(header)
        for i, tpl in enumerate(tuple_list):
            csv_out.writerow(list(tpl))

    logger.info(f"{csv_file} successfully created!")


if __name__ == '__main__':
    data_folder = '{}/data/ots_french/FRF_ASR001/Processed/'.format(Path.home())
    list_folder = '../filelists/ots_french/frf_asr001'
    ext = 'csv'
    save_train = os.path.join(list_folder, 'train.{}'.format(ext))
    save_valid = os.path.join(list_folder, 'valid.{}'.format(ext))
    save_test = os.path.join(list_folder, 'test.{}'.format(ext))
    prepare_frf_asr001(data_folder, ext, save_train, save_valid, save_test)
