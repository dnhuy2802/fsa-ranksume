from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class UsersModel(BaseModel):
    id_user: UUID = Field(default_factory=uuid4, alias="_id")
    name: str = Field(default="name")
    email: str = Field(default="email")
    role: str = Field(default="role")
    created_by: str = Field(default="admin")
    created_at: str = Field(default=None)
    updated_at: str = Field(default=None)

class CreateUsersModel(BaseModel):
    name: str = Field(default="name")
    email: str = Field(default="email")
    role: str = Field(default="role")
