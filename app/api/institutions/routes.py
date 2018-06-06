from flask import request, url_for, current_app
from sqlalchemy.orm.exc import NoResultFound

from app import APIResponseFactory, db, auth
from app.api.routes import api_bp, query_json_endpoint
from app.models import Institution


@api_bp.route('/api/<api_version>/institutions')
@api_bp.route('/api/<api_version>/institutions/<institution_id>')
def api_institution(api_version, institution_id=None):
    try:
        if institution_id is not None:
            institutions = [Institution.query.filter(Institution.id == institution_id).one()]
        else:
            institutions = Institution.query.all()
        response = APIResponseFactory.make_response(data=[a.serialize() for a in institutions])
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Institution {0} not found".format(institution_id)
        })
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/institutions', methods=['DELETE'])
@api_bp.route('/api/<api_version>/institutions/<institution_id>', methods=['DELETE'])
@auth.login_required
def api_delete_institution(api_version, institution_id=None):
    response = None
    user = current_app.get_current_user()
    if user.is_anonymous or not (user.is_teacher or user.is_admin):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })
    if response is None:
        try:
            if institution_id is not None:
                institutions = [Institution.query.filter(Institution.id == institution_id).one()]
            else:
                institutions = Institution.query.all()

            for i in institutions:
                db.session.delete(i)
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
                "status": 404, "title": "Institution {0} not found".format(institution_id)
            })
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/institutions', methods=['PUT'])
@auth.login_required
def api_put_institution(api_version):
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

                modifed_data = []
                try:
                    for institution in data:
                        if "id" not in institution:
                            raise Exception("Institution id is missing from the payload")
                        a = Institution.query.filter(Institution.id == institution["id"]).one()
                        if "ref" in institution:
                            a.ref = institution["ref"]
                        if "name" in institution:
                            a.name = institution["name"]
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
                            url_for("api_bp.api_institution", api_version=api_version, institution_id=a.id)
                        )
                        print(json_obj)
                        data.append(json_obj["data"])
                    response = APIResponseFactory.make_response(data=data)

        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "Institution not found"
            })

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/institutions', methods=['POST'])
@auth.login_required
def api_post_institution(api_version):
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
                for institution in data:
                    if "id" in institution:
                        institution.pop("id")
                    a = Institution(**institution)
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
                            url_for("api_bp.api_institution", api_version=api_version, institution_id=a.id)
                        )
                        data.append(json_obj["data"])
                    response = APIResponseFactory.make_response(data=data)

        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "Institution not found"
            })

    return APIResponseFactory.jsonify(response)

