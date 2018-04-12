from flask import url_for, request
from requests import HTTPError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from urllib.request import build_opener

from app.api.open_annotation import make_annotation, make_annotation_list
from app.api.response import APIResponseFactory
from app.api.routes import query_json_endpoint, json_loads, api_bp, get_validated_transcription
from app.models import AlignmentImage, ImageZone, Image, Document, Transcription


@api_bp.route("/api/<api_version>/documents/<doc_id>/first-canvas")
def api_documents_first_canvas(api_version, doc_id):

    json_obj = query_json_endpoint(
        request,
        url_for('api_bp.api_documents_manifest', api_version=api_version, doc_id=doc_id)
    )

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


@api_bp.route("/api/<api_version>/documents/<doc_id>/annotations")
def api_documents_annotations(api_version, doc_id):
    """

    :param api_version:
    :param doc_id:
    :return:
    """
    json_obj = query_json_endpoint(
        request,
        url_for('api_bp.api_documents_first_canvas', api_version=api_version, doc_id=doc_id)
    )

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


@api_bp.route("/api/<api_version>/documents/<doc_id>/annotations/list")
def api_documents_annotations_list(api_version, doc_id):
    """

    :param api_version:
    :param doc_id:
    :return:
    """

    json_obj = query_json_endpoint(
        request,
        url_for('api_bp.api_documents_first_canvas', api_version=api_version, doc_id=doc_id)
    )

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
                "api_bp.api_documents_annotations_zone",
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


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/list')
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
                    url_for('api_bp.api_documents_first_canvas', api_version=api_version, doc_id=doc_id)
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
                            "api_bp.api_documents_annotations_zone",
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


@api_bp.route("/api/<api_version>/documents/<doc_id>/annotations/<zone_id>")
def api_documents_annotations_zone(api_version, doc_id, zone_id):
    """

    :param api_version:
    :param doc_id:
    :param zone_id:
    :return:
    """
    json_obj = query_json_endpoint(
        request,
        url_for('api_bp.api_documents_first_canvas', api_version=api_version, doc_id=doc_id)
    )

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

