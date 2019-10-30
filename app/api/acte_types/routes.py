from flask import request, url_for, current_app
from sqlalchemy.orm.exc import NoResultFound

from app import APIResponseFactory, db, auth
from app.api.routes import api_bp, query_json_endpoint
from app.models import ActeType


@api_bp.route('/api/<api_version>/acte-types')
@api_bp.route('/api/<api_version>/acte-types/<acte_type_id>')
def api_acte_type(api_version, acte_type_id=None):
    try:
        if acte_type_id is not None:
            acte_types = [ActeType.query.filter(ActeType.id == acte_type_id).one()]
        else:
            acte_types = ActeType.query.all()
        response = APIResponseFactory.make_response(data=[a.serialize() for a in acte_types])
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "ActeType {0} not found".format(acte_type_id)
        })
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/acte-types', methods=['DELETE'])
@api_bp.route('/api/<api_version>/acte-types/<acte_type_id>', methods=['DELETE'])
@auth.login_required
def api_delete_acte_type(api_version, acte_type_id=None):
    response = None
    user = current_app.get_current_user()
    if user.is_anonymous or not (user.is_teacher or user.is_admin):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })
    if response is None:
        try:
            if acte_type_id is not None:
                acte_types = [ActeType.query.filter(ActeType.id == acte_type_id).one()]
            else:
                acte_types = ActeType.query.all()

            for a in acte_types:
                db.session.delete(a)
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
                "status": 404, "title": "ActeType {0} not found".format(acte_type_id)
            })
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/acte-types', methods=['PUT'])
@auth.login_required
def api_put_acte_type(api_version):
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
                modified_data = []

                if not isinstance(data, list):
                    data = [data]
                try:
                    for acte_type in data:
                        a = ActeType.query.filter(ActeType.id == acte_type["id"]).one()
                        a.label = acte_type.get("label")
                        a.description = acte_type.get("description")
                        db.session.add(a)
                        modified_data.append(a)

                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    response = APIResponseFactory.make_response(errors={
                        "status": 403, "title": "Cannot update data", "details": str(e)
                    })

                if response is None:
                    data = []
                    for a in modified_data:
                        data.append(a.serialize())
                    response = APIResponseFactory.make_response(data=data)

        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "ActeType not found"
            })

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/acte-types', methods=['POST'])
@auth.login_required
def api_post_acte_type(api_version):
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
                for acte_type in data:
                    a = ActeType(**acte_type)
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
                            url_for("api_bp.api_acte_type", api_version=api_version, acte_type_id=a.id)
                        )
                        data.append(json_obj["data"])
                    response = APIResponseFactory.make_response(data=data)

        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "ActeType not found"
            })

    return APIResponseFactory.jsonify(response)

