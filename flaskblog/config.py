import os


class Config:
    SECRET_KEY = "2bb9f76262354924f0f38b6e119a6e72"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    DEBUG = True
    MAIL_PORT = 587
    MAIL_USERNAME = True
    MAIL_USE_TLS = True
    MAIL_PASSWORD = os.environ.get('pass')
