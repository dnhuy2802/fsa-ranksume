from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class ExamsModel(BaseModel):
    id_exam: UUID = Field(default_factory=uuid4, alias="_id")
    created_at: str = Field(default=None)
    exam_description: str = Field(default="exam_description")
    exam_file_name: str = Field(default="exam_file_name")
    exam_file_url: str = Field(default="exam_file_url")
    exam_file_content: str = Field(default=None)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "created_at": "2022-01-01 00:00:00",
                "exam_description": "exam_description",
                "exam_file_name": "exam_file_name",
                "exam_file_url": "exam_file_url",
                "exam_file_content": "exam_file_content"
            }
        }