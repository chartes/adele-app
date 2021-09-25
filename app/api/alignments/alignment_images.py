from flask import current_app, request

from app import db
from app.api.transcriptions.routes import get_reference_transcription
from app.models import AlignmentImage, Image, Transcription, Document
from app.utils import make_200, make_404,  make_400,  forbid_if_not_in_whitelist


##@api_bp.route('/api/<api_version>/documents/<doc_id>/annotations')
#def api_documents_get_annotations(api_version, doc_id):
#    """
#    :param api_version:
#    :param doc_id:
#    :param user_id:
#    :return:
#    """
#    transcription = get_reference_transcription(doc_id)
#
#    if transcription is None:
#        return make_404()
#
#    alignments = AlignmentImage.query.filter(
#        AlignmentImage.transcription_id == transcription.id,
#        AlignmentImage.user_id == transcription.user_id
#    ).all()
#
#    return make_200(data=[al.serialize() for al in alignments])
#
#
##@api_bp.route('/api/<api_version>/documents/<doc_id>/annotations', methods=['POST'])
##@jwt_required
##@forbid_if_nor_teacher_nor_admin
#def api_post_documents_transcriptions_alignments_images(api_version, doc_id):
#    """
#        {
#            "data": {
#                "annotations" : [
#                    {
#                        "canvas_idx" : 0,
#                        "img_idx" : 1,
#                        "zone_id" : 1,
#                        "ptr_transcription_start": 1,
#                        "ptr_transcription_end": 20
#                    },
#                ]
#            }
#        }
#
#        :param api_version:
#        :param doc_id:
#        :return:
#        """
#    transcription = get_reference_transcription(doc_id)
#
#    if transcription is None:
#        return make_404()
#
#    created_data = []
#    data = request.get_json()
#    if "data" in data and "annotations" in data["data"]:
#        data = data["data"]
#
#        alignments = data["annotations"]
#
#        try:
#            manifest_url = Image.query.filter(Image.doc_id == doc_id).first().manifest_url
#
#            # TRUNCATE
#            for old_al in AlignmentImage.query.filter(
#                AlignmentImage.transcription_id == transcription.id,
#                AlignmentImage.user_id == transcription.user_id,
#                AlignmentImage.manifest_url == manifest_url
#            ).all():
#                print("delete alignment image:", old_al)
#                db.session.delete(old_al)
#
#            # INSERT
#            for new_al in alignments:
#                new_al = AlignmentImage(
#                    transcription_id=transcription.id,
#                    user_id=transcription.user_id,
#                    manifest_url=manifest_url,
#                    img_idx=new_al["img_idx"],
#                    canvas_idx=new_al["canvas_idx"],
#                    zone_id=new_al["zone_id"],
#                    ptr_transcription_start=new_al["ptr_transcription_start"],
#                    ptr_transcription_end=new_al["ptr_transcription_end"]
#                )
#                print("alignment data:", new_al.serialize())
#                db.session.add(new_al)
#                created_data.append(new_al)
#                print("new image zone alignement created")
#
#            db.session.commit()
#        except Exception as e:
#            db.session.rollback()
#            print(str(e))
#            return make_400(details=str(e))
#    else:
#        return make_400(details="Wrong data")
#
#    return make_200([d.serialize() for d in created_data])
#
#
##@api_bp.route('/api/<api_version>/documents/<doc_id>/annotations/<anno_id>', methods=['PUT'])
##@jwt_required
##@forbid_if_nor_teacher_nor_admin
#def api_put_documents_transcriptions_alignments_images(api_version, doc_id):
#    """
#        {
#            "data": {
#                "annotations" : [
#                    {
#                        "canvas_idx" : 0,
#                        "img_idx" : 1,
#                        "zone_id" : 1,
#                        "ptr_transcription_start": 1,
#                        "ptr_transcription_end": 20
#                    },
#                ]
#            }
#        }
#
#        :param api_version:
#        :param doc_id:
#        :return:
#        """
#    transcription = get_reference_transcription(doc_id)
#
#    if transcription is None:
#        return make_404()
#
#    created_data = []
#    data = request.get_json()
#    if "data" in data and "annotations" in data["data"]:
#        data = data["data"]
#
#        alignments = data["annotations"]
#
#        try:
#            manifest_url = Image.query.filter(Image.doc_id == doc_id).first().manifest_url
#
#            # TRUNCATE
#            for old_al in AlignmentImage.query.filter(
#                    AlignmentImage.transcription_id == transcription.id,
#                    AlignmentImage.user_id == transcription.user_id,
#                    AlignmentImage.manifest_url == manifest_url
#            ).all():
#                print("delete alignment image:", old_al)
#                db.session.delete(old_al)
#
#            # INSERT
#            for new_al in alignments:
#                new_al = AlignmentImage(
#                    transcription_id=transcription.id,
#                    user_id=transcription.user_id,
#                    manifest_url=manifest_url,
#                    img_idx=new_al["img_idx"],
#                    canvas_idx=new_al["canvas_idx"],
#                    zone_id=new_al["zone_id"],
#                    ptr_transcription_start=new_al["ptr_transcription_start"],
#                    ptr_transcription_end=new_al["ptr_transcription_end"]
#                )
#                print("alignment data:", new_al.serialize())
#                db.session.add(new_al)
#                created_data.append(new_al)
#                print("new image zone alignement created")
#
#            db.session.commit()
#        except Exception as e:
#            db.session.rollback()
#            print(str(e))
#            return make_400(details=str(e))
#    else:
#        return make_400(details="Wrong data")
#
#    return make_200([d.serialize() for d in created_data])


