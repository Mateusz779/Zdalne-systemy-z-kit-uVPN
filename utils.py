import hashlib
import secrets
import string
import random
import os

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