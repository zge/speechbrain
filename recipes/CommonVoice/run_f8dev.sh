#/bin/bash
#
# run training

#if aws s3api wait bucket-exists --bucket "zge-exp/" ; then
#  echo "bucket zge-exp exist"
#fi

# download data from s3 bucket
if [ -d data/CommonVoice ] && [ -d data/ots_french ]; then
    echo "data pre-included"
else
    echo "downloading data ..."
    python ../../aws/download_data_tiny.py zge-exp data/tiny /opt

# run the training
python ASR/seq2seq/train_exp_cv_with_ots.py \
    ASR/seq2seq/hparams/train_fr_exp_cv_with_ots_bs2.yml \
    --batch_size=2 --data_parallel_backend


# run the training with CPU (just for test, it will be very slow)
python ASR/seq2seq/train_exp_cv_with_ots.py \
    ASR/seq2seq/hparams/train_fr_exp_cv_with_ots_bs2.yml \
    --batch_size=2 --device='cpu'