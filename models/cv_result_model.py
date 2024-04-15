from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class CvResultsModel(BaseModel):
    id_cv_result: UUID = Field(default_factory=uuid4, alias="_id")
    id_cv: UUID = Field(default=None)
    id_jd: UUID = Field(default=None)
    id_user: UUID = Field(default=None)
    id_user_config: UUID = Field(default=None)
    cv_score:dict = Field(default=None)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id_cv": "id_cv",
                "id_jd": "id_jd",
                "id_user": "id_user",
                "id_user_config": "id_user_config",
                "cv_score": {}
            }
        }
