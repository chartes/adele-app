import math

import pprint
from flask import url_for, request, current_app
from flask_jwt_extended import jwt_required
from requests import HTTPError
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from urllib.request import build_opener, urlopen

from app import db
from app.api.iiif.open_annotation import make_annotation, make_annotation_list, make_annotation_layer
from app.api.response import APIResponseFactory
from app.api.routes import json_loads, api_bp
from app.models import AlignmentImage, ImageZone, Image, ImageZoneType, Document, ImageUrl, ANNO_ZONE_TYPE, TR_ZONE_TYPE
from app.utils import make_404, make_200, make_400, forbid_if_nor_teacher_nor_admin

"""
===========================
    Manifest
===========================
"""


def make_manifest(api_version, doc_id):
    img = Image.query.filter(Image.doc_id == doc_id).first()
    manifest_data = urlopen(img.manifest_url).read()
    data = json_loads(manifest_data)

    # enrich the manifest with annotation lists
    for canvas_idx, canvas in enumerate(data["sequences"][0]["canvases"]):
        if "otherContent" not in canvas:
            canvas["otherContent"] = []
        kwargs = {
            "api_version": 1.0,
            "doc_id": doc_id
        }

        canvas["otherContent"].extend([
            {
                "@type": "sc:Layer",
                "@id": request.host_url[:-1] + url_for("api_bp.api_documents_annotations_layer",
                                                       motivation="commenting", **kwargs)
            },
            {
                "@type": "sc:Layer",
                "@id": request.host_url[:-1] + url_for("api_bp.api_documents_annotations_layer",
                                                       motivation="describing", **kwargs)
            }
        ])

    return data


@api_bp.route('/api/<api_version>/documents/<doc_id>/iiif/manifest')
def api_documents_manifest(api_version, doc_id):
    try:
        manifest = make_manifest(api_version, doc_id)
        return make_200(manifest)
    except Exception as e:
        return make_400(str(e))


@api_bp.route('/api/<api_version>/documents/<doc_id>/iiif/manifest/origin')
def api_documents_manifest_origin(api_version, doc_id):
    img = Image.query.filter(Image.doc_id == doc_id).first()
    if img is None:
        return make_404("Cannot fetch manifest for the document {0}".format(doc_id))
    return make_200(data={"origin": img.manifest_url})


"""
===========================
    Annotations
===========================
"""


@api_bp.route("/api/<api_version>/documents/<doc_id>/iiif/layer/<motivation>")
def api_documents_annotations_layer(api_version, doc_id, motivation):
    manifest = make_manifest(api_version, doc_id)
    sequence = manifest["sequences"][0]
    anno_lists = []
    for canvas_idx, canvas in enumerate(sequence["canvases"]):
        anno_lists.append(url_for('api_bp.api_documents_annotations_list_by_canvas', **{
            "api_version": api_version,
            "doc_id": doc_id,
            "motivation": motivation,
            "canvas_idx": canvas_idx
        }, _external=True))
    layer = make_annotation_layer(request.base_url, anno_lists, motivation)
    return make_200(layer)


