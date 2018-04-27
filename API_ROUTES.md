/api/<api_version>/acte-types {'HEAD', 'PUT', 'POST', 'OPTIONS', 'DELETE', 'GET'}
/api/<api_version>/acte-types/<acte_type_id> {'HEAD', 'OPTIONS', 'DELETE', 'GET'}
/api/<api_version>/alignments/translation/<transcription_id>/<translation_id> {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/countries {'HEAD', 'PUT', 'POST', 'OPTIONS', 'DELETE', 'GET'}
/api/<api_version>/countries/<country_id> {'HEAD', 'OPTIONS', 'DELETE', 'GET'}
/api/<api_version>/documents {'HEAD', 'PUT', 'POST', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id> {'HEAD', 'OPTIONS', 'DELETE', 'GET'}
/api/<api_version>/documents/<doc_id>/annotations {'HEAD', 'PUT', 'POST', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/annotations/<zone_id> {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/annotations/<zone_id>/from-user/<user_id> {'HEAD', 'OPTIONS', 'DELETE', 'GET'}
/api/<api_version>/documents/<doc_id>/annotations/from-user/<user_id> {'OPTIONS', 'DELETE'}
/api/<api_version>/documents/<doc_id>/annotations/from-user/<user_id>/list {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/annotations/list {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/commentaries/notes {'HEAD', 'PUT', 'POST', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/commentaries/notes/<note_id> {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/commentaries/notes/<note_id>/from-user/<user_id> {'OPTIONS', 'DELETE'}
/api/<api_version>/documents/<doc_id>/commentaries/notes/from-user/<user_id> {'HEAD', 'OPTIONS', 'DELETE', 'GET'}
/api/<api_version>/documents/<doc_id>/commentaries/reference/notes {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/first-canvas {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/manifest {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/notes {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/notes/<note_id> {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/notes/from-user/<user_id> {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions {'HEAD', 'PUT', 'POST', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/from-user/<user_id> {'HEAD', 'OPTIONS', 'DELETE', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/from-user/<user_id>/list {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/list {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/notes {'HEAD', 'PUT', 'POST', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/notes/<note_id> {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/notes/<note_id>/from-user/<user_id> {'OPTIONS', 'DELETE'}
/api/<api_version>/documents/<doc_id>/transcriptions/notes/from-user/<user_id> {'HEAD', 'OPTIONS', 'DELETE', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/reference {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/reference/notes {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/users {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/translations {'HEAD', 'PUT', 'POST', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/translations/from-user/<user_id> {'HEAD', 'OPTIONS', 'DELETE', 'GET'}
/api/<api_version>/documents/<doc_id>/translations/notes {'HEAD', 'PUT', 'POST', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/translations/notes/<note_id> {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/translations/notes/<note_id>/from-user/<user_id> {'OPTIONS', 'DELETE'}
/api/<api_version>/documents/<doc_id>/translations/notes/from-user/<user_id> {'HEAD', 'OPTIONS', 'DELETE', 'GET'}
/api/<api_version>/documents/<doc_id>/translations/reference {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/translations/reference/notes {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/translations/users {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/institutions {'HEAD', 'PUT', 'POST', 'OPTIONS', 'DELETE', 'GET'}
/api/<api_version>/institutions/<institution_id> {'HEAD', 'OPTIONS', 'DELETE', 'GET'}
/api/<api_version>/note-types {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/notes {'OPTIONS', 'HEAD', 'POST', 'GET'}
/api/<api_version>/test/auth/<doc_id> {'OPTIONS', 'DELETE', 'POST'}
/api/<api_version>/user {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/users/<user_id> {'OPTIONS', 'HEAD', 'GET'}
/api/user-role {'OPTIONS', 'HEAD', 'GET'}
