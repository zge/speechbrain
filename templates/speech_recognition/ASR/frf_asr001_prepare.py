"""
Prepare manifest files for speech recognition with OTS FRF_ASR001 dataset.

Author:
  * Zhenhao Ge, 2022-01-24
"""

import os
import json
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
    data_folder, save_json_train, save_json_valid, save_json_test):

    wav_list = sorted(get_all_files(data_folder, match_and=[".wav"]))
    trans_list = sorted(get_all_files(data_folder, match_and=[".txt"]))
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

    # Create the json files
    create_json(wav_list_train, save_json_train)
    create_json(wav_list_valid, save_json_valid)
    create_json(wav_list_test, save_json_test)

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


if __name__ == '__main__':
    data_folder = '{}/data/ots_french/FRF_ASR001/Processed/'.format(Path.home())
    save_json_train, save_json_valid, save_json_test = 'train.json', 'valid.json', 'test.json'
    prepare_frf_asr001(data_folder, save_json_train, save_json_valid, save_json_test)
