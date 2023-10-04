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
key='liar.txt'
with open("liar.txt", 'rb') as data:
  s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=S3_REGION)
  s3.upload_fileobj(data, S3_BUCKET_NAME, "text")

presigned_url = s3.generate_presigned_url(
  ClientMethod = 'get_object',
  Params = {
    'Bucket': S3_BUCKET_NAME,
    'Key': 'liar.txt'
  },
  ExpiresIn = 360)

print('url: ', presigned_url)
