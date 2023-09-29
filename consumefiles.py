import pika
import pymysql
import json
import os
import boto3
from dotenv import load_dotenv 
import pyttsx3
from dotenv import load_dotenv 


current_directory = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_directory, '.env')

# Load environment variables from the .env file
load_dotenv(dotenv_path)


#Connecting to database
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


AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
S3_BUCKET_NAME = 'flaskfile'
S3_REGION = 'ap-south-1'
b = os.environ.get("RQ_AMQPS")

#RabbitMQ Connections
url = os.environ.get('CLOUDAMQP_URL', b)
params = pika.URLParameters(url)
connection1 = pika.BlockingConnection(params)
rq_channel = connection1.channel()
rq_channel.queue_declare(queue="speech_queue", durable=True)
connection = db_connection()
connection_cursor = connection.cursor()


#Cosnsume functionality
def download_txt(ch, method, properties, body):
    print(body.decode().replace("'", "\""))
    payload = json.loads(body.decode().replace("'", "\""))
    job_id = payload["job_id"]
    filename = payload["job_file"]
    user_id = payload["user_id"]
    s3_bucket_name = payload["s3_bucket_name"]
    print(f"Bucket_name--->{s3_bucket_name}")
    aws_secret_key = payload["aws_secret_key"]
    print(f"aws_key---->{aws_secret_key}")
    print(f"filename----{filename}")
    print(job_id, filename, user_id)
    path = os.getcwd()
    UPLOAD_FOLDER = os.path.join(path, 'uploads')
    print(f"--------->{UPLOAD_FOLDER}")
    base = os.path.basename(filename)
    c = os.path.splitext(base)[0]
    print

    if not os.path.exists(os.path.join(UPLOAD_FOLDER, str(user_id))):
        os.makedirs(os.path.join(UPLOAD_FOLDER, str(user_id)))
        
    engine = pyttsx3.init()
    engine.setProperty('voice', 'com.apple.speech.synthesis.voice.Alex')
    engine.save_to_file(open(f"{UPLOAD_FOLDER}/{user_id}/{filename}", 'r').read(), os.path.join(f"{UPLOAD_FOLDER}/{user_id}/{c}.mp3"))
    engine.say(open(f"{UPLOAD_FOLDER}/{user_id}/{filename}", 'r'))  
    engine.runAndWait()
    engine.stop()
    # Insert files into the audio table

    query = f"INSERT INTO audios (user_id, filename) VALUES ('{user_id}', '{c}.mp3');"
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=S3_REGION)
    s3.upload_fileobj(filename, S3_BUCKET_NAME,f"{c}.mp3")
    print(f"Audio_POST--->{query}")
    connection_cursor.execute(query)
    connection.commit()

    # Updating the stage
    query2 = f"UPDATE speech_file SET stage = 'completed' where job_id='{job_id}';"
    print(query2)
    connection_cursor.execute(query2)
    connection.commit()

rq_channel.basic_consume(queue="speech_queue",on_message_callback=download_txt,auto_ack=True)
rq_channel.start_consuming()
connection1.close()
connection_cursor.close()
    # return "download completed"