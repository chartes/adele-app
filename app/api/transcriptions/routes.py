from flask import url_for, request, redirect, current_app
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound

from app import db, auth
from app.api.response import APIResponseFactory
from app.api.routes import query_json_endpoint, api_bp
from app.api.translations.routes import get_reference_translation
from app.models import Transcription, User, Document, AlignmentTranslation, Translation, AlignmentDiscours, \
    SpeechPartType, Note, AlignmentImage, ImageZone

"""
===========================
    Transcriptions
===========================
"""


def get_reference_transcription(doc_id):
    """

    :param doc_id:
    :return:
    """
    doc = Document.query.filter(Document.id == doc_id).one()
    transcription = Transcription.query.filter(
        doc_id == Transcription.doc_id,
        doc.user_id == Transcription.user_id
    ).first()
    return transcription


def get_reference_alignment_discours(doc_id):
    alignments = []
    transcription = get_reference_transcription(doc_id)
    if transcription is not None:
        alignments = AlignmentDiscours.query.filter(
                AlignmentDiscours.transcription_id == transcription.id,
                AlignmentDiscours.user_id == transcription.user_id
        ).all()
    return alignments


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/reference')
def api_documents_transcriptions_reference(api_version, doc_id):
    tr = get_reference_transcription(doc_id)
    if tr is None:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Transcription not found"
        })
    else:
        # filter notes
        notes = []
        for thn in tr.notes:
            if thn.note.user_id == tr.user_id:
                notes.append(thn)
        tr.notes = notes
        response = APIResponseFactory.make_response(data=tr.serialize())
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/users')
def api_documents_transcriptions_users(api_version, doc_id):
    try:
        transcriptions = Transcription.query.filter(Transcription.doc_id == doc_id).all()
        users = User.query.filter(User.id.in_(set([tr.user_id for tr in transcriptions]))).all()
        users = [{"id": user.id, "username": user.username} for user in users]
    except NoResultFound:
        users = []
    response = APIResponseFactory.make_response(data=users)
    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions')
