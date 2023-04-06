from flask import Flask, send_file

app = Flask(__name__)

@app.route("/api/getvpn")
def hello_world():
    return send_file("praktyki.squashfs")