#!/bin/bash
#
# run inference_batch.py with input arguments
#
# Zhenhao Ge, 2022-06-29

RESULT_DIR="../../../recipes/CommonVoice/results"
EC2="speech_dev_dl_pytorch2"
MODEL_NAME="cv8.0_with_ots_fr_seq2seq_ctc_attention_now2v_nosmooth_sb"

source_dir=${RESULT_DIR}/${EC2}/${MODEL_NAME}
filelist="../filelists/demo/demo_100.lst"
data_root="tmp_dir"
num_files=15
batch_size=3

python inference_batch.py \
    --source-dir ${source_dir} \
    --filelist ${filelist} \
    --data-root ${data_root} \
    --num-files ${num_files} \
    --batch-size ${batch_size}
