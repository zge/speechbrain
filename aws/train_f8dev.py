import sys
import os
sys.path.append(os.getcwd())

from sagemaker.estimator import Estimator
from aws_handler import get_exec_role

instance_type = 'ml.g4dn.xlarge'

# AWS F8Dev
ecr_image = '462738068089.dkr.ecr.us-east-1.amazonaws.com/sb-asr-fr-test'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

training_subnets_1 = "subnet-0d823e23d10e049ae" # zge-subnet-private1-us-east-1a
training_subnets_2 = "subnet-0c9f3fde2c427e33c" # zge-subnet-private2-us-east-1b
training_subnets_3 = "subnet-06a8729ff47e7f504" # zge-subnet-private3-us-east-1c

# # AWS F8
# ecr_image = '411719562396.dkr.ecr.us-east-1.amazonaws.com/sb-asr-fr-test:latest'
# os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
#
# training_subnets_1 = "subnet-e284d7c9" # us-east-1e subnet-vpc-sandbox-us-east-1e
# training_subnets_2 = "subnet-eea9a299" # us-east-1e subnet-vpc-sandbox-us-east-1a
# training_subnets_3 = "subnet-bcdbf6e5" # us-east-1b subnet-vpc-sandbox-us-east-1b
# training_sg_ids = "sg-808a42fb" # sandbox-ecs

# AWS Staging
# ecr_image = '220211432420.dkr.ecr.us-west-2.amazonaws.com/sb-asr-fr-test:latest' # staging
# os.environ['AWS_DEFAULT_REGION']  = 'us-west-2'

# training_subnets_1 = "subnet-a41fdbd3" # TiPrivAppSubnet1Stage
# training_subnets_2 = "subnet-c351f7a6" # TiPrivAppSubnet2Stage
# training_subnets_3 = "subnet-e4f13193" # TiPrivAppSubnet1
# training_subnets_4 = "subnet-2f69cb4a" # TiPrivAppSubnet2
# training_sg_ids = "sg-xxxxxxxx"

# def train(instance_type, ecr_image):
#     exec_role = get_exec_role()
#
#     estimator = Estimator(
#         role=exec_role,
#         train_instance_count=1,
#         train_instance_type=instance_type,
#         image_uri=ecr_image,
#         subnets=[training_subnets_1, training_subnets_2, training_subnets_3],
#         security_group_ids=[training_sg_ids]
#     )
#     estimator.fit()

def train(instance_type, ecr_image):
    exec_role = get_exec_role()

    estimator = Estimator(
        role=exec_role,
        train_instance_count=1,
        train_instance_type=instance_type,
        image_uri=ecr_image,
        subnets=[training_subnets_1, training_subnets_2, training_subnets_3],
        checkpoint_s3_uri="s3://zge-exp/results/",
        checkpoint_local_path="/opt/speechbrain/recipes/CommonVoice/results/",
    )
    estimator.fit()

# sagemaker_session = sagemaker.Session()
# role = sagemaker.get_execution_role()

train(instance_type, ecr_image)
