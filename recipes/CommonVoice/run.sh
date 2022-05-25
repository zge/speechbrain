#/bin/bash
#
# run training

#if aws s3api wait bucket-exists --bucket "zge-exp/" ; then
#  echo "bucket zge-exp exist"
#fi

# download data from s3 bucket
python ../../aws/download_data_tiny.py zge-exp data/tiny /opt

# run the training
CUSA_VISIBLE_DEVICES=0,1 python ASR/seq2seq/train_exp_cv_with_ots.py ASR/seq2seq/hparams/train_fr_exp_cv_with_ots_bs2.yml --batch_size=2 --data_parallel_backend
