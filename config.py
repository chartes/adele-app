from time import time

import os
import shutil
import urllib

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    SQLALCHEMY_DATABASE_URI = 'sqlite:////' + os.path.join(os.path.abspath(os.getcwd()), 'db', 'adele.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SCSS_STATIC_DIR = os.path.join(basedir, "app/static/css")
    SCSS_ASSET_DIR = os.path.join(basedir, "app/assets/scss")

    DOC_PER_PAGE = 30

    CSRF_ENABLED = True

    # Flask-User settings
    USER_AFTER_LOGOUT_ENDPOINT = ''

    # Flask-Mail settings
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'adele@chartes.psl.eu')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', os.environ.get('ADELE_MAIL_PWD') or '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'Adele <adele@chartes.psl.eu>')
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.chartes.psl.eu')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_SSL = int(os.getenv('MAIL_USE_SSL', True))

    APP_DOMAIN_NAME = "adele.chartes.psl.eu"
    APP_PREFIX = ''

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):

    COPY = False

    @staticmethod
    def init_app(app):
        if DevelopmentConfig.COPY:
            path = os.path.join('db', 'adele.sqlite')
            if time() - os.path.getmtime(path) > 3:
                # get fresh new db
                with urllib.request.urlopen('https://github.com/chartes/adele/raw/master/adele.sqlite') as response, \
                        open(path, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
                    print("** DB ready **")

        app.debug = True

    # SQLALCHEMY_ECHO=True


class TestConfig(Config):
    pass


config = {
    "dev": DevelopmentConfig,
    "prod": Config,
    "test": TestConfig
}
