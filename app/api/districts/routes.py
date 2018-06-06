from flask import request, url_for, current_app
from sqlalchemy.orm.exc import NoResultFound

from app import APIResponseFactory, db, auth
from app.api.routes import api_bp, query_json_endpoint
from app.models import District, Country


@api_bp.route('/api/<api_version>/districts')
@api_bp.route('/api/<api_version>/districts/<district_id>')
@api_bp.route('/api/<api_version>/districts/from-country/<country_id>')
def api_district(api_version, district_id=None, country_id=None):
    try:
        if district_id is not None:
            districts = [District.query.filter(District.id == district_id).one()]
        elif country_id is not None:
            districts = [District.query.filter(District.country_id == country_id).one()]
        else:
            districts = District.query.all()
        response = APIResponseFactory.make_response(data=[a.serialize() for a in districts])
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "District {0} not found".format(district_id)
        })
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/districts', methods=['DELETE'])
@api_bp.route('/api/<api_version>/districts/<district_id>', methods=['DELETE'])
@api_bp.route('/api/<api_version>/districts/from-country/<country_id>', methods=['DELETE'])
@auth.login_required
def api_delete_district(api_version, district_id=None, country_id=None):
    response = None
    user = current_app.get_current_user()
    if user.is_anonymous or not (user.is_teacher or user.is_admin):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })
    if response is None:
        try:
            if district_id is not None:
                districts = [District.query.filter(District.id == district_id).one()]
            elif country_id is not None:
                districts = [District.query.filter(District.country_id == country_id).all()]
            else:
                districts = District.query.all()

            for c in districts:
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
                "status": 404, "title": "District {0} not found".format(district_id)
            })
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/districts', methods=['PUT'])
@auth.login_required
def api_put_district(api_version):
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
                    for district in data:
                        if "id" not in district:
                            raise Exception("District id is missing from the payload")
                        d = District.query.filter(District.id == district["id"]).one()
                        if "country_id" in district:
                            d.country_id = district["country_id"]
                        if "label" in district:
                            d.label = district["label"]
                        db.session.add(d)
                        modifed_data.append(d)

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
                            url_for("api_bp.api_district",
                                    api_version=api_version, district_id=a.id)
                        )
                        print(json_obj)
                        data.append(json_obj["data"])
                    response = APIResponseFactory.make_response(data=data)

        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "District not found"
            })

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/districts', methods=['POST'])
@auth.login_required
def api_post_district(api_version):
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
                for district in data:
                    if "id" in district:
                        district.pop("id")
                    a = District(**district)
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
                            url_for("api_bp.api_district", api_version=api_version, district_id=a.id)
                        )
                        data.append(json_obj["data"])
                    response = APIResponseFactory.make_response(data=data)

        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "District not found"
            })

    return APIResponseFactory.jsonify(response)

