from flask import url_for, request, redirect
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound

from app import get_user_from_username, get_current_user, db, auth
from app.api.response import APIResponseFactory
from app.api.routes import query_json_endpoint, api_bp
from app.models import Transcription, User, Document

"""
===========================
    Transcriptions
===========================
"""


def get_reference_transcription(doc_id):
    """

    :param doc_id:
    :return:
    """
    transcription = None
    try:
        transcriptions = Transcription.query.filter(doc_id == Transcription.doc_id).all()
        for tr in transcriptions:
            user = User.query.filter(User.id == tr.user_id).first()
            if user.is_teacher:
                transcription = tr
                break
    except NoResultFound:
        pass

    return transcription


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/reference')
def api_documents_transcriptions_reference(api_version, doc_id):
    tr = get_reference_transcription(doc_id)
    if tr is None:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Transcription not found"
        })
    else:
        response = APIResponseFactory.make_response(data=tr.serialize())
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions')
@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/from-user/<user_id>')
def api_documents_transcriptions(api_version, doc_id, user_id=None):
    user = get_current_user()
    if user is None:
        return redirect(url_for("api_bp.api_documents_transcriptions_reference", api_version="1.0", doc_id=doc_id))

    response = None
    # only teacher and admin can see everything
    if (not user.is_teacher and not user.is_admin) and user_id is not None and int(user_id) != int(user.id):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })

    if response is None:
        if user_id is None:
            if not user.is_teacher and not user.is_admin:
                user_id = user.id
            else:
                # In that case do not filter
                user_id = Transcription.user_id

        try:
            transcriptions = Transcription.query.filter(
                Transcription.doc_id == doc_id,
                Transcription.user_id == user_id
            ).all()

            response = APIResponseFactory.make_response(data=[tr.serialize() for tr in transcriptions])
        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "Transcription not found"
            })

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions', methods=["POST"])
@auth.login_required
def api_post_documents_transcriptions(api_version, doc_id):
    """
    {
        "data":
            {
                "content" :  "My first transcription",   (mandatory)
                "username":  "Eleve1"                    (optionnal)
            }
    }
    :param api_version:
    :param doc_id:
    :return:
    """
    data = request.get_json()
    response = None
    user = get_current_user()
    usernames = set()
    created_users = set()

    try:
        doc = Document.query.filter(Document.id == doc_id).one()
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Document {0} not found".format(doc_id)
        })

    if "data" in data and response is None:
        data = data["data"]

        if not isinstance(data, list):
            data = [data]

        # do not allow multiple transcriptions for a single user
        for d in data:
            if "username" in d:
                username = d["username"]
            else:
                username = user.username

            if username in usernames:
                response = APIResponseFactory.make_response(errors={
                    "status": 403,
                    "title": "Insert forbidden",
                    "details": "Only one transcription per user and document is allowed"
                })
            else:
                usernames.add(username)

        if response is None:

            user = get_current_user()
            user_id = user.id

            for tr in data:
                user = get_current_user()
                user_id = user.id
                # teachers and admins can put/post/delete on others behalf
                if (user.is_teacher or user.is_admin) and "username" in tr:
                    user = get_user_from_username(tr["username"])
                    if user is not None:
                        user_id = user.id

                # check that there's no transcription yet for this document/user
                existing_tr = Transcription.query.filter(
                    Transcription.user_id == user_id,
                    Transcription.doc_id == doc_id
                ).first()

                if existing_tr is not None:
                    response = APIResponseFactory.make_response(errors={
                        "status": 403,
                        "title": "Insert forbidden",
                        "details": "Only one transcription per user and document is allowed"
                    })

                if response is None:
                    # check the request data structure
                    if "content" not in tr:
                        response = APIResponseFactory.make_response(errors={
                            "status": 403,
                            "title": "Insert forbidden",
                            "details": "Data structure is incorrect: missing a 'content' field"
                        })
                    else:

                        # get the transcription id max
                        try:
                            transcription_max_id = db.session.query(func.max(Transcription.id)).one()
                            transcription_max_id = transcription_max_id[0] + 1
                        except NoResultFound:
                            # it is the transcription for this user and this document
                            transcription_max_id = 1

                        new_transcription = Transcription(
                            id=transcription_max_id,
                            content=tr["content"],
                            doc_id=doc_id,
                            user_id=user_id
                        )

                        db.session.add(new_transcription)
                        created_users.add(user)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                response = APIResponseFactory.make_response(errors={
                    "status": 403, "title": "Cannot insert data", "details": str(e)
                })

            if response is None:
                created_data = []
                for usr in created_users:
                    json_obj = query_json_endpoint(
                        request,
                        url_for(
                            "api_bp.api_documents_transcriptions",
                            api_version=api_version,
                            doc_id=doc_id,
                            user_id=usr.id
                        ),
                        user=usr
                    )
                    if "data" in json_obj:
                        created_data.append(json_obj["data"])
                    elif "errors":
                        created_data.append(json_obj["errors"])

                response = APIResponseFactory.make_response(data=created_data)

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions', methods=["PUT"])
@auth.login_required
def api_put_documents_transcriptions(api_version, doc_id):
    """
    {
        "data": [
            {
                "content" :  "My first transcription",   (mandatory)
                "username":  "Eleve1"                    (optionnal)
            },
            {
                "content" :  "My first transcription",   (mandatory)
                "username":  "Eleve2"                    (optionnal)
            }
        ]
    }
    :param api_version:
    :param doc_id:
    :return:
    """
    data = request.get_json()
    response = None

    try:
        doc = Document.query.filter(Document.id == doc_id).one()
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Document {0} not found".format(doc_id)
        })

    if "data" in data and response is None:
        data = data["data"]

        if not isinstance(data, list):
            data = [data]

        if response is None:

            updated_users = set()
            user = get_current_user()
            user_id = user.id

            for tr in data:

                user = get_current_user()
                user_id = user.id

                # teachers and admins can put/post/delete on others behalf
                if (user.is_teacher or user.is_admin) and "username" in tr:
                    user = get_user_from_username(tr["username"])
                    if user is not None:
                        user_id = user.id

                # check the request data structure
                if "content" not in tr:
                    response = APIResponseFactory.make_response(errors={
                        "status": 403,
                        "title": "Update forbidden",
                        "details": "Data structure is incorrect: missing a 'content' field"
                    })
                    break
                else:

                    try:
                        # get the transcription to update
                        transcription = Transcription.query.filter(
                            Transcription.user_id == user_id,
                            Transcription.doc_id == doc_id
                        ).one()

                        transcription.content = tr["content"]
                        db.session.add(transcription)
                        # save which users to retriever later
                        updated_users.add(user)
                    except NoResultFound:
                        response = APIResponseFactory.make_response(errors={
                            "status": 404,
                            "title": "Update forbidden",
                            "details": "Transcription not found"
                        })
                        break

            if response is None:
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    response = APIResponseFactory.make_response(errors={
                        "status": 403, "title": "Cannot update data", "details": str(e)
                    })

            if response is None:
                updated_data = []
                for usr in updated_users:
                    json_obj = query_json_endpoint(
                        request,
                        url_for(
                            "api_bp.api_documents_transcriptions",
                            api_version=api_version,
                            doc_id=doc_id,
                            user_id=user_id
                        ),
                        user=usr
                    )
                    updated_data.append(json_obj)

                response = APIResponseFactory.make_response(data=updated_data)

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/from-user/<user_id>', methods=["DELETE"])
@auth.login_required
def api_delete_documents_transcriptions(api_version, doc_id, user_id):
    """
     :param api_version:
     :param doc_id:
     :return:
     """
    response = None

    try:
        doc = Document.query.filter(Document.id == doc_id).one()
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Document {0} not found".format(doc_id)
        })

    user = get_current_user()
    if user is not None:
        if (not user.is_teacher and not user.is_admin) and user_id != user.id:
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Access forbidden"
            })

    # delete transcriptions for the given user id
    if response is None:
        try:
            # bring the transcription to delete
            transcription = Transcription.query.filter(
                Transcription.user_id == user_id,
                Transcription.doc_id == doc_id
            ).one()
            db.session.delete(transcription)
        except NoResultFound:
            pass

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
