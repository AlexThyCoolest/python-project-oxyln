import os

class Config:
    NEWSAPI_API_KEY = os.environ.get('NEWSAPI_API_KEY')
    DB_CONNECTION_STRING = os.environ.get('DB_CONNECTION_STRING')
    DEBUG = bool(os.environ.get('DEBUG'))
