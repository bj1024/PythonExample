
# FastAPI Example(python)


## install 

```
pip install fastapi
pip install "uvicorn[standard]"
```


# auth

[パスワード（およびハッシュ化）によるOAuth2、JWTトークンによるBearer \- FastAPI](https://fastapi.tiangolo.com/ja/tutorial/security/oauth2-jwt/)

```
pip install python-multipart

pip install 'python-jose[cryptography]'
pip install 'passlib[bcrypt]'

```

```
openssl rand -hex 32


b4158e52dd8e6c397436a49b235da89b93ee82bc9beaa82eaeffa43f3f649f9a

```

# logger

```
logger = logging.getLogger("uvicorn")

↑uvicorn とする。

```

- uvicorn内で3つのloggerインスタンスが生成される模様。


```
/usr/local/lib/python3.9/site-packages/uvicorn/config.py:118


 "loggers": {
        "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    },

```




# sqlite(with sqlalchemy)

```
pip install sqlalchemy

```

# pyinstaller

```
pyinstaller --clean --onefile --hidden-import=main  app/main.py 
```

- todo
  static files.
