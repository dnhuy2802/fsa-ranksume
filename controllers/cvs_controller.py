import http
from fastapi import APIRouter, Body, File, UploadFile, Query

from models.base import GenericResponseModel
from services.cvs_service import CvsService

cvs_router = APIRouter(prefix="/apis/cvs", tags=["CRUD_cvs"])

# get all cvs
@cvs_router.get('/',status_code=http.HTTPStatus.OK ,response_model=GenericResponseModel)
async def get_all_cvs():
    response = await CvsService.get_all_cvs()
    return response

# get cv by id
@cvs_router.get('/{id_cv}',status_code=http.HTTPStatus.OK,response_model=GenericResponseModel)
async def get_by_id_cv(id_cv: str):
    response = await CvsService.get_by_id_cv(id_cv=id_cv)
    return response

# create cv
@cvs_router.post('/',status_code=http.HTTPStatus.CREATED, response_model_by_alias=False)
async def create_cv(id_jd: str = Body(...),
                    # list_mentors: list[str] = Query(...),
                    files_cvs: list[UploadFile] = File(..., description="Upload cv files (upload .pdf or .docx)")):
    list_cv_add = {
       "id_jd": id_jd,
       "list_mentors": ["495da79f-9ab0-46b7-84d7-698ca0f6e227","9e1126c1-d0e8-42cc-a045-6c99226647d2"],
       "files_cvs": files_cvs
    }
    response = await CvsService.create_cv(list_cv_add)
    return response

# delete cv by id
@cvs_router.delete('/{id_cv}',status_code=http.HTTPStatus.OK,response_model=GenericResponseModel)
async def delete_by_cv(id_cv: str):
    response = await CvsService.delete_by_cv(id_cv=id_cv)
    return response
