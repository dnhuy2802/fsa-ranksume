import http
from datetime import datetime
import pytz

from fastapi.encoders import jsonable_encoder

# from scripts.context_manager import context_log_meta
# from logs import logger

from models.base import GenericResponseModel
from models.exam_model import ExamsModel
from data_adapter.exams import Exams
from data_adapter.qdrant import QdrantDb
from utils.exam import create_exam_file, remove_exam_file

from utils.text2vector import text2vector


class ExamsService:
    ERROR_ITEM_NOT_FOUND = "Item not found"

    def __init__(self):
        pass

    # create exam
    async def _create_exam(self, mongo_data_insert: ExamsModel):
        mongo_data_insert_dict = jsonable_encoder(mongo_data_insert)
        # MongoDB insert_one data
        exams = Exams()
        new_exam = exams.insert_one(mongo_data_insert_dict)
        # find the created exam
        created_exam = exams.find_one({"_id": new_exam.inserted_id})
        return created_exam
    
    
    # upload to qdrant
    async def _upload_exam_description_to_qdrant(self, id_exam: str, exam_description: str):
        qdrant_db = QdrantDb(collection_name="RANKSUME_exams")
        # get collection_info
        collection_info = qdrant_db.collection_info
        points_count = collection_info.points_count
        # get models_qdrant
        models_qdrant = qdrant_db.models_qdrant
        # text2vector
        exam_description_vector = text2vector(exam_description)
        payload = {"id_exam": id_exam}
        point = models_qdrant.PointStruct(id=points_count+1, payload=payload, vector=exam_description_vector)
        points = [point]
        # upsert points
        qdrant_db.upsert_points(points)

    # delete exam description from qdrant
    async def _delete_exam_description_from_qdrant(self, id_exam: str):
        qdrant_db = QdrantDb(collection_name="RANKSUME_exams")
        # get models_qdrant
        models_qdrant = qdrant_db.models_qdrant
        # delete corresponding vector from Qdrant
        points_selector = models_qdrant.FilterSelector(
            filter=models_qdrant.Filter(
                must=[
                    models_qdrant.FieldCondition(
                        key="id_exam",
                        match=models_qdrant.MatchValue(value=id_exam)
                    )
                ],
            )
        )
        qdrant_db.delete_corresponding_vector(points_selector)

    def _get_by_id_exam(self, id_jd: str):
        exams = Exams()
        exam_data = exams.find_one({"_id": id_jd})
        return exam_data
    
    # get all exams
    @staticmethod
    async def get_all_exams() -> GenericResponseModel:
        exams = Exams()
        exams_data = exams.find({})
        exams_list = [exam for exam in exams_data]
        return GenericResponseModel(status_code=http.HTTPStatus.OK, message="Get all Exams", data=exams_list)
    
    @staticmethod
    async def get_exam_by_id(id_exam: str) -> GenericResponseModel:
        exam_service = ExamsService()
        exam_data = exam_service._get_by_id_exam(id_exam)
        if not exam_data:
            return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND, error=ExamsService.ERROR_ITEM_NOT_FOUND)
        return GenericResponseModel(status_code=http.HTTPStatus.OK, message="Get Exam by ID", data=exam_data)
    
    # create exam
    @staticmethod
    async def create_exam(exam_data_add: dict) -> GenericResponseModel:
        # Specify the Vietnam time zone
        vietnam_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        # Get the current time in UTC
        datetime_VN = datetime.now(vietnam_timezone)
        # Convert the current time to Vietnam time zone
        vietnam_now = datetime_VN.strftime("%Y-%m-%d %H:%M:%S")

        exams_model = ExamsModel()
        exams_model.created_at = vietnam_now
        exams_model.exam_description = exam_data_add.get("exam_description")
        exams_model.exam_file_name = exam_data_add.get("exam_file_name")
        exams_model.exam_file_content = exam_data_add.get("exam_file_content")
        exams_model.exam_file_url = None

        # add exam to MongoDB
        exam_service = ExamsService()
        created_exam = await exam_service._create_exam(exams_model)
        
        # get id_exam from created_exam
        id_exam = created_exam["_id"]
        # upload exam description to qdrant
        await exam_service._upload_exam_description_to_qdrant(id_exam=id_exam, exam_description=exams_model.exam_description)
        
        # upload to firebase storage
        exam_file_data = {}
        exam_file_url, save_name = create_exam_file(exams_model.exam_file_content, id_exam)
        exam_file_data["exam_file_url"] = exam_file_url
        exam_file_data["exam_file_name"] = save_name
        # exam_file_data["exam_file_name"] = exams_model.exam_file_name
        # exam_file_data["exam_file_name"] = save_path

        # update exam_file_url to MongoDB
        exams = Exams()
        exams.update_one({"_id": id_exam}, {"$set": exam_file_data})
        
        return GenericResponseModel(status_code=http.HTTPStatus.CREATED, message="Create Exam", data=created_exam)
    
    # deleted exam by id
    @staticmethod
    async def delete_exam_by_id(id_exam: str) -> GenericResponseModel:
        exam_service = ExamsService()
        exams = Exams()

        # get exam by id
        exam_data = exam_service._get_by_id_exam(id_exam)
        if not exam_data:
            return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND, error=ExamsService.ERROR_ITEM_NOT_FOUND)\
        
        exam_file_name = exam_data["exam_file_name"]
        if exam_file_name:
            # remove exam file from firebase storage
            remove_exam_file(exam_file_name)

        # delete exam description from qdrant
        exam_service = ExamsService()
        await exam_service._delete_exam_description_from_qdrant(id_exam=id_exam)
        
        # delete exam from MongoDB
        exams.delete_one({"_id": id_exam})

        return GenericResponseModel(status_code=http.HTTPStatus.OK, message="Exam deleted successfully")