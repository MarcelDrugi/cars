import json
from os.path import join, dirname, abspath
import boto3
import environ

env = environ.Env()
env.read_env(
    join(dirname(dirname(abspath(__file__))), '/config/setting/.env')
)

# bucket policy
bucket_name = env('BUCKET_NAME')
bucket_policy = {
    'Version': '2012-10-17',
    'Statement': [{
        'Sid': 'AddPerm',
        'Effect': 'Allow',
        'Principal': '*',
        'Action': ['s3:GetObject'],
        'Resource': f'arn:aws:s3:::{bucket_name}/*'
    }]
}

bucket_policy = json.dumps(bucket_policy)

# Set the new policy
s3 = boto3.client('s3')
s3.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)
