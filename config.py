import os
import urllib.request

import shutil

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    try:
        with urllib.request.urlopen('https://github.com/chartes/adele/raw/master/adele.sqlite') as response,\
                open(os.path.join('db', 'adele.sqlite'), 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
    except:
        pass
        #local_filename="/Users/mrgecko/Documents/Dev/Data/adele/adele.sqlite"

    SQLALCHEMY_DATABASE_URI = os.path.join('db', 'adele.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    TESTS_DB_URL=SQLALCHEMY_DATABASE_URI

    SCSS_STATIC_DIR = os.path.join(basedir, "app/static/css")
    SCSS_ASSET_DIR = os.path.join(basedir, "app/assets/scss")
