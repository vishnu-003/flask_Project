import boto3
import os
from dotenv import load_dotenv 

current_directory = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_directory, '.env')

# Load environment variables from the .env file
load_dotenv(dotenv_path)

AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
S3_BUCKET_NAME = 'flaskfile'
S3_REGION = 'ap-south-1'

s3_C = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=S3_REGION)
s3_R = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=S3_REGION)

from boto3.session import Session

session = Session(aws_access_key_id=AWS_ACCESS_KEY,
                  aws_secret_access_key=AWS_ACCESS_KEY)
s3 = session.resource('s3')
your_bucket = s3.Bucket('flaskfile')

for s3_file in your_bucket.objects.all():
    content=s3_file.key

    base = os.path.basename(content)
    c = os.path.splitext(base)[0]
    print(c)
    # obj = s3_R.Object(S3_BUCKET_NAME,c )
    # a=obj.get()['Body'].read().decode('utf-8')
    # print(a)



