from flask import *
import mysql.connector
import MySQLdb.cursors
import re
from flask_mail import Mail, Message
from random import *

# initialize first flask
app = Flask(__name__)
mail = Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'nethra325reddy@gmail.com'
app.config['MAIL_PASSWORD'] = 'uaij ksij fjap tecl'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

otp=randint(000000,999999)
print(otp)

def db_connection():
  connection = mysql.connector.connect(
  host="mysql-1ed7bbbc-wlmycn-2bde.aivencloud.com",
  user="nethra",
  password="AVNS_VZBjSvRHMNrTujGWv84",
  port="26098",
  database="defaultdb")
  return connection


def validate_otp(email, otp):
		email = request.form['email']
		otp = request.form['otp']
		return True
		# connection = db_connection()
		# connection_cursor = connection.cursor()
		# query = f"SELECT * from login_flask_345 where email = '{email}' and otp = '{otp}'"
		# connection_cursor.execute(query)
		# users=connection_cursor.fetchall()
		# print(len(users))
		# if len(users)>0:
		# 	return True
		
		
	#Open Connetion
	#Open Cursor
	# SELECT * FROM users WHERE email="email" and otp="otp"
	# return True/False
	# return True

@app.route('/', methods=['GET','POST'])
def login():
	if request.method == 'GET':
		return render_template('login.html',message="")
	elif request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		query = f"SELECT * from Users where username = '{username}' and password = '{password}'"
		connection = db_connection()
		connection_cursor = connection.cursor()
		connection_cursor.execute(query)
		result = connection_cursor.fetchall()
		print(result)
		if len(result)>0:
			message="login success"
		elif result == []:
			message="user not found"
		return render_template('login.html',message=message)

@app.route('/register', methods=['GET', 'POST'])
def register():
		message=" "
		if request.method == 'GET':
			return render_template('register.html', message="please fill out the form")
		elif request.method == 'POST':

			print(request.form)
			if 'verify' in request.form:
				email = request.form['email']
				otp_req = request.form['otp']
				if validate_otp(email, otp_req):
					return render_template("login.html", message="Successfully Verified... Please Login.")
				else:
					return render_template("verify.html")
				
			if 'register' in request.form:
				phonenum=request.form['phonenum']
				password = request.form['password']
				email = request.form['email']
				username = request.form['username']
				validation=request.form['validation']
				query= f"SELECT * from login_flask_345 where email = '{email}'"
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
					query= f"INSERT INTO Users (username,email,password,phonenum) VALUES ('{username}','{email}', '{password}','{phonenum}');"
					connection_cursor.execute(query)
					connection.commit()
					connection_cursor.close()
					connection.close()
					message='Registration successful'
					msg = Message(subject='OTP',sender ='nethra325reddy@gmail.com',recipients = [email] )
					msg.body = str(otp)
					mail.send(msg)
					return render_template('verify.html', message=message, email=email)
			else:
				message = "Please enter an email address"
			return render_template('register.html')

@app.route('/validate', methods=['POST'])
def validate():
	user_otp=request.form['otp']
	if otp==int(user_otp):
		return render_template('register.html')

if __name__=="__main__":
	app.run(debug= True)









