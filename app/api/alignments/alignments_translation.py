from flask import current_app, request, url_for
from sqlalchemy.orm.exc import NoResultFound

from app import auth, APIResponseFactory, db, api_bp
from app.api.routes import query_json_endpoint
from app.models import AlignmentTranslation, Translation
from app.utils import forbid_if_nor_teacher_nor_admin_and_wants_user_data, make_404, make_200


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/alignments/from-user/<user_id>')
@auth.login_required
def api_get_alignment_translation_from_user(api_version, doc_id, user_id):
    from app.api.transcriptions.routes import get_reference_transcription
    from app.api.translations.routes import get_translation

    forbid = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
    if forbid:
        return forbid

    transcription = get_reference_transcription(doc_id)
    if transcription is None:
        return make_404(details="No transcription available")

    translation = get_translation(doc_id=doc_id, user_id=user_id)
    if translation is None:
        return make_404(details="No translation available")

    alignments = AlignmentTranslation.query.filter(
        AlignmentTranslation.transcription_id == transcription.id,
        AlignmentTranslation.translation_id == translation.id
    ).all()

    ptrs = [(a.ptr_transcription_start, a.ptr_transcription_end,
             a.ptr_translation_start, a.ptr_translation_end)
            for a in alignments]

    return make_200(data=ptrs)


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/alignments')
def api_get_alignment_translation(api_version, doc_id):
    from app.api.transcriptions.routes import get_reference_transcription
    from app.api.translations.routes import get_reference_translation

    transcription = get_reference_transcription(doc_id)
    if transcription is None:
        return make_404(details="No transcription available")

    translation = get_reference_translation(doc_id)
    if translation is None:
        return make_404(details="No translation available")

    alignments = AlignmentTranslation.query.filter(
        AlignmentTranslation.transcription_id == transcription.id,
        AlignmentTranslation.translation_id == translation.id
    ).all()

    ptrs = [(a.ptr_transcription_start, a.ptr_transcription_end,
             a.ptr_translation_start, a.ptr_translation_end)
            for a in alignments]

    return make_200(data=ptrs)


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/alignments/from-user/<user_id>', methods=['DELETE'])
@auth.login_required
def api_delete_documents_transcriptions_alignments(api_version, doc_id, user_id):
    """
        If user_id is None: get the reference translation (if any) to find the alignment
    :param api_version:
    :param doc_id:
    :param user_id:
    :return:
    """
    response = None
    user = current_app.get_current_user()
    if user.is_anonymous or (not user.is_teacher and not user.is_admin) and int(user_id) != user.id:
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })

    if response is None:
        transcription = get_reference_transcription(doc_id)
        if transcription is None:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "Reference transcription not found"
            })

        translation = Translation.query.filter(
            Translation.doc_id == doc_id,
            Translation.user_id == user_id
        ).one()

        if response is None:
            try:
                alignments = AlignmentTranslation.query.filter(
                    AlignmentTranslation.transcription_id == transcription.id,
                    AlignmentTranslation.translation_id == translation.id
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


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/alignments', methods=['POST'])
@auth.login_required
def api_post_documents_transcriptions_alignments(api_version, doc_id):
    """
        {
            "data": {
                "username" : "Eleve1",
                "ptr_list" : [
                    [...],
                    [...]
                ]
            }
        }

        If user_id is None: get the reference translation (if any) to find the alignment
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
    else:
        if response is None:
            data = request.get_json()
            if "data" in data and "ptr_list" in data["data"]:
                data = data["data"]

                user = current_app.get_current_user()
                if user.is_anonymous:
                    response = APIResponseFactory.make_response(errors={
                        "status": 403, "title": "Cannot insert data"
                    })
                else:
                    if not (user.is_teacher or user.is_admin) and "username" in data and data[
                        "username"] != user.username:
                        response = APIResponseFactory.make_response(errors={
                            "status": 403, "title": "Access forbidden"
                        })

                if response is None:
                    user_id = user.id
                    # teachers and admins can put/post/delete on others behalf
                    if (user.is_teacher or user.is_admin) and "username" in data:
                        user = current_app.get_user_from_username(data["username"])
                        if user is not None:
                            user_id = user.id

                    json_obj = query_json_endpoint(
                        request,
                        url_for(
                            "api_bp.api_documents_translations",
                            api_version=api_version,
                            doc_id=doc_id,
                            user_id=user_id
                        ),
                        user=user
                    )

                    if "data" not in json_obj:
                        response = APIResponseFactory.make_response(errors=json_obj["errors"])
                        translation = None
                    else:
                        translation = json_obj["data"][0]

                        # let's make the new alignments from the data
                    if translation is not None and response is None:

                        if not isinstance(data["ptr_list"], list):
                            data = [data["ptr_list"]]
                        else:
                            data = data["ptr_list"]

                        # DELETE the old data
                        for old_al in AlignmentTranslation.query.filter(
                                AlignmentTranslation.transcription_id == transcription.id,
                                AlignmentTranslation.translation_id == translation["id"]
                        ).all():
                            db.session.delete(old_al)

                        if response is None:
                            for (ptr_transcription_start, ptr_transcription_end,
                                 ptr_translation_start, ptr_translation_end) in data:
                                new_al = AlignmentTranslation(
                                    transcription_id=transcription.id, translation_id=translation["id"],
                                    ptr_transcription_start=ptr_transcription_start,
                                    ptr_transcription_end=ptr_transcription_end,
                                    ptr_translation_start=ptr_translation_start,
                                    ptr_translation_end=ptr_translation_end
                                )
                                db.session.add(new_al)

                            try:
                                db.session.commit()
                            except Exception as e:
                                db.session.rollback()
                                response = APIResponseFactory.make_response(errors={
                                    "status": 403, "title": "Cannot insert data", "details": str(e)
                                })

                            if response is None:
                                json_obj = query_json_endpoint(
                                    request,
                                    url_for(
                                        "api_bp.api_documents_transcriptions_alignments",
                                        api_version=api_version,
                                        doc_id=doc_id,
                                        user_id=user_id
                                    ),
                                    user=user
                                )
                                response = APIResponseFactory.make_response(json_obj["data"])
        else:
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Data is malformed"
            })
    return APIResponseFactory.jsonify(response)
