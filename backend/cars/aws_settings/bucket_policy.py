import json
from os.path import join, dirname, abspath
import boto3
import environ

env = environ.Env()
env.read_env(
    join(dirname(dirname(abspath(__file__))), 'config/settings/.env')
)

bucket_name = env('BUCKET_NAME')

# Create session
session = boto3.Session(
    aws_access_key_id=env('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=env('AWS_SECRET_ACCESS_KEY'),
    region_name=env('REGION_NAME'),
)
s3_resource = session.resource('s3')

bucket = s3_resource.create_bucket(
    ACL='public-read-write',
    Bucket=bucket_name,
    CreateBucketConfiguration={
        'LocationConstraint': env('REGION_NAME'),
    },
)

# bucket policy
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
s3_client = session.client('s3')
s3_client.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)

# Upload default avatar file
filename = 'no-avatar.png'
avatar = join(dirname(abspath(__file__)), f'static/{filename}')
s3_client.upload_file(
    avatar,
    bucket_name,
    f'media/{filename}',
    ExtraArgs={'ContentType': 'image/jpeg'}
)
