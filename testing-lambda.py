import pymysql
import boto3
import os
from fpdf import *

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



print('Loading function')

s3 = boto3.client('s3')
user_id = "07"

def lambda_handler(event, context):
    connection = db_connection()
    connection_cursor = connection.cursor()
    s3_key = event['Records'][0]['s3']['object']['key']
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    user_id = s3_key.split("/")[1]
    filename = s3_key.split("/")[3]
    path = "/tmp"
    pdf_path = os.path.join(path, f"{user_id}/{filename}.pdf")
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    if os.path.exists(pdf_path):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=15)
            with open(pdf_path, "r") as text_file:
                for line in text_file:
                    pdf.cell(200, 10, txt=line, ln=1, align="C")
    pdf.output(pdf_path)

    query = f"INSERT INTO pdf (user_id, filename) VALUES ('{user_id}','{filename}.pdf');"
    connection_cursor.execute(query)
    connection.commit()
    s3.upload_file(pdf_path, bucket_name, f"uploads/{user_id}/{filename}.pdf")
    connection_cursor.close()
    connection.close()
    os.remove(pdf_path)
    return {
        'statusCode': 200,
        'body': 'Lambda function executed successfully!'
    }