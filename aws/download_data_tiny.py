import os, sys
import boto3

bucket = sys.argv[1] # e.g. zge-exp (aws:f8dev)
folder_s3 = sys.argv[2] # e.g. '/data/tiny'
folder_local = sys.argv[3] # /opt/data/ (docker), '/data6/zge-speechbrain/data/'

if not os.path.exists(folder_local):
    print('creating dir: {}'.format(folder_local))
    os.makedirs(folder_local)

print('{} --> {}'.format(os.path.join(bucket, folder_s3), folder_local))

def download_folder(bucket, folder_s3, folder_local):
    s3 = boto3.resource('s3')
    for obj in s3.Bucket(bucket).objects.filter(Prefix=folder_s3):
        infile = obj.key
        pardir = os.path.join(folder_local, os.path.dirname(infile))
        filename = os.path.basename(infile)
        if not os.path.exists(pardir):
            os.makedirs(pardir, exist_ok=True)
            print('dir: {} created'.format(pardir))
        outfile = os.path.join(pardir, filename)
        s3.Bucket(bucket).download_file(infile, outfile)
        # print('{} --> {} ...'.format(infile, outfile))

download_folder(bucket, folder_s3, folder_local)
