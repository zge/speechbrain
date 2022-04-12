#/bin/bash
#
# run training

CUSA_VISIBLE_DEVICES=0,1 python ASR/seq2seq/train_exp_cv_with_ots.py ASR/seq2seq/hparams/train_fr_exp_cv_with_ots_bs2.yml --batch_size=2 --data_parallel_backend
