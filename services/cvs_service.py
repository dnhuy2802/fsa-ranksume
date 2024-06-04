import http
import os
import pytz
from uuid import UUID, uuid4
from datetime import datetime
from fastapi.encoders import jsonable_encoder

# import firebase
from configs.firebase import firebase_bucket

# from scripts.context_manager import context_log_meta
# from logs import logger

from models.base import GenericResponseModel
from models.cv_model import CvsModel
from data_adapter.cvs import Cvs
from services.cv_results_service import CvResultsService

from utils.file2txt import file_pdf2text, file_docx2text

class CvsService:
    ERROR_ITEM_NOT_FOUND = "Item not found"

    def __init__(self):
        pass
    
    def _upload_file_cvs(self, file_path):
        # upload file to firebase storage from file_path
        name_file = file_path.split("/")[-1]
        # upload file to folder "cvs" in firebase storage
        blob = firebase_bucket.blob(f"cvs/{name_file}")
        blob.upload_from_filename(file_path)
        blob.make_public()
        # return Download URL of the file
        return blob.public_url

    def _remove_file_cvs(self, file_cv_name):
        # remove file from firebase storage using "gs://" link
        blob = firebase_bucket.blob("cvs/" + file_cv_name)
        blob.delete()
        return True

    def _create_cv(self, cv_data: dict):
        cv_service = CvsService()
        # get file_cv
        file_cv = cv_data.get("file_cv")
        # rename file name to uuid
        re_name_file = str(uuid4()).replace("-","_") + "_" + file_cv.filename
        # save uploaded file to tmp folder
        cache_path = f"tmp/{re_name_file}"
        with open(cache_path, "wb") as buffer:
            buffer.write(file_cv.file.read())
        
        # take file_cv and cv_upload type file
        file_cv_type = file_cv.filename.split(".")[-1]
        cv_text = None
        if file_cv_type in ["pdf", "PDF"]:
            cv_text = file_pdf2text(cache_path)
        elif file_cv_type in ["docx", "DOCX"]:
            cv_text = file_docx2text(cache_path)
        else:
            return GenericResponseModel(status_code=http.HTTPStatus.BAD_REQUEST, error="Invalid file type")
        # Upload file to firebase storage
        file_cv_url = cv_service._upload_file_cvs(cache_path)
        # Delete the file from the tmp folder
        os.remove(cache_path)
        
        # Specify the Vietnam time zone
        vietnam_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        # Get the current time in UTC
        datetime_VN = datetime.now(vietnam_timezone)
        # Convert the current time to Vietnam time zone
        vietnam_now = datetime_VN.strftime("%Y-%m-%d %H:%M:%S")

        # create cv model
        cvs_model = CvsModel()
        cvs_model.cv_content = cv_text
        cvs_model.file_cv_name = re_name_file
        cvs_model.file_cv_url = file_cv_url
        cvs_model.extract_status = False
        cvs_model.extract_result = None
        cvs_model.created_by = cv_data.get("created_by")
        cvs_model.created_at = vietnam_now

        # add to mongodb
        cvs = Cvs()
        mongo_data_insert_dict = jsonable_encoder(cvs_model)
        new_cv = cvs.insert_one(mongo_data_insert_dict)

        # find new cv
        created_cv = cvs.find_one({"_id": new_cv.inserted_id})
        return created_cv
    
    def _update_cv(self, id_cv: str, data_update: dict):
        # get cv from mongodb
        cvs = Cvs()

        # update cv by id_cv
        query = {"_id": id_cv}
        new_values = {"$set": {
            "extract_status": data_update.get("extract_status"),
            "extract_result": data_update.get("extract_result"),
        }}
        cvs.update_one(query, new_values)

    def _get_by_id_cv(self, id_cv: str):
        # get cv from mongodb
        cvs = Cvs()
        cv = cvs.find_one({"_id": id_cv})
        return cv

    def _get_all_cvs(self):
        # get all cvs from mongodb
        cvs = Cvs()
        all_cvs = cvs.find({})
        return all_cvs
    
    def _get_by_query(self, query: dict):
        # get cv from mongodb
        cvs = Cvs()
        cv = cvs.find_one(query)
        return cv

    # get all cvs
    @staticmethod
    async def get_all_cvs():
        cvs_list = []
        cvs = Cvs()
        # get all cvs from mongodb
        cv_service = CvsService()
        all_cvs = cv_service._get_all_cvs()

        # get cv_results using id_cv from mongodb
        cv_results_service = CvResultsService()
        for cv in all_cvs:
            cv_results = cv_results_service._get_by_id_cv(cv.get("_id"))
            cvs_list.append({
                "cv": cv,
                "list_cv_result": cv_results
            })

        return GenericResponseModel(status_code=http.HTTPStatus.OK, data=cvs_list)
    
    # get cv by id
    @staticmethod
    async def get_by_id_cv(id_cv: str) -> GenericResponseModel:
        # get cv from mongodb
        cv_service = CvsService()
        cv = cv_service._get_by_id_cv(id_cv)

        # get cv_results using id_cv from mongodb
        cv_results_service = CvResultsService()
        cv_results = cv_results_service._get_by_id_cv(id_cv)

        data_response = {
            "cv": cv,
            "cv_result": cv_results
        }

        return GenericResponseModel(status_code=http.HTTPStatus.OK, data=data_response, message="Get CV by ID Successfully")
    
    # create cv
    @staticmethod
    async def create_cv(list_cv_add:dict) -> GenericResponseModel:
        # get data from controller
        id_jd = list_cv_add.get("id_jd")
        list_mentors = list_cv_add.get("list_mentors")
        files_cvs = list_cv_add.get("files_cvs")

        count_sucessful = 0
        count_failed = 0
        cvs_list = []
        for file_cv in files_cvs:
            each_cv = {}
            file_cv_type = file_cv.filename.split(".")[-1]
            if file_cv_type in ["pdf", "docx", "PDF", "DOCX"]:
                # Add CV to the database
                cv_service = CvsService()
                cv_data_add = {
                    "id_jd": id_jd,
                    "list_mentors": list_mentors,
                    "file_cv": file_cv,
                    "created_by": "Admin"
                }
                created_cv = cv_service._create_cv(cv_data_add)

                # Add CV to the CV results database
                cv_results_service = CvResultsService()
                cv_results_data_add = {
                    "id_cv": created_cv["_id"],
                    "id_jd": id_jd,
                    "list_mentors": list_mentors,
                    "id_user_config": "id_user_config"
                }
                created_list_cv_result = cv_results_service._create_cv_result(cv_results_data_add)

                # add to each_cv
                each_cv["cv"] = created_cv
                each_cv["list_cv_result"] = created_list_cv_result
                # add to cvs_list
                cvs_list.append(each_cv)
                count_sucessful += 1
            else:
                count_failed += 1
        
        return GenericResponseModel(status_code=http.HTTPStatus.CREATED, data=cvs_list)
    
    # delete cv by id
    @staticmethod
    async def delete_by_cv(id_cv: str) -> GenericResponseModel:
        cv_service = CvsService()
        cvs = Cvs()
        # get cv from mongodb
        cv = cv_service._get_by_id_cv(id_cv)

        # remove file from firebase storage
        cv_service._remove_file_cvs(cv.get("file_cv_name"))

        # delete cv_result from mongodb
        cv_results_service = CvResultsService()
        cv_results_service._delete_by_cv(id_cv)

        # delete cv from mongodb
        cvs.delete_one({"_id": id_cv})

        return GenericResponseModel(status_code=http.HTTPStatus.OK, message="CV Deleted Successfully")