import boto3
from pathlib import Path
from botocore.config import Config
from botocore.exceptions import ClientError
import environ


BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR_STR = str(BASE_DIR)
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

ENDPOINT = env("ENDPOINT")
KEY_ID = env("KEY_ID")
APPLICATION_KEY = env("APPLICATION_KEY")
BUCKET_NAME = env("BUCKET_NAME")

def get_b2_client(endpoint, keyID, applicationKey):
    b2_client = boto3.client(service_name='s3',
                            endpoint_url=endpoint,                
                            aws_access_key_id=keyID,              
                            aws_secret_access_key=applicationKey) 
    return b2_client

def get_b2_resource(endpoint, key_id, application_key):
    b2 = boto3.resource(service_name='s3',
                        endpoint_url=endpoint,                  
                        aws_access_key_id=key_id,               
                        aws_secret_access_key=application_key,  
                        config=Config(signature_version='s3v4'))
    return b2

def download_file(bucket, directory, local_name, key_name, b2):
    file_path = directory + '/' + local_name
    try:
        b2.Bucket(bucket).download_file(key_name, file_path)
    except ClientError as ce:
        print('error', ce)

def upload_file(bucket, directory, file, b2, b2path=None):
    file_path = directory + '/' + file
    remote_path = b2path
    if remote_path is None:
        remote_path = file
    try:
        response = b2.Bucket(bucket).upload_file(file_path, remote_path)
    except ClientError as ce:
        print('error', ce)

    return response

def upload_objfile(bucket, fileobj, b2, b2path=None):
    remote_path = b2path
    if remote_path is None:
        remote_path = fileobj.name
    try:
        response = b2.Bucket(bucket).upload_fileobj(fileobj, remote_path)
    except ClientError as ce:
        print('error', ce)

    return response

def delete_files(bucket, keys, b2):
    objects = []
    for key in keys:
        objects.append({'Key': key})
    try:
        response = b2.Bucket(bucket).delete_objects(Delete={'Objects': objects})
    except ClientError as ce:
        print('error', ce)

    return response

def get_object_presigned_url(bucket, key, expiration_seconds, b2):
    try:
        response = b2.meta.client \
        .generate_presigned_url(ClientMethod='get_object',
                                ExpiresIn=expiration_seconds,
                                Params={'Bucket': bucket,'Key': key})
        return response

    except ClientError as ce:
        print('error', ce)

b2 = get_b2_resource(ENDPOINT, KEY_ID, APPLICATION_KEY)