@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/from-user/<user_id>')
def api_documents_transcriptions(api_version, doc_id, user_id=None):
    response = None
    user = current_app.get_current_user()
    if user.is_anonymous and user_id is not None:
        response = APIResponseFactory.make_response(errors={
            "status": 403, "title": "Access forbidden"
        })
    elif user.is_anonymous:
        tr = get_reference_transcription(doc_id)
        if tr is None:
            response = APIResponseFactory.make_response(errors={
                "status": 404, "title": "Transcription not found"
            })
        else:
            user_id = tr.user_id
    else:
        # user_id is None and user is not None
        if not user.is_teacher and not user.is_admin:
            user_id = user.id

    if response is None:

        if not user.is_anonymous:
            # only teacher and admin can see everything
            if (not user.is_teacher and not user.is_admin) and user_id is not None and int(user_id) != int(user.id):
                response = APIResponseFactory.make_response(errors={
                    "status": 403, "title": "Access forbidden"
                })

        if response is None:
            if user_id is None:
                user_id = Transcription.user_id

            try:
                transcriptions = Transcription.query.filter(
                    Transcription.doc_id == doc_id,
                    Transcription.user_id == user_id
                ).all()

                if len(transcriptions) == 0:
                    raise NoResultFound

                data = []
                for tr in transcriptions:
                    t = tr.serialize()
                    t["notes"] = [n for n in t["notes"] if n["user_id"] == int(user_id)]
                    data.append(t)
                response = APIResponseFactory.make_response(data=data)
            except NoResultFound:
                response = APIResponseFactory.make_response(errors={
                    "status": 404, "title": "Transcription not found"
                })

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions', methods=["POST"])
@auth.login_required
def api_post_documents_transcriptions(api_version, doc_id):
    """
    {
        "data":
            {
                "content" :  "My first transcription",   (mandatory)
                "username":  "Eleve1"                    (optionnal)
            }
    }
    :param api_version:
    :param doc_id:
    :return:
    """
    data = request.get_json()
    response = None
    created_users = set()

    try:
        doc = Document.query.filter(Document.id == doc_id).one()
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Document {0} not found".format(doc_id)
        })

    if "data" in data and response is None:
        data = data["data"]

        if not isinstance(data, list):
            data = [data]

        if response is None:

            for tr in data:
                user = current_app.get_current_user()
                existing_tr = None
                if not user.is_anonymous:
                    user_id = user.id
                    # teachers and admins can put/post/delete on others behalf
                    if (user.is_teacher or user.is_admin) and "username" in tr:
                        user = current_app.get_user_from_username(tr["username"])
                        if user is not None:
                            user_id = user.id

                    # check that there's no transcription yet for this document/user
                    existing_tr = Transcription.query.filter(
                        Transcription.user_id == user_id,
                        Transcription.doc_id == doc_id
                    ).first()

                print("existing tr:", existing_tr, user.is_anonymous)
                if existing_tr is not None or user.is_anonymous:
                    response = APIResponseFactory.make_response(errors={
                        "status": 403,
                        "title": "Insert forbidden",
                    })
                    db.session.rollback()

                if response is None:
                    # get the transcription id max
                    try:
                        transcription_max_id = db.session.query(func.max(Transcription.id)).one()
                        transcription_max_id = transcription_max_id[0] + 1
                    except NoResultFound:
                        # it is the transcription for this user and this document
                        transcription_max_id = 1

                    new_transcription = Transcription(
                        id=transcription_max_id,
                        content=tr["content"],
                        doc_id=doc_id,
                        user_id=user_id
                    )

                    db.session.add(new_transcription)
                    created_users.add(user)

                    if user.is_admin:
                        # create a reference transcription if not exist
                        if Transcription.query.filter(
                                Transcription.user_id == doc.user_id,
                                Transcription.doc_id == doc_id
                        ).first() is None:
                            new_ref_transcription = Transcription(
                                id=transcription_max_id+1,
                                content="<p></p>",
                                doc_id=doc_id,
                                user_id=doc.user_id
                            )
                            db.session.add(new_ref_transcription)

            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                response = APIResponseFactory.make_response(errors={
                    "status": 403, "title": "Cannot insert data", "details": str(e)
                })

            if response is None:
                created_data = []
                for usr in created_users:
                    json_obj = query_json_endpoint(
                        request,
                        url_for(
                            "api_bp.api_documents_transcriptions",
                            api_version=api_version,
                            doc_id=doc_id,
                            user_id=usr.id
                        ),
                        user=usr
                    )
                    if "data" in json_obj:
                        created_data.append(json_obj["data"])
                    elif "errors":
                        created_data.append(json_obj["errors"])

                response = APIResponseFactory.make_response(data=created_data)

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions', methods=["PUT"])
@auth.login_required
def api_put_documents_transcriptions(api_version, doc_id):
    """
    {
        "data": [
            {
                "content" :  "My first transcription",   (mandatory)
                "username":  "Eleve1"                    (optionnal)
            },
            {
                "content" :  "My first transcription",   (mandatory)
                "username":  "Eleve2"                    (optionnal)
            }
        ]
    }
    :param api_version:
    :param doc_id:
    :return:
    """
    data = request.get_json()
    response = None

    try:
        doc = Document.query.filter(Document.id == doc_id).one()
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Document {0} not found".format(doc_id)
        })

    if "data" in data and response is None:
        data = data["data"]

        if not isinstance(data, list):
            data = [data]

        if response is None:

            updated_users = set()
            user = current_app.get_current_user()

            if user.is_anonymous:
                response = APIResponseFactory.make_response(errors={
                    "status": 403, "title": "Access forbidden", "details": "Cannot update data"
                })
            else:
                user_id = user.id

                for tr in data:

                    user = current_app.get_current_user()
                    user_id = user.id

                    # teachers and admins can put/post/delete on others behalf
                    if (user.is_teacher or user.is_admin) and "username" in tr:
                        user = current_app.get_user_from_username(tr["username"])
                        if user is not None:
                            user_id = user.id
                    elif "username" in tr:
                        usr = current_app.get_user_from_username(tr["username"])
                        if usr is not None and usr.id != user.id:
                            db.session.rollback()
                            response = APIResponseFactory.make_response(errors={
                                "status": 403, "title": "Access forbidden", "details": "Cannot update data"
                            })
                            break

                    try:
                        # get the transcription to update
                        transcription = Transcription.query.filter(
                            Transcription.user_id == user_id,
                            Transcription.doc_id == doc_id
                        ).one()

                        transcription.content = tr["content"]
                        db.session.add(transcription)
                        # save which users to retriever later
                        updated_users.add(user)
                    except NoResultFound:
                        response = APIResponseFactory.make_response(errors={
                            "status": 404,
                            "title": "Update forbidden",
                            "details": "Transcription not found"
                        })
                        break

            if response is None:
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    response = APIResponseFactory.make_response(errors={
                        "status": 403, "title": "Cannot update data", "details": str(e)
                    })

            if response is None:
                updated_data = []
                for usr in updated_users:
                    json_obj = query_json_endpoint(
                        request,
                        url_for(
                            "api_bp.api_documents_transcriptions",
                            api_version=api_version,
                            doc_id=doc_id,
                            user_id=user_id
                        ),
                        user=usr
                    )
                    updated_data.append(json_obj["data"])

                response = APIResponseFactory.make_response(data=updated_data)

    return APIResponseFactory.jsonify(response)


@api_bp.route('/api/<api_version>/documents/<doc_id>/transcriptions/from-user/<user_id>', methods=["DELETE"])
@auth.login_required
def api_delete_documents_transcriptions(api_version, doc_id, user_id):
    """
     :param api_version:
     :param doc_id:
     :return:
     """
    response = None

    try:
        doc = Document.query.filter(Document.id == doc_id).one()
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Document {0} not found".format(doc_id)
        })

    user = current_app.get_current_user()
    if not user.is_anonymous:
        if (not user.is_teacher and not user.is_admin) and int(user_id) != user.id:
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Access forbidden"
            })

    # delete transcriptions for the given user id
    if response is None:
        try:
            # bring the transcription to delete
            transcription = Transcription.query.filter(
                Transcription.user_id == user_id,
                Transcription.doc_id == doc_id
            ).one()
            db.session.delete(transcription)
        except NoResultFound:
            pass

        if response is None:
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                response = APIResponseFactory.make_response(errors={
                    "status": 403, "title": "Cannot delete data", "details": str(e)
                })

        if response is None:
            response = APIResponseFactory.make_response(data=[])

    return APIResponseFactory.jsonify(response)


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
                    if not (user.is_teacher or user.is_admin) and "username" in data and data["username"] != user.username:
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

    transcription = get_reference_transcription(doc_id)

    if transcription is None:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Reference transcription not found"
        })
    else:
        if response is None:
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
        else:
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Data is malformed"
            })
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

    transcription = get_reference_transcription(doc_id)

    if transcription is None:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Reference transcription not found"
        })
    else:
        if response is None:
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
        else:
            response = APIResponseFactory.make_response(errors={
                "status": 403, "title": "Data is malformed"
            })
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
                                        AlignmentImage.canvas_idx.in_(set([int(alignment["canvas_idx"]) for alignment in alignments]))
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
