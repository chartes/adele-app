from flask import render_template, flash, redirect, url_for, jsonify
from app import app
from app.models import Document, User

from app.database.alignment.alignment_translation import align_translation
from flask_sqlalchemy import get_debug_queries


#@app.route('/alignment/translation/<transcription_id>')
#def r_align_translation(transcription_id):
#    res = align_translation(transcription_id)
#    if len(res) > 0:
#        alignment=[ {"transcription":t[2], "translation":t[3]} for t in res]
#    else:
#        #no result, should raise an error
#        alignment = []
#    return render_template('alignment.html', alignment=alignment)


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

@app.route('/api/document/<doc_id>')
def api_document(doc_id):
    doc = Document.query.filter(Document.id == doc_id).one()
    #dump(query)
    #print(doc.document_linked_doc_id_collection[0])
    if doc is None:
        # TOD0 : renvoyer une erreur 404 en json
        return jsonify({ 'error': 'Document introuvable'})
    return jsonify(doc.serialize())

#@app.route('/api/document/<doc_id>/traduction')
#@app.route('/api/document/<doc_id>/transcription')

@app.route('/api/user/<user_id>')
def api_user(user_id):
    user = User.query.filter(User.id == user_id).one()
    #dump(query)
    #print(doc.document_linked_doc_id_collection[0])
    if user is None:
        # TOD0 : renvoyer une erreur 404 en json
        return jsonify({ 'error': 'Document introuvable'})
    return jsonify(user.serialize())