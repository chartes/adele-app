import math

from flask import render_template, flash, redirect, url_for, session, current_app, abort
from flask_user import login_required, roles_required
from flask_user.forms import InviteUserForm
from jinja2 import Markup

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


@app_bp.route('/flash-messages/')
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


@app_bp.route('/dashboard/document-list')
@login_required
def dashboard_document_list():
    user = current_app.get_current_user()
    docs = user.documents_i_can_edit
    return render_template_with_token('main/fragments/_document_management_list.html', docs=docs, current_user=user)


@app_bp.route('/dashboard/manual')
@login_required
def dashboard_manual():
    return render_template_with_token('main/dashboard/manual.html')


@app_bp.route('/dashboard/manage-users/userlist/<list_id>', methods=["POST"])
@roles_required(['admin', 'teacher'])
@login_required
def dashboard_manage_users_list(list_id):
    user_list = Whitelist.query.filter(Whitelist.id == list_id).first()

    userlist_page = request.form.get('userlist_page')
    userlist_page = int(userlist_page if userlist_page and userlist_page != '' else 1)
    nav_uri = []

    _page_max = current_app.config['USERS_PER_PAGE']
    if len(user_list.users) == _page_max:
        nav_uri = [1]
    else:
        for p in range(0, int(math.floor(len(user_list.users) / _page_max)) + 1):
            nav_uri.append(p + 1)

    def get_page(p):
        return user_list.users[0 + (p - 1) * _page_max: 0 + p * _page_max]

    paged_users = get_page(userlist_page)
    if len(paged_users) == 0 and userlist_page > 1:
        paged_users = get_page(userlist_page - 1)

    return render_template_with_token(
        'main/fragments/_manage_users_list.html',
        users=paged_users,
        current_userlist_page=userlist_page,
        nav_uri=nav_uri
    )


@app_bp.route('/dashboard/manage-users/users/<list_id>', methods=["POST"])
@roles_required(['admin', 'teacher'])
@login_required
def dashboard_manage_users_users(list_id):

    user_list = Whitelist.query.filter(Whitelist.id == list_id).first()
    users = User.query.filter(User.id.notin_([u.id for u in user_list.users])).all()

    # manage pagination
    users = sorted(users, key=lambda u: "%s %s" % (u.last_name, u.first_name))

    user_page = request.form.get('user_page')
    user_page = int(user_page if user_page and user_page != '' else 1)
    nav_uri = []

    _page_max = current_app.config['USERS_PER_PAGE']
    if len(users) == _page_max:
        nav_uri = [1]
    else:
        for p in range(0, int(math.floor(len(users) / _page_max)) + 1):
            nav_uri.append(p + 1)

    def get_page(p):
        return users[0 + (p - 1) * _page_max: 0 + p * _page_max]

    paged_users = get_page(user_page)
    if len(paged_users) == 0 and user_page > 1:
        paged_users = get_page(user_page - 1)

    return render_template_with_token(
        'main/fragments/_manage_users.html',
        users=paged_users,
        current_user_page=user_page,
        nav_uri=nav_uri
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


@app_bp.route('/dashboard/add-document')
def dashboard_add_document():
    user = current_app.get_current_user()

    return render_template_with_token('main/dashboard/add_document.html', title='Documents - Adele')


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
    if user.is_anonymous:
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
            current_page=page,
            current_user=user
    )


@app_bp.route('/documents/<doc_id>')
def view_document(doc_id):
    user = current_app.get_current_user()
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is not None:
        if user.is_anonymous and not doc.is_published:
            doc = None

    if doc is None:
        flash('Document {doc_id} introuvable.'.format(doc_id=doc_id), 'error')
        return redirect(url_for('app_bp.documents'))

    can_edit = doc in user.documents_i_can_edit

    return render_template_with_token('main/document_view.html', title='Documents - Adele', doc=doc, can_edit=can_edit)


@app_bp.route('/documents/<doc_id>/view/notice')
def view_document_notice(doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    return render_template('main/fragments/document_view/_notice.html', doc=doc)


@app_bp.route('/documents/<doc_id>/view/transcription')
def view_document_transcription(doc_id):
    from .api.transcriptions.routes import get_reference_transcription
    tr = get_reference_transcription(doc_id)
    return render_template('main/fragments/document_view/_transcription.html',
                           transcription=Markup(tr.content))


@app_bp.route('/documents/<doc_id>/view/translation')
def view_document_translation(doc_id):
    from .api.translations.routes import get_reference_translation
    tr = get_reference_translation(doc_id)
    return render_template('main/fragments/document_view/_translation.html',
                           translation=Markup(tr.content))


@app_bp.route('/documents/<doc_id>/view/transcription_alignment')
def view_document_transcription_alignment(doc_id):
    from .api.translations.routes import get_reference_translation
    from .api.transcriptions.routes import get_reference_transcription
    translation = get_reference_translation(doc_id)
    transcription = get_reference_transcription(doc_id)
    return render_template('main/fragments/document_view/_transcription_alignment.html',
                           doc_id=doc_id,
                           transcription=Markup(transcription.content),
                           translation=Markup(translation.content))


@app_bp.route('/documents/<doc_id>/view/commentaries')
def view_document_commentaries(doc_id):
    from .api.commentaries.routes import get_reference_commentaries
    commentaries = get_reference_commentaries(doc_id)
    return render_template('main/fragments/document_view/_commentaries.html',
                           commentaries=commentaries)


@app_bp.route('/documents/<doc_id>/view/speech-parts')
def view_document_speech_parts(doc_id):
    from .api.transcriptions.routes import get_reference_alignment_discours
    from .api.transcriptions.routes import get_reference_transcription
    transcription = get_reference_transcription(doc_id)
    speech_parts = get_reference_alignment_discours(doc_id)
    return render_template('main/fragments/document_view/_speech_parts.html',
                           transcription=Markup(transcription.content),
                           speech_parts=speech_parts)


@app_bp.route('/documents/<doc_id>/edition')
@login_required
def document_edit(doc_id):
    user = current_app.get_current_user()
    doc = None
    if not user.is_anonymous:
        doc = Document.query.filter(Document.id == doc_id).first()

    if doc is None:
        flash('Document {doc_id} introuvable.'.format(doc_id=doc_id), 'error')
        return redirect(url_for('app_bp.documents'))

    if doc not in user.documents_i_can_edit:
        abort(403)

    return render_template_with_token('main/document_edit.html', title='Document - Adele', doc=doc)


"""
---------------------------------
API routes
---------------------------------
"""

from app.api.routes import *
