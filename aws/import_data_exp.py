# Experiment data import with S3
#
# Zhenhao Ge, 2022-08-12

import os
import torchaudio
import boto3
import botocore

# check the torch and torchaudio version
print('torch version: {}'.format(torch.__version__))
print('torchaudio version: {}'.format(torchaudio.__version__))

def is_file_exist_s3(bucket_name, file_path_s3):
    # check if file exist in S3
    s3_resource = boto3.resource('s3')

    try: 
        s3_resource.Object(bucket_name, file_path_s3).load()
    except botocore.exception.ClientError as e:
        flag = False
        if e.response['Error']['Code'] == '404':
            print('file {} does NOT exist in S3 bucket {}.'.format(file_path_s3, bucket_name))
        else:
            print('something else has gone wrong.')
    else:
        print('file {} exists in S3 bucket {}'.format(file_path_s3, bucket_name))
        flag = True
    return flag    
    

# specify the bucket name
bucket_name = 'zge-exp'

# specify the S3 file path to the file to be downloaded
file_path_s3 = 'data/cv-corpus-8.0-2022-01-19/fr/clips/common_voice_fr_27042964.mp3'


# check if file exist in S3
flag = is_file_exist_s3(bucket_name, file_path_s3)

# specify the local file path
local_dir = 'tmp'
os.makedirs(local_dir, exist_ok=True)
file_name = 'test.mp3'
file_path_local = os.path.join(local_dir, file_name)

# setup s3 client
s3_client = boto3.client('s3')

# download file using s3 client
s3_client.download_file(bucket_name, file_path, local_file_path)

# load audio file from S3 (without downloading)
response = s3_client.get_object(Bucket=bucket_name, Key=file_path_s3)
waveform, sample_rate = torchaudio.load(response['Body'])
print('waveform shape: {}'.format(waveform.shape))
print('sampling rate: {}'.format(sample_rate))

file_path_bucket = 's3://{}'.format(os.path.join(bucket_name, file_path_s3))
print('s3 bucket path: {}'.format(file_path_bucket))