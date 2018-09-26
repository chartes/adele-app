from flask import request, url_for, current_app
from sqlalchemy.orm.exc import NoResultFound

from app import APIResponseFactory, db, auth
from app.api.routes import api_bp, query_json_endpoint
from app.api.transcriptions.routes import get_reference_transcription
from app.models import Commentary, User


def get_reference_commentary(doc_id, type_id):
    """

    :param doc_id:
    :return:
    """
    commentary = None
    try:
        tr_ref = get_reference_transcription(doc_id)
        if tr_ref is None:
            return None
            #raise NoResultFound("Reference transcription not found")
        commentary = Commentary.query.filter(
            doc_id == Commentary.doc_id,
            type_id == Commentary.type_id,
            tr_ref.user_id == Commentary.user_id
        ).one()
    except NoResultFound:
        commentary = None

    return commentary


def get_reference_commentaries(doc_id):
    """

    :param doc_id:
    :return:
    """
    tr_ref = get_reference_transcription(doc_id)
    if tr_ref is None:
        commentaries = []
    else:
        commentaries = Commentary.query.filter(
            doc_id == Commentary.doc_id,
            tr_ref.user_id == Commentary.user_id
        ).all()
    return commentaries


@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries')
@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id>')
@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/of-type/<type_id>')
@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id>/and-type/<type_id>')
def api_commentary(api_version, doc_id, user_id=None, type_id=None):
    user = current_app.get_current_user()
    response = None

    if not user.is_anonymous:
        # only teacher and admin can see everything
        if not (user.is_teacher or user.is_admin) and user_id is not None and int(user_id) != int(user.id):
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Access forbidden"
            })
    else:
        if user_id is not None:
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Access forbidden"
            })
        else:
            tr = get_reference_transcription(doc_id)
            user_id = tr.user_id

    if response is None:

        if not user.is_anonymous:
            if not (user.is_teacher or user.is_admin) and type_id is not None and user_id is None:
                user_id = user.id

        if response is None:

            if type_id is None:
                type_id = Commentary.type_id
            if user_id is None:
                user_id = Commentary.user_id

            commentaries = Commentary.query.filter(
                Commentary.doc_id == doc_id,
                Commentary.user_id == user_id,
                Commentary.type_id == type_id
            ).all()

            response = APIResponseFactory.make_response(data=[c.serialize() for c in commentaries])

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/reference')
@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/reference/of-type/<type_id>')
def api_commentary_reference(api_version, doc_id, type_id=None):
    tr = get_reference_transcription(doc_id)
    response = None
    if tr is None:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Reference transcription note found"
        })

    if response is None:
        user = User.query.filter(User.id == tr.user_id).one()
        json_obj = query_json_endpoint(
            request,
            url_for("api_bp.api_commentary", api_version=api_version,
                    doc_id=doc_id, user_id=tr.user_id, type_id=type_id),
            user=user
        )
        response = APIResponseFactory.make_response(data=json_obj["data"])

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries', methods=['DELETE'])
@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id>', methods=['DELETE'])
@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/of-type/<type_id>', methods=['DELETE'])
@api_bp.route('/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id>/and-type/<type_id>',
              methods=['DELETE'])
@auth.login_required
def api_delete_commentary(api_version, doc_id, user_id=None, type_id=None):
    user = current_app.get_current_user()
    response = None

    # only teacher and admin can see everything
    if user.is_anonymous or (not (user.is_teacher or user.is_admin) and user_id is not None and int(user_id) != int(user.id)):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })

    if response is None:

        if not (user.is_teacher or user.is_admin) and type_id is not None and user_id is None:
            user_id = user.id

        if response is None:

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
                response = APIResponseFactory.make_response(data=[])
            except (Exception, KeyError) as e:
                db.session.rollback()
                response = APIResponseFactory.make_response(errors={
                    "status": 403, "title": "Cannot update data", "details": str(e)
                })

    return APIResponseFactory.jsonify(response)


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
    response = None
    user = current_app.get_current_user()
    if user.is_anonymous or not (user.is_teacher or user.is_admin):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })

    if response is None:
        try:
            data = request.get_json()

            if "data" in data:
                data = data["data"]

                if not isinstance(data, list):
                    data = [data]

                created_data = []
                for co in data:

                    if "user_id" not in co:
                        co["user_id"] = user.id

                    # only teacher and admin can see everything
                    if (not user.is_teacher and not user.is_admin) and int(co["user_id"]) != int(user.id):
                        response = APIResponseFactory.make_response(errors={
                            "status": 403, "title": "Access forbidden"
                        })
                        db.session.rollback()
                        break

                    c = Commentary(doc_id=co["doc_id"], user_id=co["user_id"], type_id=co["type_id"],
                                   content=co["content"])
                    db.session.add(c)
                    created_data.append(c)

                try:
                    db.session.commit()
                except (Exception, KeyError) as e:
                    db.session.rollback()
                    response = APIResponseFactory.make_response(errors={
                        "status": 403, "title": "Cannot insert data", "details": str(e)
                    })

                if response is None:
                    data = []
                    for c in created_data:
                        json_obj = query_json_endpoint(
                            request,
                            url_for("api_bp.api_commentary", api_version=api_version,
                                    doc_id=c.doc_id, user_id=c.user_id, type_id=c.type_id),
                            user=user
                        )
                        data.append(json_obj["data"])
                    response = APIResponseFactory.make_response(data=data)

        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "Commentary not found"
            })

    return APIResponseFactory.jsonify(response)


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
    response = None
    user = current_app.get_current_user()
    if user.is_anonymous or not (user.is_teacher or user.is_admin):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })

    if response is None:
        try:
            data = request.get_json()

            if "data" in data:
                data = data["data"]

                if not isinstance(data, list):
                    data = [data]

                updated_data = []
                try:
                    for co in data:

                        if "user_id" not in co:
                            co["user_id"] = user.id

                        # only teacher and admin can see everything
                        if (not user.is_teacher and not user.is_admin) and int(co["user_id"]) != int(user.id):
                            response = APIResponseFactory.make_response(errors={
                                "status": 403, "title": "Access forbidden"
                            })
                            db.session.rollback()
                            break

                        c = Commentary.query.filter(
                            Commentary.doc_id == co["doc_id"],
                            Commentary.user_id == co["user_id"],
                            Commentary.type_id == co["type_id"]
                        ).one()
                        c.content = co["content"]

                        db.session.add(c)
                        updated_data.append(c)

                    db.session.commit()
                except (Exception, KeyError) as e:
                    db.session.rollback()
                    response = APIResponseFactory.make_response(errors={
                        "status": 403, "title": "Cannot update data", "details": str(e)
                    })

                if response is None:
                    data = []
                    for c in updated_data:
                        json_obj = query_json_endpoint(
                            request,
                            url_for("api_bp.api_commentary", api_version=api_version,
                                    doc_id=c.doc_id, user_id=c.user_id, type_id=c.type_id),
                            user=user
                        )
                        data.append(json_obj["data"])
                    response = APIResponseFactory.make_response(data=data)

        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "Commentary not found"
            })

    return APIResponseFactory.jsonify(response)
