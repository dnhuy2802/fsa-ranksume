import http
import os
import pytz
from datetime import datetime
from fastapi.encoders import jsonable_encoder

from scripts.context_manager import context_log_meta
# from logs import logger

from models.base import GenericResponseModel
from models.cv_result_model import CvResultsModel
from data_adapter.cv_results import CvResults

class CvResultsService:
    ERROR_ITEM_NOT_FOUND = "Item not found"

    def __init__(self):
        pass

    def get_all_cv_results(self):
        pass

    def _get_by_id_cv_result(self, id_cv_result: str):
        # get cv_results by id_cv_result
        cv_results = CvResults()
        query = {"_id": id_cv_result}
        cv_result = cv_results.find_one(query)
        return cv_result
    
    def _get_by_id_user(self, id_user: str):
        # get all cv_results have id_user
        cv_results = CvResults()
        query = {"id_user": id_user}
        cv_results_list = cv_results.find(query)
        return cv_results_list

    def _get_by_id_cv(self, id_cv: str):
        # get all cv_results have id_cv
        cv_results = CvResults()
        query = {"id_cv": id_cv}
        cv_results_list = cv_results.find(query)
        return cv_results_list

    def _create_cv_result(self, cv_results_data_add: dict):
        # get cv_results_data_add
        id_cv = cv_results_data_add.get("id_cv")
        id_jd = cv_results_data_add.get("id_jd")
        list_mentors = cv_results_data_add.get("list_mentors")
        id_user_config = cv_results_data_add.get("id_user_config")

        # Specify the Vietnam time zone
        vietnam_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        # Get the current time in UTC
        datetime_VN = datetime.now(vietnam_timezone)
        # Convert the current time to Vietnam time zone
        vietnam_now = datetime_VN.strftime("%Y-%m-%d %H:%M:%S")

        list_cv_result = []
        # create cv_results_model
        for mentor in list_mentors:
            cv_results_model = CvResultsModel()
            cv_results_model.id_cv = id_cv
            cv_results_model.id_jd = id_jd
            cv_results_model.id_user = mentor
            cv_results_model.id_user_config = id_user_config
            cv_results_model.cv_score = None
            cv_results_model.matching_status = False
            cv_results_model.created_at = vietnam_now
            cv_results_model.updated_at = vietnam_now

            # add to mongodb
            mongo_data_insert_dict = jsonable_encoder(cv_results_model)
            cv_results = CvResults()
            new_cv_result = cv_results.insert_one(mongo_data_insert_dict)

            # find new cv_result
            created_cv_result = cv_results.find_one({"_id": new_cv_result.inserted_id})
            list_cv_result.append(created_cv_result)
        
        return list_cv_result        
    
    def _update_cv_result(self, id_cv_result: str, data_update: dict):
        # get data_update
        cv_score = data_update.get("cv_score")
        matching_status = data_update.get("matching_status")

        # Specify the Vietnam time zone
        vietnam_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        # Get the current time in UTC
        datetime_VN = datetime.now(vietnam_timezone)
        # Convert the current time to Vietnam time zone
        updated_at = datetime_VN.strftime("%Y-%m-%d %H:%M:%S")

        # update cv_results by id_cv_result
        cv_results = CvResults()
        query = {"_id": id_cv_result}
        new_values = {"$set": {
            "cv_score": cv_score,
            "matching_status": matching_status,
            "updated_at": updated_at
        }}
        cv_results.update_one(query, new_values)

    def _delete_by_cv_result(self, id_cv_result: str):
        pass
    
    def _delete_by_cv(self, id_cv: str):
        # delete all cv_results have id_cv
        cv_results = CvResults()
        query = {"id_cv": id_cv}
        cv_results.delete_many(query)
