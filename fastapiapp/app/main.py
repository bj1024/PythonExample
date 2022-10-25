import logging

import uvicorn
from enum import Enum

from fastapi import Response
from fastapi import Cookie
from typing import Optional

from fastapi.staticfiles import StaticFiles

from datetime import datetime, timedelta
from typing import Union

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
# from passlib.handlers.bcrypt

from passlib.hash import bcrypt


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None


app = FastAPI()
logger = logging.getLogger("uvicorn")

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

# app.mount("/static", StaticFiles(directory="static"), name="static")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


@app.get("/items/")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}


# @app.get("/items/")
# async def read_item(skip: int = 0, limit: int = 10):
#     return fake_items_db[skip : skip + limit]


@app.get("/items/{item_id}")
async def read_item(item_id: str, q: Union[str, None] = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item


# to get a string like this run:
# openssl rand -hex 32
# TODO:Must change in production.
SECRET_KEY = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Username: johndoe Password: secret
# Username: anonymous Password: anonymous
fake_users_db = {
    "anonymous": {
        "username": "anonymous",
        "full_name": "anonymous",
        "email": "anonymous",
        "hashed_password": "$2b$12$3.yfiWhwkE1/C2/g60w2Ye.F/qIQazHsahu5uUtHdO5Jvo6W7A01O",
        "disabled": False,
    },
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]


# TODO: for test. to be deleted.
@app.get("/passwordhash")
async def read_own_items(password: str):
    hash = get_password_hash(password)

    return [{"password": password, "hash": hash}]


@app.post("/items/")
async def create_item(item: Item, current_user: User = Depends(get_current_active_user)):
    item.description += f"\n by {current_user.username}"
    return item


# cookie test

@app.get("/cookietest")
async def cookietest_get(response: Response, mycookiekey: Optional[str] = Cookie(None)):
    logger.info(f"cookietest_get")
    logging.getLogger("uvicorn.error").info("uvicorn.error test")
    logging.getLogger("uvicorn.access").info("uvicorn.access test")

    if mycookiekey is not None:
        # print(f"mycookiekey=[{mycookiekey}]")
        mycookieval = mycookiekey
        logger.info(f"mycookiekey=[{mycookieval}]")
    else:
        pass
    #     logger.INFO(f"mycookiekey={mycookiekey}")
    #
    # else:
    #     dtstr = datetime.today()
    #     response.set_cookie(key="mycookiekey", value=f"{dtstr}",path="/cookietest",httponly=True,secure=True)

    return [{"reply_time": "aaa"}]


# pyinstallerの場合、__main__ で起動される。
# python の場合、__main__ ,mainで起動される。

print(f"name = [{__name__}]")
import sys, os

if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

print(f"application_path = [{application_path}]")
if __name__ == "__main__":
    # uvicorn.run("main:app", host="127.0.0.1", port=8000,reload=True)
    # uvicorn.run("sql_app.main:app", host="127.0.0.1", port=8000,reload=True)
    # uvicorn.run("sql_app.main:app", host="127.0.0.1", port=8000, reload=False)
    uvicorn.run("__main__:app", host="127.0.0.1", port=8000, reload=True)
    # uvicorn.run("__main__:app", host="127.0.0.1", port=8000, reload=False)
