import math

import pprint
from flask import render_template, flash, redirect, url_for, session, current_app, get_flashed_messages, abort
from flask_user import login_required, roles_required
from flask_user.forms import InviteUserForm

from app import app_bp
from app.models import Document, Language, ActeType, Tradition, Country, District, Institution, CommentaryType, \
    Whitelist


def render_template_with_token(*args, **kargs):
    user = current_app.get_current_user()
    if not user.is_anonymous:
        token = user.generate_auth_token()
        session['auth_token'] = token.decode("utf-8")
        kargs["auth_token"] = session['auth_token']
    else:
        kargs["auth_token"] = ""
    return render_template(*args, **kargs)


"""
---------------------------------
Test routes
---------------------------------
"""

"""
@app_bp.route('/test/alignments/translation/<transcription_id>/<translation_id>')
def align_translation(transcription_id, translation_id):
    res = align_translation(transcription_id, translation_id)
    if len(res) > 0:
        alignment = [{"transcription": t[6], "translation": t[7]} for t in res]
    else:
        # no result, should raise an error
        alignment = []
    return render_template_with_token('alignment.html', alignment=alignment)
"""

"""
---------------------------------
User related routes
---------------------------------
"""


@app_bp.route('/login')
def login_make_token():
    user = current_app.get_current_user()
    if not user.is_anonymous:
        token = user.generate_auth_token()
        session['auth_token'] = token.decode("utf-8")
    return redirect(url_for('app_bp.index'))


@app_bp.route('/logout')
def logout_delete_token():
    session['auth_token'] = ""
    return redirect(url_for('app_bp.index'))


@app_bp.route('/user/after-invite')
@roles_required(['admin', 'teacher'])
def after_invite():
    return "OK"


"""
---------------------------------
Generic routes
---------------------------------
"""


@app_bp.route('/')
def index():
    return render_template_with_token('main/index.html')


@app_bp.route('/contact')
def contact():
    return render_template_with_token('main/contact.html')


@app_bp.route('/flash-messages/<last_msg_only>')
def get_flash_messages(last_msg_only=None):
    last_msg_only = last_msg_only is not None
    return render_template('main/fragments/_flash_messages.html', last_msg_only=last_msg_only)


@app_bp.route('/flash-messages/<last_msg_only>', methods=['POST'])
@login_required
def set_flash_messages(last_msg_only=None):
    data = request.get_json()
    for d in data["messages"]:
        flash(d["message"], d["category"])
    return ""


"""
---------------------------------
Dashboard routes
---------------------------------
"""


@app_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template_with_token('main/dashboard/user_dashboard.html')


@app_bp.route('/dashboard/documents')
@login_required
def dashboard_documents():
    user = current_app.get_current_user()
    docs = user.documents_i_can_edit
    return render_template_with_token('main/dashboard/documents.html', docs=docs, current_user=user)


@app_bp.route('/dashboard/manual')
@login_required
def dashboard_manual():
    return render_template_with_token('main/dashboard/manual.html')


@app_bp.route('/dashboard/manage-users/userlist/<list_id>')
@roles_required(['admin', 'teacher'])
@login_required
def dashboard_manage_users_list(list_id):
    user_list = Whitelist.query.filter(Whitelist.id == list_id).first()
    return render_template_with_token(
        'main/fragments/_manage_users_list.html',
        user_list=user_list
    )


@app_bp.route('/dashboard/manage-users/users/<list_id>')
@roles_required(['admin', 'teacher'])
@login_required
def dashboard_manage_users_users(list_id):
    user_list = Whitelist.query.filter(Whitelist.id == list_id).first()
    users = User.query.filter(User.id.notin_([u.id for u in user_list.users])).all()

    return render_template_with_token(
        'main/fragments/_manage_users.html',
        users=users
    )


@app_bp.route('/dashboard/manage-users')
@roles_required(['admin', 'teacher'])
def dashboard_manage_users():
    user = current_app.get_current_user()
    docs = user.documents_i_can_edit
    user_lists = Whitelist.query.all()
    if len(user_lists) > 0:
        selected_user_list = 0
    else:
        selected_user_list = -1
    return render_template_with_token(
        'main/dashboard/manage_users.html',
        user_lists=user_lists,
        selected_user_list=selected_user_list,
        docs=docs,
        invite_form=InviteUserForm()
    )


"""
---------------------------------
Document related routes
---------------------------------
"""


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


