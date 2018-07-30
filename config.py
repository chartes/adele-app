from time import time

import os
import shutil
import urllib

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')

    SQLALCHEMY_DATABASE_URI = 'sqlite:////' + os.path.join(os.path.abspath(os.getcwd()), 'db', 'adele.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SCSS_STATIC_DIR = os.path.join(basedir, "app/static/css")
    SCSS_ASSET_DIR = os.path.join(basedir, "app/assets/scss")

    DOC_PER_PAGE = 20
    USERS_PER_PAGE = 10

    CSRF_ENABLED = True

    APP_URL_PREFIX = '/adele'

    # Flask-User settings
    USER_APP_NAME = 'Adele'
    USER_AFTER_LOGOUT_ENDPOINT = 'app_bp.logout_delete_token'
    USER_AFTER_INVITE_ENDPOINT = 'app_bp.after_invite'
    USER_AFTER_REGISTER_ENDPOINT = 'app_bp.index'

    USER_ENABLE_REGISTER = True
    USER_ENABLE_REMEMBER_ME = False
    USER_ENABLE_INVITE_USER = True
    USER_REQUIRE_INVITATION = True
    USER_AUTO_LOGIN_AFTER_CONFIRM = True

    USER_CHANGE_PASSWORD_URL = '%s/user/change-password' % APP_URL_PREFIX
    USER_CHANGE_USERNAME_URL = '%s/user/change-username' % APP_URL_PREFIX
    USER_CONFIRM_EMAIL_URL = '%s/user/confirm-email/<token>' % APP_URL_PREFIX
    USER_EDIT_USER_PROFILE_URL = '%s/user/edit_user_profile' % APP_URL_PREFIX
    USER_EMAIL_ACTION_URL = '%s/user/email/<id>/<action>' % APP_URL_PREFIX
    USER_FORGOT_PASSWORD_URL = '%s/user/forgot-password' % APP_URL_PREFIX
    USER_INVITE_USER_URL = '%s/user/invite' % APP_URL_PREFIX
    USER_LOGIN_URL = '%s/user/sign-in' % APP_URL_PREFIX
    USER_LOGOUT_URL = '%s/user/sign-out' % APP_URL_PREFIX
    USER_MANAGE_EMAILS_URL = '%s/user/manage-emails' % APP_URL_PREFIX
    USER_REGISTER_URL = '%s/user/register' % APP_URL_PREFIX
    USER_RESEND_EMAIL_CONFIRMATION_URL = '%s/user/resend-email-confirmation' % APP_URL_PREFIX

    # Flask-Mail settings
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    USER_EMAIL_SENDER_NAME = os.getenv('USER_EMAIL_SENDER_NAME')
    USER_EMAIL_SENDER_EMAIL = os.getenv('USER_EMAIL_SENDER_EMAIL')
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT') or 465)
    MAIL_USE_SSL = int(os.getenv('MAIL_USE_SSL') or True)

    # used when generating the IIIF annotation lists urls
    APP_DOMAIN_NAME = "adele.chartes.psl.eu" #TODO: vérifier si encore utilisé

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):

    COPY = False

    SECRET_KEY = 'you-will-never-guess-but-please-change-me'
    APP_DOMAIN_NAME = "locahost:5000"  #TODO: vérifier si encore utilisé

    MAIL_USERNAME = 'adele@chartes.psl.eu'
    USER_EMAIL_SENDER_NAME = 'Adele'
    USER_EMAIL_SENDER_EMAIL = 'adele@chartes.psl.eu'
    MAIL_SERVER = 'smtp.chartes.psl.eu'
    MAIL_PORT = 465
    MAIL_USE_SSL = 1

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

    DB_PATH = 'tests/data'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////' + os.path.join(os.path.abspath(os.getcwd()), DB_PATH, 'adele.sqlite')

    SECRET_KEY = 'you-will-never-guess-but-please-change-me'
    APP_DOMAIN_NAME = "locahost:5000"  #TODO: vérifier si encore utilisé

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
        print("APP STARTED FROM TEST CONFIG")
        app.testing = True

        path = os.path.join(TestConfig.DB_PATH, 'adele.sqlite')
        print("** fetching new db **")
        db_url = 'https://github.com/chartes/adele/raw/master/adele.sqlite'
        with urllib.request.urlopen(db_url) as response, open(path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
            print("** DB ready **")


config = {
    "dev": DevelopmentConfig,
    "prod": Config,
    "test": TestConfig
}
