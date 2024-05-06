import http
from datetime import datetime
import pytz

from fastapi.encoders import jsonable_encoder

from scripts.context_manager import context_log_meta
# from logs import logger

from models.base import GenericResponseModel
from models.jd_model import JdsModel
from data_adapter.jds import Jds
from data_adapter.qdrant import QdrantDb

from utils.summary_jd import summary_jd
from utils.text2vector import text2vector
from utils.jd_history import create_jd_history, remove_file_chat_history

class JdsService:
    ERROR_ITEM_NOT_FOUND = "Item not found"

    def __init__(self):
        pass
        
    # create jd
    async def _create_jd(self, mongo_data_insert: JdsModel):
        mongo_data_insert_dict = jsonable_encoder(mongo_data_insert)
        # MongoDB insert_one data
        jds = Jds()
        new_jd = jds.insert_one(mongo_data_insert_dict)
        # find the created jd
        created_jd = jds.find_one({"_id": new_jd.inserted_id})
        return created_jd

    # upload to qdrant
    async def _upload_jd_summary_to_qdrant(self, id_jd: str, jd_summary: str):
        qdrant_db = QdrantDb(collection_name="jds")
        # get collection_info
        collection_info = qdrant_db.collection_info
        points_count = collection_info.points_count
        # get models_qdrant
        models_qdrant = qdrant_db.models_qdrant
        # text2vector
        summary_jd_vector = text2vector(jd_summary)
        payload = {"id_jd": id_jd}
        point = models_qdrant.PointStruct(id=points_count+1, payload=payload, vector=summary_jd_vector)
        points = [point]
        # upsert points
        qdrant_db.upsert_points(points)
    
    # delete jd summary from qdrant
    async def _delete_jd_summary_from_qdrant(self, id_jd: str):
        qdrant_db = QdrantDb(collection_name="jds")
        # get models_qdrant
        models_qdrant = qdrant_db.models_qdrant
        # delete corresponding vector from Qdrant
        points_selector = models_qdrant.FilterSelector(
            filter=models_qdrant.Filter(
                must=[
                    models_qdrant.FieldCondition(
                        key="id_jd",
                        match=models_qdrant.MatchValue(value=id_jd),
                    ),
                ],
            )
        )
        qdrant_db.delete_corresponding_vector(points_selector)

    def _get_by_id_jd(self, id_jd: str):
        jds = Jds()
        jd_data = jds.find_one({"_id": id_jd})
        return jd_data

    # get all jds
    @staticmethod
    async def get_all_jds() -> GenericResponseModel:
        jds = Jds()
        jds_data = jds.find({})
        jds_list = [jd for jd in jds_data]
        return GenericResponseModel(status_code=http.HTTPStatus.OK, message="Get All JD", data=jds_list)

    # get jd by id
    @staticmethod
    async def get_by_jd(id_jd: str) -> GenericResponseModel:
        jd_service = JdsService()
        jd_data = jd_service._get_by_id_jd(id_jd)
        if not jd_data:
            # logger.error(extra=context_log_meta.get(), msg=JdsService.ERROR_ITEM_NOT_FOUND)
            return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND, error=JdsService.ERROR_ITEM_NOT_FOUND)
        return GenericResponseModel(status_code=http.HTTPStatus.OK, message="Get JD by ID", data=jd_data)
    
    @staticmethod
    async def create_jd(jd_data_add: dict) -> GenericResponseModel:
        # summary jd
        jd_summary = summary_jd(jd_data_add["jd_text"])
        # Specify the Vietnam time zone
        vietnam_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        # Get the current time in UTC
        datetime_VN = datetime.now(vietnam_timezone)
        # Convert the current time to Vietnam time zone
        vietnam_now = datetime_VN.strftime("%Y-%m-%d %H:%M:%S")

        jds_model = JdsModel()
        jds_model.name_jd = jd_data_add.get("name_jd")
        jds_model.chat_history_file_name = None
        jds_model.chat_history_url = None
        jds_model.have_exam = False
        jds_model.id_exam = None
        jds_model.is_generate_exam = False
        jds_model.jd_summary = jd_summary
        jds_model.jd_text = jd_data_add.get("jd_text")
        jds_model.created_by = jd_data_add.get("created_by")
        jds_model.created_at = vietnam_now
        jds_model.updated_at = vietnam_now

        # add to mongodb
        jd_service = JdsService()
        created_jd = await jd_service._create_jd(jds_model)

        # get id_jd from created_jd
        id_jd = created_jd["_id"]
        # upload to qdrant
        await jd_service._upload_jd_summary_to_qdrant(id_jd=id_jd, jd_summary=jd_summary)

        # Create JD history
        history_save_data = {}
        chat_history_url, save_json_name = create_jd_history(jd_summary, id_jd)
        history_save_data["chat_history_url"] = chat_history_url
        history_save_data["chat_history_file_name"] = save_json_name
        
        # update jd with chat_history_url and chat_history_file_name
        jds = Jds()
        jds.update_one({"_id": id_jd}, {"$set": history_save_data})

        return GenericResponseModel(status_code=http.HTTPStatus.CREATED, message="JD Created Successfully", data=created_jd)

    # delete jd by id
    @staticmethod
    async def delete_by_jd(id_jd: str) -> GenericResponseModel:
        jd_service = JdsService()
        jds = Jds()
        
        # get jd by id
        jd_data = jd_service._get_by_id_jd(id_jd)
        if not jd_data:
            # logger.error(extra=context_log_meta.get(), msg=JdsService.ERROR_ITEM_NOT_FOUND)
            return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND, error=JdsService.ERROR_ITEM_NOT_FOUND)
        
        # Delete history of JD
        chat_history_file_name = jd_data["chat_history_file_name"]
        if chat_history_file_name:
            # delete chat_history_file_name
            remove_file_chat_history(chat_history_file_name)
        
        # delete jd summary from qdrant
        jd_service = JdsService()
        await jd_service._delete_jd_summary_from_qdrant(id_jd=id_jd)
        
        # delete jd from mongodb
        jds.delete_one({"_id": id_jd})

        return GenericResponseModel(status_code=http.HTTPStatus.OK, message="JD Deleted Successfully")
