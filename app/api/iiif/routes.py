import math

import pprint
from flask import url_for, request, current_app
from requests import HTTPError
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from urllib.request import build_opener, urlopen

from app import auth, db
from app.api.iiif.open_annotation import make_annotation, make_annotation_list
from app.api.response import APIResponseFactory
from app.api.routes import query_json_endpoint, json_loads, api_bp
from app.api.transcriptions.routes import get_reference_transcription
from app.models import AlignmentImage, ImageZone, Image, ImageZoneType

TR_ZONE_TYPE = 1
ANNO_ZONE_TYPE = 2

"""
===========================
    Manifest
===========================
"""


@api_bp.route('/api/<api_version>/documents/<doc_id>/manifest')
def api_documents_manifest(api_version, doc_id):
    img = Image.query.filter(Image.doc_id == doc_id).first()
    if img is None:
        response = APIResponseFactory.make_response(errors={
            "status": 404,
            "details": "Cannot fetch manifest for the document {0}".format(doc_id)
        })
    else:
        manifest_data = urlopen(img.manifest_url).read()
        data = json_loads(manifest_data)
        response = APIResponseFactory.make_response(data=data)

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/manifest-url')
def api_documents_manifest_url(api_version, doc_id):
    try:
        img = Image.query.filter(Image.doc_id == doc_id).one()
        url = img.manifest_url
        response = APIResponseFactory.make_response(data={"manifest_url": url})
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404,
            "details": "Cannot fetch manifest for the document {0}".format(doc_id)
        })
    return APIResponseFactory.jsonify(response)


"""
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
"""


@api_bp.route("/api/<api_version>/documents/<doc_id>/canvas/<canvas_name>")
def api_documents_canvas(api_version, doc_id, canvas_name):
    json_obj = query_json_endpoint(
        request,
        url_for('api_bp.api_documents_first_sequence', api_version=api_version, doc_id=doc_id)
    )

    if "errors" in json_obj:
        response = APIResponseFactory.make_response(errors=[
            json_obj["errors"],
            {"title": "Cannot fetch manifest for the document {0}".format(doc_id)}
        ])
    else:
        response = None
        sequence = json_obj["data"]
        for c in sequence["canvases"]:
            if c["@id"].endswith("/" + canvas_name):
                response = APIResponseFactory.make_response(data=c)
                break
    if response is None:
        response = APIResponseFactory.make_response(errors={
            "title": "Canvas '{1}' not found in manifest for document {0}".format(doc_id, canvas_name)
        })

    return APIResponseFactory.jsonify(response)


@api_bp.route("/api/<api_version>/documents/<doc_id>/first-sequence")
def api_documents_first_sequence(api_version, doc_id):
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
            canvas = json_obj["data"]["sequences"][0]
            response = APIResponseFactory.make_response(data=canvas)
        except (IndexError, KeyError):
            response = APIResponseFactory.make_response(errors={
                "title": "Sequence not found in manifest for document {0}".format(doc_id)
            })

    return APIResponseFactory.jsonify(response)


"""
===========================
    Annotations
===========================
"""


@api_bp.route("/api/<api_version>/documents/<doc_id>/annotations")
def api_documents_annotations(api_version, doc_id):
    """

    :param api_version:
    :param doc_id:
    :return:
    """
    json_obj = query_json_endpoint(
        request,
        url_for('api_bp.api_documents_first_sequence', api_version=api_version, doc_id=doc_id)
    )

    if "errors" in json_obj:
        response = APIResponseFactory.make_response(errors=json_obj["errors"])
    else:
        sequence = json_obj["data"]
        new_annotation_list = []
        for canvas in sequence["canvases"]:
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
                            errors={"details": str(e),
                                    "title": "The annotation list {0} cannot be reached".format(oc["@id"]),
                                    "status": 404}
                        )
                        return APIResponseFactory.jsonify(response)

                    resp = json_loads(resp)
                    if "errors" in resp:
                        return resp
                    else:
                        new_annotation_list.append(resp)

        response = APIResponseFactory.make_response(data=new_annotation_list)

    return APIResponseFactory.jsonify(response)


