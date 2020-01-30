from flask import request, current_app
from flask_jwt_extended import jwt_required
from markupsafe import Markup
from sqlalchemy.orm.exc import NoResultFound

from app import db
from app.api.routes import api_bp
from app.api.transcriptions.routes import get_reference_transcription, add_notes_refs_to_text
from app.models import Commentary, Document
from app.utils import make_403, make_200, make_404, forbid_if_nor_teacher_nor_admin_and_wants_user_data, make_409, \
    make_400, get_doc


def get_commentaries(doc_id, user_id):
    """

    :param user_id:
    :param type_id:
    :param doc_id:
    :return:
    """
    return Commentary.query.filter(
        doc_id == Commentary.doc_id,
        user_id == Commentary.user_id,
    ).all()


def get_reference_commentaries(doc_id, type_id=None):
    """

    :param type_id:
    :param doc_id:
    :return:
    """
    from app.api.transcriptions.routes import get_reference_transcription
    tr_ref = get_reference_transcription(doc_id)
    if tr_ref is None:
        return []

    if type_id is None:
        type_id = Commentary.type_id

    return Commentary.query.filter(
        doc_id == Commentary.doc_id,
        tr_ref.user_id == Commentary.user_id,
        type_id == Commentary.type_id
    ).all()


@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries')
def api_all_commentary(api_version, doc_id):
    if not get_doc(doc_id).is_transcription_validated:
        return make_403()

    tr = get_reference_transcription(doc_id)
    if tr is None:
        return make_404()

    commentaries = Commentary.query.filter(
        Commentary.doc_id == doc_id,
        Commentary.user_id == tr.user_id,
    ).all()

    return make_200(data=[c.serialize() for c in commentaries])


@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id>')
@jwt_required
def api_commentary_from_user(api_version, doc_id, user_id):

    forbid = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
    if forbid:
        return forbid

    # teachers can still post notes in validated transcription
    current_user = current_app.get_current_user()
    if not current_user.is_teacher and get_doc(doc_id).is_transcription_validated:
        return make_403()

    commentaries = Commentary.query.filter(
        Commentary.doc_id == doc_id,
        Commentary.user_id == user_id,
    ).all()

    if len(commentaries) == 0:
        return make_404()

    return make_200(data=[c.serialize() for c in commentaries])


@api_bp.route('/api/<api_version>/documents/<doc_id>/view/commentaries')
@api_bp.route('/api/<api_version>/documents/<doc_id>/view/commentaries/from-user/<user_id>')
def view_document_commentaries(api_version, doc_id, user_id=None):
    if user_id is not None:
        forbid = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
        if forbid:
            return forbid
        coms = get_commentaries(doc_id, user_id)
    else:
        coms = get_reference_commentaries(doc_id)

    if coms is None or len(coms) == 0:
        return make_404()

    _coms = [c.serialize() for c in coms]
    _coms_content = [add_notes_refs_to_text(c["content"], c["notes"]) for c in _coms]

    commentaries = zip(_coms, _coms_content)

    return make_200(data=[{
        "doc_id": com["doc_id"],
        "user_id": com["user_id"],
        "type": com["type"],
        "content": Markup(com["content"]) if com["content"] is not None else "",
        "notes": {"{:010d}".format(n["id"]): n["content"] for n in com["notes"]}
    } for com, notes in commentaries])


@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries', methods=['DELETE'])
@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id>', methods=['DELETE'])
@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/of-type/<type_id>', methods=['DELETE'])
@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id>/and-type/<type_id>', methods=['DELETE'])
@jwt_required
def api_delete_commentary(api_version, doc_id, user_id=None, type_id=None):
    user = current_app.get_current_user()

    # only teacher and admin can see everything
    access_is_forbidden = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
    if access_is_forbidden:
        return access_is_forbidden

    if not (user.is_teacher or user.is_admin) and type_id is not None and user_id is None:
        user_id = user.id

    if type_id is None:
        type_id = Commentary.type_id
    if user_id is None:
        if user.is_teacher:
            user_id = Commentary.user_id
        else:
            user_id = user.id

    commentaries = Commentary.query.filter(
        Commentary.doc_id == doc_id,
        Commentary.user_id == user_id,
        Commentary.type_id == type_id
    ).all()

    for c in commentaries:
        db.session.delete(c)

    try:
        db.session.commit()

        # change validation step

        return make_200(data={
            #"validation_step": doc.validation_step,
            #"validation_step_label": get_validation_step_label(doc.validation_step)
        })
    except (Exception, KeyError) as e:
        db.session.rollback()
        return make_400(str(e))


@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries', methods=['POST'])
@jwt_required
def api_post_commentary(api_version, doc_id):
    """
    {
        "data":
            {
                "doc_id" : 1,
                "user_id" : 1,
                "type_id": 2,
                "content" : "This is a commentary"
            }
    }
    :param api_version:
    :param doc_id:
    :return:
    """
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None:
        return make_404()

    if not doc.is_transcription_validated:
        return make_403()

    data = request.get_json()
    if "data" in data:
        co = data["data"]
        if len(data) == 0:
            return make_400("No data")

        if "user_id" not in co:
            user = current_app.get_current_user()
            co["user_id"] = user.id

        # only teacher and admin can see everything
        access_is_forbidden = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, co["user_id"])
        if access_is_forbidden:
            return access_is_forbidden

        c = Commentary(doc_id=doc_id, user_id=co["user_id"], type_id=co["type_id"], content=co["content"])
        db.session.add(c)

        try:
            db.session.commit()
        except (Exception, KeyError) as e:
            db.session.rollback()
            return make_400(str(e))

        return make_200(c.serialize())
    else:
        return make_400("no data")


@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries', methods=['PUT'])
@jwt_required
def api_put_commentary(api_version, doc_id):
    """
    {
        "data": [
            {
                "doc_id" : 1,
                "user_id" : 1,
                "type_id": 2,
                "content" : "This is a commentary"
            }
        ]
    }
    :param api_version:
    :param doc_id:
    :return:
    """
    user = current_app.get_current_user()
    if user.is_anonymous:
        return make_403()

    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None:
        return make_404()

    if not doc.is_transcription_validated:
        return make_403()

    data = request.get_json()
    if "data" in data:
        data = data["data"]

        updated_data = []
        try:
            for co in data:
                if "user_id" not in co:
                    co["user_id"] = user.id

                # only teacher and admin can see everything
                if (not user.is_teacher and not user.is_admin) and int(co["user_id"]) != int(user.id):
                    db.session.rollback()
                    return make_403()

                c = Commentary.query.filter(
                    Commentary.doc_id == doc_id,
                    Commentary.user_id == co["user_id"],
                    Commentary.type_id == co["type_id"]
                ).one()

                # update the content
                c.content = co["content"]

                db.session.add(c)
                updated_data.append(c)

            db.session.commit()
        except NoResultFound as e:
            db.session.rollback()
            return make_404(str(e))
        except (Exception, KeyError) as e:
            db.session.rollback()
            return make_409(str(e))

        return make_200([d.serialize() for d in updated_data])
    else:
        return make_400("no data")
