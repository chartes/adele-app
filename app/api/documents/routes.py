import datetime
import pprint
from math import ceil
from urllib.request import build_opener

from flask import request,  current_app
from flask_jwt_extended import jwt_required
from sqlalchemy import or_, and_, any_
from sqlalchemy.testing import in_

from app.api.routes import api_bp, json_loads
from app.models import Document, Institution, Editor, Country, District, ActeType, Language, Tradition, Whitelist, \
    ImageUrl, Image, Note
from app.utils import make_404, make_200, forbid_if_nor_teacher_nor_admin_and_wants_user_data, make_400, \
    forbid_if_nor_teacher_nor_admin, make_204, make_409, forbid_if_not_in_whitelist, check_no_XMLParserError

"""
===========================
    Document
===========================
"""


@api_bp.route('/api/<api_version>/documents/<doc_id>')
def api_documents(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc:
        return make_200(doc.serialize())
    else:
        return make_404("Document {0} not found".format(doc_id))


@api_bp.route('/api/<api_version>/documents/<doc_id>/status')
@jwt_required
def api_documents_status(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None:
        return make_404()
    return make_200(data=doc.serialize_status())

@api_bp.route('/api/<api_version>/documents/<doc_id>/publish')
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_documents_publish(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None:
        return make_404()

    is_not_allowed = forbid_if_not_in_whitelist(current_app, doc)
    if is_not_allowed:
        return is_not_allowed

    try:
        doc.is_published = True
        db.session.commit()
        return make_200(data=doc.serialize_status())
    except Exception as e:
        return make_400(str(e))

@api_bp.route('/api/<api_version>/documents/<doc_id>/unpublish')
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_documents_unpublish(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None:
        return make_404()

    is_not_allowed = forbid_if_not_in_whitelist(current_app, doc)
    if is_not_allowed:
        return is_not_allowed
    try:
        doc.is_published = False
        db.session.commit()
        return make_200(data=doc.serialize_status())
    except Exception as e:
        return make_400(str(e))


@api_bp.route('/api/<api_version>/documents', methods=['POST'])
def api_get_documents(api_version):
    data = request.get_json()
    page_size = max(data.get("pageSize", 20), 1)
    page_number = max(data.get("pageNum", 1), 1)

    query = Document.query

    filters = data.get("filters", [])
    or_stmts = []

    # FILTERS
    if "centuries" in filters:
        centuries = []
        for c in filters["centuries"]:
            s = int(c["id"])
            centuries.append(Document.creation.between((s-1) * 100, s * 100))
        if len(centuries) > 0:
            or_stmts.append(or_(*centuries))

    # same field on the model but dealing with years and not centuries
    if "creationRange" in filters and filters.get("filterByCreationRange", True):
        start, end = filters["creationRange"]
        print(start, end)
        or_stmts.append(Document.creation.between(int(start), int(end)))

    if "copyCenturies" in filters:
        centuries = []
        for c in filters["copyCenturies"]:
            centuries.append(Document.copy_cent == int(c["id"]))
        if len(centuries) > 0:
            or_stmts.append(or_(*centuries))

    if "languages" in filters:
        asked_codes = [c["code"] for c in filters["languages"]]
        if len(asked_codes) > 0:
            or_stmts.append(Document.languages.any(Language.code.in_(asked_codes)))

    if "traditions" in filters:
        asked_traditions = [c["id"] for c in filters["traditions"]]
        if len(asked_traditions) > 0:
            or_stmts.append(Document.traditions.any(Tradition.id.in_(asked_traditions)))

    if "acteTypes" in filters:
        asked_acteTypes = [c["id"] for c in filters["acteTypes"]]
        if len(asked_acteTypes) > 0:
            or_stmts.append(Document.acte_types.any(ActeType.id.in_(asked_acteTypes)))

    if "countries" in filters:
        asked_countries = [c["id"] for c in filters["countries"]]
        if len(asked_countries) > 0:
            or_stmts.append(Document.countries.any(Country.id.in_(asked_countries)))

    if "districts" in filters:
        asked_districts = [c["id"] for c in filters["districts"]]
        if len(asked_districts) > 0:
            or_stmts.append(Document.districts.any(District.id.in_(asked_districts)))

    if "institutions" in filters:
        asked_institutions = [c["id"] for c in filters["institutions"]]
        if len(asked_institutions) > 0:
            or_stmts.append(Document.institution.has(Institution.id.in_(asked_institutions)))

    # SORTS
    sorts = data.get("sorts", [])

    query = query.filter(and_(*or_stmts))
    print(query)
    count = query.count()
    docs = query.paginate(int(page_number), int(page_size), max_per_page=100, error_out=False).items

    return make_200(data={"meta": {"totalCount": count, "currentPage": page_number, "nbPages": ceil(count/page_size)}, "data": [doc.serialize() for doc in docs]})


@api_bp.route('/api/<api_version>/documents', methods=['POST'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_post_documents(api_version):
    data = request.get_json()
    if "data" in data:
        data = data["data"]

    tmp_doc = {
        "title": "Sans titre"
    }
    for key in ("title", "subtitle", "argument", "pressmark",
                "creation", "creation_lab", "copy_year", "copy_cent"):
        if key in data:
            tmp_doc[key] = data[key]

    if "institution_id" in data:
        tmp_doc["institution"] = Institution.query.filter(Institution.id == data["institution_id"]).first()

    if "editor_id" in data:
        if not isinstance(data["editor_id"], list):
            data["editor_id"] = [data["editor_id"]]
        tmp_doc["editors"] = Editor.query.filter(Editor.id.in_(data["editor_id"])).all()

    if "country_id" in data:
        if not isinstance(data["country_id"], list):
            data["country_id"] = [data["country_id"]]
        tmp_doc["countries"] = Country.query.filter(Country.id.in_(data["country_id"])).all()

    if "district_id" in data:
        if not isinstance(data["district_id"], list):
            data["district_id"] = [data["district_id"]]
        tmp_doc["districts"] = District.query.filter(District.id.in_(data["district_id"])).all()

    if "acte_type_id" in data:
        if not isinstance(data["acte_type_id"], list):
            data["acte_type_id"] = [data["acte_type_id"]]
        tmp_doc["acte_types"] = ActeType.query.filter(ActeType.id.in_(data["acte_type_id"])).all()

    if "language_code" in data:
        if not isinstance(data["language_code"], list):
            data["language_code"] = [data["language_code"]]
        tmp_doc["languages"] = Language.query.filter(Language.code.in_(data["language_code"])).all()

    if "tradition_id" in data:
        if not isinstance(data["tradition_id"], list):
            data["tradition_id"] = [data["tradition_id"]]
        tmp_doc["traditions"] = Tradition.query.filter(Tradition.id.in_(data["tradition_id"])).all()

    if "linked_document_id" in data:
        if not isinstance(data["linked_document_id"], list):
            data["linked_document_id"] = [data["linked_document_id"]]
        tmp_doc["linked_documents"] = Document.query.filter(Document.id.in_(data["linked_document_id"])).all()

    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    tmp_doc["date_insert"] = now
    tmp_doc["date_update"] = now

    user = current_app.get_current_user()
    tmp_doc["user_id"] = user.id
    doc = Document(**tmp_doc)

    try:
        db.session.add(doc)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_400(str(e))

    return make_200(data=doc.serialize())


@api_bp.route('/api/<api_version>/documents/<doc_id>', methods=['PUT'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_put_documents(api_version, doc_id):
    data = request.get_json()
    if "data" in data:
        data = data["data"]

    tmp_doc = Document.query.filter(Document.id == doc_id).first()
    if tmp_doc is None:
        return make_404("Document not found")

    is_not_allowed = forbid_if_not_in_whitelist(current_app, tmp_doc)
    if is_not_allowed:
        return is_not_allowed

    if "title" in data: tmp_doc.title = data["title"]
    if "subtitle" in data: tmp_doc.subtitle = data["subtitle"]

    if "argument" in data:
        error = check_no_XMLParserError(data["argument"])
        if error:
            return error
        tmp_doc.argument = data["argument"]

    if "pressmark" in data: tmp_doc.pressmark = data["pressmark"]
    if "creation" in data: tmp_doc.creation = data["creation"]
    if "creation_lab" in data: tmp_doc.creation_lab = data["creation_lab"]
    if "copy_year" in data: tmp_doc.copy_year = data["copy_year"]
    if "copy_cent" in data: tmp_doc.copy_cent = data["copy_cent"]

    if "institution_id" in data:
        tmp_doc.institution = Institution.query.filter(Institution.id == data["institution_id"]).first()

    if "editor_ref" in data:
        tmp_doc.editors = Editor.query.filter(Editor.ref.in_(data["editor_ref"])).all()

    if "country_ref" in data:
        tmp_doc.countries = Country.query.filter(Country.ref.in_(data["country_ref"])).all()

    if "district_id" in data:
        tmp_doc.districts = District.query.filter(District.id.in_(data["district_id"])).all()

    if "acte_type_id" in data:
        tmp_doc.acte_types = ActeType.query.filter(ActeType.id.in_(data["acte_type_id"])).all()

    if "language_code" in data:
        tmp_doc.languages = Language.query.filter(Language.code.in_(data["language_code"])).all()

    if "tradition_id" in data:
        tmp_doc.traditions = Tradition.query.filter(Tradition.id.in_(data["tradition_id"])).all()

    if "linked_document_id" in data:
        tmp_doc.linked_documents = Document.query.filter(Document.id.in_(data["linked_document_id"])).all()

    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    tmp_doc.date_update = now

    try:
        db.session.add(tmp_doc)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_400(str(e))

    return make_200(data=tmp_doc.serialize())


@api_bp.route('/api/<api_version>/documents/<doc_id>', methods=['DELETE'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_delete_documents(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None:
        return make_404("Document not found")

    try:
        db.session.delete(doc)
        db.session.commit()
        print("document", doc_id, "deleted")
    except Exception as e:
        db.session.rollback()
        return make_400("Cannot delete data: %s" % str(e))

    return make_204()

@api_bp.route('/api/<api_version>/documents/notes/<note_id>', methods=["DELETE"])
@jwt_required
def api_delete_notes(api_version, note_id):
    current_user = current_app.get_current_user()
    note = Note.query.filter(Note.id == note_id).first()
    if note is None:
        return make_400('This note does not exist')
    if current_user.is_admin or current_user.is_teacher or note.user_id == current_user.id:
        try:
            db.session.delete(note)
            db.session.commit()
            return make_200()
        except Exception as e:
            db.session.rollback()
            return make_400("Cannot delete data: %s" % str(e))
    else:
        return make_403('You cannot delete this note')

@api_bp.route('/api/<api_version>/documents/<doc_id>/whitelist', methods=['POST'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_change_documents_whitelist(api_version, doc_id):
    """
    {
        "data" : {
            "whitelist_id" : 1
        }
    }
    :param api_version:
    :param doc_id:
    :return:
    """

    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None:
        return make_404()

    # maybe forbid to other teachers ?
    is_not_allowed = forbid_if_not_in_whitelist(current_app, doc)
    if is_not_allowed:
        return is_not_allowed

    data = request.get_json()
    data = data.get('data')

    try:
        new_white_list_id = data.get('whitelist_id')
        if new_white_list_id is None or int(new_white_list_id) == -1:
            doc.whitelist_id = None
        else:
            wl = Whitelist.query.filter(Whitelist.id == new_white_list_id).first()
            doc.whitelist = wl
        db.session.commit()
    except Exception as e:
        return make_400(str(e))

    return make_200(data=doc.serialize())


@api_bp.route('/api/<api_version>/documents/<doc_id>/open')
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_change_documents_open(api_version, doc_id):
    """
    :param api_version:
    :param doc_id:
    :return:
    """
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None:
        return make_404()

    doc.date_closing = None
    db.session.add(doc)
    db.session.commit()

    return make_200(data=doc.serialize_status())


@api_bp.route('/api/<api_version>/documents/<doc_id>/close', methods=['POST'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_change_documents_closing_date(api_version, doc_id):
    """
    {
        "data" : {
            "closing_date" : "15/10/2020"
        }
    }
    # dd/mm/YYYY
    :param api_version:
    :param doc_id:
    :return:
    """

    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None:
        return make_404()

    data = request.get_json()
    data = data.get('data')
    try:
        new_closing_date = data.get('closing_date')
        if not new_closing_date or len(new_closing_date) == 0:
            new_closing_date = None
        else:
            new_closing_date = datetime.datetime.strptime(new_closing_date, '%d/%m/%Y')
            new_closing_date = new_closing_date.strftime('%Y-%m-%d %H:%M:%S')

        doc.date_closing = new_closing_date
        db.session.commit()
    except Exception as e:
        return make_400(str(e))

    return make_200(data=doc.serialize_status())


@api_bp.route('/api/<api_version>/documents/add', methods=['POST'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_add_document(api_version):

    data = request.get_json()
    data = data["data"]

    user = current_app.get_current_user()
    kwargs = {
        "title": data.get('title'),
        "subtitle": data.get('subtitle'),
        "user_id": user.id,
        "is_published": 1,
        "whitelist_id": data.get('whitelist-id', 34)  # TODO
    }

    new_doc = Document(**kwargs)
    db.session.add(new_doc)
    db.session.commit()
    return make_200(data=new_doc.serialize())


@api_bp.route('/api/<api_version>/documents/<doc_id>/iiif/manifest', methods=['POST'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_post_document_manifest(api_version, doc_id):
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None:
        return make_404()

    is_not_allowed = forbid_if_not_in_whitelist(current_app, doc)
    if is_not_allowed:
        return is_not_allowed

    data = request.get_json()
    data = data["data"]
    manifest_url = data.get("manifest_url")

    if Image.query.filter(Image.manifest_url == manifest_url).first() or \
            ImageUrl.query.filter(ImageUrl.manifest_url == manifest_url).first():
        return make_409(
            details="This manifest is already used by another document. Please choose another or upload it to another "
                    "URL. "
        )

    # FETCH the manifest
    try:
        op = build_opener()
        manifest = op.open(manifest_url, timeout=20).read()
        manifest = json_loads(manifest)
    except Exception as e:
        return make_400(details="Cannot fetch manifest: %s" % str(e))

    # delete old images
    for old_image in Image.query.filter(Image.doc_id == doc.id).all():
        db.session.delete(old_image)
    for old_image_url in ImageUrl.query.filter(ImageUrl.manifest_url == manifest_url).all():
        db.session.delete(old_image_url)

    # add new images
    for canvas_idx, canvas in enumerate(manifest["sequences"][0]['canvases']):
        for img_idx, img in enumerate(canvas["images"]):
            new_img = Image(manifest_url=manifest_url, canvas_idx=canvas_idx, img_idx=img_idx, doc_id=doc_id)
            new_img_url = ImageUrl(manifest_url=manifest_url, canvas_idx=canvas_idx, img_idx=img_idx,
                                   img_url=img["resource"]["@id"])
            db.session.add(new_img)
            db.session.add(new_img_url)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_400(details=str(e))

    return make_200(data=[i.serialize() for i in doc.images])


# IMPORT DOCUMENT VALIDATION STEP ROUTES
from .document_validation import *
from .document_management import *