@api_bp.route("/api/<api_version>/documents/<doc_id>/annotations/list/<canvas_name>")
@api_bp.route("/api/<api_version>/documents/<doc_id>/annotations/from-user/<user_id>/list/<canvas_name>")
def api_documents_annotations_list(api_version, doc_id, canvas_name, user_id=None):
    """

    :param user_id:
    :param api_version:
    :param doc_id:
    :return:
    """
    response = None
    if user_id is None:
        tr = get_reference_transcription(doc_id)
        if tr is None:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "Reference transcription of document {0} cannot be found".format(doc_id)
            })

    user = current_app.get_current_user()
    if not user.is_anonymous:
        if (not user.is_teacher and not user.is_admin) and user_id is not None and int(user_id) != user.id:
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Access forbidden"
            })
    elif user_id is not None:
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })

    if response is None:
        json_obj = query_json_endpoint(
            request,
            url_for('api_bp.api_documents_first_sequence', api_version=api_version, doc_id=doc_id,
                    canvas_name=canvas_name)
        )

        if "errors" in json_obj:
            response = APIResponseFactory.make_response(errors=json_obj["errors"])
        else:
            sequence = json_obj["data"]
            canvas = None
            for c_idx, c in enumerate(sequence["canvases"]):
                if c["@id"].endswith("/" + canvas_name):
                    canvas_idx, canvas = c_idx, c
                    break

            if canvas is None:
                response = APIResponseFactory.make_response(errors={
                    "status": 404, "details": "Canvas %s not found" % canvas_name
                })
                return APIResponseFactory.jsonify(response)

            json_obj = query_json_endpoint(
                request,
                url_for('api_bp.api_documents_manifest_url', api_version=api_version, doc_id=doc_id)
            )
            manifest_url = json_obj["data"].get("manifest_url")

            # TODO s'il y a plusieurs images dans un canvas
            img = Image.query.filter(Image.manifest_url == manifest_url, Image.doc_id == doc_id,
                                     Image.canvas_idx == canvas_idx).first()
            img_json = canvas["images"][0]
            annotations = []

            kargs = {"doc_id": doc_id, "api_version": api_version, "user_id": user_id}

            zone_type = ImageZoneType.query.filter(ImageZoneType.id == ANNO_ZONE_TYPE).one()

            if user_id is None:
                zones = [z for z in img.zones if z.zone_type.id == zone_type.id]
            else:
                zones = [z for z in img.zones if z.zone_type.id and z.user_id == int(user_id)]

            for img_zone in zones:
                kargs["zone_id"] = img_zone.zone_id
                res_uri = request.url_root[0:-1] + url_for("api_bp.api_documents_annotations_zone", **kargs)
                fragment_coords = img_zone.coords
                new_annotation = make_annotation(
                    img_zone.manifest_url, canvas["@id"], img_json, fragment_coords, res_uri, img_zone.note,
                    format="text/plain"
                )
                annotations.append(new_annotation)

            annotation_list = make_annotation_list("f1", doc_id, annotations, zone_type.serialize())
            response = annotation_list

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/list/<canvas_name>')
@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/from-user/<user_id>/list/<canvas_name>')
def api_documents_transcriptions_list(api_version, doc_id, canvas_name, user_id=None):
    """
    Fetch transcription segments formated as a sc:AnnotationList
    :param user_id:
    :param api_version: API version
    :param doc_id: Document id
    :return: a json object Obj with a sc:AnnotationList inside Obj["data"]. Return errors in Obj["errors"]
    """
    response = None

    tr = get_reference_transcription(doc_id)
    if tr is None:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Reference transcription of document {0} cannot be found".format(doc_id)
        })

    user = current_app.get_current_user()
    if not user.is_anonymous:
        if (not user.is_teacher and not user.is_admin) and user_id is not None and int(user_id) != user.id:
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Access forbidden"
            })
    elif user_id is not None:
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })

    if response is None:
        json_obj = query_json_endpoint(
            request,
            url_for('api_bp.api_documents_first_sequence', api_version=api_version, doc_id=doc_id,
                    canvas_name=canvas_name)
        )

        if "errors" in json_obj:
            response = APIResponseFactory.make_response(errors=json_obj["errors"])
        else:
            sequence = json_obj["data"]
            canvas = None
            for c_idx, c in enumerate(sequence["canvases"]):
                if c["@id"].endswith("/" + canvas_name):
                    canvas_idx, canvas = c_idx, c
                    break

            if canvas is None:
                response = APIResponseFactory.make_response(errors={
                    "status": 404, "details": "Canvas %s not found" % canvas_name
                })
                return APIResponseFactory.jsonify(response)

            manifest_url = query_json_endpoint(
                request,
                url_for('api_bp.api_documents_manifest_url', api_version=api_version, doc_id=doc_id)
            )
            manifest_url = manifest_url["data"]

            first_img = canvas["images"][0]
            manifest_url = manifest_url["manifest_url"]
            annotations = []

            # transcription zone type
            # TODO s'il y a plusieurs images dans un canvas
            img = Image.query.filter(Image.manifest_url == manifest_url, Image.doc_id == doc_id,
                                     Image.canvas_idx == canvas_idx).first()
            transcription_zone_type = ImageZoneType.query.filter(ImageZoneType.id == TR_ZONE_TYPE).one()

            if user_id is None:
                zones = [z for z in img.zones if z.zone_type.id == transcription_zone_type.id]
            else:
                zones = [z for z in img.zones if z.zone_type.id and z.user_id == int(user_id)]

            for zone in zones:
                kargs = {"api_version": api_version, "doc_id": doc_id, "zone_id": zone.zone_id}
                if user_id is not None:
                    kargs["user_id"] = user_id

                res_uri = request.url_root[0:-1] + url_for("api_bp.api_documents_annotations_zone", **kargs)

                img_al = AlignmentImage.query.filter(
                    AlignmentImage.transcription_id == tr.id,
                    AlignmentImage.user_id == user_id if user_id is not None else AlignmentImage.user_id,
                    AlignmentImage.manifest_url == zone.manifest_url,
                    AlignmentImage.canvas_idx == zone.canvas_idx,
                    AlignmentImage.img_idx == zone.img_idx,
                    AlignmentImage.zone_id == zone.zone_id
                ).first()

                # is there a text segment bound to this image zone?
                if img_al is not None:
                    tr_seg = tr.content[img_al.ptr_transcription_start:img_al.ptr_transcription_end]
                else:
                    tr_seg = ""

                annotations.append(
                    make_annotation(manifest_url, canvas["@id"], first_img, zone.coords, res_uri, tr_seg, "text/plain")
                )

            annotation_list = make_annotation_list("f2", doc_id, annotations, transcription_zone_type.serialize())
            response = annotation_list

    return APIResponseFactory.jsonify(response)


