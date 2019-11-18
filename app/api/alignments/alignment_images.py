from flask import current_app
from sqlalchemy.orm.exc import NoResultFound

from app import auth, api_bp, APIResponseFactory, db
from app.api.transcriptions.routes import get_reference_transcription
from models import AlignmentImage


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/alignments/images')
@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/alignments/images/from-user/<user_id>')
def api_documents_transcriptions_alignments_images(api_version, doc_id, user_id=None):
    """
    If user_id is None: get the reference translation (if any) to find the alignment
    :param api_version:
    :param doc_id:
    :param user_id:
    :return:
    """
    user = current_app.get_current_user()
    response = None

    transcription = get_reference_transcription(doc_id)

    if transcription is None:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Reference transcription not found"
        })

    else:
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

            if user.is_anonymous:
                user_id = transcription.user_id

            if user_id is None:
                if not (user.is_teacher or user.is_admin):
                    user_id = user.id
                else:
                    user_id = AlignmentImage.user_id
            else:
                user_id = int(user_id)

            alignments = AlignmentImage.query.filter(
                AlignmentImage.transcription_id == transcription.id,
                AlignmentImage.user_id == user_id
            ).all()

            response = APIResponseFactory.make_response(data=[al.serialize() for al in alignments])

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/alignments/images/reference')
def api_documents_transcriptions_alignments_images_reference(api_version, doc_id):
    """
    :param api_version:
    :param doc_id:
    :param user_id:
    :return:
    """
    response = None
    transcription = get_reference_transcription(doc_id)

    if transcription is None:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Reference transcription not found"
        })

    if response is None:
        alignments = AlignmentImage.query.filter(
            AlignmentImage.transcription_id == transcription.id,
            AlignmentImage.user_id == transcription.user_id
        ).all()

        response = APIResponseFactory.make_response(data=[al.serialize() for al in alignments])

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/alignments/images', methods=['POST'])
@auth.login_required
def api_post_documents_transcriptions_alignments_images(api_version, doc_id):
    """
        {
            "data": {
                "username" : "Eleve1",
                "alignments" : [
                    {
                        "canvas_idx" : 0,
                        "img_idx" : 1,
                        "zone_id" : 1,
                        "ptr_start": 1,
                        "ptr_end": 20
                    },
                    {
                        "canvas_idx" : 0,
                        "img_idx" : 1,
                        "zone_id" : 2,
                        "ptr_start": 21,
                        "ptr_end": 450
                    }
                ]
            }
        }

        :param api_version:
        :param doc_id:
        :return:
        """
    response = None

    transcription = get_reference_transcription(doc_id)

    if transcription is None:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Reference transcription not found"
        })
    else:
        if response is None:
            data = request.get_json()
            if "data" in data and "alignments" in data["data"]:
                data = data["data"]

                user = current_app.get_current_user()
                user_id = user.id

                if not (user.is_teacher or user.is_admin) and "username" in data and data["username"] != user.username:
                    response = APIResponseFactory.make_response(errors={
                        "status": 403, "title": "Access forbidden"
                    })

                if response is None:
                    # teachers and admins can put/post/delete on others behalf
                    if (user.is_teacher or user.is_admin) and "username" in data:
                        user = current_app.get_user_from_username(data["username"])
                        if user is not None:
                            user_id = user.id

                    # let's make the new alignments from the data
                    if response is None:

                        json_obj = query_json_endpoint(
                            request,
                            url_for('api_bp.api_documents_manifest_url_origin', api_version=api_version, doc_id=doc_id)
                        )
                        manifest_url = json_obj["data"]['manifest_url']

                        if not isinstance(data["alignments"], list):
                            alignments = [data["alignments"]]
                        else:
                            alignments = data["alignments"]

                        if response is None:
                            try:
                                # DELETE the old data
                                for old_al in AlignmentImage.query.filter(
                                        AlignmentImage.transcription_id == transcription.id,
                                        AlignmentImage.user_id == int(user_id),
                                        AlignmentImage.canvas_idx.in_(
                                            set([int(alignment["canvas_idx"]) for alignment in alignments]))
                                ).all():
                                    print("delete alignment image:", old_al)
                                    db.session.delete(old_al)

                                db.session.commit()
                                for alignment in alignments:
                                    print("alignment data:", alignment)
                                    zone = ImageZone.query.filter(
                                        ImageZone.zone_id == int(alignment["zone_id"]),
                                        ImageZone.manifest_url == manifest_url,
                                        ImageZone.user_id == int(user_id),
                                        ImageZone.img_idx == int(alignment["img_idx"]),
                                        ImageZone.canvas_idx == int(alignment["canvas_idx"]),
                                    ).one()
                                    print("image zone to align:", zone)
                                    new_al = AlignmentImage(
                                        transcription_id=transcription.id,
                                        user_id=user_id,
                                        manifest_url=manifest_url,
                                        img_idx=alignment["img_idx"],
                                        canvas_idx=alignment["canvas_idx"],
                                        zone_id=zone.zone_id,
                                        ptr_transcription_start=alignment["ptr_start"],
                                        ptr_transcription_end=alignment["ptr_end"]
                                    )
                                    db.session.add(new_al)
                                    print("new image zone alignement created")

                                db.session.commit()
                            except Exception as e:
                                db.session.rollback()
                                response = APIResponseFactory.make_response(errors={
                                    "status": 403, "title": "Cannot insert data", "details": str(e)
                                })
                                print(str(e))

                            if response is None:
                                json_obj = query_json_endpoint(
                                    request,
                                    url_for(
                                        "api_bp.api_documents_transcriptions_alignments_images",
                                        api_version=api_version,
                                        doc_id=doc_id,
                                        user_id=user_id
                                    ),
                                    user=user
                                )
                                if "data" in json_obj:
                                    response = APIResponseFactory.make_response(data=json_obj["data"])
                                else:
                                    response = APIResponseFactory.make_response(data=json_obj["errors"])

        else:
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Data is malformed"
            })

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/alignments/images/from-user/<user_id>',
              methods=['DELETE'])
@auth.login_required
def api_delete_documents_transcriptions_alignments_images(api_version, doc_id, user_id=None):
    """
    :param api_version:
    :param doc_id:
    :param user_id:
    :return:
    """
    response = None
    user = current_app.get_current_user()
    if user.is_anonymous or (not (user.is_teacher or user.is_admin) and int(user_id) != user.id):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })

    if response is None:
        transcription = get_reference_transcription(doc_id)
        if transcription is None:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "Reference transcription not found"
            })

        if response is None:
            try:
                alignments = AlignmentImage.query.filter(
                    AlignmentImage.transcription_id == transcription.id,
                    AlignmentImage.user_id == user_id
                ).all()

                for al in alignments:
                    db.session.delete(al)

            except NoResultFound as e:
                response = APIResponseFactory.make_response(errors={
                    "status": 404, "title": str(e)
                })
                db.session.rollback()

            if response is None:
                try:
                    db.session.commit()
                    response = APIResponseFactory.make_response()
                except Exception as e:
                    db.session.rollback()
                    response = APIResponseFactory.make_response(errors={
                        "status": 403, "title": "Cannot delete data", "details": str(e)
                    })

    return APIResponseFactory.jsonify(response)
