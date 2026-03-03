from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import date
from typing import Optional

class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    additional_info: Optional[str] = None

class ContactCreate(ContactBase):
    pass

class ContactResponse(ContactBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

class UserSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=12)

class UserResponse(BaseModel):
    id: int
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)

class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

