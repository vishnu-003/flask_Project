from flask import Flask, request, render_template, send_file,redirect
import os
import pyttsx3
from flask import url_for
 

app = Flask(__name__)

# @app.route('/', methods=['GET'])
# def audio():
#     return render_template('audio.html')
@app.route('/audio',methods=["POST","GET"])
def audio():
    if request.method == 'GET':
        if 'user_id'in session:
            user_id=session.get('user_id')
            connection = db_connection()
            connection_cursor = connection.cursor()
            query = f" SELECT  user_id,filename ,id from images  WHERE user_id='{user_id}' and filename like'%mp3';"
            print(f"Gallery get---->{query}")
            connection_cursor.execute(query)
            audios = connection_cursor.fetchall()
            print(f"These are the audios---->{audios}")
            connection_cursor.close()
            connection.close()
        return render_template('audio.html',audios=audios)
    
    if request.method == 'POST':
        if 'user_id' in session and 'text_file' in request.files:
            text_file = request.files['text_file']
            print(text_file)
            user_id=session['user_id']
            print(user_id)
            path = os.getcwd()
            print(f"path----->{path}")
            UPLOAD_FOLDER = os.path.join(path, 'uploads')
            if text_file and allowed_file(file.filename):
                filename= text_file.filename
                engine = pyttsx3.init()
                # os.makedirs(os.path.dirname(f"uploads"), exist_ok=True)
                app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
                print(f"-------------->{UPLOAD_FOLDER}")
                text_file.save(os.path.join(f"{app.config['UPLOAD_FOLDER']}",filename))
                # text_file.save(filename)
                print(type(filename))
                base=os.path.basename(f"{UPLOAD_FOLDER}/{filename}")
                print(base)
                b=os.path.splitext(base)
                print(f"base1--->{b}")
                c=os.path.splitext(base)[0]
                print(f"base2--->{c}")
                engine.setProperty('voice', 'com.apple.speech.synthesis.voice.Alex')
                engine.save_to_file(open(f"{UPLOAD_FOLDER}/{filename}", 'r').read(), os.path.join(f"{app.config['UPLOAD_FOLDER']}",f"{c}.mp3"))
                engine.say(open(f"{UPLOAD_FOLDER}/{filename}", 'r').read())   
                engine.runAndWait()
                engine.stop()
                connection = db_connection()
                connection_cursor = connection.cursor()
                query = f"INSERT INTO images (user_id,filename) VALUE ('{user_id}', '{filename}');"
                print(f"Gallery_POST--->{query}")
                connection_cursor.execute(query)
                connection.commit()
                connection_cursor.close()
                connection.close()
                return redirect(url_for('audio'))
                # return send_file('output.mp3', as_attachment=True)
            return "No file uploaded."

# @app.route('/convert', methods=['POST'])
# def convert():
#     text_file = request.files['text_file']
#     path = os.getcwd()
#     UPLOAD_FOLDER = os.path.join(path, 'uploads')
#     if text_file and allowed_file(file.filename):
#         filename= text_file.filename
#         engine = pyttsx3.init()
#         # os.makedirs(os.path.dirname(f"uploads"), exist_ok=True)
#         app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#         print(f"-------------->{UPLOAD_FOLDER}")
#         text_file.save(os.path.join(f"{app.config['UPLOAD_FOLDER']}",filename))
#         # text_file.save(filename)
#         print(type(filename))
#         base=os.path.basename(f"{UPLOAD_FOLDER}/{filename}")
#         print(base)
#         b=os.path.splitext(base)
#         print(f"base1--->{b}")
#         c=os.path.splitext(base)[0]
#         print(f"base2--->{c}")
#         engine.setProperty('voice', 'com.apple.speech.synthesis.voice.Alex')
#         engine.save_to_file(open(f"{UPLOAD_FOLDER}/{filename}", 'r').read(), os.path.join(f"{app.config['UPLOAD_FOLDER']}",f"{c}.mp3"))
#         engine.say(open(f"{UPLOAD_FOLDER}/{filename}", 'r').read())   
#         engine.runAndWait()
#         engine.stop()
#         connection = db_connection()
#         connection_cursor = connection.cursor()
#         query = f"INSERT INTO images (user_id,filename) VALUE ('{user_id}', '{filename}');"
#         print(f"Gallery_POST--->{query}")
#         connection_cursor.execute(query)
#         connection.commit()
#         connection_cursor.close()
#         connection.close()
#         return redirect(url_for('audio'))
#         # return send_file('output.mp3', as_attachment=True)
#     return "No file uploaded."


if __name__ == '__main__':
    app.run(debug=True)




