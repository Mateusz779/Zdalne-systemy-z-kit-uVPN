import hashlib
import secrets

def hash_password(password):
    return hashlib.sha512(password.encode('utf-8')).hexdigest()

def generate_auth_token():
    return secrets.token_urlsafe(32)