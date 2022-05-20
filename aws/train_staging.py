import sys
import os
import logging
import json
sys.path.append(os.getcwd())

import sagemaker
from sagemaker.estimator import Estimator
from aws_handler_staging import get_exec_role

instance_type = 'ml.g4dn.xlarge'

# AWS Staging
ecr_image = '220211432420.dkr.ecr.us-west-2.amazonaws.com/sb-asr-fr-test:latest' # staging
os.environ['AWS_DEFAULT_REGION']  = 'us-west-2'

training_subnets_1 = "subnet-a41fdbd3" # TiPrivAppSubnet1Stage
training_subnets_2 = "subnet-c351f7a6" # TiPrivAppSubnet2Stage
training_subnets_3 = "subnet-e4f13193" # TiPrivAppSubnet1
training_subnets_4 = "subnet-2f69cb4a" # TiPrivAppSubnet2

def train(instance_type, ecr_image):
    exec_role = get_exec_role()

    estimator = Estimator(
        role=exec_role,
        train_instance_count=1,
        train_instance_type=instance_type,
        image_uri=ecr_image,
        subnets=[training_subnets_1, training_subnets_2, training_subnets_3],
    )
    estimator.fit()

# sagemaker_session = sagemaker.Session()
# role = sagemaker.get_execution_role()

train(instance_type, ecr_image)
