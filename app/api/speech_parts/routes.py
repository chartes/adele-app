from flask import request, current_app
from flask_jwt_extended import jwt_required
from markupsafe import Markup
from sqlalchemy.orm.exc import NoResultFound

from app import db
from app.api.routes import api_bp
from app.api.transcriptions.routes import get_reference_transcription
from app.models import (
    User,
    Document,
    SpeechParts,
)
from app.utils import (
    make_404,
    make_200,
    forbid_if_nor_teacher_nor_admin_and_wants_user_data,
    make_400,
    forbid_if_not_in_whitelist,
    is_closed,
    make_403,
    get_doc,
    check_no_XMLParserError,
)

"""
===========================
    Speech parts
===========================
"""


def get_speech_parts(doc_id, user_id):
    return SpeechParts.query.filter(
        doc_id == SpeechParts.doc_id, user_id == SpeechParts.user_id
    ).first()


def get_reference_speech_parts(doc_id):
    """
    :param doc_id:
    :return:
    """
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is not None and doc.is_speechparts_validated:
        return SpeechParts.query.filter(
            doc_id == SpeechParts.doc_id,
            doc.user_id == SpeechParts.user_id
        ).first()

    return None


@api_bp.route("/api/<api_version>/documents/<doc_id>/speech-parts-content/users")
def api_documents_speech_parts_users(api_version, doc_id):
    users = []
    try:
        all_speech_parts = SpeechParts.query.filter(
            SpeechParts.doc_id == doc_id
        ).all()
        users = User.query.filter(
            User.id.in_(set([sp.user_id for sp in all_speech_parts]))
        ).all()
        users = [{"id": user.id, "username": user.username} for user in users]
    except NoResultFound:
        pass
    return make_200(data=users)


@api_bp.route(
    "/api/<api_version>/documents/<doc_id>/speech-parts-content/from-user/<user_id>"
)
@jwt_required
def api_documents_speech_parts_from_user(api_version, doc_id, user_id=None):
    sp = get_speech_parts(doc_id, user_id)
    if sp is None:
        return make_404()
    return make_200(data=sp.serialize())


@api_bp.route(
    "/api/<api_version>/documents/<doc_id>/speech-parts-content/from-user/<user_id>",
    methods=["POST"],
)
@jwt_required
def api_post_documents_speech_parts(api_version, doc_id, user_id):
    """
    :param user_id:
    :param api_version:
    :param doc_id:
    :return:
    """

    is_not_allowed = forbid_if_not_in_whitelist(
        current_app, Document.query.filter(Document.id == doc_id).first()
    )
    if is_not_allowed:
        return is_not_allowed

    # teachers can still post notes in validated transcription
    current_user = current_app.get_current_user()
    if not get_doc(doc_id).is_transcription_validated:
        return make_403()
    if not current_user.is_teacher and get_doc(doc_id).is_speechparts_validated:
        return make_403()

    forbid = is_closed(doc_id)
    if forbid:
        return forbid

    try:
        sp = SpeechParts(
            doc_id=doc_id, content=get_reference_transcription(doc_id).content, user_id=user_id
        )
        db.session.add(sp)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Error", str(e))
        return make_400(str(e))
    return make_200(data=sp.serialize())


@api_bp.route(
    "/api/<api_version>/documents/<doc_id>/speech-parts-content/from-user/<user_id>",
    methods=["PUT"],
)
@jwt_required
def api_put_documents_speech_parts(api_version, doc_id, user_id):
    """
    {
        "data":
            {
                "content" :  "My transcription with speech parts"
            }
    }
    :param user_id:
    :param api_version:
    :param doc_id:
    :return:
    """

    is_not_allowed = forbid_if_not_in_whitelist(
        current_app, Document.query.filter(Document.id == doc_id).first()
    )
    if is_not_allowed:
        return is_not_allowed

    # teachers can still update validated transcription
    current_user = current_app.get_current_user()
    if not get_doc(doc_id).is_transcription_validated:
        return make_403()
    if not current_user.is_teacher and get_doc(doc_id).is_speechparts_validated:
        return make_403()

    forbid = is_closed(doc_id)
    if forbid:
        return forbid

    data = request.get_json()
    if "data" in data:
        data = data["data"]
        sp = get_speech_parts(doc_id=doc_id, user_id=user_id)
        if sp is None:
            return make_404()
        try:
            if "content" in data:
                error = check_no_XMLParserError(data["content"])
                if error:
                    raise Exception(
                        "Speech part content is malformed: %s", str(error)
                    )
                sp.content = data["content"]
                db.session.add(sp)
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            print("Error", str(e))
            return make_400(str(e))
        return make_200(data=sp.serialize())
    else:
        return make_400("no data")


def delete_document_speech_parts(doc_id, user_id):
    forbid = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
    if forbid:
        return forbid

    is_not_allowed = forbid_if_not_in_whitelist(
        current_app, Document.query.filter(Document.id == doc_id).first()
    )
    if is_not_allowed:
        return is_not_allowed

    closed = is_closed(doc_id)
    if closed:
        return closed

    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None:
        return make_404()

    is_not_allowed = forbid_if_not_in_whitelist(current_app, doc)
    if is_not_allowed:
        return is_not_allowed

    sp = get_speech_parts(doc_id=doc_id, user_id=user_id)
    if sp is None:
        return make_404()

    try:
        db.session.delete(sp)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(str(e))
        return make_400(str(e))

    return make_200(data=doc.validation_flags)


@api_bp.route(
    "/api/<api_version>/documents/<doc_id>/speech-parts-content/from-user/<user_id>",
    methods=["DELETE"],
)
@jwt_required
def api_delete_documents_speech_parts(api_version, doc_id, user_id):
    return delete_document_speech_parts(doc_id, user_id)


@api_bp.route("/api/<api_version>/documents/<doc_id>/view/speech-parts-content")
@api_bp.route(
    "/api/<api_version>/documents/<doc_id>/view/speech-parts-content/from-user/<user_id>"
)
def view_document_speech_parts(api_version, doc_id, user_id=None):
    if user_id is not None:
        sp = get_speech_parts(doc_id, user_id)
    else:
        sp = get_reference_speech_parts(doc_id)

    if sp is None:
        return make_404()

    if user_id is None:
        user_id = sp.user_id
    return make_200(data=
        {
            "doc_id": sp.doc_id,
            "user_id": user_id,
            "content": Markup(sp.content) if sp.content is not None else "",
        }
    )
