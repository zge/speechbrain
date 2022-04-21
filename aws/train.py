import sys
import os
import logging
import json
sys.path.append(os.getcwd())

import sagemaker
from sagemaker.estimator import Estimator
from aws_handler import get_exec_role

training_subnets_1 = "subnet-e284d7c9"
training_subnets_2 = "subnet-eea9a299"
training_subnets_3 = "subnet-bcdbf6e5"
training_sg_ids = "sg-808a42fb"

instance_type = 'ml.g4dn.xlarge'

# AWS F8
ecr_image = '411719562396.dkr.ecr.us-east-1.amazonaws.com/sb-asr-fr-test:latest' # f8
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

# # AWS Staging
# ecr_image = '220211432420.dkr.ecr.us-west-2.amazonaws.com/sb-asr-fr-test:latest' # staging
# os.environ['AWS_DEFAULT_REGION']  = 'us-west-2'

def train(instance_type, ecr_image):
    exec_role = get_exec_role()

    estimator = Estimator(
        role=exec_role,
        train_instance_count=1,
        train_instance_type=instance_type,
        image_uri=ecr_image,
        subnets=[training_subnets_1, training_subnets_2, training_subnets_3],
        security_group_ids=[training_sg_ids]
    )
    estimator.fit()

# eval $(aws sts assume-role --role-arn arn:aws:iam::411719562396:role/ml-trainable-container-sandbox --role-session-name test | jq -r '.Credentials | "export AWS_ACCESS_KEY_ID=\(.AccessKeyId)\nexport AWS_SECRET_ACCESS_KEY=\(.SecretAccessKey)\nexport AWS_SESSION_TOKEN=\(.SessionToken)\n"')


# sagemaker_session = sagemaker.Session()
# role = sagemaker.get_execution_role()

train(instance_type, ecr_image)