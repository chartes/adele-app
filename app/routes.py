from flask import render_template
from app import app, db



@app.route('/')
@app.route('/index')
def index():
    doc = db.execute("select * from document").fetchall()
    user = {'username': 'Miguel'}
    return render_template('index.html', title='Home', user=user, doc=doc)
