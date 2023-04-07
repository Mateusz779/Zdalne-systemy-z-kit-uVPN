from flask import Flask, send_file, jsonify, request
import db
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "configs/squash"
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 512 #512MB

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
    
    db.AddVPNImage(filename, token)

    return jsonify(message="ok")
   

@app.route("/api/getvpn")
def get_image():
    try:
        filename = db.GetVPNImage(request.args['token'])
    except:
        filename = "default.squashfs"
    if filename is None or filename == "":
        filename = "default.squashfs"
        
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))