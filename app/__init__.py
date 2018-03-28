import os
import pprint

from flask import Flask
from config import Config
from flask_scss import Scss

from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_user import UserManager, SQLAlchemyAdapter

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Flask extensions
db = SQLAlchemy(app)  # Initialize Flask-SQLAlchemy
mail = Mail(app)  # Initialize Flask-Mail
scss = Scss(app)



from app import routes, models


# Create all database tables
#db.create_all()

# Setup Flask-User
db_adapter = SQLAlchemyAdapter(db, models.User)  # Register the User model
user_manager = UserManager(db_adapter, app)  # Initialize Flask-User


#from sqlalchemy.engine import create_engine
#engine = create_engine('sqlite://///Users/mrgecko/Documents/Dev/Projects/ENC/adele-app/db/adele.sqlite')
#connection = engine.connect()
#
#result = connection.execute("select id from document")
#names = []
#for row in result:
#    names.append(row[0])
#
#print(names)
#