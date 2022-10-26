import logging

from typing import Union, Optional

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status, Cookie
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel

from app.common import get_current_active_user, oauth2_scheme, get_password_hash
from app.routers import auth
# from passlib.handlers.bcrypt

from app.routers.auth import *
from app.schemas import ModelName, User


class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None


app = FastAPI()
app.include_router(auth.router)

# app.mount("/static", StaticFiles(directory="static"), name="static")


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
