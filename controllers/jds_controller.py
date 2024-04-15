import http

from fastapi import APIRouter, UploadFile, File, Body

from models.base import GenericResponseModel
from services.jds_service import JdsService

jds_router = APIRouter(prefix="/apis/jds", tags=["jds"])

# get all jds
@jds_router.get('/',status_code=http.HTTPStatus.OK,response_model=GenericResponseModel)
async def get_all_jds():
    response = await JdsService.get_all_jds()
    return response

# get jd by id
@jds_router.get('/{id_jd}',status_code=http.HTTPStatus.OK,response_model=GenericResponseModel)
async def get_by_jd(id_jd: str):
    response = await JdsService.get_by_jd(id_jd=id_jd)
    return response

# create jd
@jds_router.post('/',status_code=http.HTTPStatus.CREATED, response_model=GenericResponseModel, response_model_by_alias=False)
async def create_jd(name_jd: str = Body(...), 
                    created_by: str = Body(...), 
                    file_jd: UploadFile = File(..., description="Upload jd file (upload .txt)")):
    try:
        file_jd_type = file_jd.filename.split(".")[-1]
        if file_jd_type != "txt":
            return GenericResponseModel(status_code=http.HTTPStatus.BAD_REQUEST, error="Invalid file type")
        
        jd_text = file_jd.file.read().decode("utf-8")
        jd_data_add = {
            "name_jd": name_jd,
            "jd_text": jd_text,
            "created_by": created_by
        }
        response = await JdsService.create_jd(jd_data_add=jd_data_add)
        return response
    except Exception as e:
        return GenericResponseModel(status_code=http.HTTPStatus.BAD_REQUEST, error=f"Cannot Create JD with error: {e}")

# delete jd by id
@jds_router.delete('/{id_jd}',status_code=http.HTTPStatus.OK,response_model=GenericResponseModel)
async def delete_by_jd(id_jd: str):
    response = await JdsService.delete_by_jd(id_jd=id_jd)
    return response
