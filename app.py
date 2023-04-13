from flask import Flask, flash, make_response, redirect, send_file, jsonify, request, render_template, url_for
import db
import os
from werkzeug.utils import secure_filename
import subprocess
import threading

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "configs/squash"
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 512 #512MB

def ssh_thread_function():
    subprocess.run(['wssh','--fbidhttp=False'])
    
ssh_thread = threading.Thread(target=ssh_thread_function)
ssh_thread.start()

@app.route('/')
def main():
    auth_token = request.cookies.get('auth_token')
    if auth_token != "" or auth_token is not None:
        if db.get_user_bytoken(auth_token) is None:
            return render_template('login.html')
    return render_template('index.html')



@app.route('/api/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']

    auth_token = db.login(username, password)
    if auth_token is None:
        response = make_response(redirect("/"), render_template('login.html', incorrect="Incorrect username or password!"))
        return response
    
    response = make_response(render_template('index.html'))
    response.set_cookie('auth_token', auth_token)

    return response


@app.route("/api/addimage", methods=['POST'])
def add_image():
    db.Connect()
    name = None
    try:
        file = request.files['file']
        if file is None or file == "":
            return jsonify(message="nofile")
    except Exception as e:
        return jsonify(message="nofile")
    
    try:
        token = request.form['token']
        if token is None or token == "":
            return jsonify(message="notoken")
    except:
        if token is None:
            return jsonify(message="notoken")
    
    incorrect = True
    while incorrect:
        if db.GetVPNImage(token) is not None:
            if name[-1:].isdigit():
                name = name[:-1] + str(int(name[-1:])+1)
            else:
                name = name+"1"
        else:
            incorrect = False

    filename = secure_filename(file.filename)
    while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        if filename[0].isdigit():
            filename = str(int(filename[0])+1)+filename[1:]
        else:
            filename = "1"+filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    db.add_conf_image(filename, token)

    return jsonify(message="ok")
   

@app.route("/api/getconf")
def get_image():
    filename = db.get_conf_image(request.headers['token'])
    if filename is None or filename == "":
        filename = "default.squashfs"
        
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))
