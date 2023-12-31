from flask import Flask, render_template, request,redirect, session,make_response, send_file
from flask_mail import Mail, Message
import boto3
import pymysql
import requests
import bs4 as bs
import os
import pika
import uuid
import re
import datetime
from pytube import YouTube
from flask import url_for
from random import *
from dotenv import load_dotenv 
from werkzeug.utils import secure_filename

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
S3_BUCKET_NAME = 'flaskfile'
S3_REGION = 'ap-south-1'

mail = Mail(app)

#Validating the otp given by user
@app.route('/validate', methods=['POST'])
def validate_otp(email,otp):
        email = request.form['email']
        otp = request.form['otp']
        connection = db_connection()
        connection_cursor = connection.cursor()
        query = f"SELECT * from Details where email = '{email}' and otp = '{otp}'"
        connection_cursor.execute(query)
        users=connection_cursor.fetchall()
        print(len(users))
        connection_cursor.close()
        connection.close()
        d = os.environ.get("MAIL_USERNAME")
        if len(users)>0:
            email = request.form["email"]
            msg = Message('Welcome to our website!', sender = d, recipients = [email])
            msg.body = f"Thank you for registering on our website. We hope you enjoy our services!"
            mail.send(msg)
            return True
        else:
            return False
        

#Handiling Extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif','mp4','txt','mp3'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    d = os.environ.get("RQ_AMQPS")
    url = os.environ.get('CLOUDAMQP_URL', d)
    print(url)
    params = pika.URLParameters(url)
    connectionr = pika.BlockingConnection(params)
    return connectionr

#Login functionality 
@app.route('/', methods =['GET', 'POST'])
def login():
     if request.method == 'GET':
        if 'user_id' in session:
         return redirect(url_for('profile'))
        else:
         return render_template('login.html')
     
     elif request.method == 'POST':
        email=request.form["email1"]
        password=request.form["password"]
        conn = db_connection()
        cur = conn.cursor()
        Query = f"SELECT email,passwrd,personid FROM Details WHERE email='{email}' AND passwrd='{password}';"
        print(Query)
        cur.execute(Query)
        details=cur.fetchone()
        print(f"Details--->{details}")
        if  details is not None:
            if details['email']==email and details['passwrd']==password:
                session['user_id'] = details['personid']
                return redirect(url_for('home'))  
        else:
           message = "Wrong Username or Password"
           return render_template('login.html',message=message)
    
#Registration functionality
@app.route('/register', methods =['GET', 'POST'])
def register():
    if request.method == 'GET':  
        return render_template('register.html')
    
    elif request.method == 'POST':
        print(request.form)
        if 'otpvalidation' in request.form:
            email = request.form['email']
            otp_req = request.form['otp']
            print("vishnuvardhan22222")
            if validate_otp(email, otp_req):
                return render_template("login.html", message="Successfully Verified... Please Login.")
            else:
                 return render_template("otpvalidation.html")
        if 'register' in request.form:
             ("Register")
             lastname=request.form["lastname"]
             firstname=request.form["firstname"]
             email=request.form["email"]
             print(email)
             mobile=request.form["mobile"]
             city=request.form["city"]
             password=request.form["password"]
             query= f"SELECT * from Details where email = '{email}'"
             connection = db_connection()
             connection_cursor = connection.cursor()
             connection_cursor.execute(query)
             users=connection_cursor.fetchall()
             print(len(users))
             if len(users)>0:
                message = "The email address already exists"
                connection_cursor.close()
                connection.close()
                return render_template('register.html', message=message)
             else:
                otp=randint(000000,999999)
                msg = f"{otp}"
                validation_value=0
                query = f"INSERT INTO Details (lastname, firstname, email, mobile, city,passwrd,otp,validation_value) VALUE ('{lastname}', '{firstname}', '{email}', '{mobile}', '{city}','{password}','{otp}','{validation_value}');"
                connection_cursor.execute(query)
                connection.commit()
                connection_cursor.close()
                connection.close()
                msg1 = Message(subject='OTP',sender ='liarchary007@gmail.com',recipients = [email] )
                msg1.body = str(otp)
                mail.send(msg1)

                return render_template('otpvalidation.html',email=email)
        else:
            message = "Please another mail"
        return render_template('login.html', message=message)
    
