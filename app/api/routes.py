import json
import pprint
import sys
from urllib.error import HTTPError
from urllib.request import urlopen, build_opener

from flask import request, url_for, Response
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from app import app
from app.api.open_annotation import make_annotation_list, make_annotation
from app.api.response import APIResponseFactory
from app.database.alignment.alignment_translation import align_translation
from app.models import Image, User, Document, Transcription, Translation, ImageZone, AlignmentImage

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
    return APIResponseFactory.jsonify(response)


@app.route('/api/<api_version>/documents/<doc_id>')
def api_documents(api_version, doc_id):
    try:
        doc = Document.query.filter(Document.id == doc_id).one()
        response = APIResponseFactory.make_response(data=doc.serialize())
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Document {0} introuvable".format(doc_id)
        })
    return APIResponseFactory.jsonify(response)

@app.route('/api/<api_version>/documents/<doc_id>/manifest')
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

@app.route('/api/<api_version>/documents/<doc_id>/transcriptions')
def api_documents_transcriptions(api_version, doc_id):
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

    return APIResponseFactory.jsonify(response)

@app.route('/api/<api_version>/documents/<doc_id>/transcriptions/<seg_id>')
def api_documents_transcriptions_segments(api_version, doc_id, seg_id):
    raise NotImplementedError

@app.route('/api/<api_version>/documents/<doc_id>/transcriptions/from/<user_id>')
def document_transcription_from_user(api_version, doc_id, user_id):
    try:
        transcription = Transcription.query.filter(
            Transcription.doc_id == doc_id, Transcription.user_id == user_id
        ).one()
        response = APIResponseFactory.make_response(
            data=transcription.serialize()
        )
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Transcription {0} introuvable".format(doc_id)
        })
    return APIResponseFactory.jsonify(response)

@app.route('/api/<api_version>/documents/<doc_id>/translations')
def api_documents_translations(api_version, doc_id):
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
    return APIResponseFactory.jsonify(response)

@app.route('/api/<api_version>/user')
def api_current_user(api_version):
    # TODO: change hard coded id
    try:
        user = User.query.filter(User.id == 1).one()
        response = APIResponseFactory.make_response(data=user.serialize())
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Utilisateur introuvable"
        })
    return APIResponseFactory.jsonify(response)


@app.route('/api/<api_version>/users/<user_id>')
def api_users(api_version, user_id):
    try:
        user = User.query.filter(User.id == user_id).one()
        response = APIResponseFactory.make_response(data=user.serialize())
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Utilisateur {0} introuvable".format(user_id)
        })
    return APIResponseFactory.jsonify(response)

@app.route("/api/<api_version>/documents/<doc_id>/first-canvas")
def api_documents_first_canvas(api_version, doc_id):

    json_obj = query_json_endpoint(request, url_for('api_documents_manifest', api_version=api_version, doc_id=doc_id))

    if "errors" in json_obj:
        response = APIResponseFactory.make_response(errors=[
            json_obj["errors"],
            {"title": "Cannot fetch manifest for the document {0}".format(doc_id)}
        ])
    else:
        try:
            canvas = json_obj["data"]["sequences"][0]["canvases"][0]
            response = APIResponseFactory.make_response(data=canvas)
        except (IndexError, KeyError):
            response = APIResponseFactory.make_response(errors={
                    "title": "Canvas not found in manifest for document {0}".format(doc_id)
            })

    return APIResponseFactory.jsonify(response)

#TODO : ajouter les coords
@app.route("/api/<api_version>/documents/<doc_id>/annotations")
def api_documents_annotations(api_version, doc_id):
    """

    :param api_version:
    :param doc_id:
    :return:
    """
    json_obj = query_json_endpoint(request, url_for('api_documents_first_canvas', api_version=api_version, doc_id=doc_id))

    if "errors" in json_obj:
        response = APIResponseFactory.make_response(errors=json_obj["errors"])
    else:
        canvas = json_obj["data"]
        new_annotation_list = []

        if "otherContent" in canvas:
            op = build_opener()
            op.addheaders = [("Content-type", "text/plain")]
            # for each annotation list reference in the manifest, make a new annotation list
            for oc in [oc for oc in canvas["otherContent"] if oc["@type"] == "sc:AnnotationList"]:
                # make a call to api_documents_manifest_annotations_list
                try:
                    resp = op.open(oc["@id"], timeout=10).read()
                except HTTPError as e:
                    response = APIResponseFactory.make_response(
                        errors={"details": e.msg, "title": "The annotation list {0} cannot be reached".format(oc["@id"]), "status": e.code}
                    )
                    return APIResponseFactory.jsonify(response)

                resp = json_loads(resp)
                if "errors" in resp:
                    return resp
                else:
                    new_annotation_list.append(resp)

        response = APIResponseFactory.make_response(data=new_annotation_list)

    return APIResponseFactory.jsonify(response)

@app.route("/api/<api_version>/documents/<doc_id>/annotations/list")
def api_documents_annotations_list(api_version, doc_id):
    """

    :param api_version:
    :param doc_id:
    :return:
    """

    json_obj = query_json_endpoint(request, url_for('api_documents_first_canvas', api_version=api_version, doc_id=doc_id))

    if "errors" in json_obj:
        response = APIResponseFactory.make_response(errors=json_obj["errors"])
    else:
        canvas = json_obj["data"]
        img = Image.query.filter(Image.doc_id == doc_id).one()
        #TODO s'il n'y a pas d'image dans le manifest
        img_json = canvas["images"][0]
        annotations = []

        for img_zone in [z for z in img.zones if z.note is not None]:
            res_uri = request.url_root[0:-1] + url_for(
                "api_documents_annotations_zone",
                api_version=api_version,
                doc_id=doc_id,
                zone_id=img_zone.zone_id
            )
            fragment_coords = img_zone.coords
            new_annotation = make_annotation(
                img_zone.manifest_url, img_json, fragment_coords, res_uri, img_zone.note, format="text/plain"
            )
            annotations.append(new_annotation)

        annotation_list = make_annotation_list("f1", doc_id, annotations)
        response = annotation_list

    return APIResponseFactory.jsonify(response)

