from flask import Flask, render_template, request, redirect, url_for

import os

 

app = Flask(__name__)

 

# Define the folder where uploaded files will be stored

UPLOAD_FOLDER = 'uploads'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

 

@app.route('/')

def index():

    return render_template('upload.html')

 

@app.route('/upload', methods=['POST'])

def upload_files():

    # Get the list of uploaded files

    uploaded_files = request.files.getlist('file[]')

 

    for file in uploaded_files:

        if file:

            # Save the file to the specified folder

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

 

    return redirect(url_for('index'))

 

if __name__ == '__main__':

app.run(debug=True)