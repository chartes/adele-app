from bs4 import BeautifulSoup
from flask import url_for, request, current_app
from flask_jwt_extended import jwt_required
from sqlalchemy.orm.exc import NoResultFound
from urllib.request import  urlopen

from app import db
from app.api.iiif.open_annotation import make_annotation, make_annotation_list, make_annotation_layer
from app.api.routes import json_loads, api_bp
from app.api.transcriptions.routes import get_reference_transcription
from app.models import AlignmentImage, ImageZone, Image, ImageZoneType, Document
from app.utils import make_404, make_200, make_400, forbid_if_nor_teacher_nor_admin, make_201

"""
===========================
    Manifest
===========================
"""


def make_manifest(api_version, doc_id):
    img = Image.query.filter(Image.doc_id == doc_id).first()
    if img is None:
        return {}

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
                "@id": request.host_url[:-1] + url_for("api_bp.api_documents_annotations_list_by_canvas",
                                                       motivation="commenting", canvas_idx=canvas_idx, **kwargs),
                "@type": "sc:AnnotationList",
                "within": {
                    "@type": "sc:Layer",
                    "@id": request.host_url[:-1] + url_for("api_bp.api_documents_annotations_layer",
                                                           motivation="commenting", **kwargs),
                    "label": "commenting"
                }
            },
            #{
            #    "@id": request.host_url[:-1] + url_for("api_bp.api_documents_annotations_list_by_canvas",
            #                                           motivation="describing", canvas_idx=canvas_idx, **kwargs),
            #    "@type": "sc:AnnotationList",
            #    "within": {
            #        "@type": "sc:Layer",
            #        "@id": request.host_url[:-1] + url_for("api_bp.api_documents_annotations_layer",
            #                                               motivation="describing", **kwargs),
            #        "label": "describing"
            #    }
            #}
        ])

    return data


@api_bp.route('/api/<api_version>/iiif/<doc_id>/manifest')
def api_documents_manifest(api_version, doc_id):
    try:
        manifest = make_manifest(api_version, doc_id)
        manifest["@id"] = request.base_url
        return manifest
    except Exception as e:
        return make_400(str(e))


@api_bp.route('/api/<api_version>/iiif/<doc_id>/manifest/origin')
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


@api_bp.route("/api/<api_version>/iiif/<doc_id>/layer/<motivation>")
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
    return layer


@api_bp.route("/api/<api_version>/iiif/<doc_id>/list/<motivation>-<canvas_idx>")
def api_documents_annotations_list_by_canvas(api_version, doc_id, motivation, canvas_idx):
    """
    """
    user = current_app.get_current_user()
    doc = Document.query.filter(Document.id == doc_id).first()

    if user.is_anonymous and doc.is_published is False:
        annotation_list = make_annotation_list(request.base_url, [])
        return annotation_list

    try:
        manifest = make_manifest(api_version, doc_id)
        sequence = manifest["sequences"][0]
        canvas = sequence["canvases"][int(canvas_idx)]

        annotations = []
        img = Image.query.filter(Image.doc_id == doc_id).first()
        img = Image.query.filter(Image.manifest_url == img.manifest_url, Image.doc_id == doc_id,
                                 Image.canvas_idx == canvas_idx).first()

        # TODO s'il y a plusieurs images dans un seul et même canvas ?
        #img_json = canvas["images"][0]
        kwargs = {
            "doc_id": doc_id,
            "api_version": api_version
        }

        manifest_url = current_app.with_url_prefix(
            url_for("api_bp.api_documents_manifest", api_version=1.0, doc_id=doc_id))

        for img_zone in [zone for zone in img.zones]:
            kwargs["zone_id"] = img_zone.zone_id
            res_uri = current_app.with_url_prefix(url_for("api_bp.api_documents_annotations", **kwargs))

            print(img_zone, img_zone.zone_type.label)
            if img_zone.zone_type.label == "describing":
                from app.api.transcriptions.routes import get_reference_transcription
                tr = get_reference_transcription(doc_id)
                if tr is None:
                    annotation_list = make_annotation_list(request.base_url, [])
                    return annotation_list

                img_al = AlignmentImage.query.filter(
                    AlignmentImage.transcription_id == tr.id,
                    AlignmentImage.manifest_url == img_zone.manifest_url,
                    AlignmentImage.canvas_idx == img_zone.canvas_idx,
                    AlignmentImage.img_idx == img_zone.img_idx,
                    AlignmentImage.zone_id == img_zone.zone_id
                ).first()

                # is there a text segment bound to this image zone?
                if img_al is not None:
                    parsed_content = BeautifulSoup(tr.content, "html.parser")
                    note_nodes = parsed_content.find_all(
                        "adele-annotation",
                        {
                            "manifest-url": img_al.manifest_url,
                            "img-idx": str(img_al.img_idx),
                            "zone-id": str(img_al.zone_id),
                            "canvas-idx": str(img_al.canvas_idx),
                        }
                    )
                    text_content = ""
                    for node in note_nodes:
                        text_content += str(node)
                else:
                    text_content = ""

            else:
                text_content = img_zone.note

            new_annotation = make_annotation(
                manifest_url,
                canvas["@id"],
                img_zone.fragment,
                img_zone.svg,
                res_uri,
                content=text_content,
                format="text/html"
            )
            annotations.append(new_annotation)
        annotation_list = make_annotation_list(request.base_url, annotations)
        return annotation_list

    except Exception as e:
        print(str(e))
        return make_400(str(e))