#Forgot Password
@app.route('/forgototp', methods=['GET', 'POST'])
def forgototp():
    if request.method == 'POST':
        email = request.form['email']
        otp = str(randint(100000, 999999))
        msg = Message(subject='Forgot Password OTP', sender='liarchary007@gmail.com', recipients=[email])
        msg.body = f'Your OTP for resetting the password is: {otp}'
        mail.send(msg)
        session['reset_password_otp'] = otp
        print(f"otp in forgot--->{otp}")
        session['reset_password_email'] = email
        return redirect(url_for('verifyotp'))
    return render_template('forgototp.html')

#verifying OTP and setting a new password
@app.route('/verifyotp', methods=['GET', 'POST'])
def verifyotp():
    if request.method == 'POST':
        entered_otp = request.form['otp']
        Name = request.form['new_password']
        Name1 = request.form['confirm_password']
        print(Name)
        print(Name1)
        print(f"verifyotp---->{entered_otp}")
        new_password = request.form['new_password']
        if 'reset_password_otp' in session and 'reset_password_email' in session:
            if entered_otp == session['reset_password_otp']:
                if Name == Name1:
                    email = session['reset_password_email']
                    connection = db_connection()
                    connection_cursor = connection.cursor()
                    query1=f"SELECT passwrd from Details where email = '{email}';"
                    print(f"Query to check same password--->{query1}")
                    connection_cursor.execute(query1)
                    samepass=connection_cursor.fetchone()
                    print(samepass)
                    connection_cursor.close()
                    connection.close()

                    connection = db_connection()
                    connection_cursor = connection.cursor()
                    query = f"UPDATE Details SET passwrd = '{new_password}' WHERE email = '{email}';"
                    connection_cursor.execute(query)
                    connection.commit()
                    connection_cursor.close()
                    connection.close()
                    msg1 = Message(subject='Password has changed Successfully',sender ='liarchary007@gmail.com',recipients = [email] )
                    mail.send(msg1)
                    return redirect(url_for('login'))
                else:
                    msg='Password does not matched. Please try again.'
                    return render_template('verifyotp.html',msg=msg)
            else:
                msg="Invalid OTP"
                return render_template('verifyotp.html',msg=msg)
        else:
            return render_template('verifyotp.html')
 
    return render_template('verifyotp.html')

#Home Page
@app.route('/home')
def home():
    if 'user_id' in session:
     return render_template("home.html")
    
#Profile functionality   
@app.route('/profile',methods=['POST','GET'])
def profile():
        if 'user_id' in session:
            connection = db_connection()
            connection_cursor = connection.cursor()
            user_id = session['user_id']
            query=f"SELECT * FROM Details WHERE personid = '{user_id}';"
            connection_cursor.execute(query)
            users=connection_cursor.fetchone()
            print(users)
            return render_template("profile.html",users=users)
        else:
            message="You must be logged in"
            return render_template('login.html',message=message)
    