@api_bp.route("/api/<api_version>/documents/<doc_id>/iiif/list/<motivation>-<canvas_idx>")
def api_documents_annotations_list_by_canvas(api_version, doc_id, motivation, canvas_idx):
    """
    """
    user = current_app.get_current_user()
    doc = Document.query.filter(Document.id == doc_id).first()

    if user.is_anonymous and doc.is_published is False:
        annotation_list = make_annotation_list(request.base_url, [])
        return make_200(annotation_list)

    try:
        manifest = make_manifest(api_version, doc_id)
        sequence = manifest["sequences"][0]
        canvas = sequence["canvases"][int(canvas_idx)]

        annotations = []
        img = Image.query.filter(Image.doc_id == doc_id).first()
        img = Image.query.filter(Image.manifest_url == img.manifest_url, Image.doc_id == doc_id,
                                 Image.canvas_idx == canvas_idx).first()

        # TODO s'il y a plusieurs images dans un seul et même canvas ?
        img_json = canvas["images"][0]
        kwargs = {
            "doc_id": doc_id,
            "api_version": api_version,
            "canvas_idx": canvas_idx
        }

        manifest_url = current_app.with_url_prefix(
            url_for("api_bp.api_documents_manifest", api_version=1.0, doc_id=doc_id))
        for img_zone in [zone for zone in img.zones if zone.zone_type.label == motivation]:
            kwargs["zone_id"] = img_zone.zone_id
            kwargs["motivation"] = img_zone.zone_type.label
            res_uri = current_app.with_url_prefix(url_for("api_bp.api_documents_annotations", **kwargs))
            fragment_coords = img_zone.coords

            if img_zone.zone_type.label == "commenting":
                from app.api.transcriptions.routes import get_reference_transcription
                tr = get_reference_transcription(doc_id)
                if tr is None:
                    annotation_list = make_annotation_list(request.base_url, [])
                    return make_200(annotation_list)

                img_al = AlignmentImage.query.filter(
                    AlignmentImage.transcription_id == tr.id,
                    AlignmentImage.manifest_url == img_zone.manifest_url,
                    AlignmentImage.canvas_idx == img_zone.canvas_idx,
                    AlignmentImage.img_idx == img_zone.img_idx,
                    AlignmentImage.zone_id == img_zone.zone_id
                ).first()

                # is there a text segment bound to this image zone?
                if img_al is not None:
                    text_content = tr.content[img_al.ptr_transcription_start:img_al.ptr_transcription_end]
                else:
                    text_content = ""

            else:
                text_content = img_zone.note

            new_annotation = make_annotation(
                manifest_url,
                canvas["@id"], img_json, fragment_coords, res_uri, text_content,
                format="text/plain"
            )
            annotations.append(new_annotation)
        annotation_list = make_annotation_list(request.base_url, annotations)
        return make_200(annotation_list)

    except Exception as e:
        print(str(e))
        return make_400(str(e))


@api_bp.route("/api/<api_version>/documents/<doc_id>/iiif/list/<motivation>-<canvas_idx>/annotation/<zone_id>")
def api_documents_annotations(api_version, doc_id, motivation, canvas_idx, zone_id):
    """

    :param canvas_name:
    :param api_version:
    :param doc_id:
    :param zone_id:
    :return:
    """

    from app.api.transcriptions.routes import get_reference_transcription
    tr = get_reference_transcription(doc_id)
    if tr is None:
        return make_404()
    try:
        manifest = make_manifest(api_version, doc_id)
        sequence = manifest["sequences"][0]

        img = Image.query.filter(Image.doc_id == doc_id).first()

        # select annotations zones
        img_zone = ImageZone.query.filter(
            ImageZone.zone_id == zone_id,
            ImageZone.manifest_url == img.manifest_url
        ).one()

        res_uri = current_app.with_url_prefix(request.path)

        # if the note content is empty, then you need to fetch a transcription segment
        img_al = None
        if img_zone.note is None:
            try:
                img_al = AlignmentImage.query.filter(
                    AlignmentImage.transcription_id == tr.id,
                    AlignmentImage.zone_id == img_zone.zone_id,
                    AlignmentImage.user_id == tr.user_id,
                    AlignmentImage.manifest_url == img.manifest_url
                ).one()
                note_content = tr.content[img_al.ptr_transcription_start:img_al.ptr_transcription_end]
            except NoResultFound:
                return make_404(details="This transcription zone has no text fragment attached to it".format(doc_id))
        # else it is a mere image note
        else:
            note_content = img_zone.note

        # TODO: gerer erreur si pas d'image dans le canvas
        canvas = sequence["canvases"][img_zone.canvas_idx]
        img_json = canvas["images"][img_zone.img_idx]
        fragment_coords = img_zone.coords
        url = current_app.with_url_prefix(url_for("api_bp.api_documents_manifest", api_version=1.0, doc_id=doc_id))
        new_annotation = make_annotation(
            url,
            canvas["@id"], img_json, fragment_coords,
            res_uri,
            note_content,
            format="text/plain"
        )
        return make_200(new_annotation)

    except Exception as e:
        print(str(e))
        return make_400(str(e))


