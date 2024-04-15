import firebase_admin
from firebase_admin import credentials
# from firebase_admin import firestore
from firebase_admin import storage

import os
from dotenv import load_dotenv

# load the environment variables
load_dotenv()

firebase_url_storageBucket = os.getenv("RANKSUME_FIREBASE_URL_STORAGEBUCKET")

# get credentials from .env
credential_firebase = {
    "type": os.getenv("RANKSUME_FIREBASE_TYPE"),
    "project_id": os.getenv("RANKSUME_FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("RANKSUME_FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("RANKSUME_FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.getenv("RANKSUME_FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("RANKSUME_FIREBASE_CLIENT_ID"),
    "auth_uri": os.getenv("RANKSUME_FIREBASE_AUTH_URI"),
    "token_uri": os.getenv("RANKSUME_FIREBASE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("RANKSUME_FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("RANKSUME_FIREBASE_CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("RANKSUME_FIREBASE_UNIVERSE_DOMAIN")
}

# check if firebase is not initialized
if not firebase_admin._apps:
    # Initialize the app with a service account, granting admin privileges
    cred = credentials.Certificate(credential_firebase)
    firebase_admin.initialize_app(cred, {
        'storageBucket': firebase_url_storageBucket
    })

# # Initialize Firestore
# firebase_db = firestore.client()
# print("Firestore connected")

# Initialize Storage
firebase_bucket = storage.bucket(app=firebase_admin.get_app())
print("Storage connected")

# setup CORS allow for http://localhost:3000 in google cloud storage
firebase_bucket.cors = [{
    "origin": ["http://localhost:3000"],
    "responseHeader": ["*"],
    "method": ["GET"],
    "maxAgeSeconds": 3600
}]
firebase_bucket.patch()
print("CORS setup successfully")
