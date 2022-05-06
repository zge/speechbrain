import os
import boto3
from pathlib import Path

# AWS-F8Dev
exec_role_name = 'AmazonSageMaker-ExecutionRole-20220429T104671'
source_profile = 'zge-f8dev'

# # AWS-F8
# exec_role_name = 'ml-trainable-container-sandbox'
# source_profile = 'zge-f8'

# # AWS-Staging
# exec_role_name = 'AmazonSageMaker-ExecutionRole-20200114T141144'
# source_profile = 'zge'

def get_credentials(source_profile):
    credential_file = os.path.join(Path.home(), '.aws', 'credentials')
    lines = open(credential_file, 'r').readlines()
    idx1, idx2 = 0, len(lines)-1
    for i, line in enumerate(lines):
        if line.rstrip()[1:-1] == source_profile:
            idx1 = i + 1
        if idx1 > 0:
            if i == idx2:
                idx2 += 1
            elif line.rstrip() == '':
                idx2 = i
    lines_sel = lines[idx1:idx2]
    credentials = {}
    for line in lines_sel:
        idx = line.find('=')
        key = line[:idx]
        value = line[idx+1:].rstrip().strip('"')
        credentials[key] = value
    return credentials

credentials = get_credentials(source_profile)


# zge-f8 credentials
os.environ['AWS_ACCESS_KEY_ID'] = credentials['aws_access_key_id']
os.environ['AWS_SECRET_ACCESS_KEY'] = credentials['aws_secret_access_key']
os.environ['AWS_SESSION_TOKEN'] = credentials['aws_session_token']

def get_exec_role():
    session = boto3.Session(region_name='us-east-1',
                            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                            aws_session_token=os.environ['AWS_SESSION_TOKEN'])
    credentials = session.get_credentials()
    iam = boto3.client('iam', aws_access_key_id=credentials.access_key,
                       aws_secret_access_key=credentials.secret_key,
                       aws_session_token=credentials.token)
    exec_role = iam.get_role(RoleName=exec_role_name)['Role']['Arn']
    return exec_role