from flask import render_template, flash, redirect, url_for

from app import app, db
from app.database.alignment.alignment_translation import align_translation
from app.models import Document


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
    #dump(query)
    #print(doc.document_linked_doc_id_collection[0])
    if doc is None:
        flash('Document {doc_id} introuvable.'.format(doc_id=doc_id), 'error')
        return redirect(url_for('admin_documents'))
    return render_template('admin/document.html', title='Documents - Adele',  doc=doc)

@app.route('/admin/document/<doc_id>/edition')
def admin_document_edit(doc_id):
    query = db.query(Document)
    doc = query.get(doc_id)
    if doc is None:
        flash('Document {doc_id} introuvable.'.format(doc_id=doc_id), 'error')
        return redirect(url_for('admin_documents'))
    return render_template('admin/document_edit.html', title='Document - Adele', doc=doc)

#@app.route('/admin/document/<doc_id>/transcrption')
#def admin_document_transcription(doc_id):


#@app.route('/admin/login')
#@app.route('/admin/logout')