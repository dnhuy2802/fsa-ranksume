from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class GeneratedExamsModel(BaseModel):
    id_exam: UUID = Field(default_factory=uuid4, alias="_id")
    created_at: str = Field(default=None)
    id_jd: UUID = Field(default=None)
    generated_exam_file_name: str = Field(default="generated_exam_file_name")
    generated_exam_file_url: str = Field(default="generated_exam_file_url")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "created_at": "2022-01-01 00:00:00",
                "id_jd": "id_jd",
                "generated_exam_file_name": "generated_exam_file_name",
                "generated_exam_file_url": "generated_exam_file_url"
            }
        }