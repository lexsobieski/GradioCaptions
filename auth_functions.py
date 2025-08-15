from Resources.salt import salt
import hashlib


def encrypt(password):
    result = hashlib.pbkdf2_hmac('sha256', bytes(password, "utf-8"), salt, 100000)
    return result.hex()


def auth_function(username, password, db_ref):
    user_password = db_ref.child(username).get()
    if user_password is None:
        return False
    pass_input = encrypt(password)
    if user_password == pass_input:
        return True
    return False
