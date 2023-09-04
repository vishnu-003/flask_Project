from flask import Flask, render_template, request
import pymysql

app=Flask(__name__)

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

 

@app.route('/login', methods =['GET', 'POST'])

def login():
     if request.method == 'GET':
        return render_template('login.html')
     
     elif request.method == 'POST':
        email=request.form["email1"]
        password=request.form["password"]
        conn = db_connection()
        cur = conn.cursor()
        Query = f"SELECT email,passwrd FROM new1 WHERE email='{email}' AND passwrd='{password}';"
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
        Query = f"INSERT INTO `defaultdb`.`new1` (`lastname`, `firstname`, `email`, `mobile`, `city`,`passwrd`) VALUE ('{lastname}', '{firstname}', '{email}', '{mobile}', '{city}','{password}');"
        print(Query)
        cur.execute(Query)
        conn.commit()
        cur.close()
        conn.close()
        print(cur.fetchall())

        return render_template("login.html")

        

if __name__=='__main__':
    app.run()

 