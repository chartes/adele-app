from flask import render_template, flash, redirect, url_for, jsonify, render_template_string
from flask_user import login_required
from sqlalchemy.orm.exc import NoResultFound

from app import app
from app.api.response import APIResponseFactory
from app.database.alignment.alignment_translation import align_translation
from app.models import Document, User


@app.route('/alignment/translation/<transcription_id>')
def r_align_translation(transcription_id):
    res = align_translation(transcription_id)
    if len(res) > 0:
        alignment=[ {"transcription": t[2], "translation": t[3]} for t in res]
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

@app.route('/admin/document/<doc_id>')
def admin_document(doc_id):
    doc = Document.query.filter(Document.id == doc_id).one()
    if doc is None:
        flash('Document {doc_id} introuvable.'.format(doc_id=doc_id), 'error')
        return redirect(url_for('admin_documents'))
    return render_template('admin/document.html', title='Documents - Adele',  doc=doc)

@app.route('/admin/document/<doc_id>/edition')
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



@app.route('/api/<api_version>/document/<doc_id>')
def api_document(api_version, doc_id):
    try:
        doc = Document.query.filter(Document.id == doc_id).one()
    except NoResultFound:
        doc = None

    if doc is None:
        response = APIResponseFactory.make_response(errors={"status": 404, "title": "Document introuvable"})
    else:
        response = APIResponseFactory.make_response(data=doc.serialize())
    return jsonify(response)

#@app.route('/api/document/<doc_id>/traduction')
#@app.route('/api/document/<doc_id>/transcription')

@app.route('/api/<api_version>/user/<user_id>')
def api_user(api_version, user_id):
    try:
        user = User.query.filter(User.id == user_id).one()
    except NoResultFound:
        user = None

    if user is None:
        response = APIResponseFactory.make_response(errors={"status": 404, "title": "Utilisateur introuvable"})
    else:
        response = APIResponseFactory.make_response(data=user.serialize())
    return jsonify(response)