from flask import request, url_for
from sqlalchemy.orm.exc import NoResultFound

from app import APIResponseFactory, get_current_user, db, auth
from app.api.routes import api_bp, query_json_endpoint
from app.models import Tradition


@api_bp.route('/api/<api_version>/traditions')
@api_bp.route('/api/<api_version>/traditions/<tradition_id>')
def api_tradition(api_version, tradition_id=None):
    try:
        if tradition_id is not None:
            traditions = [Tradition.query.filter(Tradition.id == tradition_id).one()]
        else:
            traditions = Tradition.query.all()
        response = APIResponseFactory.make_response(data=[a.serialize() for a in traditions])
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Tradition {0} not found".format(tradition_id)
        })
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/traditions', methods=['DELETE'])
@api_bp.route('/api/<api_version>/traditions/<tradition_id>', methods=['DELETE'])
@auth.login_required
def api_delete_tradition(api_version, tradition_id=None):
    response = None
    user = get_current_user()
    if user is None or not (user.is_teacher or user.is_admin):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })
    if response is None:
        try:
            if tradition_id is not None:
                traditions = [Tradition.query.filter(Tradition.id == tradition_id).one()]
            else:
                traditions = Tradition.query.all()

            for c in traditions:
                db.session.delete(c)
            try:
                db.session.commit()
                response = APIResponseFactory.make_response(data=[])
            except Exception as e:
                db.session.rollback()
                response = APIResponseFactory.make_response(errors={
                    "status": 403, "title": "Cannot delete data", "details": str(e)
                })

        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "Tradition {0} not found".format(tradition_id)
            })
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/traditions', methods=['PUT'])
@auth.login_required
def api_put_tradition(api_version):
    response = None
    user = get_current_user()
    if user is None or not (user.is_teacher or user.is_admin):
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

                modifed_data = []
                try:
                    for tradition in data:
                        if "id" not in tradition:
                            raise Exception("Tradition id is missing from the payload")
                        a = Tradition.query.filter(Tradition.id == tradition["id"]).one()
                        if "label" in tradition:
                            a.label = tradition["label"]
                        db.session.add(a)
                        modifed_data.append(a)

                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    response = APIResponseFactory.make_response(errors={
                        "status": 403, "title": "Cannot update data", "details": str(e)
                    })

                if response is None:
                    data = []
                    for a in modifed_data:
                        json_obj = query_json_endpoint(
                            request,
                            url_for("api_bp.api_tradition", api_version=api_version, tradition_id=a.id)
                        )
                        print(json_obj)
                        data.append(json_obj["data"])
                    response = APIResponseFactory.make_response(data=data)

        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "Tradition not found"
            })

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/traditions', methods=['POST'])
@auth.login_required
def api_post_tradition(api_version):
    response = None
    user = get_current_user()
    if user is None or not (user.is_teacher or user.is_admin):
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
                for tradition in data:
                    a = Tradition(**tradition)
                    db.session.add(a)
                    created_data.append(a)

                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    response = APIResponseFactory.make_response(errors={
                        "status": 403, "title": "Cannot insert data", "details": str(e)
                    })

                if response is None:
                    data = []
                    for a in created_data:
                        json_obj = query_json_endpoint(
                            request,
                            url_for("api_bp.api_tradition", api_version=api_version, tradition_id=a.id)
                        )
                        data.append(json_obj["data"])
                    response = APIResponseFactory.make_response(data=data)

        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "Tradition not found"
            })

    return APIResponseFactory.jsonify(response)

