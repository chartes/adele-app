from flask import url_for, request, current_app
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound

from app import db, auth
from app.api.documents.document_validation import set_document_validation_step
from app.api.response import APIResponseFactory
from app.api.routes import query_json_endpoint, api_bp
from app.api.translations.routes import get_reference_translation
from app.models import Transcription, User, Document, AlignmentTranslation, Translation, AlignmentDiscours, \
    SpeechPartType, Note, AlignmentImage, ImageZone, TranscriptionHasNote, VALIDATION_TRANSCRIPTION, VALIDATION_NONE
from app.utils import make_404, make_200, forbid_if_nor_teacher_nor_admin_and_wants_user_data, \
    forbid_if_nor_teacher_nor_admin, make_400, forbid_if_another_teacher, make_403, is_closed, forbid_if_validation_step

"""
===========================
    Transcriptions
===========================
"""


def get_transcription(doc_id, user_id):
    return Transcription.query.filter(
        doc_id == Transcription.doc_id,
        user_id == Transcription.user_id
    ).first()


def get_reference_transcription(doc_id):
    """

    :param doc_id:
    :return:
    """
    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is not None and doc.validation_step >= VALIDATION_TRANSCRIPTION:
        return Transcription.query.filter(
            doc_id == Transcription.doc_id,
            doc.user_id == Transcription.user_id
        ).first()

    return None