@api_bp.route("/api/<api_version>/documents/<doc_id>/annotations/<zone_id>")
@api_bp.route("/api/<api_version>/documents/<doc_id>/annotations/<zone_id>/from-user/<user_id>")
def api_documents_annotations_zone(api_version, doc_id, zone_id, user_id=None):
    """

    :param user_id:
    :param api_version:
    :param doc_id:
    :param zone_id:
    :return:
    """
    response = None
    img_zone = None
    tr = None

    user = current_app.get_current_user()
    if not user.is_anonymous:
        if (not user.is_teacher and not user.is_admin) and user_id is not None and int(user_id) != user.id:
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Access forbidden"
            })
        elif user_id is None:
            user_id = user.id
    else:
        if user_id is not None:
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Access forbidden"
            })

        if response is None:
            tr = get_reference_transcription(doc_id)
            if tr is not None:
                user_id = tr.user_id
            else:
                response = APIResponseFactory.make_response(errors={
                    "status": 404, "title": "Reference transcription of document {0} cannot be found".format(doc_id)
                })

    if response is None:
        json_obj = query_json_endpoint(
            request,
            url_for('api_bp.api_documents_first_sequence', api_version=api_version, doc_id=doc_id)
        )

        if "errors" in json_obj:
            response = APIResponseFactory.make_response(errors=json_obj["errors"])
        else:
            sequence = json_obj["data"]
            try:
                img = Image.query.filter(Image.doc_id == doc_id).one()
                # select annotations zones
                img_zone = ImageZone.query.filter(
                    ImageZone.zone_id == zone_id,
                    ImageZone.manifest_url == img.manifest_url,
                    ImageZone.user_id == user_id
                ).one()
            except NoResultFound:
                response = APIResponseFactory.make_response(
                    errors={
                        "status": 404,
                        "title": "The current user has no annotation {0} for the document {1}".format(zone_id, doc_id)
                    }
                )

    if response is None:
        kargs = {"doc_id": doc_id, "api_version": api_version, "zone_id": img_zone.zone_id}
        if user_id is not None:
            kargs["user_id"] = user_id
        res_uri = request.url_root[0:-1] + url_for("api_bp.api_documents_annotations_zone", **kargs)

        # if the note content is empty, then you need to fetch a transcription segment
        note_content = ""
        if img_zone.note is None:

            if tr is None:
                tr = get_reference_transcription(doc_id)
                if tr is None:
                    response = APIResponseFactory.make_response(errors={
                        "status": 404, "title": "Reference transcription of document {0} cannot be found".format(doc_id)
                    })
            else:
                try:
                    img_al = AlignmentImage.query.filter(
                        AlignmentImage.transcription_id == tr.id,
                        AlignmentImage.zone_id == img_zone.zone_id,
                        AlignmentImage.user_id == tr.user_id,
                        AlignmentImage.manifest_url == img.manifest_url
                    ).one()
                    note_content = tr.content[img_al.ptr_transcription_start:img_al.ptr_transcription_end]
                except NoResultFound:
                    response = APIResponseFactory.make_response(errors={
                        "status": 404,
                        "title": "This transcription zone has no text fragment attached to it".format(doc_id)
                    })
        # else it is a mere image note
        else:
            note_content = img_zone.note

        if response is None:
            # TODO: gerer erreur si pas d'image dans le canvas
            canvas = sequence["canvases"][img_zone.canvas_idx]
            img_json = canvas["images"][img_zone.img_idx]
            fragment_coords = img_zone.coords
            new_annotation = make_annotation(img.manifest_url, canvas["@id"], img_json, fragment_coords,
                                             res_uri,
                                             note_content,
                                             format="text/plain")
            response = new_annotation

    return APIResponseFactory.jsonify(response)