@api_bp.route("/api/<api_version>/iiif/<doc_id>/annotation/<zone_id>")
def api_documents_annotations(api_version, doc_id, zone_id):
    """

    :param canvas_name:
    :param api_version:
    :param doc_id:
    :param zone_id:
    :return:
    """

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
            parsed_content = BeautifulSoup(tr.content, "html.parser")
            try:
                img_al = AlignmentImage.query.filter(
                    AlignmentImage.transcription_id == tr.id,
                    AlignmentImage.zone_id == img_zone.zone_id,
                    AlignmentImage.user_id == tr.user_id,
                    AlignmentImage.manifest_url == img.manifest_url
                ).one()
                note_nodes = parsed_content.find_all(
                    "adele-annotation",
                    {
                        "manifest-url": img_al.manifest_url,
                        "img-idx": str(img_al.img_idx),
                        "zone-id": str(img_al.zone_id),
                        "canvas-idx": str(img_al.canvas_idx),
                    }
                )
                if not note_nodes:
                    return make_404(details="This annotation does not exist on this transcription".format(doc_id))
                note_content = ""
                for note in note_nodes:
                    note_content += str(note)
            except NoResultFound:
                return make_404(details="This transcription zone has no text fragment attached to it".format(doc_id))
        # else it is a mere image note
        else:
            note_content = img_zone.note

        # TODO: gerer erreur si pas d'image dans le canvas
        canvas = sequence["canvases"][img_zone.canvas_idx]
        img_json = canvas["images"][img_zone.img_idx]
        url = current_app.with_url_prefix(url_for("api_bp.api_documents_manifest", api_version=1.0, doc_id=doc_id))
        new_annotation = make_annotation(
            url,
            canvas["@id"],
            img_json.get('fragment', None),
            img_json.get('svg', None),
            res_uri,
            note_content,
            format="text/html"
        )
        return new_annotation

    except Exception as e:
        print(str(e))
        return make_400(str(e))


