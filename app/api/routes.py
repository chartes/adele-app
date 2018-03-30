import json
from urllib.request import urlopen

from flask import jsonify
from sqlalchemy.orm.exc import NoResultFound

from app import app
from app.api.response import APIResponseFactory
from app.database.alignment.alignment_translation import align_translation
from app.models import Image, User, Document


"""
---------------------------------
API Routes
---------------------------------
"""

@app.route('/api/<api_version>/alignment/translation/<transcription_id>/<translation_id>')
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


@app.route('/api/<api_version>/document/<doc_id>/manifest')
def api_document_manifest(api_version, doc_id):
    no_result = False
    try:
        img = Image.query.filter(Image.doc_id == doc_id).one()
        manifest_data = urlopen(img.manifest_url).read()
    except NoResultFound:
        no_result = True

    if no_result:
        response = APIResponseFactory.make_response(errors={
            "details": "Impossible de récupérer le manifeste pour le document {0}".format(doc_id)
        })
    else:
        data = json.loads(manifest_data)
        response = APIResponseFactory.make_response(data=data)

    return jsonify(response)

@app.route('/api/<api_version>/document/<doc_id>')
def api_document(api_version, doc_id):
    try:
        doc = Document.query.filter(Document.id == doc_id).one()
        response = APIResponseFactory.make_response(data=doc.serialize())
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Document {0} introuvable".format(doc_id)
        })
    return jsonify(response)

#@app.route('/api/document/<doc_id>/traduction')
#@app.route('/api/document/<doc_id>/transcription')

@app.route('/api/<api_version>/user/<user_id>')
def api_user(api_version, user_id):
    try:
        user = User.query.filter(User.id == user_id).one()
        response = APIResponseFactory.make_response(data=user.serialize())
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Utilisateur {0} introuvable".format(user_id)
        })
    return jsonify(response)