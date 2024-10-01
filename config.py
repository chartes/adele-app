import os

basedir = os.path.abspath(os.path.dirname(__file__))

def parse_var_env(var_name):
    v = os.environ.get(var_name)
    if v == "True":
        v = True
    elif v == "False":
        v = False
    return v


class Config(object):
    ENV = "production"
    DEBUG = False

    SECRET_KEY = parse_var_env("SECRET_KEY")

    APP_URL_PREFIX = "/adele"  # used to build correct iiif urls

    SQLALCHEMY_DATABASE_URI = 'sqlite:////' + os.path.join(basedir, parse_var_env('DATABASE_URI'))
    SQLALCHEMY_TRACK_MODIFICATIONS = parse_var_env('SQLALCHEMY_TRACK_MODIFICATIONS') or False

    DOC_PER_PAGE = int(parse_var_env('DOC_PER_PAGE'))
    USERS_PER_PAGE = int(parse_var_env('USERS_PER_PAGE'))

    CSRF_ENABLED = parse_var_env("CSRF_ENABLED")

    # Flask-Mail settings
    MAIL_SERVER = parse_var_env('MAIL_SERVER')
    MAIL_PORT = int(parse_var_env('MAIL_PORT'))
    MAIL_USE_TLS = parse_var_env("MAIL_USE_TLS")
    MAIL_USE_SSL = parse_var_env("MAIL_USE_SSL")
    MAIL_USERNAME = parse_var_env("MAIL_USERNAME")

    JWT_SECRET_KEY = parse_var_env('JWT_SECRET_KEY')
    JWT_TOKEN_LOCATION = [location.strip() for location in parse_var_env('JWT_TOKEN_LOCATION').split(',')]
    JWT_COOKIE_CSRF_PROTECT = parse_var_env("JWT_COOKIE_CSRF_PROTECT")
    JWT_COOKIE_SECURE =parse_var_env("JWT_COOKIE_SECURE")
    JWT_IDENTITY_CLAIM = parse_var_env("JWT_IDENTITY_CLAIM")

    # JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(seconds=int(os.getenv(('JWT_ACCESS_TOKEN_EXPIRES'))))

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    ENV = 'development'
    DEBUG = True

    @staticmethod
    def init_app(app):
        print('THIS APP IS IN PRE-PROD MODE. YOU SHOULD NOT SEE THIS IN PRODUCTION.')


class LocalConfig(Config):
    ENV = 'development'
    DEBUG = True

    @staticmethod
    def init_app(app):
        print('THIS APP IS IN LOCAL DEV MODE. YOU SHOULD NOT SEE THIS IN PRODUCTION.')


class TestConfig(Config):
    ENV = 'test'
    DEBUG = True

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
        """
        path = os.path.join(TestConfig.DB_PATH, 'adele.sqlite')
        print("** fetching new db **")
        db_url = 'https://github.com/chartes/adele/raw/master/adele.sqlite'
        with urllib.request.urlopen(db_url) as response, open(path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
            print("** DB ready **")
        """


config = {
    "local": LocalConfig,
    "dev": DevelopmentConfig,
    "prod": Config,
    "test": TestConfig
}
