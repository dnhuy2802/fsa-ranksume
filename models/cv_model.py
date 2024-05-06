from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class CvsModel(BaseModel):
    id_cv: UUID = Field(default_factory=uuid4, alias="_id")
    cv_content: str = Field(default="cv_text")
    file_cv_name: str = Field(default=None)
    file_cv_url: str = Field(default=None)
    extract_status: bool = Field(default=False)
    extract_result: dict = Field(default=None)
    created_by: str = Field(default="Admin")
    created_at: str = Field(default=None)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "name_cv": "name_cv",
                "cv_content": "cv_content",
                "file_cv_name": "file_cv_name",
                "file_cv_url": "file_cv_url",
                "extract_status": False,
                "extract_result": {},
                "created_by": "Admin",
                "created_at": "2022-01-01 00:00:00",
            }
        }
