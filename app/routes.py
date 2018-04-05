from flask import render_template, flash, redirect, url_for, render_template_string
from flask_user import login_required

from app import app

"""
---------------------------------
Test routes
---------------------------------
"""
@app.route('/test/alignments/translations/<transcription_id>/<translation_id>')
def align_translation(transcription_id, translation_id):
    res = align_translation(transcription_id, translation_id)
    if len(res) > 0:
        alignment=[ {"transcription": t[6], "translation": t[7]} for t in res]
    else:
        #no result, should raise an error
        alignment = []
    return render_template('alignment.html', alignment=alignment)


"""
---------------------------------
User Managment Routes
---------------------------------
"""

@app.route('/members')
@login_required
def members_page():
    return render_template_string("""
        {% extends "base.html" %}
        {% block content %}
            <h2>Members page</h2>
            <p>This page can only be accessed by authenticated users.</p><br/>
            <p><a href={{ url_for('user.logout') }}>logout</a></p>
        {% endblock %}
        """)


"""
---------------------------------
Admin Routes
---------------------------------
"""

@app.route('/')
@app.route('/admin')
def admin():
    return render_template('admin/index.html')#

@app.route('/admin/documents')
def admin_documents():
    docs = Document.query.all()
    return render_template('admin/documents.html', title='Documents - Adele',  docs=docs)

@app.route('/admin/documents/<doc_id>')
def admin_document(doc_id):
    doc = Document.query.filter(Document.id == doc_id).one()
    if doc is None:
        flash('Document {doc_id} introuvable.'.format(doc_id=doc_id), 'error')
        return redirect(url_for('admin_documents'))
    return render_template('admin/document.html', title='Documents - Adele',  doc=doc)

@app.route('/admin/documents/<doc_id>/edition')
def admin_document_edit(doc_id):
    doc = Document.query.filter(Document.id == doc_id).one()
    if doc is None:
        flash('Document {doc_id} introuvable.'.format(doc_id=doc_id), 'error')
        return redirect(url_for('admin_documents'))
    return render_template('admin/document_edit.html', title='Document - Adele', doc=doc)

"""
---------------------------------
API Routes
---------------------------------
"""

from app.api.routes import *