#Gallery functionality
@app.route('/gallery',methods=["POST","GET"])
def gallery():
    if request.method == 'GET':
        if 'user_id'in session:
            user_id=session.get('user_id')
            connection = db_connection()
            connection_cursor = connection.cursor()
            query = f" SELECT  user_id,filename ,id from images  WHERE user_id='{user_id}' and filename like'%jpg';"
            print(f"Gallery get---->{query}")
            connection_cursor.execute(query)
            images = connection_cursor.fetchall()
            print(type(images))
            print(f"These are the images---->{images}")
            query1 = f" SELECT  user_id,filename ,id from images  WHERE user_id='{user_id}' and filename like'%mp4';"
            print(f"Gallery get---->{query1}")
            connection_cursor.execute(query1)
            videos = connection_cursor.fetchall()
            print(type(videos))
            print(f"These are the videos---->{videos}")
            connection_cursor.close()
            connection.close()
            
        return render_template('gallery.html',images=images,videos=videos)
        
    
    if request.method == 'POST':
        if 'user_id' in session and 'file' in request.files:
            file=request.files['file']
            print(file)
            user_id=session['user_id']
            print(user_id)
            path = os.getcwd()
            print(f"path----->{path}")
            UPLOAD_FOLDER = os.path.join(path, 'uploads')
        
            if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # for file in filename:
                    print(f"actual filename------>{filename}")
                    os.makedirs(os.path.dirname(f"uploads/{user_id}/{filename}"), exist_ok=True)
                    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
                    file.save(os.path.join(f"{app.config['UPLOAD_FOLDER']}/{user_id}", filename))
                    print("2342324223432")
                    connection = db_connection()
                    connection_cursor = connection.cursor()
                    query = f"INSERT INTO images (user_id,filename) VALUE ('{user_id}', '{filename}');"
                    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=S3_REGION)
                    s3.upload_file(f"{UPLOAD_FOLDER}/{user_id}/{filename}",S3_BUCKET_NAME,f"uploads/{user_id}/gallery/{filename}")
                    print(f"Gallery_POST--->{query}")
                    connection_cursor.execute(query)
                    connection.commit()
                    connection_cursor.close()
                    connection.close()
                    
            
            return redirect(url_for('gallery'))


# Audio files functionality
@app.route('/audio', methods=["POST", "GET"])
def audio():
    if request.method == 'GET':
        if 'user_id' in session:
            user_id = session.get('user_id')
            connection = db_connection()
            connection_cursor = connection.cursor()
            query = f"SELECT  *FROM speech_file WHERE user_id='{user_id}' ;"
            print(f"Audio_get---->{query}")
            connection_cursor.execute(query)
            audios = connection_cursor.fetchall()
            print(f"Audios Details---->{audios}")
            connection_cursor.close()
            connection.close()
            s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=S3_REGION)
            urls=[]
            for elements in audios:
                key_value=f"{elements['s3_key']}"
                presigned_urls = s3.generate_presigned_url(
                    ClientMethod = 'get_object',
                    Params = {'Bucket': S3_BUCKET_NAME,
                            'Key': key_value
                            },
                            ExpiresIn = 3600)
                urls.append(presigned_urls)
            return render_template('audio.html', audios=audios,urls=urls)
        
    if request.method == 'POST':
        if 'user_id' in session:
            user_id = session['user_id']
            for text_file in request.files.getlist('text_file'):
                if text_file and allowed_file(text_file.filename):
                    filename = text_file.filename
                    #db_connections & RabbitMQ_connections
                    connection = db_connection()
                    connection_cursor = connection.cursor()
                    rq_con=rabbit_conn()
                    rq_channel=rq_con.channel()
                    rq_channel.queue_declare(queue="speech_queue",durable=True)
                    user_id=session['user_id']
                    upload_time=datetime.datetime.now()
                    stage="queued"
                    id=uuid.uuid1()
                    # bucket_name = S3_BUCKET_NAME
                    key = f"uploads/{user_id}/audios/{filename}"
                    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=S3_REGION)
                    s3.upload_fileobj(text_file, S3_BUCKET_NAME, key)
                    #Decalre & Insert into speech_file table
                    query2=f"INSERT INTO speech_file(job_id,user_id,bucket_name,s3_key,stage,upload_time) VALUES ('{id}','{user_id}','{S3_BUCKET_NAME}','{key}','{stage}','{upload_time}');"
                    print(query2)
                    connection_cursor.execute(query2)
                    connection.commit()
                    payload={
                        "job_id":str(id),
                        "s3_key":key,
                        "user_id":user_id,
                        "upload_time":str(upload_time),
                        "bucket_name": S3_BUCKET_NAME    
                    }
                    rq_channel.basic_publish(body=str(payload),exchange='',routing_key='speech_queue')

            msg="Your file has been converted into speech and downloaded" 
           
            connection.close()
            connection_cursor.close()
            rq_channel.close()
            rq_con.close()        
            return render_template('audio.html',msg=msg)
    return "No file uploaded."


