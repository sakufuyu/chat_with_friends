# generate_temp_password.py
import secrets
import string
from flask_bcrypt import generate_password_hash, check_password_hash


def generate_temp_password(length):
    pass_chars = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(pass_chars) for _ in range(length))
    return password


def hashing_password(password):
    return str(generate_password_hash(password))[2:-1]


def confirm_password(hashed_pass, entered_pass):
    return check_password_hash(hashed_pass, entered_pass)
