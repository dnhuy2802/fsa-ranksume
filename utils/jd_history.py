import os
import json

from langchain.memory import ConversationBufferMemory
from langchain.schema import messages_to_dict
from langchain.chains import LLMChain

# import promt template
from scripts.chat_templates import chat_template_history_jd
from configs.llm_model import llm

# import firebase
from configs.firebase import firebase_bucket

def upload_file_chat_history(file_path):
    # upload file to firebase storage from file_path
    name_file = file_path.split("/")[-1]
    # upload file to folder "chat_history" in firebase storage
    blob = firebase_bucket.blob(f"chat_histories/{name_file}")
    blob.upload_from_filename(file_path)
    blob.make_public()
    # return Download URL of the file
    return blob.public_url

def remove_file_chat_history(chat_history_file_name):
    # remove file from firebase storage chat_history_file_name
    blob = firebase_bucket.blob("chat_histories/" + chat_history_file_name)
    blob.delete()
    return True

def create_jd_history(jd_summary: str, id_jd: str):
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    chat_llm_chain_jd = LLMChain(
        llm=llm,
        prompt=chat_template_history_jd,
        verbose=True,
        memory=memory,
    )

    chat_llm_chain_jd.invoke({"jd_summary": jd_summary})

    # check if the folder exist
    if not os.path.exists("tmp"):
        os.makedirs("tmp")

    save_json_name = id_jd+"_chat_history.json"
    save_json_path = f"tmp/{save_json_name}"

    extracted_messages = chat_llm_chain_jd.memory.chat_memory.messages
    ingest_to_db = messages_to_dict(extracted_messages)

    json_history = json.dumps(ingest_to_db)
    with open(save_json_path, 'w') as f:
        f.write(json_history)

    # upload file to firebase storage
    chat_history_url = upload_file_chat_history(save_json_path)

    # remove file from local
    os.remove(save_json_path)

    return chat_history_url, save_json_name