def get_reference_alignment_discours(doc_id):
    transcription = get_reference_transcription(doc_id)
    if transcription is None:
        return None
    else:
        return AlignmentDiscours.query.filter(
            AlignmentDiscours.transcription_id == transcription.id,
            AlignmentDiscours.user_id == transcription.user_id
        ).all()


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/users')
def api_documents_transcriptions_users(api_version, doc_id):
    users = []
    try:
        transcriptions = Transcription.query.filter(Transcription.doc_id == doc_id).all()
        users = User.query.filter(User.id.in_(set([tr.user_id for tr in transcriptions]))).all()
        users = [{"id": user.id, "username": user.username} for user in users]
    except NoResultFound:
        pass
    return make_200(data=users)


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions')
def api_documents_transcriptions(api_version, doc_id):
    tr = get_reference_transcription(doc_id)
    if tr is None:
        return make_404()
    return make_200(data=tr.serialize_for_user(tr.user_id))


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/from-user/<user_id>')
@auth.login_required
def api_documents_transcriptions_from_user(api_version, doc_id, user_id=None):
    forbid = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
    if forbid:
        return forbid
    tr = get_transcription(doc_id, user_id)
    if tr is None:
        return make_404()
    return make_200(data=tr.serialize_for_user(user_id))


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/from-user/<user_id>', methods=["POST"])
@auth.login_required
def api_post_documents_transcriptions(api_version, doc_id, user_id):
    """
    at least one of "content" or "notes" is required
    "notes" when there is no tr in base is forbidden so
    you can in a first time post "content" and later "notes", or both at the same time

    {
        "data":
            {
                "content" :  "My first transcription"
                "notes": [
                        {
                           "content": "note1 content",
                           "ptr_start": 5,
                           "ptr_end": 7
                       }
                ]
            }
    }
    :param user_id:
    :param api_version:
    :param doc_id:
    :return:
    """
    forbid = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
    if forbid:
        return forbid

    forbid = forbid_if_validation_step(doc_id, gte=VALIDATION_TRANSCRIPTION)
    if forbid:
        return forbid

    forbid = is_closed(doc_id)
    if forbid:
        return forbid

    data = request.get_json()
    if "data" in data:
        data = data["data"]
        try:
            # case 1) "content" in data
            if "content" in data:
                tr = Transcription(doc_id=doc_id, content=data["content"], user_id=user_id)
            # case 2) there's only "notes" in data
            elif "notes" in data:
                tr = Transcription.query.filter(Transcription.doc_id == doc_id,
                                                Transcription.user_id == user_id).first()
                if tr is None:
                    return make_404()
            else:
                return make_400(details="Wrong data")
            # register new notes if any
            if "notes" in data:
                new_notes = [Note(type_id=n.get("type_id", 0), user_id=user_id, content=n["content"])
                             for n in data["notes"]]
                for n in new_notes:
                    db.session.add(n)
                if len(new_notes) > 0:
                    db.session.flush()
                    # bind new notes to the transcription
                    tr.transcription_has_note = [TranscriptionHasNote(transcription_id=tr.id,
                                                                      note_id=n.id,
                                                                      ptr_start=data["notes"][num_note]["ptr_start"],
                                                                      ptr_end=data["notes"][num_note]["ptr_end"])
                                                 for num_note, n in enumerate(new_notes)]

            # save the tr and commit all
            db.session.add(tr)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(str(e))
            return make_400(str(e))

        return make_200(data=tr.serialize_for_user(user_id))
    else:
        return make_400("no data")


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/from-user/<user_id>', methods=["PUT"])
@auth.login_required
@forbid_if_nor_teacher_nor_admin
def api_put_documents_transcriptions(api_version, doc_id, user_id):
    """
     {
         "data":
             {
                 "content" :  "My first transcription"  (mandatory)
             }
     }
     :param user_id:
     :param api_version:
     :param doc_id:
     :return:
     """
    forbid = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
    if forbid:
        return forbid

    # teachers can still update validated transcription
    current_user = current_app.get_current_user()
    if not current_user.is_teacher:
        forbid = forbid_if_validation_step(doc_id, gte=VALIDATION_TRANSCRIPTION)
        if forbid:
            return forbid

    forbid = is_closed(doc_id)
    if forbid:
        return forbid

    data = request.get_json()
    if "data" in data:
        data = data["data"]
        tr = get_transcription(doc_id=doc_id, user_id=user_id)
        if tr is None:
            return make_404()
        try:
            tr.content = data["content"]
            db.session.add(tr)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return make_400(str(e))
        return make_200(data=tr.serialize_for_user(user_id))
    else:
        return make_400("no data")


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/from-user/<user_id>', methods=["DELETE"])
@auth.login_required
def api_delete_documents_transcriptions(api_version, doc_id, user_id):
    forbid = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
    if forbid:
        return forbid

    closed = is_closed(doc_id)
    if closed:
        return closed

    doc = Document.query.filter(Document.id == doc_id).first()
    if doc is None:
        return make_404()

    is_another_teacher = forbid_if_another_teacher(current_app, doc.user_id)
    if is_another_teacher:
        return is_another_teacher

    # forbid students to delete a transcription when there is a valid transcription
    user = current_app.get_current_user()
    if not user.is_teacher:
        forbid = forbid_if_validation_step(doc_id, gte=VALIDATION_TRANSCRIPTION)
        if forbid:
            return forbid

    tr = get_transcription(doc_id=doc_id, user_id=user_id)
    if tr is None:
        return make_404()

    try:
        for thn in tr.transcription_has_note:
            if thn.note.user_id == int(user_id):
                db.session.delete(thn.note)
        db.session.delete(tr)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(str(e))
        return make_400(str(e))

    set_document_validation_step(doc=doc, stage_id=VALIDATION_NONE)

    return make_200()


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/alignments')
@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/alignments/from-user/<user_id>')
def api_documents_transcriptions_alignments(api_version, doc_id, user_id=None):
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
        alignments = []
        if not user.is_anonymous:
            if (not user.is_teacher and not user.is_admin) and user_id is not None and int(user_id) != user.id:
                response = APIResponseFactory.make_response(errors={
                    "status": 403, "title": "Access forbidden"
                })
        elif user_id is not None:
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Access forbidden"
            })
        # pick the reference translation if you are not logged
        if user.is_anonymous:
            translation = get_reference_translation(doc_id)
            alignments = AlignmentTranslation.query.filter(
                AlignmentTranslation.transcription_id == transcription.id,
                AlignmentTranslation.translation_id == translation.id
            ).all()
        else:
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
            else:
                translation = json_obj["data"][0]

                alignments = AlignmentTranslation.query.filter(
                    AlignmentTranslation.transcription_id == transcription.id,
                    AlignmentTranslation.translation_id == translation["id"]
                ).all()

        if response is None:
            ptrs = [(a.ptr_transcription_start, a.ptr_transcription_end,
                     a.ptr_translation_start, a.ptr_translation_end)
                    for a in alignments]

            response = APIResponseFactory.make_response(data=ptrs)

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/alignments/reference')
def api_documents_transcriptions_alignments_reference(api_version, doc_id):
    """
    :param api_version:
    :param doc_id:
    :param user_id:
    :return:
    """
    transcription = get_reference_transcription(doc_id)

    if transcription is None:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Reference transcription not found"
        })
        return APIResponseFactory.jsonify(response)

    translation = get_reference_translation(doc_id)

    if translation is None:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Reference translation not found"
        })
        return APIResponseFactory.jsonify(response)

    alignments = AlignmentTranslation.query.filter(
        AlignmentTranslation.transcription_id == transcription.id,
        AlignmentTranslation.translation_id == translation.id
    ).all()

    ptrs = [
        (a.ptr_transcription_start, a.ptr_transcription_end, a.ptr_translation_start, a.ptr_translation_end)
        for a in alignments
    ]

    response = APIResponseFactory.make_response(data=ptrs)

    return APIResponseFactory.jsonify(response)


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


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/alignments/discours')
@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/alignments/discours/from-user/<user_id>')
def api_documents_transcriptions_alignments_discours(api_version, doc_id, user_id=None):
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
                    user_id = AlignmentDiscours.user_id

            alignments = AlignmentDiscours.query.filter(
                AlignmentDiscours.transcription_id == transcription.id,
                AlignmentDiscours.user_id == user_id
            ).all()

            response = APIResponseFactory.make_response(data=[al.serialize() for al in alignments])

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/alignments/discours', methods=['POST'])
@auth.login_required
def api_post_documents_transcriptions_alignments_discours(api_version, doc_id):
    """
        {
            "data": {
                "username" : "Eleve1",
                "speech_parts" : [
                    {
                        "type_id" : 1,
                        "ptr_start": 1,
                        "ptr_end": 20,
                        "note": "aaa"
                    },
                    {
                        "type_id" : 2,
                        "ptr_start": 21,
                        "ptr_end": 450,
                        "note": "bb"
                    }
                ]
            }
        }

        If user_id is None: get the reference translation (if any) to find the alignment
        :param api_version:
        :param doc_id:
        :return:
        """
    response = None
    data = request.get_json()
    if "data" in data and "speech_parts" in data["data"]:
        data = data["data"]

        user = current_app.get_current_user()

        if user.is_anonymous or (not (user.is_teacher or user.is_admin) and "username" in data and data[
            "username"] != user.username):
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

            # let's make the new alignments from the data
            if response is None:

                transcription = get_reference_transcription(doc_id)
                if transcription is None:
                    transcription = Transcription.query.filter(Transcription.doc_id == doc_id,
                                                               Transcription.user_id == user_id).first()

                if not isinstance(data["speech_parts"], list):
                    data = [data["speech_parts"]]
                else:
                    data = data["speech_parts"]

                # DELETE the old data
                for old_al in AlignmentDiscours.query.filter(
                        AlignmentDiscours.transcription_id == transcription.id,
                        AlignmentDiscours.user_id == user_id
                ).all():
                    db.session.delete(old_al)

                if response is None:
                    try:

                        for speech_part in data:
                            part_type = SpeechPartType.query.filter(
                                SpeechPartType.id == int(speech_part["type_id"])
                            ).one()

                            new_al = AlignmentDiscours(
                                transcription_id=transcription.id,
                                speech_part_type_id=part_type.id,
                                user_id=user_id,
                                ptr_start=speech_part["ptr_start"],
                                ptr_end=speech_part["ptr_end"],
                                note=speech_part.get("note")
                            )
                            db.session.add(new_al)

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
                                "api_bp.api_documents_transcriptions_alignments_discours",
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

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/alignments/discours', methods=['PUT'])
@auth.login_required
def api_put_documents_transcriptions_alignments_discours(api_version, doc_id):
    """
        {
            "data": {
                "id" : 1,
                "username" : "Eleve1",
                "speech_parts" : [
                    {
                        "type_id" : 1,
                        "ptr_start": 1,
                        "ptr_end": 20,
                        "note": "aaa"
                    },
                    {
                        "type_id" : 2,
                        "ptr_start": 21,
                        "ptr_end": 450,
                        "note": "aaa"
                    }
                ]
            }
        }

        If user_id is None: get the reference translation (if any) to find the alignment
        :param api_version:
        :param doc_id:
        :return:
        """
    response = None

    data = request.get_json()
    if "data" in data and "speech_parts" in data["data"]:
        data = data["data"]

        user = current_app.get_current_user()

        if user.is_anonymous or (not (user.is_teacher or user.is_admin) and "username" in data and data[
            "username"] != user.username):
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

            # let's make the new alignments from the data
            if response is None:
                al_id = data.get("id")
                if not isinstance(data["speech_parts"], list):
                    data = [data["speech_parts"]]
                else:
                    data = data["speech_parts"]

                if response is None:
                    try:
                        for speech_part in data:
                            part_type = SpeechPartType.query.filter(
                                SpeechPartType.id == int(speech_part["type_id"])
                            ).one()

                            al = AlignmentDiscours.query.filter(AlignmentDiscours.id == int(al_id)).first()
                            al.ptr_start = speech_part['ptr_start']
                            al.ptr_end = speech_part['ptr_end']
                            al.type_id = part_type.id
                            al.note = speech_part['note']

                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        response = APIResponseFactory.make_response(errors={
                            "status": 403, "title": "Cannot update data", "details": str(e)
                        })

                    if response is None:
                        json_obj = query_json_endpoint(
                            request,
                            url_for(
                                "api_bp.api_documents_transcriptions_alignments_discours",
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

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/alignments/discours/reference')
def api_documents_transcriptions_alignments_discours_reference(api_version, doc_id):
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
        alignments = AlignmentDiscours.query.filter(
            AlignmentDiscours.transcription_id == transcription.id,
            AlignmentDiscours.user_id == transcription.user_id
        ).all()

        response = APIResponseFactory.make_response(data=[al.serialize() for al in alignments])

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/alignments/discours/from-user/<user_id>',
              methods=['DELETE'])
@auth.login_required
def api_delete_documents_transcriptions_alignments_discours(api_version, doc_id, user_id=None):
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
                alignments = AlignmentDiscours.query.filter(
                    AlignmentDiscours.transcription_id == transcription.id,
                    AlignmentDiscours.user_id == user_id
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


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/clone/from-user/<user_id>', methods=['GET'])
@auth.login_required
def api_documents_clone_transcription(api_version, doc_id, user_id=None):
    response = None
    teacher = current_app.get_current_user()
    if teacher.is_anonymous or (not (teacher.is_teacher or teacher.is_admin)):
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })

    print("cloning transcription (doc %s) from user %s" % (doc_id, user_id))

    tr_to_be_cloned = Transcription.query.filter(Transcription.user_id == user_id,
                                                 Transcription.doc_id == doc_id).first()
    if tr_to_be_cloned:
        teacher_tr = Transcription.query.filter(Transcription.user_id == teacher.id,
                                                Transcription.doc_id == doc_id).first()

        if teacher_tr is None:
            teacher_tr = Transcription(doc_id=doc_id, user_id=teacher.id, content=tr_to_be_cloned.content)
        else:
            # replace the teacher's tr content
            teacher_tr.content = tr_to_be_cloned.content
            # remove the old teacher's notes
            for thn in teacher_tr.notes:
                db.session.delete(thn.note)
            teacher_tr.notes = []
        db.session.add(teacher_tr)
        db.session.commit()

        # clone notes
        for thn_to_be_cloned in tr_to_be_cloned.notes:
            note = Note(type_id=thn_to_be_cloned.note.type_id, user_id=teacher.id,
                        content=thn_to_be_cloned.note.content)
            db.session.add(note)
            db.session.flush()
            teacher_tr.notes.append(
                TranscriptionHasNote(ptr_start=thn_to_be_cloned.ptr_start,
                                     ptr_end=thn_to_be_cloned.ptr_end,
                                     note_id=note.id,
                                     transcription_id=teacher_tr.id),
            )

        db.session.add(teacher_tr)
        db.session.commit()

    response = APIResponseFactory.make_response(data=[])
    return APIResponseFactory.jsonify(response)