#Upload functionality
@app.route('/uploads/<user_id>/<filename>',methods=["GET"])
def uploads(user_id, filename):
    session_user_id=session.get('user_id')
    print(f"it's uploads img ---->{session_user_id}")
    print(type(session_user_id))
    if session_user_id is not None:
         print(f"it is from UPLOAD Fun-->{user_id}" )
         if str(session_user_id)== str(user_id):
           return send_file(f"uploads/{user_id}/{filename}")
         else:
           return "Forbidden", 403
    return "Forbidden", 403


#Delete functionality for images
@app.route('/delete/<int:user_id>/<filename>', methods=['POST'])
def delete_image(user_id, filename):
    session_user_id = session.get('user_id')
    if session_user_id is not None and str(session_user_id) == str(user_id):
        path_to_delete = os.path.join('uploads', str(user_id), filename)
        print(f"path_to_delete---->{path_to_delete}")
        if os.path.exists(path_to_delete):
            os.remove(path_to_delete)
            print(f"After delete--->{path_to_delete}")
            connection = db_connection()
            connection_cursor = connection.cursor()
            query = f"DELETE FROM images WHERE user_id='{user_id}' AND filename='{filename}';"
            print(query)
            connection_cursor.execute(query)
            connection.commit()
            connection_cursor.close()
            connection.close()
        return redirect(url_for('gallery'))
    else:
        return "Forbidden", 403

#Delete functionality for deleting audio
@app.route('/delete_audio/<int:user_id>/<job_id>', methods=['POST'])
def delete_audio(user_id,job_id):
    session_user_id = session.get('user_id')
    if session_user_id is not None and str(session_user_id) == str(user_id):
        connection = db_connection()
        connection_cursor1 = connection.cursor()
        query2 = f"SELECT *FROM speech_file WHERE user_id='{user_id}' and  job_id='{job_id}';"
        print(query2)
        connection_cursor1.execute(query2)
        s3_keys = connection_cursor1.fetchall()
        print(f"s3_keys---->{s3_keys}")
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=S3_REGION)
        s3_delete=s3_keys[0]['s3_key']
        print(f"--------------->{s3_delete}")
        response =s3.delete_object(Bucket=S3_BUCKET_NAME,Key=s3_delete,)
        base = os.path.basename(s3_delete)
        c = os.path.splitext(base)[0]
        response =s3.delete_object(Bucket=S3_BUCKET_NAME,Key=f"uploads/49/audios/{c}.txt",)
        print(response)

        connection_cursor1.close()
        connection_cursor = connection.cursor()
        print(job_id)
        query = f"DELETE FROM speech_file WHERE user_id='{user_id}' AND job_id='{job_id}';"
        print(query)
        connection_cursor.execute(query)
        connection.commit()
        connection_cursor.close()
        connection.close()
        return redirect(url_for('audio'))
    else:
        return "Forbidden", 403


#Edit Profile functionality
@app.route('/profilenew',methods=['POST','GET'])
def profilenew():
    if 'user_id' in session:
            user_id=session.get('user_id')
            if request.method=='GET':
                connection = db_connection()
                connection_cursor = connection.cursor()
                user_id = session['user_id']
                query=f"SELECT * FROM Details WHERE personid = '{user_id}';"
                print(f"Profile get query--->{query}")
                connection_cursor.execute(query)
                users=connection_cursor.fetchone()
                print(users)
                return render_template("profilenew.html",users=users)
            
            elif request.method=="POST":
                new_lastname=request.form['lastname']
                new_firstname=request.form['firstname']
                new_mobile=request.form['mobile']
                new_city=request.form['city']
                new_email=request.form['email']
                # new_email=request.form['user_id']
                print(f"lastname in Profile_POST--->{new_lastname}")
                print(f"lastname in Profile_POST--->{new_firstname}")
                # print(f"lastname in Profile_POST--->{user_id}")
                print(f"email in Profile_POST--->{new_email}")
                connection = db_connection()
                connection_cursor = connection.cursor()
                query=f"UPDATE Details SET lastname='{new_lastname}', firstname='{new_firstname}', mobile='{new_mobile}',city='{new_city}',email='{new_email}' WHERE personid= '{user_id}';"
                connection_cursor.execute(query)
                print(f"Update Query---->{query}")
                connection.commit()
                connection_cursor.close()
                connection.close()
                return redirect(url_for('profile',user_id=user_id))

    else:
            message="You must be logged in"
            return render_template('login.html',message=message)

