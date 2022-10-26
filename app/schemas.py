from typing import Union

from pydantic import BaseModel
from sqlalchemy import Enum


class Token(BaseModel):
    access_token: str
    # token_type: str


class Refresh(BaseModel):
    status: str
    # token_type: str


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


class TokenData(BaseModel):
    username: Union[str, None] = None


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserInDB(User):
    hashed_password: str
