from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# Field → used for min/max lengths and validation
# BaseModel → base class for all Pydantic models
# ConfigDict → modern Pydantic way to configure model behavior


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)


class UserCreate(UserBase):
    password: str=Field(min_length=8)  # password field for user creation; not stored directly in the database


class UserPublic(BaseModel): #where is base model coming from??
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str 
    image_file: str | None
    image_path: str

class UserPrivate(UserPublic):
    email: EmailStr

class UserUpdate(BaseModel): #patch method for user update
    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=120)
    image_file: str | None = Field(default=None, min_length=1, max_length=200)

class Token(BaseModel):
    access_token: str
    token_type: str




class PostBase(BaseModel):
    # defines what we accept and return from our API
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)


class PostCreate(PostBase):
    user_id: int  # temporary for testing; later comes from authenticated user

class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None, min_length=1)


class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    date_posted: datetime
    author: UserPublic
    # nested response model
    # allows returning author details with the post
    # useful for showing username/profile picture on frontend


# request → pydantic validates it
# → SQLAlchemy stores/retrieves data
# → pydantic formats the response
# → response is sent back
