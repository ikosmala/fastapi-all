from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    id: int
    created_at: datetime


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass


class Post(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut


class PostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    Post: Post
    votes: int


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int | None = None


class Vote(BaseModel):
    post_id: int
    dir: int = Field(ge=0, le=1)
