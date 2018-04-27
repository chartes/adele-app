import base64
import json
import sys
from urllib.request import urlopen, build_opener

from flask import request, Blueprint

from app import app, auth, db, role_required
from app.api.response import APIResponseFactory
from app.database.alignment.alignment_translation import align_translation
from app.models import Commentary, User


api_bp = Blueprint('api_bp', __name__, template_folder='templates')

if sys.version_info < (3, 6):
    json_loads = lambda s: json_loads(s.decode("utf-8")) if isinstance(s, bytes) else json.loads(s)
else:
    json_loads = json.loads


def query_json_endpoint(request_obj, endpoint_url, user=None):
    url = "{root}{endpoint}".format(root=request_obj.url_root, endpoint=endpoint_url)

    op = build_opener()
    op.addheaders = [
        ("Content-type", "text/plain")
    ]

    if user is not None:
        base64string = base64.b64encode(bytes('%s:%s' % (user.username, user.password), "utf-8"))
        op.addheaders.append(
            ("Authorization", "Basic %s" % base64string.decode("ascii"))
        )

    try:
        data = op.open(url, timeout=10, ).read()
        response = json_loads(data)
    except:
        response = APIResponseFactory.make_response(errors={"title": "Error : cannot fetch {0}".format(endpoint_url)})

    return response


"""
===========================
    Test routes 
===========================
"""


@api_bp.route("/api/user-role")
@auth.login_required
@role_required("teacher", "admin")
def api_test_user_role():
    """
    I cannot be accessed by a student
    """
    user = User.query.filter(User.username == auth.username()).one()
    role_names = [r.name for r in user.roles]
    return APIResponseFactory.jsonify(role_names)


@api_bp.route("/api/<api_version>/test/auth/<doc_id>", methods=["DELETE"])
@auth.login_required
def api_test_auth_delete(api_version, doc_id):
    user = User.query.filter(User.username == auth.username()).one()

    for c in Commentary.query.filter(Commentary.doc_id == doc_id).all():
        db.session.delete(c)
    db.session.commit()

    response = APIResponseFactory.make_response(data=[
        user.serialize(), request.get_json(), [c.serialize() for c in Commentary.query.all()]
    ])

    return APIResponseFactory.jsonify(response)


@api_bp.route("/api/<api_version>/test/auth/<doc_id>", methods=["POST"])
@auth.login_required
def api_test_auth_post(api_version, doc_id):
    user = User.query.filter(User.username == auth.username()).one()

    data = request.get_json()
    if "content" in data and "type_id" in data and "doc_id" in data:
        c = Commentary(doc_id=data["doc_id"], type_id=data["type_id"],
                       user_id=user.id, content=data["content"])
        db.session.add(c)
        db.session.commit()

    response = APIResponseFactory.make_response(data=[
        user.serialize(), request.get_json(), [c.serialize() for c in Commentary.query.all()]
    ])

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/alignments/translation/<transcription_id>/<translation_id>')
def api_align_translation(api_version, transcription_id, translation_id):
    alignment = align_translation(transcription_id, translation_id)
    if len(alignment) > 0:
        data = []
        for al in alignment:
            data.append({
                "ptr_transcription_start": al[2],
                "ptr_transcription_end": al[3],
                "ptr_translation_start": al[4],
                "ptr_translation_end": al[5],
                "transcription": al[6],
                "translation": al[7],
            })
        response = APIResponseFactory.make_response(data=data)
    else:
        response = APIResponseFactory.make_response(errors={"status": 404, "title": "Alignement introuvable"})
    return APIResponseFactory.jsonify(response)


"""
===========================
    Import routes 
===========================
"""

from app.api.acte_types import routes
from app.api.commentaries import routes
from app.api.countries import routes
from app.api.documents import routes
from app.api.iiif import routes
from app.api.institutions import routes
from app.api.notes import routes
from app.api.transcriptions import routes
from app.api.translations import routes
from app.api.users import routes


app.register_blueprint(api_bp)