#
# @api_bp.route("/api/<api_version>/documents/<doc_id>/annotations/<canvas_name>", methods=["POST"])
# @jwt_required
# @forbid_if_nor_teacher_nor_admin
# def api_post_documents_annotations(api_version, doc_id, canvas_name):
#    """
#        {
#            "data" : [{
#                "coords" : "10,40,500,50",
#                "content": "Je suis une première annotation avec <b>du markup</b>"
#                "zone_type_id" : 1,
#            },
#        ...
#            },
#            {
#                "coords" : "30,40,500,50",
#                "content": "Je suis une n-ième annotation avec <b>du markup</b>"
#                "zone_type_id" : 1,
#            }]
#        }
#    :param canvas_name:
#    :param api_version:
#    :param doc_id:
#    :return: the inserted annotations
#    """
#    new_img_zones = []
#    data = request.get_json()
#    response = None
#    if "data" in data:
#        data = data["data"]
#        if not isinstance(data, list):
#            data = [data]
#
#        user = current_app.get_current_user()
#        if user.is_anonymous:
#            response = APIResponseFactory.make_response(errors={
#                "status": 403, "title": "Access forbidden", "details": "Cannot insert data"
#            })
#        else:
#            json_obj = query_json_endpoint(
#                request,
#                url_for('api_bp.api_documents_manifest_url_origin', api_version=api_version, doc_id=doc_id)
#            )
#            manifest_url = json_obj["data"]['manifest_url']
#            canvas_idx = get_canvas_idx_from_name(api_version, doc_id, canvas_name)
#            img_idx = 0
#
#            """
#                Delete annotations for the implicated canvases
#
#            print(data)
#            print("delete image zones:")
#            print("deleting zones for canvas ", canvas_idx)
#            for old_zone in ImageZone.query.filter(
#                ImageZone.canvas_idx == canvas_idx,
#                ImageZone.img_idx == img_idx,
#                ImageZone.manifest_url == manifest_url,
#                ImageZone.user_id == user.id
#            ).all():
#                print("deleting zone ", old_zone.zone_id)
#                db.session.delete(old_zone)
#            db.session.commit()
#            """
#
#            """
#                Insert the new annotations
#            """
#            print("posting new image zones")
#            for anno in data:
#                print("posting anno", anno)
#                user_id = user.id
#                # teacher and admin MAY post/put/delete for others
#                if (user.is_teacher or user.is_admin) and "username" in anno:
#                    usr = current_app.get_user_from_username(anno["username"])
#                    if usr is not None:
#                        user_id = usr.id
#                elif "username" in anno:
#                    usr = current_app.get_user_from_username(anno["username"])
#                    if usr is not None and usr.id != user.id:
#                        db.session.rollback()
#                        response = APIResponseFactory.make_response(errors={
#                            "status": 403, "title": "Access forbidden", "details": "Cannot insert data"
#                        })
#                        break
#
#                if "zone_id" not in anno:
#                    # it's a new zone, let's get it a new zone_id
#                    try:
#                        img_zone_max_zone_id = db.session.query(func.max(ImageZone.zone_id)).filter(
#                            ImageZone.manifest_url == manifest_url,
#                            ImageZone.img_idx == img_idx,
#                            ImageZone.canvas_idx == canvas_idx,
#                            ImageZone.user_id == user.id
#                        ).group_by(
#                            ImageZone.manifest_url, ImageZone.canvas_idx, ImageZone.img_idx, ImageZone.user_id
#                        ).one()
#                        zone_id = img_zone_max_zone_id[0] + 1
#                    except (NoResultFound, IndexError):
#                        # it is the first zone for this image in this manifest
#                        zone_id = 1
#                else:
#                    zone_id = anno["zone_id"]
#
#                # INSERT data but dont commit yet
#                img_zone = ImageZone(
#                    manifest_url=manifest_url,
#                    canvas_idx=canvas_idx,
#                    img_idx=img_idx,
#                    note=anno["content"],
#                    coords=anno["coords"],
#                    zone_id=zone_id,
#                    zone_type_id=anno["zone_type_id"],
#                    user_id=user_id
#                )
#
#                db.session.add(img_zone)
#                new_img_zones.append(img_zone)
#
#        if response is None:
#            try:
#                db.session.commit()
#            except Exception as e:
#                db.session.rollback()
#                response = APIResponseFactory.make_response(errors={
#                    "status": 403, "title": "Cannot insert data", "details": str(e)
#                })
#
#        if response is None:
#            response = APIResponseFactory.make_response(data=[z.serialize() for z in new_img_zones])
#
#    return APIResponseFactory.jsonify(response)
#
#
##@api_bp.route("/api/<api_version>/documents/<doc_id>/annotations", methods=["PUT"])
##@jwt_required
##def api_put_documents_annotations(api_version, doc_id):
##    """
##        {
##            "data" : [{
##                "canvas_idx" : 0,
##                "img_idx" : 0,
##                "zone_id" : 32,
##                "coords" : "10,40,500,50",
##                "content": "Je suis une première annotation avec <b>du markup</b>",
##                "zone_type_id" : 1,
##                "username": "Eleve1"    (optionnal)
##            },
##        ...
##            },
##            {
##                "canvas_idx" : 0,
##                "img_idx" : 0,
##                "zone_id" : 30,
##                "coords" : "30,40,500,50",
##                "content": "Je suis une n-ième annotation avec <b>du markup</b>",
##                "zone_type_id" : 1,
##                "username": "Professeur1"    (optionnal)
##            }]
##        }
##    :param api_version:
##    :param doc_id:
##    :param zone_id:
##    :return: the updated annotations
##    """
##
##    data = request.get_json()
##    response = None
##
##    if "data" in data:
##        data = data["data"]
##
##        if not isinstance(data, list):
##            data = [data]
##
##        # find which zones to update
##        img_zones = []
##        user = current_app.get_current_user()
##        if user.is_anonymous:
##            response = APIResponseFactory.make_response(errors={
##                "status": 403, "title": "Access forbidden", "details": "Cannot update data"
##            })
##        else:
##            for anno in data:
##
##                user_id = user.id
##                # teacher and admin MAY post/put/delete for others
##                if (user.is_teacher or user.is_admin) and "username" in anno:
##                    usr = current_app.get_user_from_username(anno["username"])
##                    if usr is not None:
##                        user_id = usr.id
##                elif "username" in anno:
##                    usr = current_app.get_user_from_username(anno["username"])
##                    if usr is not None and usr.id != user.id:
##                        response = APIResponseFactory.make_response(errors={
##                            "status": 403, "title": "Access forbidden", "details": "Cannot update data"
##                        })
##                        break
##
##                json_obj = query_json_endpoint(
##                    request,
##                    url_for('api_bp.api_documents_manifest_url_origin', api_version=api_version, doc_id=doc_id)
##                )
##                manifest_url = json_obj["data"]['manifest_url']
##
##                try:
##                    img_zone = ImageZone.query.filter(
##                        ImageZone.zone_id == anno["zone_id"],
##                        ImageZone.manifest_url == manifest_url,
##                        ImageZone.img_idx == anno["img_idx"],
##                        ImageZone.canvas_idx == anno["canvas_idx"],
##                        ImageZone.user_id == user_id
##                    ).one()
##                    img_zones.append((user_id, img_zone))
##                except NoResultFound as e:
##                    response = APIResponseFactory.make_response(errors={
##                        "status": 404,
##                        "title": "Image zone {0} not found".format(anno["zone_id"]),
##                        "details": "Cannot update image zone: {0}".format(str(e))
##                    })
##                    break
##
##        if response is None:
##            # update the annotations
##            for i, (user_id, img_zone) in enumerate(img_zones):
##                anno = data[i]
##                img_zone.coords = anno["coords"]
##                img_zone.note = anno["content"]
##                img_zone.zone_type_id = anno["zone_type_id"]
##                db.session.add(img_zone)
##
##            try:
##                db.session.commit()
##            except Exception as e:
##                db.session.rollback()
##                response = APIResponseFactory.make_response(errors={
##                    "status": 403, "title": "Cannot update data", "details": str(e)
##                })
##
##            if response is None:
##                updated_zones = []
##                # perform a GET to retrieve the freshly updated data
##                for user_id, img_zone in img_zones:
##                    json_obj = query_json_endpoint(
##                        request,
##                        url_for(
##                            "api_bp.api_documents_annotations_zone",
##                            api_version=api_version,
##                            doc_id=doc_id,
##                            zone_id=img_zone.zone_id,
##                            user_id=user_id
##                        ),
##                        user=user
##                    )
##                    if "errors" not in json_obj:
##                        updated_zones.append(json_obj)
##
##                response = APIResponseFactory.make_response(data=updated_zones)
##    else:
##        response = APIResponseFactory.make_response(errors={
##            "status": 403, "title": "Cannot update data", "details": "Check your request syntax"
##        })
##
##    return APIResponseFactory.jsonify(response)
#
#
# @api_bp.route("/api/<api_version>/documents/<doc_id>/annotations/from-user/<user_id>", methods=["DELETE"])
# @api_bp.route("/api/<api_version>/documents/<doc_id>/annotations/<canvas_name>/<zone_id>/from-user/<user_id>", methods=["DELETE"])
# @jwt_required
# @forbid_if_nor_teacher_nor_admin
# def api_delete_documents_annotations(api_version, doc_id, user_id, canvas_name=None, zone_id=None):
#    """
#    :param user_id:
#    :param api_version:
#    :param doc_id:
#    :param zone_id:
#    :return:  {"data": {}}
#    """
#
#    response = None
#    user = current_app.get_current_user()
#
#    if not user.is_anonymous:
#        if (not user.is_teacher and not user.is_admin) and int(user_id) != user.id:
#            response = APIResponseFactory.make_response(errors={
#                "status": 403, "title": "Access forbidden"
#            })
#
#    img = Image.query.filter(Image.doc_id == doc_id).first()
#    if zone_id is None:
#        zone_id = ImageZone.zone_id
#
#    canvas_idx = ImageZone.canvas_idx
#    if canvas_name is not None:
#        canvas_idx = get_canvas_idx_from_name(api_version, doc_id, canvas_name)
#
#    try:
#        img_zones = ImageZone.query.filter(
#            ImageZone.zone_id == zone_id,
#            ImageZone.manifest_url == img.manifest_url,
#            ImageZone.user_id == user_id,
#            ImageZone.canvas_idx == canvas_idx
#        ).all()
#
#        for img_zone in img_zones:
#            db.session.delete(img_zone)
#    except NoResultFound as e:
#        response = APIResponseFactory.make_response(errors={
#            "status": 404,
#            "title": "Image zone not found".format(zone_id),
#            "details": "Cannot delete image zone: {0}".format(str(e))
#        })
#
#    if response is None:
#        try:
#            db.session.commit()
#        except Exception as e:
#            response = APIResponseFactory.make_response(errors={
#                "status": 403, "title": "Cannot delete data", "details": str(e)
#            })
#
#        # the DELETE is OK, respond with no data
#        if response is None:
#            response = APIResponseFactory.make_response()
#
#    return APIResponseFactory.jsonify(response)
#

