from flask import request, current_app
from sqlalchemy.orm.exc import NoResultFound

from app import db, auth
from app.api.routes import api_bp, json_loads
from app.models import District, Country
from app.utils import forbid_if_nor_teacher_nor_admin, make_404, make_200, make_409


@api_bp.route('/api/<api_version>/districts/from-country/<country_id>')
@api_bp.route('/api/<api_version>/districts/<district_id>/from-country/<country_id>')
def api_district(api_version, country_id, district_id=None):

    c = Country.query.filter(Country.id == country_id).first()
    if c is None:
        return make_404("Country does not exist")

    if district_id is None:
        districts = District.query.filter(District.country_id == country_id).all()
    else:
        # single
        at = District.query.filter(District.country_id == country_id, District.id == district_id).first()
        if at is None:
            return make_404("District {0} not found".format(district_id))
        else:
            districts = [at]
    return make_200([a.serialize() for a in districts])


@api_bp.route('/api/<api_version>/districts/from-country/<country_id>', methods=['DELETE'])
@api_bp.route('/api/<api_version>/districts/<district_id>/from-country/<country_id>', methods=['DELETE'])
@auth.login_required
def api_delete_district(api_version, country_id, district_id=None):
    access_is_forbidden = forbid_if_nor_teacher_nor_admin(current_app)
    if access_is_forbidden:
        return access_is_forbidden
    c = Country.query.filter(Country.id == country_id).first()
    if c is None:
        return make_404("Country does not exist")

    if district_id is None:
        districts = District.query.filter(District.country_id == country_id).all()
    else:
        districts = District.query.filter(District.country_id == country_id, District.id == district_id).all()

    for a in districts:
        db.session.delete(a)
    try:
        db.session.commit()
        return make_200([])
    except Exception as e:
        db.session.rollback()
        return make_409(str(e))


@api_bp.route('/api/<api_version>/districts/from-country/<country_id>', methods=['PUT'])
@auth.login_required
def api_put_district(api_version, country_id):
    access_is_forbidden = forbid_if_nor_teacher_nor_admin(current_app)
    if access_is_forbidden:
        return access_is_forbidden

    c = Country.query.filter(Country.id == country_id).first()
    if c is None:
        return make_404("Country does not exist")

    try:
        data = request.get_json()

        if "data" in data:
            data = data["data"]

            try:
                modifed_data = []
                for district in data:
                    a = District.query.filter(District.country_id == country_id,
                                              District.id == district.get('id', None)).one()
                    a.label = district.get("label")

                    db.session.add(a)
                    modifed_data.append(a)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(str(e))
                return make_409(str(e))

            data = []
            for a in modifed_data:
                r = api_district(api_version=api_version, district_id=a.id, country_id=country_id)
                data.append(json_loads(r.data)["data"])

            return make_200(data)
        else:
            return make_409("no data")
    except NoResultFound:
        return make_404("District not found")


@api_bp.route('/api/<api_version>/districts', methods=['POST'])
@auth.login_required
def api_post_district(api_version):
    access_is_forbidden = forbid_if_nor_teacher_nor_admin(current_app)
    if access_is_forbidden:
        return access_is_forbidden

    data = request.get_json()

    if "data" in data:
        data = data["data"]

        created_data = []
        try:
            for district in data:
                a = District(**district)
                db.session.add(a)
                created_data.append(a)

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return make_409(str(e))

        data = []
        for a in created_data:
            r = api_district(api_version=api_version, district_id=a.id, country_id=a.country_id)
            data.append(json_loads(r.data)["data"])

        return make_200(data)
    else:
        return make_409("no data")
