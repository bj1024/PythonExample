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

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]
authed_user = {}