#@api_bp.route('/api/<api_version>/documents/<doc_id>/annotations/<anno_id>', methods=['DELETE'])
#@jwt_required
#@forbid_if_nor_teacher_nor_admin
def api_delete_documents_transcriptions_alignments_images(api_version, doc_id, anno_id):
    """
    :param api_version:
    :param doc_id:
    :param user_id:
    :return:
    """
    transcription = get_reference_transcription(doc_id)

    if transcription is None:
        return make_404()

    manifest_url = Image.query.filter(Image.doc_id == doc_id).first().manifest_url

    alignments = AlignmentImage.query.filter(
        AlignmentImage.transcription_id == transcription.id,
        AlignmentImage.user_id == transcription.user_id,
        AlignmentImage.manifest_url == manifest_url,
        AlignmentImage.zone_id == anno_id
    ).all()

    if len(alignments) > 0:
        try:
            for al in alignments:
                db.session.delete(al)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(str(e))
            return make_400(str(e))

    return make_200()


def clone_alignment_image(doc_id, old_user_id, user_id):
    old_tr = Transcription.query.filter(Transcription.user_id == old_user_id,
                                        Transcription.doc_id == doc_id).first()

    new_tr = Transcription.query.filter(Transcription.user_id == user_id,
                                        Transcription.doc_id == doc_id).first()

    if not old_tr or not new_tr:
        return make_404()

    is_not_allowed = forbid_if_not_in_whitelist(current_app, Document.query.filter(Document.id == doc_id).first())
    if is_not_allowed:
        return is_not_allowed

    old_alignments = AlignmentImage.query.filter(
        AlignmentImage.transcription_id == old_tr.id,
        AlignmentImage.user_id == old_user_id
    ).all()

    new_alignments = [
        AlignmentImage(
            transcription_id=new_tr.id,
            user_id=user_id,
            zone_id=ol.zone_id,
            manifest_url=ol.manifest_url,
            canvas_idx=ol.canvas_idx,
            img_idx=ol.img_idx,
            ptr_transcription_start=ol.ptr_transcription_start,
            ptr_transcription_end=ol.ptr_transcription_end
        )
        for ol in old_alignments
    ]

    db.session.bulk_save_objects(new_alignments)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(str(e))
        return make_400(str(e))

    return make_200()
