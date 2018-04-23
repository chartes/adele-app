from flask import url_for, request
from requests import HTTPError
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from urllib.request import build_opener, urlopen

from app import auth, db, get_current_user, get_user_from_username
from app.api.iiif.open_annotation import make_annotation, make_annotation_list
from app.api.response import APIResponseFactory
from app.api.routes import query_json_endpoint, json_loads, api_bp
from app.api.transcriptions.routes import get_reference_transcription
from app.models import AlignmentImage, ImageZone, Image


"""
===========================
    Manifest
===========================
"""


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
                        errors={"details": e.msg,
                                "title": "The annotation list {0} cannot be reached".format(oc["@id"]),
                                "status": e.code}
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
@api_bp.route("/api/<api_version>/documents/<doc_id>/annotations/from-user/<user_id>/list")
def api_documents_annotations_list(api_version, doc_id, user_id=None):
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

    user = get_current_user()
    if user is not None:
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
            url_for('api_bp.api_documents_first_canvas', api_version=api_version, doc_id=doc_id)
        )

        if "errors" in json_obj:
            response = APIResponseFactory.make_response(errors=json_obj["errors"])
        else:
            canvas = json_obj["data"]
            img = Image.query.filter(Image.doc_id == doc_id).one()
            # TODO s'il n'y a pas d'image dans le manifest
            img_json = canvas["images"][0]
            annotations = []

            kargs = {"doc_id": doc_id, "api_version": api_version, "user_id": user_id}

            if user_id is None:
                zones = [z for z in img.zones if z.note is not None]
            else:
                zones = [z for z in img.zones if z.note is not None and z.user_id == int(user_id)]

            for img_zone in zones:
                kargs["zone_id"] = img_zone.zone_id
                res_uri = request.url_root[0:-1] + url_for("api_bp.api_documents_annotations_zone", **kargs)
                fragment_coords = img_zone.coords
                new_annotation = make_annotation(
                    img_zone.manifest_url, img_json, fragment_coords, res_uri, img_zone.note, format="text/plain"
                )
                annotations.append(new_annotation)

            annotation_list = make_annotation_list("f1", doc_id, annotations)
            response = annotation_list

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/list')
@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/from-user/<user_id>/list')
def api_documents_transcriptions_list(api_version, doc_id, user_id=None):
    """
    Fetch transcription segments formated as a sc:AnnotationList
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

    user = get_current_user()
    if user is not None:
        if (not user.is_teacher and not user.is_admin) and user_id is not None and int(user_id) != user.id:
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Access forbidden"
            })
    elif user_id is not None:
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })

    if response is None:
        # let's go finding the alignment segments
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

                img_als = AlignmentImage.query.filter(
                    AlignmentImage.transcription_id == tr.id,
                    AlignmentImage.user_id == user_id if user_id is not None else AlignmentImage.user_id
                ).all()
                for img_al in img_als:
                    tr_seg = tr.content[img_al.ptr_transcription_start:img_al.ptr_transcription_end]

                    kargs = {"api_version": api_version, "doc_id": doc_id, "zone_id": img_al.zone_id}
                    if user_id is not None:
                        kargs["user_id"] = user_id

                    res_uri = request.url_root[0:-1] + url_for("api_bp.api_documents_annotations_zone", **kargs)

                    # TODO: gerer erreur
                    img_zone = ImageZone.query.filter(
                        ImageZone.manifest_url == img_al.manifest_url,
                        ImageZone.img_id == img_al.img_id,
                        ImageZone.zone_id == img_al.zone_id,
                        ImageZone.user_id == tr.user_id
                    ).one()

                    fragment_coords = img_zone.coords
                    annotations.append(
                        make_annotation(img_al.manifest_url, img_json, fragment_coords, res_uri, tr_seg, "text/plain")
                    )

                annotation_list = make_annotation_list("f2", doc_id, annotations)
                response = annotation_list

        except NoResultFound:
            response = APIResponseFactory.make_response()

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

    user = get_current_user()
    if user is not None:
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
            url_for('api_bp.api_documents_first_canvas', api_version=api_version, doc_id=doc_id)
        )

        if "errors" in json_obj:
            response = APIResponseFactory.make_response(errors=json_obj["errors"])
        else:
            canvas = json_obj["data"]
            print("user_id", user_id)
            try:
                img = Image.query.filter(Image.doc_id == doc_id).one()
                # select annotations zones
                img_zone = ImageZone.query.filter(
                    ImageZone.img_id == img.id,
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
            img_json = canvas["images"][0]
            fragment_coords = img_zone.coords

            new_annotation = make_annotation(img.manifest_url, img_json, fragment_coords, res_uri, note_content,
                                             format="text/plain")
            response = new_annotation


    return APIResponseFactory.jsonify(response)


def validate_annotation_data_format(anno):
    if "content" in anno and "coords" in anno and "manifest_url" in anno and "img_id" in anno:
        # check type of data and that there is at least 3 coords value (a circle)
        return isinstance(anno["content"], str) and \
               isinstance(anno["img_id"], str) and \
               isinstance(anno["manifest_url"], str) and \
               len([int(c) for c in anno["coords"].split(",")]) >= 3
    else:
        return False


@api_bp.route("/api/<api_version>/documents/<doc_id>/annotations", methods=["POST"])
@auth.login_required
def api_post_documents_annotations(api_version, doc_id):
    """
        {
            "data" : [{
                "manifest_url" : "http://193.48.42.68/adele/iiif/manifests/man20.json",
                "img_id" : "http://193.48.42.68/loris/adele/dossiers/20.jpg/full/full/0/default.jpg",
                "coords" : "10,40,500,50",
                "content": "Je suis une première annotation avec <b>du markup</b>"
                "username" : "Eleve1"    (optionnal)
            },
        ...
            },
            {
                "manifest_url" : "http://193.48.42.68/adele/iiif/manifests/man20.json",
                "img_id" : "http://193.48.42.68/loris/adele/dossiers/20.jpg/full/full/0/default.jpg",
                "coords" : "30,40,500,50",
                "content": "Je suis une n-ième annotation avec <b>du markup</b>"
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

        validated_annotations = [a for a in data if validate_annotation_data_format(a)]
        user = get_current_user()

        # get the zone_id max
        try:
            img_zone_max_zone_id = db.session.query(func.max(ImageZone.zone_id)).filter(
                ImageZone.manifest_url == validated_annotations[0]["manifest_url"],
                ImageZone.img_id == validated_annotations[0]["img_id"]
            ).group_by(
                ImageZone.manifest_url, ImageZone.img_id
            ).one()
            img_zone_max_zone_id = img_zone_max_zone_id[0] + 1
        except NoResultFound:
            # it is the first zone for this image in this manifest
            img_zone_max_zone_id = 1

        new_img_zone_ids = []
        for anno in validated_annotations:

            user_id = user.id
            # teacher and admin MAY post/put/delete for others
            if (user.is_teacher or user.is_admin) and "username" in anno:
                usr = get_user_from_username(anno["username"])
                if usr is not None:
                    user_id = usr.id
            elif "username" in anno:
                usr = get_user_from_username(anno["username"])
                if usr is not None and usr.id != user.id:
                    db.session.rollback()
                    response = APIResponseFactory.make_response(errors={
                        "status": 403, "title": "Access forbidden", "details": "Cannot insert data"
                    })
                    break

            # INSERT data but dont commit yet
            img_zone = ImageZone(
                manifest_url=anno["manifest_url"],
                img_id=anno["img_id"],
                note=anno["content"],
                coords=anno["coords"],
                zone_id=img_zone_max_zone_id,
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
                "img_id" : "http://193.48.42.68/loris/adele/dossiers/20.jpg/full/full/0/default.jpg",
                "zone_id" : 32,
                "coords" : "10,40,500,50",
                "content": "Je suis une première annotation avec <b>du markup</b>",
                "username": "Eleve1"    (optionnal)
            },
        ...
            },
            {
                "manifest_url" : "http://193.48.42.68/adele/iiif/manifests/man20.json",
                "img_id" : "http://193.48.42.68/loris/adele/dossiers/20.jpg/full/full/0/default.jpg",
                "zone_id" : 30
                "coords" : "30,40,500,50",
                "content": "Je suis une n-ième annotation avec <b>du markup</b>",
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
        validated_annotations = [a for a in data if validate_annotation_data_format(a) and "zone_id" in a]
        img_zones = []
        user = get_current_user()
        for anno in validated_annotations:

            user_id = user.id
            # teacher and admin MAY post/put/delete for others
            if (user.is_teacher or user.is_admin) and "username" in anno:
                usr = get_user_from_username(anno["username"])
                if usr is not None:
                    user_id = usr.id
            elif "username" in anno:
                usr = get_user_from_username(anno["username"])
                if usr is not None and usr.id != user.id:
                    response = APIResponseFactory.make_response(errors={
                        "status": 403, "title": "Access forbidden", "details": "Cannot update data"
                    })
                    break

            try:
                img_zone = ImageZone.query.filter(
                    ImageZone.zone_id == anno["zone_id"],
                    ImageZone.manifest_url == anno["manifest_url"],
                    ImageZone.img_id == anno["img_id"],
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
                anno = validated_annotations[i]
                img_zone.coords = anno["coords"]
                img_zone.note = anno["content"]
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

    user = get_current_user()
    if user is not None:
        if (not user.is_teacher and not user.is_admin) and int(user_id) != user.id:
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Access forbidden"
            })

    json_obj = query_json_endpoint(
        request,
        url_for('api_bp.api_documents_manifest', api_version=api_version, doc_id=doc_id)
    )

    if "errors" in json_obj:
        response = APIResponseFactory.make_response(errors=json_obj["errors"])
    else:
        manifest = json_obj["data"]

        if zone_id is None:
            img_id = ImageZone.img_id
            zone_id = ImageZone.zone_id
        else:
            # TODO c'est pas ouf
            img_id = manifest["sequences"][0]["canvases"][0]["images"][0]["resource"]["@id"]

        try:
            img_zones = ImageZone.query.filter(
                ImageZone.zone_id == zone_id,
                ImageZone.manifest_url == manifest["@id"],
                ImageZone.img_id == img_id,
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
