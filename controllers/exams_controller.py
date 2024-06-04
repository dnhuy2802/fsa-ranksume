import http

from fastapi import APIRouter, UploadFile, File, Body

from models.base import GenericResponseModel
from services.exams_service import ExamsService

exams_router = APIRouter(prefix="/apis/exams", tags=["CRUD_exams"])

# get all exams
@exams_router.get('/', status_code=http.HTTPStatus.OK, response_model=GenericResponseModel)
async def get_all_exams():
    response = await ExamsService.get_all_exams()
    return response

# get exam by id
@exams_router.get('/{id_exam}', status_code=http.HTTPStatus.OK, response_model=GenericResponseModel)
async def get_exam_by_id(id_exam: str):
    response = await ExamsService.get_exam_by_id(id_exam=id_exam)
    return response

# create exam
# @exams_router.post('/',status_code=http.HTTPStatus.CREATED, response_model=GenericResponseModel, response_model_by_alias=False)
# async def create_exam(exam_description: str = Body(...),
#                         exam_file: UploadFile = File(..., description="Upload exam file (upload .txt or .pdf)")):
#     try:
#         exam_file_type = exam_file.filename.split(".")[-1]
#         if exam_file_type != "txt" and exam_file_type != "pdf":
#             return GenericResponseModel(status_code=http.HTTPStatus.BAD_REQUEST, error="Invalid file type")
        
#         exam_content = exam_file.file.read().decode("utf-8")
#         exam_data_add = {
#             "exam_description": exam_description,
#             "exam_file_name": exam_file.filename,
#             "exam_file_content": exam_content
#         }

#         response = await ExamsService.create_exam(exam_data_add=exam_data_add)
#         return response
#     except Exception as e:
#         return GenericResponseModel(status_code=http.HTTPStatus.BAD_REQUEST, error=f"Cannot create Exam with error: {e}")

@exams_router.post('/',status_code=http.HTTPStatus.CREATED, response_model=GenericResponseModel, response_model_by_alias=False)
async def create_exam(exam_description: str = Body(...),
                        exam_file: UploadFile = File(..., description="Upload exam file (upload .txt or .pdf)")):
    try:
        exam_file_type = exam_file.filename.split(".")[-1]
        if exam_file_type != "txt" and exam_file_type != "pdf":
            return GenericResponseModel(status_code=http.HTTPStatus.BAD_REQUEST, error="Invalid file type")
        
        exam_content = exam_file.file.read().decode("utf-8")
        exam_data_add = {
            "exam_description": exam_description,
            "exam_file_name": exam_file.filename,
            "exam_file_content": exam_content
        }

        response = await ExamsService.create_exam(exam_data_add=exam_data_add)
        return response
    except Exception as e:
        return GenericResponseModel(status_code=http.HTTPStatus.BAD_REQUEST, error=f"Cannot create Exam with error: {e}")

# delete exam by id
@exams_router.delete('/{id_exam}',status_code=http.HTTPStatus.OK,response_model=GenericResponseModel)
async def delete_exam_by_id(id_exam: str):
    response = await ExamsService.delete_exam_by_id(id_exam=id_exam)
    return response