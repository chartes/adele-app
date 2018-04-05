import json
import pprint
import sys
from urllib.request import urlopen, build_opener

from flask import jsonify, request, url_for
from sqlalchemy.orm.exc import NoResultFound

from app import app
from app.api.open_annotation import make_annotation_list, make_annotation
from app.api.response import APIResponseFactory
from app.database.alignment.alignment_translation import align_translation
from app.models import Image, User, Document, Transcription, Translation, ImageZone

if sys.version_info < (3, 6):
    json_loads = lambda s: json_loads(s.decode("utf-8")) if isinstance(s, bytes) else json.loads(s)
else:
    json_loads = json.loads


def query_json_endpoint(request_obj, endpoint_url):
    op = build_opener()
    op.addheaders = [("Content-type", "text/json")]
    data = op.open("{root}{endpoint}".format(root=request_obj.url_root, endpoint=endpoint_url), timeout=10, ).read()
    return json_loads(data)

"""
---------------------------------
API Routes
---------------------------------
"""

@app.route('/api/<api_version>/alignments/translations/<transcription_id>/<translation_id>')
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
    return jsonify(response)


@app.route('/api/<api_version>/documents/<doc_id>')
def api_document(api_version, doc_id):
    try:
        doc = Document.query.filter(Document.id == doc_id).one()
        response = APIResponseFactory.make_response(data=doc.serialize())
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Document {0} introuvable".format(doc_id)
        })
    return jsonify(response)

@app.route('/api/<api_version>/documents/<doc_id>/manifest')
def api_document_manifest(api_version, doc_id):
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
            "details": "Impossible de récupérer le manifeste pour le document {0}".format(doc_id)
        })
    else:
        data = json_loads(manifest_data)
        response = APIResponseFactory.make_response(data=data)

    return jsonify(response)

@app.route('/api/<api_version>/documents/<doc_id>/transcriptions')
def api_document_transcriptions(api_version, doc_id):
    try:
        # Check if document exist first
        doc = Document.query.filter(Document.id == doc_id).one()
        transcriptions = Transcription.query.filter(Transcription.doc_id == doc_id).all()
        response = APIResponseFactory.make_response(
            data=[tr.serialize() for tr in transcriptions]
        )
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Document {0} introuvable".format(doc_id)
        })
    return jsonify(response)

@app.route('/api/<api_version>/documents/<doc_id>/transcriptions/from/<user_id>')
def document_transcription_from_user(api_version, doc_id, user_id):
    # TODO : changer la requête qui n'est pas bonne
    try:
        transcription = Transcription.query.filter(Transcription.doc_id == doc_id).one()
        response = APIResponseFactory.make_response(
            data=transcription.serialize()
        )
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Transcription {0} introuvable".format(doc_id)
        })
    return jsonify(response)

@app.route('/api/<api_version>/documents/<doc_id>/translations')
def api_document_translations(api_version, doc_id):
    try:
        # Check if document exist first
        doc = Document.query.filter(Document.id == doc_id).one()
        translations = Translation.query.filter(Translation.doc_id == doc_id).all()
        response = APIResponseFactory.make_response(
            data=[tr.serialize() for tr in translations]
        )
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Document {0} introuvable".format(doc_id)
        })
    return jsonify(response)

@app.route('/api/<api_version>/user')
def api_current_user(api_version):
    # TODO: change hard coded id
    try:
        user = User.query.filter(User.id == 3).one()
        response = APIResponseFactory.make_response(data=user.serialize())
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Utilisateur introuvable"
        })
    return jsonify(response)


@app.route('/api/<api_version>/users/<user_id>')
def api_user(api_version, user_id):
    try:
        user = User.query.filter(User.id == user_id).one()
        response = APIResponseFactory.make_response(data=user.serialize())
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Utilisateur {0} introuvable".format(user_id)
        })
    return jsonify(response)


#TODO : gerer les erreurs
#TODO : ajouter les coords
#TODO: ajouter aussi les annotations de la table alignement image dans une seconde AnnotationList ?

@app.route("/api/<api_version>/documents/<doc_id>/annotations/list")
def api_documents_annotations_list(api_version, doc_id):

    json_obj = query_json_endpoint(request, url_for('api_document_manifest', api_version=api_version, doc_id=doc_id))

    if "errors" in json_obj:
        response = APIResponseFactory.make_response(errors=json_obj["errors"])
    else:
        canvas = json_obj["data"]["sequences"][0]["canvases"][0]

        img = Image.query.filter(Image.doc_id == doc_id).one()

        canvas_uri = canvas["@id"]
        annotations = []
        for img_zone in [z for z in img.zones if z.note is not None]:
            res_uri = request.url_root[0:-1] + url_for(
                "api_documents_annotations",
                api_version=api_version,
                doc_id=doc_id,
                zone_id=img_zone.zone_id
            )
            new_annotation = make_annotation(canvas_uri, res_uri, img_zone.note, format="text/plain")
            annotations.append(new_annotation)

        annotation_list = make_annotation_list("f1", doc_id, annotations)

        response = APIResponseFactory.make_response(data=annotation_list)

    return jsonify(response)

#TODO: ajouter aussi les annotations de la table alignement image
@app.route("/api/<api_version>/documents/<doc_id>/annotations/<zone_id>")
def api_documents_annotations(api_version, doc_id, zone_id):

    json_obj = query_json_endpoint(request, url_for('api_document_manifest', api_version=api_version, doc_id=doc_id))

    if "errors" in json_obj:
        response = APIResponseFactory.make_response(errors=json_obj["errors"])
    else:
        canvas = json_obj["data"]["sequences"][0]["canvases"][0]

        img = Image.query.filter(Image.doc_id == doc_id).one()

        img_zone = ImageZone.query.filter(
            ImageZone.img_id == img.id,
            ImageZone.zone_id == zone_id,
            ImageZone.manifest_url == img.manifest_url,
            ImageZone.note != None
        ).one()

        canvas_uri = canvas["@id"]
        res_uri = request.url_root[0:-1] + url_for(
            "api_documents_annotations",
            api_version=api_version,
            doc_id=doc_id,
            zone_id=img_zone.zone_id
        )
        new_annotation = make_annotation(canvas_uri, res_uri, img_zone.note, format="text/plain")

        response = APIResponseFactory.make_response(data=new_annotation)

    return jsonify(response)
