import base64
import json
import sys

from flask_user import roles_required
from urllib.request import build_opener

from flask import request, current_app

from app import auth, db, api_bp
from app.api.response import APIResponseFactory
from app.models import Commentary, User



if sys.version_info < (3, 6):
    json_loads = lambda s: json_loads(s.decode("utf-8")) if isinstance(s, bytes) else json.loads(s)
else:
    json_loads = json.loads


def query_json_endpoint(request_obj, endpoint_url, user=None, method='GET', headers_arg=None, direct=False):
    if direct:
        url = endpoint_url
    else:
        root_url = request_obj.url_root[0:request.url_root.rfind(current_app.config["APP_URL_PREFIX"])]
        url = "{root}{endpoint}".format(root=root_url, endpoint=endpoint_url)

    headers = {'Content-Type': 'application/json;charset=UTF-8'}

    if headers_arg is not None:
        headers.update(headers_arg)

    if user is not None and not user.is_anonymous:
        base64string = base64.b64encode(bytes('%s:%s' % (user.username, user.password), "utf-8"))
        headers['Authorization'] = "Basic %s" % base64string.decode("ascii")

    try:
        if method == 'GET':
            op = build_opener()
            op.addheaders = [(k, v) for k, v in headers.items()]

            if current_app.config["ENV"] == "test" and not direct:
                resp = current_app.test_server.get(url)
                data = resp.data
            else:
                data = op.open(url, timeout=15).read()
        else:
            raise NotImplementedError
        response = json_loads(data)

    except Exception as e:
        response = APIResponseFactory.make_response(status=403,
                                                    errors={
            "title": "Error : cannot {0} {1} | {2}".format(method, endpoint_url, headers),
            "details": str(e)
        })

    return response


"""
===========================
    Test routes 
===========================
"""

#
#@api_bp.route("/api/user-role")
#@auth.login_required
#@roles_required("teacher", "admin")
#def api_test_user_role():
#    """
#    I cannot be accessed by a student
#    """
#    user = User.query.filter(User.username == auth.username()).one()
#    role_names = [r.name for r in user.roles]
#    return APIResponseFactory.jsonify(role_names)
#
#
#@api_bp.route("/api/<api_version>/test/auth/<doc_id>", methods=["DELETE"])
#@auth.login_required
#def api_test_auth_delete(api_version, doc_id):
#    user = User.query.filter(User.username == auth.username()).one()
#
#    for c in Commentary.query.filter(Commentary.doc_id == doc_id).all():
#        db.session.delete(c)
#    db.session.commit()
#
#    response = APIResponseFactory.make_response(data=[
#        user.serialize(), request.get_json(), [c.serialize() for c in Commentary.query.all()]
#    ])
#
#    return APIResponseFactory.jsonify(response)
#
#
#@api_bp.route("/api/<api_version>/test/auth/<doc_id>", methods=["POST"])
#@auth.login_required
#def api_test_auth_post(api_version, doc_id):
#    user = User.query.filter(User.username == auth.username()).one()
#
#    data = request.get_json()
#    if "content" in data and "type_id" in data and "doc_id" in data:
#        c = Commentary(doc_id=data["doc_id"], type_id=data["type_id"],
#                       user_id=user.id, content=data["content"])
#        db.session.add(c)
#        db.session.commit()
#
#    response = APIResponseFactory.make_response(data=[
#        user.serialize(), request.get_json(), [c.serialize() for c in Commentary.query.all()]
#    ])
#
#    return APIResponseFactory.jsonify(response)


"""
===========================
    Import routes 
===========================
"""

from app.api.acte_types import routes
from app.api.commentaries import routes
from app.api.commentary_types import routes
from app.api.countries import routes
from app.api.districts import routes
from app.api.documents import routes
from app.api.editors import routes
from app.api.iiif import routes
from app.api.institutions import routes
from app.api.languages import routes
from app.api.notes import routes
from app.api.speech_part_types import routes
from app.api.traditions import routes
from app.api.transcriptions import routes
from app.api.translations import routes
from app.api.users import routes



