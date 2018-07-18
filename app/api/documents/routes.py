import datetime

from flask import request, url_for, current_app
from flask_user import roles_required
from sqlalchemy.orm.exc import NoResultFound

from app import auth, db
from app.api.response import APIResponseFactory
from app.api.routes import api_bp, query_json_endpoint
from app.models import Document, Institution, Editor, Country, District, ActeType, Language, Tradition, Whitelist

"""
===========================
    Document
===========================
"""


@api_bp.route('/api/<api_version>/documents/<doc_id>')
def api_documents(api_version, doc_id):
    try:
        doc = Document.query.filter(Document.id == doc_id).one()
        response = APIResponseFactory.make_response(data=doc.serialize())
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Document {0} not found".format(doc_id)
        })
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/publish')
@auth.login_required
@roles_required(["admin", "teacher"])
def api_documents_publish(api_version, doc_id):
    try:
        doc = Document.query.filter(Document.id == doc_id).one()
        user = current_app.get_current_user()
        if user.is_anonymous or not (user.is_teacher or user.is_admin):
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Access forbidden"
            })
        else:
            doc.is_published = True
            db.session.commit()
            response = APIResponseFactory.make_response(data=doc.serialize())
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Document {0} not found".format(doc_id)
        })
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/unpublish')
@roles_required(["admin", "teacher"])
@auth.login_required
def api_documents_unpublish(api_version, doc_id):
    try:
        doc = Document.query.filter(Document.id == doc_id).one()
        user = current_app.get_current_user()
        if user.is_anonymous or not (user.is_teacher or user.is_admin):
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Access forbidden"
            })
        else:
            doc.is_published = False
            db.session.commit()
            response = APIResponseFactory.make_response(data=doc.serialize())
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Document {0} not found".format(doc_id)
        })
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents')
def api_documents_id_list(api_version):
    try:
        docs = Document.query.all()
        data = [doc.id for doc in docs]
        response = APIResponseFactory.make_response(data=data)
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Documents not found"
        })
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents', methods=['POST', 'PUT'])
@auth.login_required
@roles_required(["admin", "teacher"])
def api_post_documents(api_version):
    """
    {
    "data":
        {
          "title":  "My new title",
          "subtitle": "My new subtitle",
          "argument" : "<p>L’infante Urra</p>"
          "creation": 1400,
          "creation_lab" : "1400",
          "copy_year" : "[1409-1420 ca.]",
          "copy_cent" : 15,
          "institution_id" :  1
          "pressmark" : "J 340, n° 21",

          "editor_id" : [1, 2],
          "country_id" : [1, 2, 3],
          "district_id" : [1, 2, 3],
          "acte_type_id" : [1],
          "language_code" : "fro",
          "tradition_id": [1]
          "linked_document_id" : [110, 22]
        }
    }

    :param api_version:
    :return:
    """
    response = None
    user = current_app.get_current_user()

    if user.is_anonymous or not (user.is_teacher or user.is_admin):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })

    if response is None:
        data = request.get_json()

        if "data" in data:
            data = data["data"]

            is_post_method = request.method == "POST"

            """
                POST: prepare a new doc
                PUT: fetch the doc to modify
            """
            if is_post_method:
                tmp_doc = {
                    "title": "Sans titre"
                }
            else:
                tmp_doc = None
                # PUT method
                if "id" not in data:
                    response = APIResponseFactory.make_response(errors={
                        "status": 404, "title": "Document id is missing from the payload"
                    })
                else:
                    try:
                        tmp_doc = Document.query.filter(Document.id == data["id"]).one()
                    except NoResultFound:
                        response = APIResponseFactory.make_response(errors={
                            "status": 404, "title": "Document {0} does not exist".format(data["id"])
                        })

            if response is None:

                if is_post_method:
                    for key in ("title", "subtitle", "argument", "pressmark",
                                "creation", "creation_lab", "copy_year", "copy_cent"):
                        if key in data:
                            tmp_doc[key] = data[key]
                else:
                    if "title" in data: tmp_doc.title = data["title"]
                    if "subtitle" in data: tmp_doc.subtitle = data["subtitle"]
                    if "argument" in data: tmp_doc.argument = data["argument"]
                    if "pressmark" in data: tmp_doc.pressmark = data["pressmark"]
                    if "creation" in data: tmp_doc.creation = data["creation"]
                    if "creation_lab" in data: tmp_doc.creation_lab = data["creation_lab"]
                    if "copy_year" in data: tmp_doc.copy_year = data["copy_year"]
                    if "copy_cent" in data: tmp_doc.copy_cent = data["copy_cent"]

                if "institution_id" in data:
                    institution = Institution.query.filter(Institution.id == data["institution_id"]).one()
                    if is_post_method:
                        tmp_doc["institution"] = institution
                    else:
                        tmp_doc.institution = institution

                if "editor_id" in data:
                    if not isinstance(data["editor_id"], list):
                        data["editor_id"] = [data["editor_id"]]
                    editors = Editor.query.filter(Editor.id.in_(data["editor_id"])).all()
                    if is_post_method:
                        tmp_doc["editors"] = editors
                    else:
                        tmp_doc.editors = editors

                if "country_id" in data:
                    if not isinstance(data["country_id"], list):
                        data["country_id"] = [data["country_id"]]
                    countries = Country.query.filter(Country.id.in_(data["country_id"])).all()
                    if is_post_method:
                        tmp_doc["countries"] = countries
                    else:
                        tmp_doc.countries = countries

                if "district_id" in data:
                    if not isinstance(data["district_id"], list):
                        data["district_id"] = [data["district_id"]]
                    districts = District.query.filter(District.id.in_(data["district_id"])).all()
                    if is_post_method:
                        tmp_doc["districts"] = districts
                    else:
                        tmp_doc.districts = districts

                if "acte_type_id" in data:
                    if not isinstance(data["acte_type_id"], list):
                        data["acte_type_id"] = [data["acte_type_id"]]
                    acte_types = ActeType.query.filter(ActeType.id.in_(data["acte_type_id"])).all()
                    if is_post_method:
                        tmp_doc["acte_types"] = acte_types
                    else:
                        tmp_doc.acte_types = acte_types

                if "language_code" in data:
                    if not isinstance(data["language_code"], list):
                        data["language_code"] = [data["language_code"]]
                    languages = Language.query.filter(Language.code.in_(data["language_code"])).all()
                    if is_post_method:
                        tmp_doc["languages"] = languages
                    else:
                        tmp_doc.languages = languages

                if "tradition_id" in data:
                    if not isinstance(data["tradition_id"], list):
                        data["tradition_id"] = [data["tradition_id"]]
                    traditions = Tradition.query.filter(Tradition.id.in_(data["tradition_id"])).all()
                    if is_post_method:
                        tmp_doc["traditions"] = traditions
                    else:
                        tmp_doc.traditions = traditions

                if "linked_document_id" in data:
                    if not isinstance(data["linked_document_id"], list):
                        data["linked_document_id"] = [data["linked_document_id"]]
                    linked_documents = Document.query.filter(Document.id.in_(data["linked_document_id"])).all()
                    if is_post_method:
                        tmp_doc["linked_documents"] = linked_documents
                    else:
                        tmp_doc.linked_documents = linked_documents

                now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if is_post_method:
                    tmp_doc["date_insert"] = now
                    tmp_doc["date_update"] = now
                else:
                    tmp_doc.date_update = now

                if response is None:

                    if is_post_method:
                        doc = Document(**tmp_doc)
                    else:
                        doc = tmp_doc

                    db.session.add(doc)

                    try:
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        response = APIResponseFactory.make_response(errors={
                            "status": 403, "title": "Cannot insert data", "details": str(e)
                        })

                    if response is None:
                        json_obj = query_json_endpoint(
                            request,
                            url_for("api_bp.api_documents", api_version=api_version, doc_id=doc.id)
                        )
                        if "data" in json_obj:
                            response = APIResponseFactory.make_response(data=json_obj["data"])
                        else:
                            response = APIResponseFactory.make_response(errors=json_obj["errors"])

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>', methods=['DELETE'])
@auth.login_required
@roles_required(["admin", "teacher"])
def api_delete_documents(api_version, doc_id):

    response = None
    user = current_app.get_current_user()

    if user.is_anonymous or not (user.is_teacher or user.is_admin):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })

    if response is None:
        try:
            doc = Document.query.filter(Document.id == doc_id).one()
            db.session.delete(doc)
        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "Document {0} not found".format(doc_id)
            })

        if response is None:
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                response = APIResponseFactory.make_response(errors={
                    "status": 403, "title": "Cannot delete data", "details": str(e)
                })

        if response is None:
            response = APIResponseFactory.make_response(data=[])

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/whitelist', methods=['POST'])
@auth.login_required
@roles_required(["admin", "teacher"])
def api_change_documents_whitelist(api_version, doc_id):

    user = current_app.get_current_user()

    if user.is_anonymous or not (user.is_teacher or user.is_admin):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })
        return APIResponseFactory.jsonify(response)

    data = request.get_json()
    data = data.get('data')

    doc = Document.query.filter(Document.id == doc_id).first()

    try:
        new_white_list_id = int(data.get('whitelist_id'))
        if new_white_list_id == -1:
            new_white_list_id = None
        else:
            wl = Whitelist.query.filter(Whitelist.id == new_white_list_id).first()
            if wl is None:
                raise Exception("Whitelist does not exist")
        doc.whitelist_id = new_white_list_id
        db.session.commit()
    except Exception as e:
        print(e)

    response = APIResponseFactory.make_response(data=doc.serialize())

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/close', methods=['POST'])
@auth.login_required
@roles_required(["admin", "teacher"])
def api_change_documents_closing_date(api_version, doc_id):

    user = current_app.get_current_user()

    if user.is_anonymous or not (user.is_teacher or user.is_admin):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })
        return APIResponseFactory.jsonify(response)

    data = request.get_json()
    data = data.get('data')

    doc = Document.query.filter(Document.id == doc_id).first()

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
        print(e)

    response = APIResponseFactory.make_response(data=doc.serialize())

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/add', methods=['POST'])
@auth.login_required
@roles_required(["admin", "teacher"])
def api_add_document(api_version):

    user = current_app.get_current_user()

    if user.is_anonymous or not (user.is_teacher or user.is_admin):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })
        return APIResponseFactory.jsonify(response)

    response = None

    data = request.get_json()
    data = data["data"]

    kwargs = {
        "title" : data.get('title'),
        "subtitle": data.get('subtitle'),
        "user_id": user.id,
        "is_published" : 0,
    }

    new_doc = Document(**kwargs)
    db.session.add(new_doc)
    db.session.commit()
    print(new_doc.id)

    response = APIResponseFactory.make_response(data=new_doc.serialize())

    return APIResponseFactory.jsonify(response)