from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class JdsModel(BaseModel):
    id_jd: UUID = Field(default_factory=uuid4, alias="_id")
    name_jd: str = Field(default="name_jd")
    chat_history_file_name: str = Field(default=None)
    chat_history_url: str = Field(default=None)
    have_exam: bool = Field(default=False)
    id_exam: str = Field(default=None)
    is_generate_exam: bool = Field(default=False)
    jd_summary: str = Field(default="jd_summary")
    jd_text: str = Field(default="jd_text")
    created_by: str = Field(default="Admin")
    created_at: str = Field(default=None)
    updated_at: str = Field(default=None)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "name_jd": "name_jd",
                "chat_history_file_name": "chat_history_file_name",
                "chat_history_url": "chat_history_url",
                "have_exam": False,
                "id_exam": "id_exam",
                "is_generate_exam": False,
                "jd_summary": "jd_summary",
                "jd_text": "jd_text",
                "created_by": "Admin",
                "created_at": "2022-01-01 00:00:00",
                "updated_at": "2022-01-01 00:00:00"
            }
        }
