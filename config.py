import os
import urllib.request

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    local_filename, headers = urllib.request.urlretrieve(
        'https://github.com/chartes/adele/raw/master/adele.sqlite',
        os.path.join('db', 'adele.sqlite')
    )


    SQLALCHEMY_DATABASE_URI = local_filename
    SQLALCHEMY_TRACK_MODIFICATIONS = False
