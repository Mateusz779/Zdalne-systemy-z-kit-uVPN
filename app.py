import datetime
from functools import wraps
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

def login_required(f):
    @wraps(f)
    def login_function(*args, **kwargs):
        auth_token = request.cookies.get('auth_token')
        if auth_token != "" or auth_token is not None:
            if db.get_user_bytoken(auth_token) is None:
                return redirect("/login")
        return f(*args, **kwargs)
    return login_function

@app.route('/')
@login_required
def main():
    machines_all = db.get_machines()
    return render_template('index.html', ssh_port=config.webssh_port, machines=machines_all.machines)


@app.route('/login')
@login_required
def login():
    return render_template('index.html', ssh_port=config.webssh_port, machines=machines_all.machines)


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


@app.route('/images')
@login_required
def list_images():
    images_all = db.get_images()
    return render_template("images.html", images=images_all.images)


@app.route('/create')
@login_required
def create_conf():
    return render_template("create.html")


@app.route('/api/createconf', methods=['POST'])
@login_required
def create_conf_post():
    try:
        config_name = request.form['config_name']
        token_name = request.form['token_name']
        key_length = request.form['key_length']
        ip = request.form['ip']
        password = request.form['pass']
    except:
        return jsonify(message="400")
    if db.get_conf_id_name(config_name+".squashfs") is not None:
        return jsonify(message="400")
    if db.get_conf_id(token_name) is not None:
        return jsonify(message="400")
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
    authorized_keys_path = os.path.join(
        os.getcwd(), 'configs', folder, "authorized_keys")
    sshd_config_path = os.path.join(os.getcwd(), 'configs', "sshd_config")
    sendmail_path = os.path.join(os.getcwd(), 'configs', "sendmail.sh")

    subprocess.run([script_path, "-i "+ini_path, "-c "+conf_path, "-k "+pub_path, "-l "+key_length, "-n"+config_name,
                   "-p "+ip, "-a "+authorized_keys_path, "-d "+sshd_config_path, "-m "+sendmail_path, " > /dev/null 2>&1 "])

    if os.path.exists(folder):
        shutil.rmtree(folder)
    output = subprocess.run(
        ['openssl', 'passwd', '-6', password], capture_output=True, text=True)
    db.add_conf_image(config_name+".squashfs", token_name, ip, output.stdout)

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


@app.route('/delete/<int:image_id>', methods=['POST'])
@login_required
def delete(image_id):
    if db.get_image_allocation(image_id) is not None:
        return jsonify(message="409")
    filename = db.get_conf_image_id(image_id)
    squashfs = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    pubkey = os.path.join(
        app.config['UPLOAD_FOLDER'], filename.split(".")[0]+".pub")
    if os.path.exists(squashfs):
        os.remove(squashfs)
    if os.path.exists(pubkey):
        os.remove(pubkey)
    db.del_image(image_id)

    return redirect(url_for('list_images'))


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


@app.route("/api/getpass")
def get_pass():
    try:
        password = db.get_conf_password(request.headers['token'])
        return password
    except:
        return ""


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
        if utils.is_valid_ip_address(ip) is False:
            return jsonify(message="400")
    except:
        return jsonify(message="400")
    if db.update_image_allocation_ip_vpn(token, ip) is not None:
        return jsonify(message="200")
    else:
        return jsonify(message="400")


if __name__ == '__main__':
    app.run(host="0.0.0.0")
