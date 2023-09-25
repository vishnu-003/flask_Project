import pika
import send_files
import pymysql
import json
import re
import os
import pyttsx3

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

#RabbitMQ Connections
def rabbit_conn():
		url = os.environ.get('CLOUDAMQP_URL', 'amqps://vuylxkvk:f6dDFwey32bzBFOYbj0tNteDCtrdhDUk@puffin.rmq2.cloudamqp.com/vuylxkvk')
		params = pika.URLParameters(url)
		connectionr = pika.BlockingConnection(params)
		return connectionr


def download_txt(ch, method, properties, body):
    print(body.decode().replace("'","\""))
    payload = json.loads(body.decode().replace("'","\""))
    job_id = payload["job_id"]
    filename = payload["job_file"]
    user_id = payload["user_id"]
    print(job_id,filename,user_id)
    #Consumes info from RabbitMQ
    path = os.getcwd()
    UPLOAD_FOLDER = os.path.join(path, 'uploads')
    base = os.path.basename(filename)
    c = os.path.splitext(base)[0]
    os.makedirs(os.path.dirname(f"uploads/{user_id}/{filename}"), exist_ok=True)
    filename.save(os.path.join(f"{UPLOAD_FOLDER}/{user_id}",filename))

    #engine which converts text file into speech
    engine = pyttsx3.init()
    engine.setProperty('voice', 'com.apple.speech.synthesis.voice.Alex')
    engine.save_to_file(open(f"{UPLOAD_FOLDER}/{user_id}/{filename}", 'r').read(), os.path.join(f"{UPLOAD_FOLDER}/{user_id}/{c}.mp3"))
    engine.say(open(f"{UPLOAD_FOLDER}/{user_id}/{filename}", 'r').read())  
    engine.runAndWait()
    engine.stop()

    #db_connections 
    connection = db_connection()
    connection_cursor = connection.cursor()
    rq_con=rabbit_conn()
    rq_channel=rq_con.channel()
    rq_channel.queue_declare(queue="speech_queue",durable=True)
    stage="Completed"

    #Insert files into audio table
    query = f"INSERT INTO audios (user_id, filename) VALUES ('{user_id}', '{c}.mp3');"
    print(f"Audio_POST--->{query}")
    connection_cursor.execute(query)
    connection.commit()

    #Updating the stage
    query2 = f"UPDATE speech_file SET stage = 'completed' where job_id='{job_id}';"
    print(query2)
    connection_cursor.execute(query2)
    connection.commit()
    rq_channel.basic_consume(queue="speec_queue",on_message_callback=download_txt,auto_ack=True)
    rq_channel.start_consuming()
    rq_channel.close()
    rq_con.close()
    connection_cursor.close()
    connection.close()
    return send_files(f'{c}.mp3', as_attachment=True)
