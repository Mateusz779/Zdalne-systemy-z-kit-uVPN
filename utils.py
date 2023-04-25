import datetime
import hashlib
import secrets
import string
import random
import os
import subprocess
import threading
from time import sleep
import db
import config
import ipaddress

DELETE_TIMEOUT = 30
RESTART_DELETE_THREAD = 10


def generate_random_string(length):
    letters = string.ascii_letters
    random_string = ''.join(random.choice(letters) for i in range(length))
    return random_string


def hash_password(password):
    return hashlib.sha512(password.encode('utf-8')).hexdigest()


def generate_auth_token():
    return secrets.token_urlsafe(32)


def ping_client(ip):
    response = os.system("ping -c 1 " + ip + "> /dev/null")

    if response == 0:
        return True
    else:
        return False


def ssh_thread_function():
    try:
        os.mkdir(os.path.join(os.getcwd(), 'keys'))
    except:
        pass
    if os.path.exists(os.path.join(os.getcwd(), 'keys', "sshkey")) is False:
        subprocess.run(['ssh-keygen', '-t rsa ', '-f key', '-q', '-P ""'])
    
    subprocess.run(['wssh', '--fbidhttp=False', '--port='+config.webssh_port, 
                    '--hostfile='+os.path.join(os.getcwd(), 'keys', "sshkey")])


def check_allocation_thread_function():
    while True:
        ids = db.get_image_allocation_all()
        if ids is not None:
            for x in ids:
                ip = db.get_image_allocation_clientip_id_vpn(x[0])
                ping_thread = PingThread(ip, x[0])
                ping_thread.start()

        sleep(RESTART_DELETE_THREAD)


class PingThread(threading.Thread):
    def __init__(self, ip, id):
        super(PingThread, self).__init__()
        self.Ip = ip
        self.Id = id

    def run(self):
        if self.Ip is None:
            return
        if ping_client(self.Ip) == False:
            date = db.get_image_allocation_time_id(self.Id)
            if date is None:
                return
            delta = datetime.datetime.utcnow() - date
            if delta.total_seconds() > DELETE_TIMEOUT:
                db.del_image_allocation_id(self.Id)
        else:
            db.update_image_allocation_time(self.Id)


def init_threads():
    ssh_thread = threading.Thread(target=ssh_thread_function)
    ssh_thread.start()

    allocation_thread = threading.Thread(
        target=check_allocation_thread_function)
    allocation_thread.start()


def is_valid_ip_address(ip: str) -> bool:
    try:
        ipaddress.IPv4Address(ip)
        return True
    except ipaddress.AddressValueError:
        try:
            ipaddress.IPv6Address(ip)
            return True
        except:
            pass
        return False
