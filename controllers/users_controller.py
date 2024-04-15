import http

from fastapi import APIRouter, Body, UploadFile, File, Depends

from models.base import GenericResponseModel
from models.user_model import CreateUsersModel
from services.users_service import UsersService

from utils.helper import check_email_input

users_router = APIRouter(prefix="/apis/users", tags=["users"])

# get all users
@users_router.get('/',status_code=http.HTTPStatus.OK,response_model=GenericResponseModel)
async def get_all_users():
    response = await UsersService.get_all_users()
    return response

# get user by id
@users_router.get('/{id_user}',status_code=http.HTTPStatus.OK,response_model=GenericResponseModel)
async def get_by_user(id_user: str):
    response = await UsersService.get_by_user(id_user=id_user)
    return response

# create user
@users_router.post('/',status_code=http.HTTPStatus.CREATED, response_model=GenericResponseModel, response_model_by_alias=False)
# async def create_user(name: str = Body(...), email: str = Body(...), role: str = Body(...)):
async def create_user(user_add:CreateUsersModel = Body()):
    user_data_add = user_add.model_dump()
    #role only accept "admin" or "hr" or "mentor"
    if user_data_add.get("role") not in ["admin", "hr", "mentor"]:
        return GenericResponseModel(status_code=http.HTTPStatus.BAD_REQUEST, error='Invalid role: role only accept "admin" or "hr" or "mentor"')
    #validate email
    if not check_email_input(user_data_add.get("email")):
        return GenericResponseModel(status_code=http.HTTPStatus.BAD_REQUEST, error="Invalid email")
    
    response = await UsersService.create_user(user_data_add=user_data_add)
    return response

# delete user by id
@users_router.delete('/{id_user}',status_code=http.HTTPStatus.OK,response_model=GenericResponseModel)
async def delete_by_user(id_user: str):
    response = await UsersService.delete_by_user(id_user=id_user)
    return response
