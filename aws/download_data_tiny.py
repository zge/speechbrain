import os, sys
import boto3
import time
from datetime import timedelta

bucket = sys.argv[1] # e.g. zge-exp (aws:f8dev)
folder_s3 = sys.argv[2] # e.g. 'data/tiny'
folder_local = sys.argv[3] # /opt/data (docker), '/data6/zge-speechbrain/data'

# # example
# bucket = 'zge-exp'
# folder_s3 = 'data/tiny'
# folder_local = '/home/sagemaker-user/data'

print('{} --> {}'.format(os.path.join(bucket, folder_s3), folder_local))

if not os.path.exists(folder_local):
    print('creating dir: {}'.format(folder_local))
    os.makedirs(folder_local)

def download_folder(bucket, folder_s3, folder_local):
    s3 = boto3.resource('s3')
    start_time = time.monotonic()
    for obj in s3.Bucket(bucket).objects.filter(Prefix=folder_s3):
        infile = obj.key
        pardir = os.path.join(folder_local, os.path.dirname(infile))
        filename = os.path.basename(infile)
        if not os.path.exists(pardir):
            os.makedirs(pardir, exist_ok=True)
            print('dir: {} created'.format(pardir))
        outfile = os.path.join(pardir, filename)
        if os.path.exists(outfile):
            print('skip {} --> {} ...'.format(infile, outfile))
        else:
            s3.Bucket(bucket).download_file(infile, outfile)
            print('{} --> {} ...'.format(infile, outfile))
    end_time = time.monotonic()
    duration = end_time - start_time
    print('data downloading time: {}'.format(timedelta(seconds=duration)))

if __name__ == '__main__':
    download_folder(bucket, folder_s3, folder_local)