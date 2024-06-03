import http
from fastapi import APIRouter, HTTPException, Body

from models.base import GenericResponseModel
from services.matching_cv_service import MatchingCvService
from services.cv_results_service import CvResultsService
from services.jds_service import JdsService
from services.cvs_service import CvsService
from services.users_service import UsersService

matching_cv_router = APIRouter(prefix="/apis/matching_cv", tags=["Matching CV"])

@matching_cv_router.get("/", status_code=http.HTTPStatus.OK, response_model=GenericResponseModel)
async def get_all_matching_cv_by_id_user():
    id_user = "495da79f-9ab0-46b7-84d7-698ca0f6e227" # change to get from userDB

    # check role of user
    users_service = UsersService()
    user = users_service._get_by_id_user(id_user)
    role = user.get("role")

    matching_cv_service = MatchingCvService()
    response = await matching_cv_service.get_all_matching_cv_by_role(id_user=id_user, role=role)
    return response

@matching_cv_router.post("/matching", status_code=http.HTTPStatus.OK, response_model=GenericResponseModel)
async def matching_cv(id_cv_result: str = Body(...),
                      config_setup: str|dict = Body(...)):
    # {
    #     "education_score_config": {
    #         "W_education_score": 0.05
    #     },
    #     "language_score_config": {
    #         "W_language_score": 0.05
    #     },
    #     "technical_score_config": {
    #         "W_technical_score": 0.35
    #     },
    #     "experience_score_config": {
    #         "W_experience_score": 0.55,
    #         "relevance_score_w": 0.8,
    #         "difficulty_score_w": 0.15,
    #         "duration_score_w": 0.05
    #     }
    # }
    data_matching = {
        "id_cv_result": id_cv_result,
        "config_setup": config_setup,   
        "re_extract": False
    }
    # check matching_status
    cv_results_service = CvResultsService()
    cv_result = cv_results_service._get_by_id_cv_result(id_cv_result)
    matching_status = cv_result.get("matching_status")
    if matching_status:
        return GenericResponseModel(status_code=http.HTTPStatus.BAD_REQUEST, message="CV is already matched")
    
    matching_cv_service = MatchingCvService()
    # check config_setup if it is a dict
    if isinstance(config_setup, dict):
        result_check_msg = matching_cv_service.check_config_score(data_matching.get("config_setup"))
        if result_check_msg != True:
            return GenericResponseModel(status_code=http.HTTPStatus.BAD_REQUEST, message=result_check_msg)
        print("config_setup is dict was checked")
    
    response = await matching_cv_service.matching_cv(data_matching)
    return response

@matching_cv_router.post("/rematching", status_code=http.HTTPStatus.OK, response_model=GenericResponseModel)
async def re_matching_cv(id_cv_result: str = Body(...),
                        config_setup: str|dict = Body(...),
                        re_extract: bool = Body(...)):
    data_re_matching = {
        "id_cv_result": id_cv_result,
        "config_setup": config_setup,
        "re_extract": re_extract
    }
    # check matching_status
    cv_results_service = CvResultsService()
    cv_result = cv_results_service._get_by_id_cv_result(id_cv_result)
    matching_status = cv_result.get("matching_status")
    if matching_status == False:
        return GenericResponseModel(status_code=http.HTTPStatus.BAD_REQUEST, message="CV is not matched yet")
    
    matching_cv_service = MatchingCvService()
    # check config_setup if it is a dict
    if isinstance(config_setup, dict):
        result_check_msg = matching_cv_service.check_config_score(data_re_matching.get("config_setup"))
        if result_check_msg != True:
            return GenericResponseModel(status_code=http.HTTPStatus.BAD_REQUEST, message=result_check_msg)
        print("config_setup is dict was checked")
    
    response = await matching_cv_service.matching_cv(data_re_matching)
    return response