@api_bp.route("/api/<api_version>/iiif/<doc_id>/annotations", methods=['POST'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_documents_post_annotation(api_version, doc_id):
    """
    expected format:

    {
        "manifest_url": "https://../manifest20.json",
        "canvas_idx": 0,
        // In case there are multiple images on a canvas, optionnal, default is 0
        "img_idx": 0,
        "zone_type_id": 2,

        "fragment": "620,128,788,159",  // FragmentSelector
        "svg": "<svg ...>"              // SvgSelector

        // in case of a COMMENTING motivation, the text content is embedded within the annotation,
        // optionnal, default is none
        "note": "Ceci est une majuscule"

        // in case of a DESCRIBING motivation, the text content is a segment of the transcription
    }

    :param api_version:
    :param doc_id:
    :return:
    """
    data = request.get_json()

    try:
        doc = Document.query.filter(Document.id == doc_id).first()

        url = data['manifest_url']
        canvas_idx = data['canvas_idx']
        doc_id = doc.id
        img_idx = data.get('img_idx', 0)

        note = data.get('note', None)
        zone_type_id = data['zone_type_id']

        if note is not None and zone_type_id == 1:
            raise Exception('ambiguous annotation type')

        # test if the image is in db first
        if Image.query.filter(
                Image.manifest_url == url,
                Image.canvas_idx == canvas_idx,
                Image.doc_id == doc_id,
                Image.img_idx == img_idx
        ).first() is None:
            raise Exception('image unknown: %s', [url, canvas_idx, doc_id, img_idx])

        # compute relative zone id
        last_zone = ImageZone.query.filter(
            ImageZone.manifest_url == url,
            ImageZone.canvas_idx == canvas_idx,
            ImageZone.img_idx == img_idx
        ).order_by(ImageZone.zone_id.desc()).first()

        if last_zone is None:
            new_zone_id = 1
        else:
            new_zone_id = int(last_zone.zone_id) + 1

        new_anno = ImageZone(
            zone_id=new_zone_id,
            manifest_url=url,
            canvas_idx=canvas_idx,
            img_idx=img_idx,
            user_id=doc.user_id,
            zone_type_id=zone_type_id,
            svg=data.get('svg', None),
            fragment=data.get('fragment', None),
            note=note
        )
        db.session.add(new_anno)

        if zone_type_id == 1:
            tr = get_reference_transcription(doc_id)
            if tr is None:
                raise Exception('There is no reference transcription use in this annotation')

            new_al = AlignmentImage(
                transcription_id=tr.id,
                user_id=doc.user_id,
                zone_id=new_zone_id,
                manifest_url=url,
                canvas_idx=canvas_idx,
                img_idx=img_idx,
            )

            db.session.add(new_al)

        db.session.commit()
    except Exception as e:
        print(data, str(e))
        db.session.rollback()
        return make_400(details="Cannot build this new annotation: %s" % str(e))

    return make_201(data=new_anno.serialize())

@api_bp.route("/api/<api_version>/iiif/<doc_id>/annotation/<zone_id>", methods=['PUT'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_documents_put_annotation(api_version, doc_id, zone_id):
    """
    expected format:

    {
        "manifest_url": "https://../manifest20.json",
        "canvas_idx": 0,
        // In case there are multiple images on a canvas, optionnal, default is 0
        "img_idx": 0,
        "zone_type_id": 2,
        "fragment': "620,128,788,159",
        "svg': "620,128,788,159, ...",

        // in case of a COMMENTING motivation, the text content is embedded within the annotation,
        // optionnal, default is none
        "note": "Ceci est une majuscule"

        // in case of a DESCRIBING motivation, the text content is a segment of the transcription
    }

    :param api_version:
    :param doc_id:
    :return:
    """
    data = request.get_json()

    try:
        doc = Document.query.filter(Document.id == doc_id).first()

        url = data['manifest_url']
        canvas_idx = data['canvas_idx']
        doc_id = doc.id
        img_idx = data.get('img_idx', 0)

        note = data.get('note', None)
        zone_type_id = data['zone_type_id']

        if note is not None and zone_type_id == 1:
            raise Exception('ambiguous annotation type')

        img_zone = ImageZone.query.with_for_update(nowait=True).filter(
            ImageZone.zone_id == zone_id,
            ImageZone.manifest_url == url,
            ImageZone.canvas_idx == canvas_idx,
            ImageZone.img_idx == img_idx,
            ImageZone.user_id == doc.user_id
        ).one()

        img_zone.zone_id = int(zone_id)
        img_zone.note = note
        img_zone.zone_type_id = data.get('zone_type_id', 2)
        img_zone.fragment = data.get('fragment', None)
        img_zone.svg = data.get('svg', None)

        db.session.flush()
        #db.session.add(img_zone)

        tr = get_reference_transcription(doc_id)
        if tr is None:
            raise Exception('There is no reference transcription to use in this annotation')

        print('finding existing al')
        al = AlignmentImage.query.filter(
            AlignmentImage.transcription_id == tr.id,
            AlignmentImage.manifest_url == url,
            AlignmentImage.canvas_idx == canvas_idx,
            AlignmentImage.img_idx == img_idx,
            AlignmentImage.zone_id == zone_id
        ).first()

        if zone_type_id == 1:
            if al is None:
                print('new al')
                new_al = AlignmentImage(
                    transcription_id=tr.id,
                    user_id=doc.user_id,
                    zone_id=zone_id,
                    manifest_url=url,
                    canvas_idx=canvas_idx,
                    img_idx=img_idx,
                )
                db.session.add(new_al)
            else:
                print('update al')
                db.session.add(al)
        else:
            # let's check if there is an old al to delete
            if al is not None:
                print("delete old al")
                db.session.delete(al)

        #db.session.add(img_zone)
        db.session.commit()
    except Exception as e:
        print(data, str(e))
        db.session.rollback()
        return make_400(details="Cannot update this annotation: %s" % str(e))

    return make_200(data=img_zone.serialize())


@api_bp.route("/api/<api_version>/iiif/<doc_id>/annotation/<zone_id>", methods=['DELETE'])
@jwt_required
@forbid_if_nor_teacher_nor_admin
def api_documents_delete_annotation(api_version, doc_id, zone_id):
    """
    :param api_version:
    :param doc_id:
    :param zone_id:
    :return:
    """
    try:
        img = Image.query.filter(Image.doc_id == doc_id).first()

        anno_to_delete = ImageZone.query.filter(
            ImageZone.zone_id == zone_id,
            ImageZone.manifest_url == img.manifest_url,
            ImageZone.canvas_idx == img.canvas_idx,
            ImageZone.img_idx == img.img_idx
        ).first()
        print('anno to delete', anno_to_delete)
        if anno_to_delete is None:
            raise Exception('annotation %s not found ' % zone_id)
        tr = get_reference_transcription(doc_id)
        if tr is not None:
            parsed_content = BeautifulSoup(tr.content, "html.parser")
            note_nodes = parsed_content.find_all(
                "adele-annotation",
                {
                    "manifest-url": anno_to_delete.manifest_url,
                    "img-idx": str(anno_to_delete.img_idx),
                    "zone-id": str(anno_to_delete.zone_id),
                    "canvas-idx": str(anno_to_delete.canvas_idx),
                }
            )
            if note_nodes:
                for node in note_nodes:
                    node.replace_with_children()
                tr.content = str(parsed_content)
                db.session.add(tr)
        db.session.delete(anno_to_delete)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_400(details="Cannot delete the annotation %s : %s" % (zone_id, str(e)))

    return make_200()

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

@api_bp.route("/api/<api_version>/annotation-types")
def api_annotations_types(api_version):
    return make_200([t.serialize() for t in ImageZoneType.query.all()])