@api_bp.route("/api/<api_version>/documents/<doc_id>/annotations", methods=["POST"])
@auth.login_required
def api_post_documents_annotations(api_version, doc_id):
    """
        {
            "data" : [{
                "manifest_url" : "http://193.48.42.68/adele/iiif/manifests/man20.json",
                "canvas_idx" : 0,
                "img_idx" : 0,
                "coords" : "10,40,500,50",
                "content": "Je suis une première annotation avec <b>du markup</b>"
                "zone_type_id" : 1,
                "username" : "Eleve1"    (optionnal)
            },
        ...
            },
            {
                "manifest_url" : "http://193.48.42.68/adele/iiif/manifests/man20.json",
                "canvas_idx" : 0,
                "img_idx" : 0,
                "coords" : "30,40,500,50",
                "content": "Je suis une n-ième annotation avec <b>du markup</b>"
                "zone_type_id" : 1,
                "username" : "Professeur1"  (optionnal)
            }]
        }
    :param api_version:
    :param doc_id:
    :return: the inserted annotations
    """

    data = request.get_json()
    response = None
    if "data" in data:
        data = data["data"]
        if not isinstance(data, list):
            data = [data]

        user = current_app.get_current_user()
        if user.is_anonymous:
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Access forbidden", "details": "Cannot insert data"
            })
        else:
            # get the zone_id max
            try:
                img_zone_max_zone_id = db.session.query(func.max(ImageZone.zone_id)).filter(
                    ImageZone.manifest_url == data[0]["manifest_url"],
                    ImageZone.img_idx == data[0]["img_idx"],
                    ImageZone.canvas_idx == data[0]["canvas_idx"],
                ).group_by(
                    ImageZone.manifest_url, ImageZone.canvas_idx, ImageZone.img_idx
                ).one()
                img_zone_max_zone_id = img_zone_max_zone_id[0] + 1
            except NoResultFound:
                # it is the first zone for this image in this manifest
                img_zone_max_zone_id = 1

            new_img_zone_ids = []
            for anno in data:
                user_id = user.id
                # teacher and admin MAY post/put/delete for others
                if (user.is_teacher or user.is_admin) and "username" in anno:
                    usr = current_app.get_user_from_username(anno["username"])
                    if usr is not None:
                        user_id = usr.id
                elif "username" in anno:
                    usr = current_app.get_user_from_username(anno["username"])
                    if usr is not None and usr.id != user.id:
                        db.session.rollback()
                        response = APIResponseFactory.make_response(errors={
                            "status": 403, "title": "Access forbidden", "details": "Cannot insert data"
                        })
                        break

                # INSERT data but dont commit yet
                img_zone = ImageZone(
                    manifest_url=anno["manifest_url"],
                    canvas_idx=anno["canvas_idx"],
                    img_idx=anno["img_idx"],
                    note=anno["content"],
                    coords=anno["coords"],
                    zone_id=img_zone_max_zone_id,
                    zone_type_id=anno["zone_type_id"],
                    user_id=user_id
                )
                db.session.add(img_zone)
                new_img_zone_ids.append((user_id, img_zone_max_zone_id))
                img_zone_max_zone_id += 1

        if response is None:
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                response = APIResponseFactory.make_response(errors={
                    "status": 403, "title": "Cannot insert data", "details": str(e)
                })

        if response is None:
            created_zones = []
            # perform a GET to retrieve the freshly inserted data
            for user_id, img_zone_id in new_img_zone_ids:
                json_obj = query_json_endpoint(
                    request,
                    url_for(
                        "api_bp.api_documents_annotations_zone",
                        api_version=api_version,
                        doc_id=doc_id,
                        zone_id=img_zone_id,
                        user_id=user_id
                    ),
                    user=user
                )
                if "errors" not in json_obj:
                    created_zones.append(json_obj)

            response = APIResponseFactory.make_response(data=created_zones)

    return APIResponseFactory.jsonify(response)


