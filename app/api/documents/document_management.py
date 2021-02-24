from flask import request, current_app
from flask_jwt_extended import jwt_required
from sqlalchemy import desc, asc, text

from app import api_bp
from app.models import Document
from app.utils import make_200


@api_bp.route('/api/<api_version>/dashboard/document-management', methods=['GET'])
@jwt_required
def api_get_dashboard_manage_documents(api_version):
    page_number = request.args.get('num-page', 1)
    page_size = request.args.get('page-size', 50)

    query = Document.query

    user = current_app.get_current_user()
    if user.is_student and not (user.is_admin or user.is_teacher):
        query = query.filter(Document.whitelist_id.in_([w.id for w in user.whitelists]))
    print(query)

    total = query.count()
    sort = request.args.get('sort-by', None)
    if sort:
        field, order = sort.split('.')
        query = query.order_by(text("%s %s" % (field, "desc" if order == "asc" else "asc")))

    docs = query.paginate(int(page_number), int(page_size), max_per_page=100, error_out=False).items

    return make_200(data={"total": total, "documents": [
        {
            "whitelist": {"id": d.whitelist.id, "label": d.whitelist.label},
            "id": d.id, "title": d.title, "pressmark": d.pressmark,
            "owner": d.user.serialize(),
            "is-published": d.is_published,
            "is-closed": d.is_closed,
            "validation": d.validation_flags,
            "exist": d.exist_flags,
            "thumbnail-url": d.images[0].url if len(d.images) > 0 else None
        } for d in docs
    ]})
