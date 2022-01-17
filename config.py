import datetime
from time import time

import os
import shutil
import urllib

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    ENV = "prod"
    SECRET_KEY = os.environ.get('SECRET_KEY')

    APP_URL_PREFIX = "/adele"  # used to build correct iiif urls

    SQLALCHEMY_DATABASE_URI = 'sqlite:////' + os.path.join(os.path.abspath(os.getcwd()), 'db', 'adele.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DOC_PER_PAGE = 20
    USERS_PER_PAGE = 10

    CSRF_ENABLED = True

    # Flask-Mail settings
    MAIL_SERVER = 'relay.huma-num.fr'
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'adele.app@chartes.psl.eu'

    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_TOKEN_LOCATION = ['cookies', 'headers']
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_COOKIE_SECURE = True
    JWT_IDENTITY_CLAIM = 'sub'

    # JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(seconds=int(os.getenv(('JWT_ACCESS_TOKEN_EXPIRES'))))

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    ENV = 'development'

    SECRET_KEY = 'you-will-never-guess-but-please-change-me!'

    APP_URL_PREFIX = ""  # used to build correct iiif urls

    JWT_COOKIE_CSRF_PROTECT = False
    JWT_COOKIE_SECURE = False

    @staticmethod
    def init_app(app):
        app.debug = True


class TestConfig(Config):
    ENV = 'test'

    DB_PATH = os.path.join(basedir, "tests", "data")
    SQLALCHEMY_DATABASE_URI = 'sqlite:////' + os.path.join(os.path.abspath(os.getcwd()), DB_PATH, 'adele.test.sqlite')

    SECRET_KEY = 'you-will-never-guess-but-please-change-me'

    MAIL_USERNAME = 'adele@chartes.psl.eu'
    USER_EMAIL_SENDER_NAME = 'Adele'
    USER_EMAIL_SENDER_EMAIL = 'adele@chartes.psl.eu'
    MAIL_SERVER = 'smtp.chartes.psl.eu'
    MAIL_PORT = 465
    MAIL_USE_SSL = 1

    LIVESERVER_TIMEOUT = 10
    LIVESERVER_PORT = 8943

    @staticmethod
    def init_app(app):
        print("APP STARTED FROM TEST CONFIG\n")
        app.testing = True
        app.debug = False
        """
        path = os.path.join(TestConfig.DB_PATH, 'adele.sqlite')
        print("** fetching new db **")
        db_url = 'https://github.com/chartes/adele/raw/master/adele.sqlite'
        with urllib.request.urlopen(db_url) as response, open(path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
            print("** DB ready **")
        """


config = {
    "dev": DevelopmentConfig,
    "prod": Config,
    "test": TestConfig
}
