from ..Resources.salt import salt
import hashlib
from db_connection import users_ref


def encrypt(password):
    result = hashlib.pbkdf2_hmac('sha256', bytes(password, "utf-8"), salt, 100000)
    return result.hex()


def auth_function(username, password):
    user_password = users_ref.child(username).get()
    if user_password is None:
        return False
    pass_input = encrypt(password)
    if user_password == pass_input:
        return True
    return False
