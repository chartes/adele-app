from flask import request, current_app
from sqlalchemy.orm.exc import NoResultFound

from app import db, auth
from app.api.routes import api_bp,  json_loads
from app.models import Commentary, Document, VALIDATION_TRANSCRIPTION
from app.utils import make_403, make_200, make_404, forbid_if_nor_teacher_nor_admin_and_wants_user_data, make_409, \
    make_400


def get_reference_commentary(doc_id, type_id):
    """

    :param type_id:
    :param doc_id:
    :return:
    """
    from app.api.transcriptions.routes import get_reference_transcription
    tr_ref = get_reference_transcription(doc_id)
    if tr_ref is None:
        return None

    return Commentary.query.filter(
        doc_id == Commentary.doc_id,
        type_id == Commentary.type_id,
        tr_ref.user_id == Commentary.user_id
    ).first()


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


@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id>')
@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id>/and-type/<type_id>')
def api_commentary(api_version, doc_id, user_id=None, type_id=None):

    user = current_app.get_current_user()
    if user.is_anonymous:
        return make_403()

    # if anonymous or mere student wants to read data of another student
    if not (user.is_teacher or user.is_admin) and user_id is not None and int(user_id) != int(user.id):
        return make_403()

    # if mere student then get its own data
    if not (user.is_teacher or user.is_admin) and type_id is not None and user_id is None:
        user_id = user.id

    if type_id is None:
        type_id = Commentary.type_id
    if user_id is None:
        user_id = Commentary.user_id

    commentaries = Commentary.query.filter(
        Commentary.doc_id == doc_id,
        Commentary.user_id == user_id,
        Commentary.type_id == type_id
    ).all()

    return make_200([c.serialize() for c in commentaries])


@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/reference')
@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/reference/of-type/<type_id>')
def api_commentary_reference(api_version, doc_id, type_id=None):
    return make_200([c.serialize() for c in get_reference_commentaries(doc_id, type_id)])


@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries', methods=['DELETE'])
@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id>', methods=['DELETE'])
@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/of-type/<type_id>', methods=['DELETE'])
@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id>/and-type/<type_id>', methods=['DELETE'])
@auth.login_required
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
        user_id = Commentary.user_id

    commentaries = Commentary.query.filter(
        Commentary.doc_id == doc_id,
        Commentary.user_id == user_id,
        Commentary.type_id == type_id
    ).all()

    for c in commentaries:
        db.session.delete(c)

    try:
        db.session.commit()
        return make_200()
    except (Exception, KeyError) as e:
        db.session.rollback()
        return make_400(str(e))


@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries', methods=['POST'])
@auth.login_required
def api_post_commentary(api_version, doc_id):
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

    data = request.get_json()
    if "data" in data:
        data = data["data"]

        created_data = []

        if len(data) == 0:
            return make_400("No data")

        for co in data:

            if "user_id" not in co:
                co["user_id"] = user.id

            # only teacher and admin can see everything
            if (not user.is_teacher and not user.is_admin) and int(co["user_id"]) != int(user.id):
                db.session.rollback()
                return make_403()

            if doc.validation_stage < VALIDATION_TRANSCRIPTION:
                return make_400("A transcription must be validated first")

            c = Commentary(doc_id=doc_id, user_id=co["user_id"], type_id=co["type_id"], content=co["content"])
            db.session.add(c)
            created_data.append(c)

        try:
            db.session.commit()
        except (Exception, KeyError) as e:
            db.session.rollback()
            return make_400(str(e))

        coms = []
        for c in created_data:
            r = api_commentary(api_version=api_version, doc_id=doc_id, user_id=c.user_id, type_id=c.type_id)
            coms.extend(json_loads(r.data)["data"])

        return make_200(coms)
    else:
        return make_400("no data")


@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries', methods=['PUT'])
@auth.login_required
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

                if doc.validation_stage < VALIDATION_TRANSCRIPTION:
                    return make_400("A transcription must be validated first")

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
            return make_400(str(e))

        coms = []
        for c in updated_data:
            r = api_commentary(api_version=api_version, doc_id=doc_id, user_id=c.user_id, type_id=c.type_id)
            coms.extend(json_loads(r.data)["data"])

        return make_200(data)
    else:
        return make_400("no data")
