from flask import request
from flask_jwt_extended import jwt_required

from app import api_bp
from app.models import Document
from app.utils import make_200


@api_bp.route('/api/<api_version>/dashboard/document-management', methods=['GET'])
@jwt_required
def api_get_dashboard_manage_documents(api_version):
    page_number = request.args.get('num-page', 1)
    page_size = request.args.get('page-size', 50)
    total = Document.query.count()
    docs = Document.query.paginate(int(page_number), int(page_size), max_per_page=100, error_out=False).items

    return make_200(data={"total": total, "documents": [
        {
            "id": d.id, "title": d.title, "pressmark": d.pressmark,
            "user-id": d.user_id, "whitelist-id": d.whitelist_id,
            "is-published": d.is_published,
            "validation": d.validation_flags,
            "exist": d.exist_flags,
            "thumbnail-url": d.images[0].url if len(d.images) > 0 else None
        } for d in docs
    ]})
