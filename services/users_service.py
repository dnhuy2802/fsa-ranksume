import http
from datetime import datetime
import pytz

from fastapi.encoders import jsonable_encoder

from scripts.context_manager import context_log_meta
# from logs import logger
from models.base import GenericResponseModel
from models.user_model import UsersModel
from data_adapter.users import Users

class UsersService:
    def __init__(self):
        pass

    async def _create_user(self, user_data_add: UsersModel):
        user_data_add_dict = jsonable_encoder(user_data_add)
        users = Users()
        new_user = users.insert_one(user_data_add_dict)
        # find the created user
        created_user = users.find_one({"_id": new_user.inserted_id})
        return created_user
    def _get_all_users(self):
        users = Users()
        users_data = users.find({})
        return users_data

    def _get_by_id_user(self, id_user: str):
        users = Users()
        user_data = users.find_one({"_id": id_user})
        return user_data

    # get all users
    @staticmethod
    async def get_all_users() -> GenericResponseModel:
        users_service = UsersService()
        users_data = users_service._get_all_users()
        users_list = [user for user in users_data]
        return GenericResponseModel(status_code=http.HTTPStatus.OK, data=users_list, message="Get all users successfully")
    
    # get user by id
    @staticmethod
    async def get_by_user(id_user: str) -> GenericResponseModel:
        user_service = UsersService()
        user_data = user_service._get_by_id_user(id_user)

        if user_data is None:
            return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND, error="User not found")
        return GenericResponseModel(status_code=http.HTTPStatus.OK, data=user_data, message="Get user successfully")

    # create user
    @staticmethod
    async def create_user(user_data_add: dict) -> GenericResponseModel:
        # Specify the Vietnam time zone
        vietnam_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        # Get the current time in UTC
        datetime_VN = datetime.now(vietnam_timezone)
        # Convert the current time to Vietnam time zone
        vietnam_now = datetime_VN.strftime("%Y-%m-%d %H:%M:%S")

        user_model = UsersModel()
        user_model.name = user_data_add.get("name")
        user_model.email = user_data_add.get("email")
        user_model.role = user_data_add.get("role")
        user_model.created_by = "2b51b8cc-f3e3-4926-9d1c-bac1a819a6b1"
        user_model.created_at = vietnam_now
        user_model.updated_at = vietnam_now

        users_service = UsersService()
        created_user = await users_service._create_user(user_model)

        return GenericResponseModel(status_code=http.HTTPStatus.CREATED, data=created_user, message="Create user successfully")
    
    # delete user by id
    @staticmethod
    async def delete_by_user(id_user: str) -> GenericResponseModel:
        users = Users()
        user_service = UsersService()
        # find user by id
        user_data = user_service._get_by_id_user(id_user)
        if user_data is None:
            return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND, error="User not found")
        users.delete_one({"_id": id_user})
        return GenericResponseModel(status_code=http.HTTPStatus.OK, message="Delete user successfully")
