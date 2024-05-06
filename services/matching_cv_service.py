import http
import json
from urllib.request import urlopen

from services.cv_results_service import CvResultsService
from services.jds_service import JdsService
from services.cvs_service import CvsService
from services.users_service import UsersService
from models.base import GenericResponseModel

from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
from langchain_core.output_parsers import JsonOutputParser
from langchain.schema import messages_from_dict
parser = JsonOutputParser()

from scripts.chat_templates import chat_template_cv_matching, input_data_cv_matching
from configs.llm_model import llm
from utils.calculate_score_matching import calculate_matching_score

class MatchingCvService:
    def __init__(self) -> None:
        pass

    def _get_all_matching_cv_by_role_mentor(self, id_user:str):
        all_cv_by_mentor = list()
        cv_results_service = CvResultsService()
        cv_results_list = cv_results_service._get_by_id_user(id_user)
        for cv_result in cv_results_list:
            cv_result_dict = dict()
            id_cv_result = cv_result.get("_id")

            # get cv_data by id_cv
            id_cv = cv_result.get("id_cv")
            cvs_service = CvsService()
            cv_data = cvs_service._get_by_id_cv(id_cv)

            # get jd_data by id_jd
            id_jd = cv_result.get("id_jd")
            jds_service = JdsService()
            jd_data = jds_service._get_by_id_jd(id_jd)

            # get user_data by id_user
            user_service = UsersService()
            user_data = user_service._get_by_id_user(id_user)
            # Add to cv_result_dict
            cv_result_dict[id_cv_result] = {
                "cv_data": cv_data,
                "jd_data": jd_data,
                "user_data": user_data
            }
            all_cv_by_mentor.append(cv_result_dict)
        return all_cv_by_mentor
    
    def _get_all_matching_cv_by_role_hr(self, id_user:str):
        all_cv_by_hr = list()
        cv_service = CvsService()
        pass

    def _load_history_and_matching(self, cv_need_matching: str, jd_summary: str, chat_history_url: str):
        response = urlopen(chat_history_url)
        retrieve_from_db = json.loads(response.read())

        retrieved_messages = messages_from_dict(retrieve_from_db)
        retrieved_chat_history = ChatMessageHistory(messages=retrieved_messages)

        retrieved_memory = ConversationBufferMemory(chat_memory=retrieved_chat_history, memory_key="chat_history", return_messages=True)
        chat_llm_chain_matchcv = LLMChain(
            llm=llm,
            prompt=chat_template_cv_matching,
            verbose=True,
            memory=retrieved_memory,)
        
        input_data = input_data_cv_matching(cv_need_matching=cv_need_matching, jd_summary=jd_summary)
        
        llm_response = chat_llm_chain_matchcv.invoke({"input_data_cv_matching": input_data})
        matched_result = llm_response.get("text")
        # convert matched_result to json
        matched_result = parser.parse(matched_result)
        
        return matched_result
    
    def check_config_score(self, config_score: dict):
        # Technical score weight
        W_technical_score = config_score["technical_score_config"]["W_technical_score"]
        # Expreience score weight
        W_expreience_score = config_score["experience_score_config"]["W_experience_score"]
        # Language score weight
        W_language_score = config_score["language_score_config"]["W_language_score"]
        # Education score weight
        W_education_score = config_score["education_score_config"]["W_education_score"]

        # Ingredient of expreience score
        relevance_score_w = config_score["experience_score_config"]["relevance_score_w"]
        difficulty_score_w = config_score["experience_score_config"]["difficulty_score_w"]
        duration_score_w = config_score["experience_score_config"]["duration_score_w"]

        if W_technical_score + W_expreience_score + W_language_score + W_education_score != 1:
            return "Sum of W_technical_score, W_expreience_score, W_language_score, W_education_score must be equal to 1"
        elif relevance_score_w + difficulty_score_w + duration_score_w != 1:
            return "Sum of relevance_score_w, difficulty_score_w, duration_score_w must be equal to 1"
        else:
            return True

    @staticmethod
    async def get_all_matching_cv_by_role(id_user:str, role:str):
        matching_cv_service = MatchingCvService()
        if role == "mentor":
            all_cv_by_user = matching_cv_service._get_all_matching_cv_by_role_mentor(id_user)
        elif role == "hr":
            all_cv_by_user = matching_cv_service._get_all_matching_cv_by_role_hr(id_user)

        return GenericResponseModel(status_code=http.HTTPStatus.OK, message="Get All CV Matching by User", data=all_cv_by_user)
    
    @staticmethod
    async def matching_cv(data_matching: dict):
        # get data_matching
        id_cv_result = data_matching.get("id_cv_result")
        config_setup = data_matching.get("config_setup")
        re_extract = data_matching.get("re_extract")

        # check config_setup id is str -> get from user_config DB
        if isinstance(config_setup, str):
            print("config_setup is str")
            pass

        # get cv_results
        cv_results_service = CvResultsService()
        cv_result = cv_results_service._get_by_id_cv_result(id_cv_result)
        id_cv = cv_result.get("id_cv")
        id_jd = cv_result.get("id_jd")

        # Using for REMATCH: check re_extract status
        if re_extract:
            # update data cv
            cvs_service = CvsService()
            cv_data = cvs_service._get_by_id_cv(id_cv)
            data_cv_update = {
                "extract_status": False,
                "extract_result": None
            }
            cvs_service._update_cv(id_cv=id_cv, data_update=data_cv_update)

            # update data cv_result
            data_update = {
                "cv_score": None,
                "matching_status": False
            }
            cv_results_service._update_cv_result(id_cv_result=id_cv_result, data_update=data_update)

        # get cv_data by id_cv
        cvs_service = CvsService()
        cv_data = cvs_service._get_by_id_cv(id_cv)
        cv_content = cv_data.get("cv_content")
        extract_status = cv_data.get("extract_status")

        # get jd_data by id_jd
        jds_service = JdsService()
        jd_data = jds_service._get_by_id_jd(id_jd)
        jd_summary = jd_data.get("jd_summary")
        chat_history_url = jd_data.get("chat_history_url")

        # start matching cv: Result matching cv and jd
        if extract_status == False:
            matching_cv_service = MatchingCvService()
            extract_result = matching_cv_service._load_history_and_matching(cv_need_matching=cv_content, jd_summary=jd_summary, chat_history_url=chat_history_url)
            # update cv
            data_update_cv = {
                "extract_status": True,
                "extract_result": extract_result
            }
            cvs_service._update_cv(id_cv=id_cv, data_update=data_update_cv)
        else:
            extract_result = cv_data.get("extract_result")
        
        cv_score = calculate_matching_score(matched_result=extract_result, config_score=config_setup)

        # update cv_result
        data_update = {
            "cv_score": cv_score,
            "matching_status": True
        }
        cv_results_service._update_cv_result(id_cv_result=id_cv_result, data_update=data_update)

        # get cv_result after matching
        cv_result = cv_results_service._get_by_id_cv_result(id_cv_result)

        return GenericResponseModel(status_code=http.HTTPStatus.OK, message="Matching CV Successfully", data=cv_result)

    @staticmethod
    def re_matching_cv(data_re_matching: dict):
        id_cv_result = data_re_matching.get("id_cv_result")
        config_setup = data_re_matching.get("config_setup")

        # check config_setup id is str -> get from user_config DB
        if isinstance(config_setup, str):
            print("config_setup is str -> get from user_config DB")
            pass