from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

class UserInDB(UserResponse):
    hashed_password: str
