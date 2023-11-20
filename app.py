from flask import Flask, render_template, request,redirect, session,make_response, send_file
from flask_mail import Mail, Message
import boto3
import pymysql
import requests
import os
import pika
import re
from dotenv import load_dotenv 
from werkzeug.utils import secure_filename
from flask import url_for

import aspose.words as aw

current_directory = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_directory, '.env')

# Load environment variables from the .env file
load_dotenv(dotenv_path)

app=Flask(__name__)
mail= Mail(app)

app.secret_key = os.environ.get('MAIL_ID')
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['RQ_AMQPS'] = os.environ.get('RQ_AMQPS')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  
app.config['AWS_ACCESS_KEY'] = os.environ.get('AWS_ACCESS_KEY')
app.config['AWS_SECRET_KEY'] = os.environ.get('AWS_SECRET_KEY')


AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
S3_BUCKET_NAME = 'gamer-lambda'
S3_REGION = 'ap-south-1'

s3_R = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=S3_REGION)
s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=S3_REGION)               
#Handiling Extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif','mp4','txt','mp3'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def db_connection():
    timeout = 10
    connection = pymysql.connect(
        charset="utf8mb4",
        connect_timeout=timeout,
        cursorclass=pymysql.cursors.DictCursor,
        db="defaultdb",
        host="mysql-1ed7bbbc-wlmycn-2bde.aivencloud.com",
        password="AVNS_bgJrNel49GgbukSs-4U",
        read_timeout=timeout,
        port=26098,
        user="avnadmin",
        write_timeout=timeout,
        )
    return connection

user_id="07"

# Audio files functionality
@app.route('/pdfs', methods=["POST", "GET"])
def pdfs():
    # if request.method == 'GET':
    #     connection = db_connection()
    #     connection_cursor = connection.cursor()
    #     query = f"SELECT * from Email where  user_id = '{user_id}' and filename = '{filename}'"
    #     connection_cursor.execute(query)
    #     users=connection_cursor.fetchall
    #     if len(users)>0:
    #         return render_template('pdfs.html',users=users)
    #     else:
    #         msg="Your file is not converted into pdf,please check from your side"
    #         return render_template('pdfs.html',msg=msg)


    if request.method == 'POST':
        for text_file in request.files.getlist('text_file'):
            if text_file and allowed_file(text_file.filename):
                filename = text_file.filename
                print(f"text-file----{text_file}")
                key = f"uploads/files/{filename}"
                s3.upload_fileobj(text_file, S3_BUCKET_NAME, key)


    return  render_template('pdfs.html')
if __name__=='__main__':
    app.run()