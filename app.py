import datetime
from time import sleep
from flask import Flask, make_response, redirect, send_file, jsonify, request, render_template, url_for
import db
import os
from werkzeug.utils import secure_filename
import subprocess
import utils
import shutil
import config
import machines

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "squash"
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 512  # 512MB

utils.init_threads()


@app.route('/')
def main():
    auth_token = request.cookies.get('auth_token')
    if auth_token != "" or auth_token is not None:
        if db.get_user_bytoken(auth_token) is None:
            return redirect("/login")
    machines_all = db.get_machines()
    return render_template('index.html', ssh_port=config.webssh_port, machines=machines_all.machines, timezone=config.timezone)


@app.route('/login')
def login():
    auth_token = request.cookies.get('auth_token')
    if auth_token != "" or auth_token is not None:
        if db.get_user_bytoken(auth_token) is not None:
            machines_all = db.get_machines()
            return render_template('index.html', ssh_port=config.webssh_port, machines=machines_all.machines, timezone=config.timezone)
    return render_template('login.html')

@app.route('/logout')
def logout():
    auth_token = request.cookies.get('auth_token')
    if auth_token != "" or auth_token is not None:
        if db.get_user_bytoken(auth_token) is not None:
            db.del_auth_token(auth_token)
            response = make_response(redirect('/'))
            response.delete_cookie('auth_token')
            return response
    return render_template('login.html')

@app.route('/create/conf')
def create_conf():
    auth_token = request.cookies.get('auth_token')
    if auth_token != "" or auth_token is not None:
        if db.get_user_bytoken(auth_token) is None:
            return redirect("/login")
    return render_template("create.html")


@app.route('/api/createconf', methods=['POST'])
def create_conf_post():
    config_name = request.form['config_name']
    token_name = request.form['token_name']
    key_length = request.form['key_length']
    folder = utils.generate_random_string(5)
    try:
        os.mkdir(os.path.join(os.getcwd(), 'configs', folder))
        authorized_keys_config = request.form['authorized_keys_config']
        authorized_keys_file = open(folder+"/authorized_keys", "w")
        authorized_keys_file.write(authorized_keys_config)
        authorized_keys_file.close()
    except:
        shutil.copy('./configs/authorized_keys',
                    './configs/' + folder+"/authorized_keys")

    script_path = os.path.join(os.getcwd(), 'configs', "create.sh")
    ini_path = os.path.join(os.getcwd(), 'configs', "uVPN.ini")
    conf_path = os.path.join(os.getcwd(), 'configs', "uVPN.conf")
    pub_path = os.path.join(os.getcwd(), 'configs', "server.pub")
    scripts_path = os.path.join(os.getcwd(), 'configs', "scripts/")
    authorized_keys_path = os.path.join(
        os.getcwd(), 'configs', folder, "authorized_keys")
    sshd_config_path = os.path.join(os.getcwd(), 'configs', "sshd_config")
    sendmail_path = os.path.join(os.getcwd(), 'configs', "sendmail.sh")

    subprocess.run([script_path, "-i "+ini_path, "-c "+conf_path, "-k "+pub_path, "-l "+key_length, "-n"+config_name,
                   "-s "+scripts_path, "-a "+authorized_keys_path, "-d "+sshd_config_path, "-m "+sendmail_path, " > /dev/null 2>&1 "])

    if os.path.exists(folder):
        shutil.rmtree(folder)

    db.add_conf_image(config_name+".squashfs", token_name)

    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], config_name+".pub"))


@app.route('/api/login', methods=['POST'])
def login_api():
    username = request.form['username']
    password = request.form['password']
    # register
    # db.add_user(username, password)
    # register
    auth_token = db.login(username, password)
    if auth_token is None:
        return render_template('login.html', incorrect="Incorrect username or password!")

    response = make_response(redirect('/'))
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
    try:
        filename = db.get_conf_image(request.headers['token'])
    except:
        pass
    try:
        date = db.get_image_allocation_time(request.headers['token'])
        if date is not None:
            delta = datetime.datetime.now() - date
            if delta.total_seconds() > 30:
                db.del_image_allocation_token(request.headers['token'])
            else:
                filename = None
        else:
            db.set_image_allocation(
                request.headers['token'], request.remote_addr)
    except:
        pass

    if filename is None or filename == "":
        filename = config.default_file

    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))


@app.route("/api/release_allocation", methods=['POST'])
def release_allocation():
    try:
        id_allocation = db.get_conf_id_name(
            request.headers['name']+".squashfs")
        if id_allocation is None or id_allocation == "":
            return jsonify(message="400")
    except:
        return jsonify(message="400")
    if id_allocation is not None:
        db.del_image_allocation_id_image(id_allocation)
    else:
        return jsonify(message="404")

    return jsonify(message="200")


@app.route("/api/addip", methods=['POST'])
def add_ip():
    try:
        token = request.headers['token']
        ip = request.form['ip']
    except:
        return jsonify(message="400")
    if db.update_image_allocation_ip_vpn(token, ip) is not None:
        return jsonify(message="200")
    else:
        return jsonify(message="400")


if __name__ == '__main__':
    app.run(host="0.0.0.0")
