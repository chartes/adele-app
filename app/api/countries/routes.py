from flask import request
from flask_jwt_extended import jwt_required
from sqlalchemy.orm.exc import NoResultFound

from app import db, auth
from app.api.routes import api_bp, json_loads
from app.models import Country
from app.utils import forbid_if_nor_teacher_nor_admin, make_404, make_200, make_409, make_400


@api_bp.route('/api/<api_version>/countries')
@api_bp.route('/api/<api_version>/countries/<country_id>')
def api_country(api_version, country_id=None):
    if country_id is None:
        countries = Country.query.order_by(Country.label).all()
    else:
        # single
        at = Country.query.filter(Country.id == country_id).first()
        if at is None:
            return make_404("Country {0} not found".format(country_id))
        else:
            countries = [at]
    return make_200([a.serialize() for a in countries])


@api_bp.route('/api/<api_version>/countries', methods=['DELETE'])
@api_bp.route('/api/<api_version>/countries/<country_id>', methods=['DELETE'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_delete_country(api_version, country_id=None):
    if country_id is None:
        countries = Country.query.all()
    else:
        countries = Country.query.filter(Country.id == country_id).all()

    for a in countries:
        db.session.delete(a)

    try:
        db.session.commit()
        return make_200([])
    except Exception as e:
        db.session.rollback()
        print(str(e))
        return make_400(str(e))


@api_bp.route('/api/<api_version>/countries', methods=['PUT'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_put_country(api_version):
    try:
        data = request.get_json()

        if "data" in data:
            data = data["data"]

            try:
                modified_data = []
                for country in data:
                    a = Country.query.filter(Country.id == country.get('id', None)).one()
                    a.label = country.get("label")
                    a.ref = country.get("ref")

                    db.session.add(a)
                    modified_data.append(a)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return make_409(str(e))

            return make_200([d.serialize() for d in modified_data])
        else:
            return make_400("no data")
    except NoResultFound:
        return make_404("Country not found")


@api_bp.route('/api/<api_version>/countries', methods=['POST'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_post_country(api_version):
    data = request.get_json()

    if "data" in data:
        data = data["data"]

        created_data = []
        try:
            for country in data:
                a = Country(**country)
                db.session.add(a)
                created_data.append(a)

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return make_400(str(e))

        return make_200([d.serialize() for d in created_data])
    else:
        return make_409("no data")
