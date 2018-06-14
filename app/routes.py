import math

import pprint
from flask import render_template, flash, redirect, url_for, Blueprint, session, current_app
from flask_user import login_required


from app.models import Document, Language, ActeType, Tradition, Country, District, Institution, CommentaryType

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
    return render_template('main/index.html')


def filter_documents(docs, form_values, field_name, get_doc_values, value_type=str):
    """
    :param docs:
    :param form_values:
    :param field_name:
    :param get_doc_values:
    :param value_type:
    :return: the doc list without the filtered values
    """
    if len(form_values[field_name]) == 0:
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
    page = request.args.get('page', 1, type=int)
    if page < 0:
        page = 1

    docs = Document.query.all()
    fields = [
        {
            "label": "Mode de tradition",
            "name": "tradition",
            "value": sorted([(trad.label, trad.id) for trad in Tradition.query.all()])
        },
        {
            "label": "Type d'acte",
            "name": "acte_type",
            "value": sorted([(act.label, act.id) for act in ActeType.query.all()])
        },
        {
            "label": "Langue du document",
            "name": "language",
            "value": sorted([( lang.label, lang.code) for lang in Language.query.all()])
        },
        {
            "label": "Siècle du document",
            "name": "creation",
            "value": sorted(set([(doc.creation, doc.creation) for doc in docs if doc.creation is not None]))
        },
        {
            "label": "Siècle de la copie",
            "name": "copy_cent",
            "value": sorted(set([(doc.copy_cent, doc.copy_cent) for doc in docs if doc.copy_cent is not None]))
        },
        {
            "label": "Pays",
            "name": "country",
            "value": sorted([(country.label, country.id) for country in Country.query.all()])
        },
        {
            "label": "Région contemporaine",
            "name": "district",
            "value": sorted([(district.label, district.id) for district in District.query.all()])
        },
        {
            "label": "Institution de conservation",
            "name": "institution",
            "value": sorted([(instit.name, instit.id) for instit in Institution.query.all()])
        },
        {
            "label": "Types de commentaires fournis",
            "name": "commentary_type",
            "value": sorted([(com.label, com.id) for com in CommentaryType.query.all()])
        },
    ]

    filtered_docs = docs[::]
    form_values = {}
    if request.method == "POST":
        pprint.pprint(request.form)
        # parse hidden inputs to get the selected values
        for field in fields:
            values = request.form.get(field['name'])
            if len(values) > 0:
                values = values.replace(',', ' ').strip().split(' ')
            else:
                values = []
            form_values[field['name']] = values

        print('form_values:', form_values)

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

    nav_urls = []
    for p in range(0, int(math.floor(len(filtered_docs) / current_app.config['DOC_PER_PAGE'])) + 1):
        nav_urls.append("%s?page=%s" % (url_for('app_bp.documents'), p+1))

    try:
        filtered_docs = filtered_docs[0 + (page-1) * current_app.config['DOC_PER_PAGE']: 0 + page * current_app.config['DOC_PER_PAGE']]
    except IndexError:
        pass

    return render_template('main/documents.html',
                           title='Documents - Adele',
                           docs=filtered_docs,
                           fields=fields,
                           selected_values=form_values,
                           nav_urls=nav_urls,
                           current_page=page)


@app_bp.route('/admin/documents/<doc_id>')
def admin_document(doc_id):
    doc = Document.query.filter(Document.id == doc_id).one()
    if doc is None:
        flash('Document {doc_id} introuvable.'.format(doc_id=doc_id), 'error')
        return redirect(url_for('app_bp.documents'))
    return render_template('main/document.html', title='Documents - Adele', doc=doc)


@app_bp.route('/admin/documents/<doc_id>/edition')
def admin_document_edit(doc_id):
    doc = Document.query.filter(Document.id == doc_id).one()
    if doc is None:
        flash('Document {doc_id} introuvable.'.format(doc_id=doc_id), 'error')
        return redirect(url_for('app_bp.documents'))
    return render_template('main/document_edit.html', title='Document - Adele', doc=doc)


"""
---------------------------------
API Routes
---------------------------------
"""

from app.api.routes import *
