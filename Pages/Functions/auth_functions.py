from ..Resources.salt import salt
import hashlib
from .db_connection import users_ref, get_user_ref


def encrypt(password):
    result = hashlib.pbkdf2_hmac('sha256', bytes(password, "utf-8"), salt, 100000)
    return result.hex()


def get_password_by_username(username):
    user_password = users_ref.child(username).get()
    return user_password


def auth_function(username, password):
    user_password = get_password_by_username(username)
    if user_password is None:
        return False
    pass_input = encrypt(password)
    if user_password == pass_input:
        return True
    return False


def register(username, password):
    if get_password_by_username(username) is not None:
        return "Registration error: Username already exists"
    user_ref = get_user_ref(username)
    pass_hash = encrypt(password)
    user_ref.set(pass_hash)
    return "Registration successful!"

