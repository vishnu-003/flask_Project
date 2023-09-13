from flask import Flask, render_template, request,redirect, session,abort,make_response,jsonify, send_file, abort
from flask_mail import Mail, Message
import pymysql
import os
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
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  
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
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

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
    
#Registration Functionality
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

#Home Page
@app.route('/home')
def home():
    if 'user_id' in session:
     return render_template("home.html")
    
#Profile Functionality   
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
    
#Gallery Functionality
@app.route('/gallery',methods=["POST","GET"])
def gallery():
    if request.method == 'GET':
        if 'user_id'in session:
            user_id=session.get('user_id')
            connection = db_connection()
            connection_cursor = connection.cursor()
            query = f" SELECT  user_id,filename ,id from images  WHERE user_id='{user_id}';"
            print(f"Gallery get---->{query}")
            connection_cursor.execute(query)
            images = connection_cursor.fetchall()
            print(type(images))
            print(f"These are the images---->{images}")
            connection_cursor.close()
            connection.close()
        return render_template('gallery.html',images=images)
        
    
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
                    file.save(os.path.join(f"{app.config['UPLOAD_FOLDER']}/{user_id}", file.filename))
                    print("2342324223432")
                    connection = db_connection()
                    connection_cursor = connection.cursor()
                    query = f"INSERT INTO images (user_id,filename) VALUE ('{user_id}', '{filename}');"
                    print(f"Gallery_POST--->{query}")
                    connection_cursor.execute(query)
                    connection.commit()
                    connection_cursor.close()
                    connection.close()
            
            return render_template('gallery.html')

#Upload Functionality
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

#Delete functionality
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


#Edit Profile Page
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
                new_email=request.form['user_id']
                print(f"lastname in Profile_POST--->{new_lastname}")
                print(f"lastname in Profile_POST--->{new_firstname}")
                print(f"lastname in Profile_POST--->{user_id}")
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
    


#Logout Functionality   
@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect(url_for('login'))

       
if __name__=='__main__':
    app.run()