def get_document_search_fields(docs):
    return [
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
            "value": sorted([(lang.label, lang.code) for lang in Language.query.all()])
        },
        {
            "label": "Siècle du document",
            "name": "creation",
            "value": sorted(set([(doc.creation_lab, doc.creation) for doc in docs if doc.creation_lab is not None]))
        },
        {
            "label": "Siècle de la copie",
            "name": "copy_cent",
            "value": sorted(set([(doc.copy_year, doc.copy_cent) for doc in docs if doc.copy_cent is not None]))
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


@app_bp.route('/documents')
def documents():
    docs = Document.query.all()
    fields = get_document_search_fields(docs)
    return render_template_with_token('main/documents.html', title='Documents - Adele', fields=fields, current_page=1)


@app_bp.route('/documents/browse', methods=['POST'])
def document_list():
    page = int(request.form.get('page'))

    user = current_app.get_current_user()
    if user.is_anonymous or not (user.is_teacher or user.is_admin):
        docs = Document.query.filter(Document.is_published.is_(True)).all()
    else:
        docs = Document.query.all()

    fields = get_document_search_fields(docs)

    filtered_docs = docs[::]
    form_values = {}
    docs_are_filtered = False

    if request.method == "POST":
        # parse hidden inputs to get the selected values
        for field in fields:
            values = request.form.get(field['name'])
            if len(values) > 0:
                values = values.replace(',', ' ').strip().split(' ')
                docs_are_filtered = True
            else:
                values = []
            form_values[field['name']] = values

        # filter documents
        filtered_docs = filter_documents(filtered_docs, form_values, 'tradition',
                                         lambda doc: [i.id for i in doc.traditions])
        filtered_docs = filter_documents(filtered_docs, form_values, 'language',
                                         lambda doc: [i.code for i in doc.languages])
        filtered_docs = filter_documents(filtered_docs, form_values, 'acte_type',
                                         lambda doc: [i.id for i in doc.acte_types], value_type=int)
        filtered_docs = filter_documents(filtered_docs, form_values, 'commentary_type',
                                         lambda doc: [c.type_id for c in
                                                      Commentary.query.filter(Commentary.doc_id == doc.id).all()],
                                         value_type=int)
        filtered_docs = filter_documents(filtered_docs, form_values, 'creation', lambda doc: [doc.creation],
                                         value_type=int)
        filtered_docs = filter_documents(filtered_docs, form_values, 'copy_cent', lambda doc: [doc.copy_cent],
                                         value_type=int)

        filtered_docs = filter_documents(filtered_docs, form_values, 'country',
                                         lambda doc: [i.id for i in doc.countries], value_type=int)
        filtered_docs = filter_documents(filtered_docs, form_values, 'district',
                                         lambda doc: [i.id for i in doc.districts], value_type=int)
        filtered_docs = filter_documents(filtered_docs, form_values, 'institution', lambda doc: [doc.institution_id],
                                         value_type=int)

    nav_uri = []
    for p in range(0, int(math.floor(len(filtered_docs) / current_app.config['DOC_PER_PAGE'])) + 1):
        nav_uri.append(p + 1)

    nb_total = len(filtered_docs)
    try:
        filtered_docs = filtered_docs[
                        0 + (page - 1) * current_app.config['DOC_PER_PAGE']: 0 + page * current_app.config[
                            'DOC_PER_PAGE']]
    except IndexError:
        pass

    return render_template_with_token(
            'main/fragments/_document_browser.html',
            docs=filtered_docs,
            fields=fields,
            selected_values=form_values,
            nav_uri=nav_uri,
            nb_total=nb_total,
            filtered=docs_are_filtered,
            current_page=page
    )


@app_bp.route('/documents/<doc_id>')
def view_document(doc_id):
    doc = Document.query.filter(Document.id == doc_id, Document.is_published.is_(True)).first()
    if doc is None:
        flash('Document {doc_id} introuvable.'.format(doc_id=doc_id), 'error')
        return redirect(url_for('app_bp.documents'))

    user = current_app.get_current_user()
    can_edit = doc in user.documents_i_can_edit

    return render_template_with_token('main/document.html', title='Documents - Adele', doc=doc, can_edit=can_edit)


@app_bp.route('/documents/<doc_id>/edition')
@login_required
def document_edit(doc_id):
    user = current_app.get_current_user()
    if user.is_anonymous or not (user.is_teacher or user.is_admin):
        doc = Document.query.first()
    else:
        doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None:
        flash('Document {doc_id} introuvable.'.format(doc_id=doc_id), 'error')
        return redirect(url_for('app_bp.documents'))

    if not doc in user.documents_i_can_edit:
        abort(403)

    return render_template_with_token('main/document_edit.html', title='Document - Adele', doc=doc)


"""
---------------------------------
API routes
---------------------------------
"""

from app.api.routes import *
