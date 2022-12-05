import base64
import json
import sys

from flask_user import roles_required
from urllib.request import build_opener
from app import api_bp
from flask import request, current_app

from app.api.response import APIResponseFactory



if sys.version_info < (3, 6):
    json_loads = lambda s: json_loads(s.decode("utf-8")) if isinstance(s, bytes) else json.loads(s)
else:
    json_loads = json.loads


#def query_json_endpoint(request_obj, endpoint_url, user=None, method='GET', headers_arg=None, direct=False):
#    if direct:
#        url = endpoint_url
#    else:
#        root_url = request_obj.url_root[0:request.url_root.rfind(current_app.config["APP_URL_PREFIX"])]
#        url = "{root}{endpoint}".format(root=root_url, endpoint=endpoint_url)
#
#    headers = {'Content-Type': 'application/json;charset=UTF-8'}
#
#    if headers_arg is not None:
#        headers.update(headers_arg)
#
#    if user is not None and not user.is_anonymous:
#        base64string = base64.b64encode(bytes('%s:%s' % (user.username, user.password), "utf-8"))
#        headers['Authorization'] = "Basic %s" % base64string.decode("ascii")
#
#    try:
#        if method == 'GET':
#            op = build_opener()
#            op.addheaders = [(k, v) for k, v in headers.items()]
#
#            if current_app.config["ENV"] == "test" and not direct:
#                resp = current_app.test_server.get(url)
#                data = resp.data
#            else:
#                data = op.open(url, timeout=15).read()
#        else:
#            raise NotImplementedError
#        response = json_loads(data)
#
#    except Exception as e:
#        response = APIResponseFactory.make_response(status=403,
#                                                    errors={
#            "title": "Error : cannot {0} {1} | {2}".format(method, endpoint_url, headers),
#            "details": str(e)
#        })
#
#    return response
#

"""
===========================
    Import routes 
===========================
"""

from app.api.acte_types import routes
from app.api.commentaries import routes
from app.api.commentary_types import routes
from app.api.countries import routes
from app.api.districts import routes
from app.api.documents import routes
from app.api.editors import routes
from app.api.iiif import routes
from app.api.institutions import routes
from app.api.languages import routes
#from app.api.notes import routes
from app.api.speech_part_types import routes
from app.api.speech_parts import routes
from app.api.traditions import routes
from app.api.transcriptions import routes
from app.api.translations import routes
from app.api.users import routes

from app.api.alignments import alignments_translation
from app.api.alignments import alignment_images

from app.api.auth import login
