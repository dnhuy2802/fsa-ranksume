import http

from fastapi import APIRouter

from models.base import GenericResponseModel
from services.cvs_service import CvsService

cvs_router = APIRouter(prefix="/apis/cvs", tags=["cvs"])

# get all cvs
@cvs_router.get('/',status_code=http.HTTPStatus.OK ,response_model=GenericResponseModel)
async def get_all_cvs():
    response = await CvsService.get_all_cvs()
    return response