def get_validated_transcription(doc_id):
    """

    :param doc_id:
    :return:
    """
    # TODO : put a filter on the user role to get only the teacher's transcriptions
    tr = None
    try:
        tr = Transcription.query.filter(doc_id == Transcription.doc_id).one()
        response = None
    except MultipleResultsFound as e:
        response = APIResponseFactory.make_response(errors={
            "status": 404,
            "title": "Multiple transcriptions found. A unique transcription must be validated first".format(doc_id)
        })
    except NoResultFound as e:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Transcription of document {0} cannot be found".format(doc_id)
        })
    return (tr, response)

@app.route('/api/<api_version>/documents/<doc_id>/transcriptions/list')
def api_documents_transcriptions_list(api_version, doc_id):
    """
    Fetch transcription segments formated as a sc:AnnotationList
    Only the teacher's transcription segments are returned
    :param api_version: API version
    :param doc_id: Document id
    :return: a json object Obj with a sc:AnnotationList inside Obj["data"]. Return errors in Obj["errors"]
    """
    #TODO : wip

    try:
        # Check if document exist first
        doc = Document.query.filter(Document.id == doc_id).one()
        # find the good transcription
        # TODO : put a filter on the user role to get only the teacher's transcriptions
        tr, response = get_validated_transcription(doc_id)

        # let's go finding the alignment segments
        if tr is not None:
            try:
                json_obj = query_json_endpoint(
                    request,
                    url_for('api_documents_first_canvas', api_version=api_version, doc_id=doc_id)
                )

                if "errors" in json_obj:
                    response = APIResponseFactory.make_response(errors=json_obj["errors"])
                else:
                    canvas = json_obj["data"]
                    img_json = canvas["images"][0]

                    annotations = []
                    img_als = AlignmentImage.query.filter(AlignmentImage.transcription_id == tr.id).all()
                    for img_al in img_als:

                        tr_seg = tr.content[img_al.ptr_transcription_start:img_al.ptr_transcription_end]

                        res_uri = request.url_root[0:-1] + url_for(
                            "api_documents_annotations_zone",
                            api_version=api_version,
                            doc_id=doc_id,
                            zone_id=img_al.zone_id
                        )
                        #TODO: gerer erreur
                        img_zone = ImageZone.query.filter(
                            ImageZone.manifest_url==img_al.manifest_url,
                            ImageZone.img_id==img_al.img_id,
                            ImageZone.zone_id==img_al.zone_id
                        ).one()

                        fragment_coords = img_zone.coords
                        annotations.append(
                            make_annotation(img_al.manifest_url, img_json, fragment_coords, res_uri, tr_seg, "text/plain")
                        )
                    annotation_list = make_annotation_list("f2", doc_id, annotations)
                    response = annotation_list

            except NoResultFound:
                response = APIResponseFactory.make_response()

    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Document {0} cannot be found".format(doc_id)
        })

    return APIResponseFactory.jsonify(response)


@app.route("/api/<api_version>/documents/<doc_id>/annotations/<zone_id>")
def api_documents_annotations_zone(api_version, doc_id, zone_id):
    """

    :param api_version:
    :param doc_id:
    :param zone_id:
    :return:
    """
    json_obj = query_json_endpoint(request, url_for('api_documents_first_canvas', api_version=api_version, doc_id=doc_id))

    if "errors" in json_obj:
        response = APIResponseFactory.make_response(errors=json_obj["errors"])
    else:
        canvas = json_obj["data"]
        response = None

        try:
            img = Image.query.filter(Image.doc_id == doc_id).one()
            # select annotations zones
            img_zone = ImageZone.query.filter(
                ImageZone.img_id == img.id,
                ImageZone.zone_id == zone_id,
                ImageZone.manifest_url == img.manifest_url
                #ImageZone.note != None
            ).one()
        except NoResultFound:
            img_zone = None
            response = APIResponseFactory.make_response(
                errors={"title": "There is no annotation {0} for the document {1}".format(zone_id, doc_id)}
            )

        if img_zone is not None:
            res_uri = request.url_root[0:-1] + url_for(
                "api_documents_annotations_zone",
                api_version=api_version,
                doc_id=doc_id,
                zone_id=img_zone.zone_id
            )

            # if the note content is empty, then you need to fetch a transcription segment
            # else it is a mere image note
            if img_zone.note is None:
                tr, response = get_validated_transcription(doc_id)
                img_al = AlignmentImage.query.filter(
                    AlignmentImage.transcription_id == tr.id,
                    AlignmentImage.zone_id == img_zone.zone_id,
                    AlignmentImage.user_id == tr.user_id,
                    AlignmentImage.manifest_url == img.manifest_url
                ).one()
                note_content = tr.content[img_al.ptr_transcription_start:img_al.ptr_transcription_end]
            else:
                note_content = img_zone.note

            if response is None:
                # TODO: gerer erreur si pas d'image dans le canvas
                img_json = canvas["images"][0]
                fragment_coords = img_zone.coords

                new_annotation = make_annotation(img.manifest_url, img_json, fragment_coords, res_uri, note_content, format="text/plain")
                response = new_annotation

    return APIResponseFactory.jsonify(response)

