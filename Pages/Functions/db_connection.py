import firebase_admin
from firebase_admin import db

KEY_PATH = '../Resources/key.json'

cred_obj = firebase_admin.credentials.Certificate(KEY_PATH)
default_app = firebase_admin.initialize_app(cred_obj, {
    'databaseURL': "https://video-link-db-default-rtdb.europe-west1.firebasedatabase.app/"
    })
videos_ref = db.reference("/Videos")
users_ref = db.reference("/Users")
