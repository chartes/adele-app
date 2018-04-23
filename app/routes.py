from flask import render_template, flash, redirect, url_for, render_template_string, Blueprint
from flask_user import login_required

import config
from app import app, role_required
from app.models import Document

app_bp = Blueprint('app_bp', __name__, template_folder='templates', static_folder='static')


"""
---------------------------------
Test routes
---------------------------------
"""


@app_bp.route('/test/alignments/translation/<transcription_id>/<translation_id>')
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

@app_bp.route('/members')
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

@app_bp.route('/')
@app_bp.route('/admin')
def admin():
    return render_template('admin/index.html')

@app_bp.route('/admin/documents')
def admin_documents():
    docs = Document.query.all()
    return render_template('admin/documents.html', title='Documents - Adele',  docs=docs)

@app_bp.route('/admin/documents/<doc_id>')
def admin_document(doc_id):
    doc = Document.query.filter(Document.id == doc_id).one()
    if doc is None:
        flash('Document {doc_id} introuvable.'.format(doc_id=doc_id), 'error')
        return redirect(url_for('app_bp.admin_documents'))
    return render_template('admin/document.html', title='Documents - Adele',  doc=doc)

@app_bp.route('/admin/documents/<doc_id>/edition')
def admin_document_edit(doc_id):
    doc = Document.query.filter(Document.id == doc_id).one()
    if doc is None:
        flash('Document {doc_id} introuvable.'.format(doc_id=doc_id), 'error')
        return redirect(url_for('app_bp.admin_documents'))
    return render_template('admin/document_edit.html', title='Document - Adele', doc=doc)


app.register_blueprint(app_bp, url_prefix=config.Config.APP_PREFIX)

"""
---------------------------------
API Routes
---------------------------------
"""

from app.api.routes import *
