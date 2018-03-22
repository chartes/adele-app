from flask import render_template
from app import app, db

from app.database.alignment.alignment_translation import align_translation


@app.route('/')
@app.route('/index')
def index():
    doc = db.execute("select * from document").fetchall()
    return render_template('index.html', title='Adele',  doc=doc)

@app.route('/alignment/translation/<transcription_id>')
def r_align_translation(transcription_id):
    res = align_translation(transcription_id)
    if len(res) > 0:
        alignment=[ {"transcription":t[2], "translation":t[3]} for t in res]
    else:
        #no result, should raise an error
        alignment = []
    return render_template('alignment.html', alignment=alignment)


"""
---------------------------------
Admin Routes
---------------------------------
"""

@app.route('/admin')
def admin():
    return render_template('admin/index.html')

@app.route('/admin/documents')
def admin_documents():
    doc = db.execute("select * from document").fetchall()
    return render_template('admin/documents.html', title='Documents - Adele',  doc=doc)

#@app.route('/admin/login')
#@app.route('/admin/logout')