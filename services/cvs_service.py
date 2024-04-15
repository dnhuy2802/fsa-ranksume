import http
from uuid import UUID

from scripts.context_manager import context_log_meta
# from logs import logger

from models.base import GenericResponseModel

class CvsService:
    @staticmethod
    async def get_all_cvs():
        response: GenericResponseModel = GenericResponseModel()
        return response