@api_bp.route("/api/<api_version>/documents/<doc_id>/images")
def api_documents_images(api_version, doc_id):
    images = Image.query.filter(Image.doc_id == doc_id).all()

    response = APIResponseFactory.make_response(data=[img.serialize() for img in images])

    return APIResponseFactory.jsonify(response)


# @api_bp.route("/api/<api_version>/documents/<doc_id>/images", methods=["POST"])
# @jwt_required
# @forbid_if_nor_teacher_nor_admin
# def api_post_documents_images(api_version, doc_id):
#    """
#    {
#        "data" : {
#            "manifest_url" : "http://my.manifests/man1.json",
#            "canvas_idx": 0,
#            "img_idx": 0,
#        }
#    }
#    :param api_version:
#    :param doc_id:
#    :return:
#    """
#    response = None
#
#    user = current_app.get_current_user()
#    if user.is_anonymous or not (user.is_teacher or user.is_admin):
#        response = APIResponseFactory.make_response(errors={
#            "status": 403, "title": "Access forbidden"
#        })
#
#    if response is None:
#        data = request.get_json()
#        data = data["data"]
#
#        if not isinstance(data, list):
#            data = [data]
#
#        new_images = []
#        try:
#            for img_data in data:
#                new_img = Image(manifest_url=img_data["manifest_url"],
#                                canvas_idx=img_data["canvas_idx"],
#                                img_idx=img_data["img_idx"],
#                                doc_id=doc_id)
#                db.session.add(new_img)
#
#                json_obj = query_json_endpoint(
#                    request,
#                    url_for('api_bp.api_documents_first_sequence', api_version=api_version, doc_id=doc_id)
#                )
#                canvas = json_obj["data"]["canvases"][img_data["canvas_idx"]]
#                img_url = canvas["images"][img_data["img_idx"]]["@id"]
#                new_img_url = Image(manifest_url=img_data["manifest_url"],
#                                canvas_idx=img_data["canvas_idx"],
#                                img_idx=img_data["img_idx"],
#                                img_url=img_url)
#                db.session.add(new_img_url)
#
#                new_images.append(new_img)
#        except KeyError:
#            response = APIResponseFactory.make_response(errors={
#                "status": 403, "title": "Insert forbidden", "details": "Data is malformed"
#            })
#            db.session.rollback()
#        except ValueError as e:
#            response = APIResponseFactory.make_response(errors={
#                "status": 403, "title": "Insert forbidden", "details": str(e)
#            })
#            db.session.rollback()
#
#        if response is None:
#            try:
#                db.session.commit()
#            except Exception as e:
#                response = APIResponseFactory.make_response(errors={
#                    "status": 403, "title": "Cannot insert data", "details": str(e)
#                })
#
#            if response is None:
#                images_after = query_json_endpoint(
#                    request,
#                    url_for("api_bp.api_documents_images", api_version=api_version, doc_id=doc_id)
#                )
#
#                response = APIResponseFactory.make_response(data=images_after["data"])
#
#    return APIResponseFactory.jsonify(response)
#
#
# @api_bp.route("/api/<api_version>/documents/<doc_id>/images", methods=['DELETE'])
# @jwt_required
# @forbid_if_nor_teacher_nor_admin
# def api_delete_documents_images(api_version, doc_id):
#    response = None
#
#    user = current_app.get_current_user()
#    if user.is_anonymous or not (user.is_teacher or user.is_admin):
#        response = APIResponseFactory.make_response(errors={
#            "status": 403, "title": "Access forbidden"
#        })
#
#    if response is None:
#
#        images = Image.query.filter(Image.doc_id == doc_id).all()
#        for img in images:
#            db.session.delete(img)
#
#        try:
#            db.session.commit()
#            response = APIResponseFactory.make_response()
#        except Exception as e:
#            response = APIResponseFactory.make_response(errors={
#                "status": 403, "title": "Cannot delete data", "details": str(e)
#            })
#
#    return APIResponseFactory.jsonify(response)
#

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


