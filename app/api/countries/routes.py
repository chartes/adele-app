from flask import request, url_for, current_app
from sqlalchemy.orm.exc import NoResultFound

from app import APIResponseFactory, db, auth
from app.api.routes import api_bp, query_json_endpoint
from app.models import Country


@api_bp.route('/api/<api_version>/countries')
@api_bp.route('/api/<api_version>/countries/<country_id>')
def api_country(api_version, country_id=None):
    try:
        if country_id is not None:
            countries = [Country.query.filter(Country.id == country_id).one()]
        else:
            countries = Country.query.all()
        response = APIResponseFactory.make_response(data=[a.serialize() for a in countries])
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Country {0} not found".format(country_id)
        })
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/countries', methods=['DELETE'])
@api_bp.route('/api/<api_version>/countries/<country_id>', methods=['DELETE'])
@auth.login_required
def api_delete_country(api_version, country_id=None):
    response = None
    user = current_app.get_current_user()
    if user.is_anonymous or not (user.is_teacher or user.is_admin):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })
    if response is None:
        try:
            if country_id is not None:
                countries = [Country.query.filter(Country.id == country_id).one()]
            else:
                countries = Country.query.all()

            for c in countries:
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
                "status": 404, "title": "Country {0} not found".format(country_id)
            })
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/countries', methods=['PUT'])
@auth.login_required
def api_put_country(api_version):
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
                    for country in data:
                        if "id" not in country:
                            raise Exception("Country id is missing from the payload")
                        a = Country.query.filter(Country.id == country["id"]).one()
                        if "ref" in country:
                            a.ref = country["ref"]
                        if "label" in country:
                            a.label = country["label"]
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
                            url_for("api_bp.api_country", api_version=api_version, country_id=a.id)
                        )
                        print(json_obj)
                        data.append(json_obj["data"])
                    response = APIResponseFactory.make_response(data=data)

        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "Country not found"
            })

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/countries', methods=['POST'])
@auth.login_required
def api_post_country(api_version):
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
                for country in data:
                    if "id" in country:
                        country.pop("id")
                    a = Country(**country)
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
                            url_for("api_bp.api_country", api_version=api_version, country_id=a.id)
                        )
                        data.append(json_obj["data"])
                    response = APIResponseFactory.make_response(data=data)

        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "Country not found"
            })

    return APIResponseFactory.jsonify(response)