@api_bp.route("/api/<api_version>/documents/<doc_id>/annotations", methods=["PUT"])
@auth.login_required
def api_put_documents_annotations(api_version, doc_id):
    """
        {
            "data" : [{
                "manifest_url" : "http://193.48.42.68/adele/iiif/manifests/man20.json",
                "canvas_idx" : 0,
                "img_idx" : 0,
                "zone_id" : 32,
                "coords" : "10,40,500,50",
                "content": "Je suis une première annotation avec <b>du markup</b>",
                "zone_type_id" : 1,
                "username": "Eleve1"    (optionnal)
            },
        ...
            },
            {
                "manifest_url" : "http://193.48.42.68/adele/iiif/manifests/man20.json",
                "canvas_idx" : 0,
                "img_idx" : 0,
                "zone_id" : 30,
                "coords" : "30,40,500,50",
                "content": "Je suis une n-ième annotation avec <b>du markup</b>",
                "zone_type_id" : 1,
                "username": "Professeur1"    (optionnal)
            }]
        }
    :param api_version:
    :param doc_id:
    :param zone_id:
    :return: the updated annotations
    """

    data = request.get_json()
    response = None

    if "data" in data:
        data = data["data"]

        if not isinstance(data, list):
            data = [data]

        # find which zones to update
        img_zones = []
        user = current_app.get_current_user()
        if user.is_anonymous:
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Access forbidden", "details": "Cannot update data"
            })
        else:
            for anno in data:

                user_id = user.id
                # teacher and admin MAY post/put/delete for others
                if (user.is_teacher or user.is_admin) and "username" in anno:
                    usr = current_app.get_user_from_username(anno["username"])
                    if usr is not None:
                        user_id = usr.id
                elif "username" in anno:
                    usr = current_app.get_user_from_username(anno["username"])
                    if usr is not None and usr.id != user.id:
                        response = APIResponseFactory.make_response(errors={
                            "status": 403, "title": "Access forbidden", "details": "Cannot update data"
                        })
                        break

                try:
                    img_zone = ImageZone.query.filter(
                        ImageZone.zone_id == anno["zone_id"],
                        ImageZone.manifest_url == anno["manifest_url"],
                        ImageZone.img_idx == anno["img_idx"],
                        ImageZone.canvas_idx == anno["canvas_idx"],
                        ImageZone.user_id == user_id
                    ).one()
                    img_zones.append((user_id, img_zone))
                except NoResultFound as e:
                    response = APIResponseFactory.make_response(errors={
                        "status": 404,
                        "title": "Image zone {0} not found".format(anno["zone_id"]),
                        "details": "Cannot update image zone: {0}".format(str(e))
                    })
                    break

        if response is None:
            # update the annotations
            for i, (user_id, img_zone) in enumerate(img_zones):
                anno = data[i]
                img_zone.coords = anno["coords"]
                img_zone.note = anno["content"]
                img_zone.zone_type_id = anno["zone_type_id"]
                db.session.add(img_zone)

            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                response = APIResponseFactory.make_response(errors={
                    "status": 403, "title": "Cannot update data", "details": str(e)
                })

            if response is None:
                updated_zones = []
                # perform a GET to retrieve the freshly updated data
                for user_id, img_zone in img_zones:
                    json_obj = query_json_endpoint(
                        request,
                        url_for(
                            "api_bp.api_documents_annotations_zone",
                            api_version=api_version,
                            doc_id=doc_id,
                            zone_id=img_zone.zone_id,
                            user_id=user_id
                        ),
                        user=user
                    )
                    if "errors" not in json_obj:
                        updated_zones.append(json_obj)

                response = APIResponseFactory.make_response(data=updated_zones)
    else:
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Cannot update data", "details": "Check your request syntax"
        })

    return APIResponseFactory.jsonify(response)