#YouTube video functionality
@app.route("/ut", methods=["GET","POST"])
def ut():      
        mesage = ''
        errorType = 0
        if request.method == 'POST' and 'video_url' in request.form:
            youtubeUrl = request.form["video_url"]
            print(youtubeUrl)
            if(youtubeUrl):
                validateVideoUrl = (r'(https?://)?(www\.)?''(youtube|youtu|youtube-nocookie)\.(com|be)/''(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
                validVideoUrl = re.match(validateVideoUrl, youtubeUrl)
                if validVideoUrl:
                    url = YouTube(youtubeUrl)
                    video = url.streams.get_highest_resolution()
                    user_id = session['user_id']
                    filename = f"{session['user_id']}_{url.title}.mp4"
                    path = os.getcwd()
                    UPLOAD_FOLDER = os.path.join(path, 'uploads')
                    os.makedirs(os.path.dirname(f"uploads/{user_id}/{filename}"), exist_ok=True)
                    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
                    downloadFolder = str(os.path.join(f"{app.config['UPLOAD_FOLDER']}/{user_id}"))
                    video.download(downloadFolder, filename=filename)
                    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=S3_REGION)
                    s3.upload_file(f"{UPLOAD_FOLDER}/{user_id}/{filename}",S3_BUCKET_NAME,f"uploads/{user_id}/youtube/{filename}")
                    connection=db_connection()
                    connection_cursor=connection.cursor()
                    query = f"INSERT INTO images (user_id, filename) VALUES ('{user_id}', '{filename}');"
                    print(query)
                    connection_cursor.execute(query)
                    connection.commit()
                    connection_cursor.close()
                    connection.close()
                    mesage = 'Video Downloaded and Added to Your Profile Successfully!'
                    errorType = 1
                    return redirect(url_for('gallery'))
                else:
                    mesage = 'Enter Valid YouTube Video URL!'
                    errorType = 0        
            else:
                mesage='enter Youtube video url'
                errorType=0
        return render_template('ut.html', mesage = mesage, errorType = errorType)

#Insta video functionality
@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    print(url)
    print(type(url))

    print("dsfdsfsdfdsdsaasfsdfsdfds")

    headers = {
        'authority': 'fastdl.app',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://fastdl.app',
        'pragma': 'no-cache',
        'referer': 'https://fastdl.app/',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }
    data = {
        'url': f"{url}",
        'lang_code': 'en',
        'token': '',
    }
    response = requests.post('https://fastdl.app/c/', headers=headers, data=data)
    anc=response.text
    print(anc)
    # source = urllib.request.urlopen('https://www.instagram.com/reel/CxGEYRBJtFj/?igshid=MzRlODBiNWFlZA==').read()
    print(f"inside---->{url}")
    soup = bs.BeautifulSoup(anc,'lxml')
    for url in soup.find_all('a'):
        href_link=url.get('href')
        print(soup.get_text())
        # download= "<a href={href_link} download>Download Video</ahref_link"
    return (f"<a href={href_link} download>Download Video</ahref_link")

@app.route('/instad')
def instad():

    return render_template('instad.html')

#Logout functionality   
@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect(url_for('login'))

       
if __name__=='__main__':
    app.run(host="0.0.0.0", port=80)

    