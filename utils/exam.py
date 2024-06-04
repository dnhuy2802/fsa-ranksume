import os
import json

# import firebase
from configs.firebase import firebase_bucket

def upload_exam_file(file_path):
    # upload file to firebase storage from file_path
    name_file = file_path.split("/")[-1]
    # upload file to folder "chat_history" in firebase storage
    blob = firebase_bucket.blob(f"exams/{name_file}")
    blob.upload_from_filename(file_path)
    blob.make_public()
    # return Download URL of the file
    return blob.public_url

def remove_exam_file(exam_file_name):
    # remove file from firebase storage chat_history_file_name
    blob = firebase_bucket.blob("exams/" + exam_file_name)
    blob.delete()
    return True

def create_exam_file(exam_file_content, id_exam: str):
    # check if the folder exist
    if not os.path.exists("tmp"):
        os.makedirs("tmp")

    save_name = id_exam+"_exam_file.txt"
    save_path = f"tmp/{save_name}"

    with open(save_path, "wb") as f:
        f.write(exam_file_content.encode("utf-8"))

    # upload file to firebase storage
    exam_file_url = upload_exam_file(save_path)

    #remove file from local
    os.remove(save_path)

    return exam_file_url, save_name