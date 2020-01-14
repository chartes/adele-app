from flask import request, current_app, url_for
from flask_jwt_extended import jwt_required
from markupsafe import Markup
from sqlalchemy.orm.exc import NoResultFound

from app import api_bp, auth, APIResponseFactory, db
from app.api.alignments.alignments_translation import add_notes_refs
from app.api.routes import query_json_endpoint
from app.api.transcriptions.routes import get_reference_transcription, get_transcription, add_notes_refs_to_text
from app.models import SpeechPartType, AlignmentDiscours
from app.utils import make_404, forbid_if_nor_teacher_nor_admin_and_wants_user_data, make_200


@api_bp.route('/api/<api_version>/documents/<doc_id>/speech-parts')
@api_bp.route('/api/<api_version>/documents/<doc_id>/speech-parts/from-user/<user_id>')
def api_documents_transcriptions_alignments_discours(api_version, doc_id, user_id=None):
    """
    If user_id is None: get the reference translation (if any) to find the alignment
    :param api_version:
    :param doc_id:
    :param user_id:
    :return:
    """
    transcription = get_reference_transcription(doc_id)

    if transcription is None:
        return make_404()

    if user_id is None:
        user_id = transcription.user_id
    else:
        forbid = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
        if forbid:
            return forbid

    alignments = AlignmentDiscours.query.filter(
        AlignmentDiscours.transcription_id == transcription.id,
        AlignmentDiscours.user_id == user_id
    ).all()

    if len(alignments) == 0:
        return make_404()

    return make_200(data=[al.serialize() for al in alignments])


def add_speechparts_refs_to_text(text, alignments):
    text_with_notes = text
    # tags to represent notes in view mode
    BTAG = "<span class='speech-part type-{speech_part_type_id:02d}' data-note-id='{note_id:010d}'>"
    ETAG = "</span>"

    notes = [
        {
            "id": al.id,
            "speech_part_type_id": al.speech_part_type.id,
            "ptr_start": al.ptr_start,
            "ptr_end": al.ptr_end,
            "content": al.note
        }
        for al in alignments
    ]

    def _ptr_start(k):
        return k["ptr_start"]

    notes.sort(key=_ptr_start)
    for num_note, note in enumerate(notes):

        btag = BTAG.format(speech_part_type_id=note['speech_part_type_id'], note_id=note["id"])
        len_of_tag = len(btag) + len(ETAG)

        offset = len_of_tag * num_note
        #offset += 3 * num_note  # decalage?
        start_offset = int(note["ptr_start"]) + offset
        end_offset = int(note["ptr_end"]) + offset
        kwargs = {
            "btag": btag,
            "etag": ETAG,
            "text_before": text_with_notes[0:start_offset],
            "text_between": text_with_notes[start_offset:end_offset],
            "text_after": text_with_notes[end_offset:]
        }
        text_with_notes = "{text_before}{btag}{text_between}{etag}{text_after}".format(**kwargs)
    return text_with_notes


@api_bp.route('/api/<api_version>/documents/<doc_id>/view/speech-parts')
@api_bp.route('/api/<api_version>/documents/<doc_id>/view/speech-parts/from-user/<user_id>')
def view_document_speech_parts_alignment(api_version, doc_id, user_id=None):
    tr = get_reference_transcription(doc_id)

    if tr is None:
        return make_404()

    if user_id is None:
        user_id = tr.user_id

    alignments = AlignmentDiscours.query.filter(
        AlignmentDiscours.transcription_id == tr.id,
        AlignmentDiscours.user_id == user_id
    ).all()

    _content = add_speechparts_refs_to_text(tr.content, alignments)

    return make_200({
        "content": Markup(_content) if tr.content is not None else "",
        "notes": {"{:010d}".format(al.id): al.note for al in alignments}
    })


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/alignments/discours', methods=['POST'])
@jwt_required
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
@jwt_required
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
@jwt_required
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

