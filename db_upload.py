import firebase_admin
from firebase_admin import db
import json

cred_obj = firebase_admin.credentials.Certificate('key.json')
default_app = firebase_admin.initialize_app(cred_obj, {
    'databaseURL': "https://video-link-db-default-rtdb.europe-west1.firebasedatabase.app/"
    })
videos_ref = db.reference("/Videos")
with open("videos.json", "r") as f:
    file_contents = json.load(f)
videos_ref.set(file_contents)
