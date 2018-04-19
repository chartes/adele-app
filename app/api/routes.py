import json
import pprint
import sys
from urllib.request import urlopen, build_opener

from flask import request, url_for,  Blueprint
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from app import app, auth, db, role_required, get_current_user
from app.api.response import APIResponseFactory
from app.database.alignment.alignment_translation import align_translation
from app.models import  Commentary, Document, Image, Note, NoteType, Transcription, Translation, User


api_bp = Blueprint('api_bp', __name__, template_folder='templates')

if sys.version_info < (3, 6):
    json_loads = lambda s: json_loads(s.decode("utf-8")) if isinstance(s, bytes) else json.loads(s)
else:
    json_loads = json.loads


def query_json_endpoint(request_obj, endpoint_url):
    op = build_opener()
    op.addheaders = [("Content-type", "text/plain")]
    try:
        data = op.open("{root}{endpoint}".format(root=request_obj.url_root, endpoint=endpoint_url), timeout=10, ).read()
        response = json_loads(data)
    except:
        response = APIResponseFactory.make_response(errors={"title":"Error : cannot fetch {0}".format(endpoint_url)})
    return response


"""
---------------------------------
API Routes
---------------------------------
"""


@api_bp.route("/api/user-role")
@auth.login_required
@role_required("teacher", "admin")
def api_test_user_role():
    """
    I cannot be accessed by a student
    """
    user = User.query.filter(User.username == auth.username()).one()
    role_names =[r.name for r in user.roles]
    return APIResponseFactory.jsonify(role_names)


@api_bp.route("/api/<api_version>/test/auth/<doc_id>", methods=["DELETE"])
@auth.login_required
def api_test_auth_delete(api_version, doc_id):
    user = User.query.filter(User.username == auth.username()).one()

    for c in Commentary.query.filter(Commentary.doc_id==doc_id).all():
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


@api_bp.route('/api/<api_version>/alignments/translations/<transcription_id>/<translation_id>')
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



def get_reference_transcription(doc_id):
    """

    :param doc_id:
    :return:
    """
    transcription = None
    try:
        transcriptions = Transcription.query.filter(doc_id == Transcription.doc_id).all()
        for tr in transcriptions:
            user = User.query.filter(User.id == tr.user_id).first()
            if user.is_teacher:
                transcription = tr
                break
    except NoResultFound:
        pass

    return transcription

def get_reference_translation(doc_id):
    """

    :param doc_id:
    :return:
    """
    translation = None
    try:
        translations = Translation.query.filter(doc_id == Translation.doc_id).all()
        for tr in translations:
            user = User.query.filter(User.id == tr.user_id).first()
            if user.is_teacher:
                translation = tr
                break
    except NoResultFound:
        pass

    return translation

@api_bp.route('/api/<api_version>/notes', methods=['GET','POST'])
def api_add_note(api_version):
    note_data = request.get_json()
    # note = Note()
    # dump(data)
    return APIResponseFactory.jsonify({
        'note_data': note_data
    })


