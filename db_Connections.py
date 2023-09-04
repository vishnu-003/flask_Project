from flask import Flask, render_template, request
from flask_mail import Mail, Message
import pymysql


app=Flask(__name__)
mail= Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'liarchary007@gmail.com'
app.config['MAIL_PASSWORD'] = 'yigovfrnnesvnbza'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)



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



@app.route('/', methods =['GET', 'POST'])

def login():
     if request.method == 'GET':
        return render_template('login.html')
     
     elif request.method == 'POST':
        email=request.form["email1"]
        password=request.form["password"]
        conn = db_connection()
        cur = conn.cursor()
        Query = f"SELECT email,passwrd FROM Users WHERE email='{email}' AND passwrd='{password}';"
        print(Query)
        cur.execute(Query)
        details=cur.fetchall()
        if len(details)==0:
            return "user not found"
        elif len(details) > 0:
            return "user found"                

           

@app.route('/register', methods =['GET', 'POST'])

def register():

    if request.method == 'GET':  
        return render_template('register.html')
    
    elif request.method == 'POST':
        lastname=request.form["lastname"]
        firstname=request.form["firstname"]
        email=request.form["email"]
        mobile=request.form["mobile"]
        city=request.form["city"]
        password=request.form["password"]
        conn = db_connection()
        cur = conn.cursor()
        Query = f"INSERT INTO `defaultdb`.`Users` (`lastname`, `firstname`, `email`, `mobile`, `city`,`passwrd`) VALUE ('{lastname}', '{firstname}', '{email}', '{mobile}', '{city}','{password}');"
        print(Query)
        cur.execute(Query)
        conn.commit()
        
        cur.close()
        conn.close()
        
        # send email
        email = request.form["email"]
        lastname = request.form['lastname']
        msg = Message('Welcome to our website!', sender = 'liarchary007@gmail.com', recipients = [email])

        msg.body = "Thank you for registering on our website. We hope you enjoy our services!"
        mail.send(msg)
        data = {
            "lastname": lastname,
        }
        return render_template("success.html",data=data)
    

if __name__=='__main__':
    app.run()
