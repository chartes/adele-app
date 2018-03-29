import os
import shutil
import urllib.request

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    try:
        with urllib.request.urlopen('https://github.com/chartes/adele/raw/master/adele.sqlite') as response,\
                open(os.path.join('db', 'adele.sqlite'), 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
    except:
        pass
        #raise Exception("DEBUG: fichier adele.sqlite non récupéré")
        #local_filename="/Users/mrgecko/Documents/Dev/Data/adele/adele.sqlite"

    #pb avec le chemin relatif ?
    SQLALCHEMY_DATABASE_URI = 'sqlite:////' + os.path.join(os.path.abspath(os.getcwd()), 'db', 'adele.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #SQLALCHEMY_ECHO=True

    SCSS_STATIC_DIR = os.path.join(basedir, "app/static/css")
    SCSS_ASSET_DIR = os.path.join(basedir, "app/assets/scss")

    CSRF_ENABLED = True

    # Flask-Mail settings
    MAIL_USERNAME =           os.getenv('MAIL_USERNAME',        'email@example.com')
    MAIL_PASSWORD =           os.getenv('MAIL_PASSWORD',        'password')
    MAIL_DEFAULT_SENDER =     os.getenv('MAIL_DEFAULT_SENDER',  '"MyApp" <noreply@example.com>')
    MAIL_SERVER =             os.getenv('MAIL_SERVER',          'smtp.gmail.com')
    MAIL_PORT =           int(os.getenv('MAIL_PORT',            '465'))
    MAIL_USE_SSL =        int(os.getenv('MAIL_USE_SSL',         True))