@api_bp.route('/api/<api_version>/documents/<doc_id>')
def api_documents(api_version, doc_id):
    try:
        doc = Document.query.filter(Document.id == doc_id).one()
        response = APIResponseFactory.make_response(data=doc.serialize())
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Document {0} introuvable".format(doc_id)
        })
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/manifest')
def api_documents_manifest(api_version, doc_id):
    no_result = False
    try:
        img = Image.query.filter(Image.doc_id == doc_id).one()
        manifest_data = urlopen(img.manifest_url).read()
    except NoResultFound:
        no_result = True
        manifest_data = "{}"

    if no_result:
        response = APIResponseFactory.make_response(errors={
            "status": 404,
            "details": "Cannot fetch manifest for the document {0}".format(doc_id)
        })
    else:
        data = json_loads(manifest_data)
        response = APIResponseFactory.make_response(data=data)

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions')
@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/from-user/<user_id>')
def api_documents_transcriptions(api_version, doc_id, user_id=None):
    response = None
    user = get_current_user()
    if user is None:
        # get the reference transcription
        tr = get_reference_transcription(doc_id)
        response = APIResponseFactory.make_response(data=tr.serialize())
    else:
        # only teacher and admin can modify everything
        if not user.is_teacher and not user.is_admin:
            user_id = user.id

    if response is None:
        if user_id is None:
            # In that case do not filter
            user_id = Transcription.user_id

        try:
            # Check if document exist first
            transcriptions = Transcription.query.filter(
                Transcription.doc_id == doc_id,
                Transcription.user_id == user_id
            ).all()
            response = APIResponseFactory.make_response(data=[tr.serialize() for tr in transcriptions])
        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "Transcription {0} not found".format(doc_id)
            })

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/translations')
@api_bp.route('/api/<api_version>/documents/<doc_id>/translations/from-user/<user_id>')
def api_documents_translations(api_version, doc_id, user_id=None):
    response = None
    user = get_current_user()
    if user is None:
        # get the reference translation
        tr = get_reference_translation(doc_id)
        response = APIResponseFactory.make_response(data=tr.serialize())
    else:
        # only teacher and admin can modify everything
        if not user.is_teacher and not user.is_admin:
            user_id = user.id

    if response is None:
        if user_id is None:
            # In that case do not filter
            user_id = Translation.user_id

        try:
            # Check if document exist first
            translations = Translation.query.filter(
                Translation.doc_id == doc_id,
                Translation.user_id == user_id
            ).all()
            response = APIResponseFactory.make_response(data=[tr.serialize() for tr in translations])
        except NoResultFound:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "Translation {0} not found".format(doc_id)
            })

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/user')
def api_current_user(api_version):
    # TODO: change hard coded id
    try:
        user = User.query.filter(User.id == 1).one()
        response = APIResponseFactory.make_response(data=user.serialize())
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "User not found"
        })
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/users/<user_id>')
def api_users(api_version, user_id):
    try:
        user = User.query.filter(User.id == user_id).one()
        response = APIResponseFactory.make_response(data=user.serialize())
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "User {0} not found".format(user_id)
        })
    return APIResponseFactory.jsonify(response)


@api_bp.route("/api/<api_version>/documents/<doc_id>/notes/from-user/<user_id>")
def api_documents_notes_from_user(api_version, doc_id, user_id):

    # sélectionner la liste des notes d'un utilisateur pour un doc
    # cad ses notes de transcrition, traduction, commentaire
    # TODO refactor
    """

    :param api_version:
    :param doc_id:
    :param user_id:
    :return:
    """
    try:
        transcription = Transcription.query.filter(Transcription.doc_id == doc_id, Transcription.user_id == user_id).first()
        translation = Translation.query.filter(Translation.doc_id == doc_id, Translation.user_id == user_id).first()
        commentaries = Commentary.query.filter(Commentary.doc_id == doc_id, Commentary.user_id == user_id).all()

        notes = []

        for it in transcription.notes:
            notes.append(it.note_id)

        for it in translation.notes:
            notes.append(it.note_id)

        for c in commentaries:
            for it in c.notes:
                notes.append(it.note_id)

        notes = Note.query.filter(Note.id.in_(notes))

        response = APIResponseFactory.make_response(data={
            'notes': [it.serialize() for it in notes]
        })
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Types de note introuvables"
        })
    return APIResponseFactory.jsonify(response)




@api_bp.route("/api/<api_version>/note-types")
def api_note_types(api_version):
    """

    :param api_version:
    :return:
    """
    try:
        note_types = NoteType.query.all()
        response = APIResponseFactory.make_response(data=[nt.serialize() for nt in note_types])
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Types de note introuvables"
        })
    return APIResponseFactory.jsonify(response)


"""
Declare IIIF related routes
"""
from app.api.iiif import routes


app.register_blueprint(api_bp)