@api_bp.route("/api/<api_version>/documents/<doc_id>/annotations/from-user/<user_id>", methods=["DELETE"])
@api_bp.route("/api/<api_version>/documents/<doc_id>/annotations/<zone_id>/from-user/<user_id>", methods=["DELETE"])
@auth.login_required
def api_delete_documents_annotations(api_version, doc_id, user_id, zone_id=None):
    """
    :param user_id:
    :param api_version:
    :param doc_id:
    :param zone_id:
    :return:  {"data": {}}
    """

    response = None

    user = current_app.get_current_user()
    if not user.is_anonymous:
        if (not user.is_teacher and not user.is_admin) and int(user_id) != user.id:
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Access forbidden"
            })

    img = Image.query.filter(Image.doc_id == doc_id).first()
    if zone_id is None:
        zone_id = ImageZone.zone_id

    try:
        img_zones = ImageZone.query.filter(
            ImageZone.zone_id == zone_id,
            ImageZone.manifest_url == img.manifest_url,
            ImageZone.user_id == user_id
        ).all()
        for img_zone in img_zones:
            db.session.delete(img_zone)
    except NoResultFound as e:
        response = APIResponseFactory.make_response(errors={
            "status": 404,
            "title": "Image zone not found".format(zone_id),
            "details": "Cannot delete image zone: {0}".format(str(e))
        })

    if response is None:
        try:
            db.session.commit()
        except Exception as e:
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Cannot delete data", "details": str(e)
            })

        # the DELETE is OK, respond with no data
        if response is None:
            response = APIResponseFactory.make_response()

    return APIResponseFactory.jsonify(response)


@api_bp.route("/api/<api_version>/documents/<doc_id>/images")
def api_documents_images(api_version, doc_id):
    images = Image.query.filter(Image.doc_id == doc_id).all()

    response = APIResponseFactory.make_response(data=[img.serialize() for img in images])

    return APIResponseFactory.jsonify(response)


@api_bp.route("/api/<api_version>/documents/<doc_id>/images", methods=["POST"])
@auth.login_required
def api_post_documents_images(api_version, doc_id):
    """
    {
        "data" : {
            "manifest_url" : "http://my.manifests/man1.json",
            "canvas_idx": 0,
            "img_idx": 0,
        }
    }
    :param api_version:
    :param doc_id:
    :return:
    """
    response = None

    user = current_app.get_current_user()
    if user.is_anonymous or not (user.is_teacher or user.is_admin):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })

    if response is None:
        data = request.get_json()
        data = data["data"]

        if not isinstance(data, list):
            data = [data]

        new_images = []
        try:
            for img_data in data:
                new_img = Image(manifest_url=img_data["manifest_url"],
                                canvas_idx=img_data["canvas_idx"],
                                img_idx=img_data["img_idx"],
                                doc_id=doc_id)
                db.session.add(new_img)

                json_obj = query_json_endpoint(
                    request,
                    url_for('api_bp.api_documents_first_sequence', api_version=api_version, doc_id=doc_id)
                )
                canvas = json_obj["data"]["canvases"][img_data["canvas_idx"]]
                img_url = canvas["images"][img_data["img_idx"]]["@id"]
                new_img_url = Image(manifest_url=img_data["manifest_url"],
                                canvas_idx=img_data["canvas_idx"],
                                img_idx=img_data["img_idx"],
                                img_url=img_url)
                db.session.add(new_img_url)

                new_images.append(new_img)
        except KeyError:
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Insert forbidden", "details": "Data is malformed"
            })
            db.session.rollback()
        except ValueError as e:
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Insert forbidden", "details": str(e)
            })
            db.session.rollback()

        if response is None:
            try:
                db.session.commit()
            except Exception as e:
                response = APIResponseFactory.make_response(errors={
                    "status": 403, "title": "Cannot insert data", "details": str(e)
                })

            if response is None:
                images_after = query_json_endpoint(
                    request,
                    url_for("api_bp.api_documents_images", api_version=api_version, doc_id=doc_id)
                )

                response = APIResponseFactory.make_response(data=images_after["data"])

    return APIResponseFactory.jsonify(response)