# @api_bp.route("/api/<api_version>/documents/<doc_id>/annotations/<canvas_name>/fragments/from-user/<user_id>")
# @api_bp.route("/api/<api_version>/documents/<doc_id>/annotations/<canvas_name>/fragments/<zone_id>/from-user/<user_id>")
# def api_documents_annotation_image_fragments(api_version, doc_id, canvas_name, zone_id=None, user_id=None):
#    """
#    Fragment urls points to the IIIF Image API url of the area of an image
#    :param api_version:
#    :param doc_id:
#    :param zone_id:
#    :param user_id:
#    :return: return a list of fragments (zone_id, coords, fragment_url) indexed by their img_id in a dict
#    """
#
#    json_obj = query_json_endpoint(
#        request,
#        url_for('api_bp.api_documents_manifest_url_origin', api_version=api_version, doc_id=doc_id)
#    )
#
#    if "errors" in json_obj:
#        response = APIResponseFactory.make_response(errors=json_obj["errors"])
#    else:
#        manifest_url = json_obj["data"]["manifest_url"]
#        if zone_id is None:
#            zone_id = ImageZone.zone_id
#        zones = ImageZone.query.filter(
#            ImageZone.zone_id == zone_id,
#            ImageZone.manifest_url == manifest_url,
#            ImageZone.user_id == user_id,
#            ImageZone.canvas_idx == get_canvas_idx_from_name(api_version, doc_id, canvas_name)
#        ).all()
#
#        frag_urls = []
#
#        for zone in zones:
#            img = ImageUrl.query.filter(
#                ImageUrl.manifest_url == zone.manifest_url,
#                ImageUrl.canvas_idx == zone.canvas_idx,
#                ImageUrl.img_idx == zone.img_idx
#            ).first()
#
#            root_img_url = img.img_url[:img.img_url.index('/full')]
#            json_obj = query_json_endpoint(request, "%s/info.json" % root_img_url, direct=True)
#
#            coords = [math.floor(float(c)) for c in zone.coords.split(',')]
#            x, y, w, h = get_bbox(coords, max_width=int(json_obj['width']), max_height=int(json_obj['height']))
#
#            if x >= 0 and y >= 0:
#                url = "%s/%i,%i,%i,%i/full/0/default.jpg" % (root_img_url, x, y, w, h)
#                frag_urls.append({
#                    'zone': zone.serialize(),
#                    'fragment_url': url,
#                    'coords': coords,
#                    'bbox_coords':  [x, y, w, h]})
#
#        response = APIResponseFactory.make_response(data={"fragments": frag_urls})
#
#    return APIResponseFactory.jsonify(response)
#

@api_bp.route("/api/<api_version>/annotation-types")
def api_annotations_types(api_version):
    return make_200([t.serialize() for t in ImageZoneType.query.all()])
