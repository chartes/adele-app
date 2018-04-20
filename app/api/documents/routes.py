
from sqlalchemy.orm.exc import NoResultFound

from app.api.response import APIResponseFactory
from app.api.routes import api_bp
from app.models import Document


"""
===========================
    Document
===========================
"""


@api_bp.route('/api/<api_version>/documents/<doc_id>')
def api_documents(api_version, doc_id):
    try:
        doc = Document.query.filter(Document.id == doc_id).one()
        response = APIResponseFactory.make_response(data=doc.serialize())
    except NoResultFound:
        response = APIResponseFactory.make_response(errors={
            "status": 404, "title": "Document {0} not found".format(doc_id)
        })
    return APIResponseFactory.jsonify(response)

