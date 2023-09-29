from flask import Flask, request, render_template,redirect
import boto3
import os
from flask import url_for
from dotenv import load_dotenv 

current_directory = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_directory, '.env')

# Load environment variables from the .env file
load_dotenv(dotenv_path)

app = Flask(__name__)

app.config['AWS_ACCESS_KEY'] = os.environ.get('AWS_ACCESS_KEY')
app.config['AWS_SECRET_KEY'] = os.environ.get('AWS_SECRET_KEY')
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
S3_BUCKET_NAME = 'flaskfile'
S3_REGION = 'ap-south-1'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    uploaded_files = request.files.getlist("file")
    for file in uploaded_files:
        if file.filename == '':
            redirect(url_for('index'))
    
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=S3_REGION)
        s3.upload_fileobj(file, S3_BUCKET_NAME, file.filename)
    return render_template("index.html",msg="files are uploaded to S3")

if __name__ == '__main__':
    app.run(debug=True)