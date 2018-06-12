import pprint
from flask import render_template, flash, redirect, url_for, render_template_string, Blueprint, session, current_app, \
    jsonify
from flask_user import login_required

import config
from app.models import Document, Editor, Language, ActeType, Tradition, Country, District, Institution, CommentaryType

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
        alignment = [{"transcription": t[6], "translation": t[7]} for t in res]
    else:
        # no result, should raise an error
        alignment = []
    return render_template('alignment.html', alignment=alignment)


"""
---------------------------------
User Managment Routes
---------------------------------
"""


@app_bp.route('/login')
@login_required
def login_make_token():
    user = current_app.get_current_user()
    token = user.generate_auth_token()

    session['auth_token'] = token.decode("utf-8")
    return redirect(url_for('user.login'))


"""
---------------------------------
Admin Routes
---------------------------------
"""


@app_bp.route('/')
@app_bp.route('/admin')
def admin():
    return render_template('admin/index.html')


def filter_documents(docs, form_values, field_name, get_doc_values, value_type=str):
    """
    :param docs:
    :param form_values:
    :param field_name:
    :param get_doc_values:
    :param value_type:
    :return: the doc list without the filtered values
    """
    if '-1' in form_values[field_name]:
        return docs
    else:
        filtered_docs = []
        filtered_values = [value_type(v) for v in form_values[field_name]]
        for doc in docs:
            if len([d for d in get_doc_values(doc) if d in filtered_values]) > 0:
                filtered_docs.append(doc)
    return filtered_docs

@app_bp.route('/documents', methods=['GET', 'POST'])
def documents():
    docs = Document.query.all()

    fields = [
        {
            "label": "Mode de tradition",
            "name": "tradition",
            "type":  "select",
            "options": {"multiple": True, "size": 3},
            "value": [(trad.id, trad.label) for trad in Tradition.query.all()]
        },
        {
            "label": "Type d'acte",
            "name": "acte_type",
            "type": "select",
            "options": {"multiple": True, "size": 3},
            "value": [(act.id, act.label) for act in ActeType.query.all()]
        },
        {
            "label": "Langue du document",
            "name": "language",
            "type":  "select",
            "options": {"multiple": True, "size": 3},
            "value": [(lang.code, lang.label) for lang in Language.query.all()]
        },
        {
            "label": "Siècle du document",
            "name": "creation",
            "type":  "select",
            "options": {"multiple": True, "size": 3},
            "value": set([(doc.creation, doc.creation) for doc in docs if doc.creation is not None])
        },
        {
            "label": "Siècle de la copie",
            "name": "copy_cent",
            "type": "select",
            "options": {"multiple": True, "size": 3},
            "value": set([(doc.copy_cent, doc.copy_cent) for doc in docs if doc.copy_cent is not None])
        },
        {
            "label": "Pays",
            "name": "country",
            "type": "select",
            "options": {"multiple": True, "size": 3},
            "value": set([(country.id, country.label) for country in Country.query.all()])
        },
        {
            "label": "Région contemporaine",
            "name": "district",
            "type": "select",
            "options": {"multiple": True, "size": 3},
            "value": set([(district.id, district.label) for district in District.query.all()])
        },
        {
            "label": "Institution de conservation",
            "name": "institution",
            "type": "select",
            "options": {"multiple": True, "size": 3},
            "value": set([(instit.id, instit.name) for instit in Institution.query.all()])
        },
        {
            "label": "Types de commentaires fournis",
            "name": "commentary_type",
            "type": "select",
            "options": {"multiple": True, "size": 3},
            "value": set([(com.id, com.label) for com in CommentaryType.query.all()])
        },
    ]

    filtered_docs = docs[::]

    if request.method == "POST":
        form_values = {}
        for field in fields:
            if field['type'] == "select" and field["options"]["multiple"]:
                form_values[field['name']] = request.form.getlist(field['name'])
            else:
                form_values[field['name']] = request.form.get(field['name'])

        # filter documents
        pprint.pprint(form_values)
        filtered_docs = filter_documents(filtered_docs, form_values, 'tradition', lambda doc: [i.id for i in doc.traditions])
        filtered_docs = filter_documents(filtered_docs, form_values, 'language', lambda doc: [i.code for i in doc.languages])
        filtered_docs = filter_documents(filtered_docs, form_values, 'acte_type', lambda doc: [i.id for i in doc.acte_types], value_type=int)
        filtered_docs = filter_documents(filtered_docs, form_values, 'commentary_type',
                                         lambda doc: [c.type_id for c in Commentary.query.filter(Commentary.doc_id == doc.id).all()],
                                         value_type=int)
        filtered_docs = filter_documents(filtered_docs, form_values, 'creation', lambda doc: [doc.creation], value_type=int)
        filtered_docs = filter_documents(filtered_docs, form_values, 'copy_cent', lambda doc: [doc.copy_cent], value_type=int)

        filtered_docs = filter_documents(filtered_docs, form_values, 'country', lambda doc: [i.id for i in doc.countries], value_type=int)
        filtered_docs = filter_documents(filtered_docs, form_values, 'district', lambda doc: [i.id for i in doc.districts], value_type=int)
        filtered_docs = filter_documents(filtered_docs, form_values, 'institution', lambda doc: [doc.institution_id], value_type=int)

    return render_template('admin/documents.html', title='Documents - Adele', docs=filtered_docs, fields=fields)


@app_bp.route('/admin/documents/<doc_id>')
def admin_document(doc_id):
    doc = Document.query.filter(Document.id == doc_id).one()
    if doc is None:
        flash('Document {doc_id} introuvable.'.format(doc_id=doc_id), 'error')
        return redirect(url_for('app_bp.documents'))
    return render_template('admin/document.html', title='Documents - Adele', doc=doc)


@app_bp.route('/admin/documents/<doc_id>/edition')
def admin_document_edit(doc_id):
    doc = Document.query.filter(Document.id == doc_id).one()
    if doc is None:
        flash('Document {doc_id} introuvable.'.format(doc_id=doc_id), 'error')
        return redirect(url_for('app_bp.documents'))
    return render_template('admin/document_edit.html', title='Document - Adele', doc=doc)


"""
---------------------------------
API Routes
---------------------------------
"""

from app.api.routes import *
