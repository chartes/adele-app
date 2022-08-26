from app import api_bp
from app.models import SpeechParts
from flask_jwt_extended import jwt_required

from app.utils import make_404, make_200


def get_speech_parts(doc_id, user_id):
    print("get speech parts (doc_id, user_id)", doc_id, user_id)
    return SpeechParts.query.filter(
        doc_id == SpeechParts.doc_id,
        user_id == SpeechParts.user_id
    ).first()


@api_bp.route('/api/<api_version>/documents/<doc_id>/speech-parts/from-user/<user_id>')
#@jwt_required
def api_documents_speechparts_from_user(api_version, doc_id, user_id=None):
    #forbid = forbid_if_nor_teacher_nor_admin_and_wants_user_data(current_app, user_id)
    #if forbid:
    #    return forbid
    tr = get_speech_parts(doc_id, user_id)
    if tr is None:
        return make_404()
    return make_200(data=tr.serialize_for_user(user_id))
