import os
import urllib.request

import shutil

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):

    with urllib.request.urlopen('https://github.com/chartes/adele/raw/master/adele.sqlite') as response,\
            open(os.path.join('db', 'adele.sqlite'), 'wb') as out_file:
        shutil.copyfileobj(response, out_file)

        #local_filename="/Users/mrgecko/Documents/Dev/Data/adele/adele.sqlite"

        SQLALCHEMY_DATABASE_URI = os.path.join('db', 'adele.sqlite')
        SQLALCHEMY_TRACK_MODIFICATIONS = False

        TESTS_DB_URL=SQLALCHEMY_DATABASE_URI
