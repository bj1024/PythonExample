import logging
from typing import Union, Optional

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.common import authenticate_user, get_current_user, get_user
from app.data import fake_users_db, authed_user, SECRET_KEY, ALGORITHM
from app.schemas import Refresh, Token, TokenData

# router = APIRouter()
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger("uvicorn")

from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Response


@router.post("/token", response_model=Token)
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(seconds=30)
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=60)
    )

    authed_user[user.username] = refresh_token
    response.set_cookie(key="refresh_token", value=refresh_token, path="/auth", httponly=True, secure=True,
                        samesite="lax")

    logger.info(f"authed_user=[{authed_user}]")
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token)
async def refresh_access_token(response: Response, refresh_token: Optional[str] = Cookie(None)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="token is not valid",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception

    if not user.username in authed_user.keys():
        raise credentials_exception

    new_access_token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=60)
    )

    logger.info(f"refresh_token=[{refresh_token}]")
    logger.info(f"access_token=[{new_access_token}]")
    # get_current_user
    return {"access_token": new_access_token, "token_type": "bearer"}


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    to_encode.update({"type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    to_encode.update({"type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