@api_bp.route("/api/<api_version>/documents/<doc_id>/images", methods=['DELETE'])
@auth.login_required
def api_delete_documents_images(api_version, doc_id):
    response = None

    user = current_app.get_current_user()
    if user.is_anonymous or not (user.is_teacher or user.is_admin):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })

    if response is None:

        images = Image.query.filter(Image.doc_id == doc_id).all()
        for img in images:
            db.session.delete(img)

        try:
            db.session.commit()
            response = APIResponseFactory.make_response()
        except Exception as e:
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Cannot delete data", "details": str(e)
            })

    return APIResponseFactory.jsonify(response)


def get_bbox(coords, max_width, max_height):
    """
    Get the bounding box from a coord lists. Clamp the results to max_width, max_height
    :param coords:
    :param max_width:
    :param max_height:
    :return: (x, y, w, h)
    """
    if len(coords) % 2 == 0:
        # poly/rect
        min_x, min_y = coords[0], coords[1]
        max_x, max_y = coords[0], coords[1]
        for i in range(0, len(coords) - 1, 2):
            # X stuff
            if coords[i] < min_x:
                min_x = coords[i]
            elif coords[i] > max_x:
                max_x = coords[i]
            # Y stuff
            if coords[i + 1] < min_y:
                min_y = coords[i + 1]
            elif coords[i + 1] > max_y:
                max_y = coords[i + 1]
        width = abs(max_x - min_x)
        height = abs(max_y - min_y)
    else:
        # circle
        cx, cy, r = coords
        min_x, min_y = cx - r, cy - r
        width, height = 2 * r, 2 * r

    # clamp to the image borders
    if min_x < 0:
        # width = width + min_x
        min_x = 0
    elif min_x > max_width:
        min_x = max_width - width

    if min_y < 0:
        # height = height + min_y
        min_y = 0
    elif min_y > max_height:
        min_y = max_height - height

    if min_x + width > max_width:
        width = max_width - min_x
    if min_y + height > max_height:
        height = max_height - min_y

    return min_x, min_y, width, height


@api_bp.route("/api/<api_version>/documents/<doc_id>/annotations/fragments/from-user/<user_id>")
@api_bp.route("/api/<api_version>/documents/<doc_id>/annotations/fragments/<zone_id>/from-user/<user_id>")
def api_documents_annotation_image_fragments(api_version, doc_id, zone_id=None, user_id=None):
    """
    Fragment urls points to the IIIF Image API url of the area of an image
    :param api_version:
    :param doc_id:
    :param zone_id:
    :param user_id:
    :return: return a list of fragments (zone_id, coords, fragment_url) indexed by their img_id in a dict
    """

    json_obj = query_json_endpoint(
        request,
        url_for('api_bp.api_documents_manifest_url', api_version=api_version, doc_id=doc_id)
    )

    if "errors" in json_obj:
        response = APIResponseFactory.make_response(errors=json_obj["errors"])
    else:
        manifest_url = json_obj["data"]["manifest_url"]
        if zone_id is None:
            zone_id = ImageZone.zone_id
        zones = ImageZone.query.filter(
            ImageZone.zone_id == zone_id,
            ImageZone.manifest_url == manifest_url,
            ImageZone.user_id == user_id
        ).all()

        frag_urls = {}
        for zone in zones:

            root_img_url = zone.img_id[:zone.img_id.index('/full')]
            json_obj = query_json_endpoint(request, "%s/info.json" % root_img_url, direct=True)

            coords = [math.floor(float(c)) for c in zone.coords.split(',')]
            x, y, w, h = get_bbox(coords, max_width=int(json_obj['width']), max_height=int(json_obj['height']))

            if x >= 0 and y >= 0:
                url = "%s/%i,%i,%i,%i/full/0/default.jpg" % (root_img_url, x, y, w, h)

                if zone.img_id not in frag_urls:
                    frag_urls[zone.img_id] = [{'zone_id': zone.zone_id, 'fragment_url': url, 'coords': coords}]
                else:
                    frag_urls[zone.img_id].append({'zone_id': zone.zone_id, 'fragment_url': url, 'coords': coords})

        response = APIResponseFactory.make_response(data={"fragments": frag_urls})

    return APIResponseFactory.jsonify(response)
