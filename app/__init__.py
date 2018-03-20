from flask import Flask
from config import Config
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import create_session
from sqlalchemy import create_engine

app = Flask(__name__)
app.config.from_object(Config)

"""
open the sqlite database
"""
#handle conflicts in name resolution
def name_for_collection_relationship(base, local_cls, referred_cls, constraint):
    disc = '_'.join(col.name for col in constraint.columns)
    return referred_cls.__name__.lower() + '_' + disc + "_collection"



try:
    engine = create_engine("sqlite:///{0}".format(Config.SQLALCHEMY_DATABASE_URI))
    automap_base().prepare(engine, reflect=True,
                           name_for_collection_relationship=name_for_collection_relationship)
    db = create_session(bind=engine)
except:
    db = None


from app import routes, models
