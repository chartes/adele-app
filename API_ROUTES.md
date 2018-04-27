/api/<api_version>/acte-types {'OPTIONS', 'PUT', 'HEAD', 'GET', 'POST', 'DELETE'}
/api/<api_version>/acte-types/<acte_type_id> {'OPTIONS', 'HEAD', 'GET', 'DELETE'}
/api/<api_version>/alignments/translation/<transcription_id>/<translation_id> {'HEAD', 'GET', 'OPTIONS'}
/api/<api_version>/commentary-types {'OPTIONS', 'PUT', 'HEAD', 'GET', 'POST', 'DELETE'}
/api/<api_version>/commentary-types/<commentary_type_id> {'OPTIONS', 'HEAD', 'GET', 'DELETE'}
/api/<api_version>/countries {'OPTIONS', 'PUT', 'HEAD', 'GET', 'POST', 'DELETE'}
/api/<api_version>/countries/<country_id> {'OPTIONS', 'HEAD', 'GET', 'DELETE'}
/api/<api_version>/districts {'OPTIONS', 'PUT', 'HEAD', 'GET', 'POST', 'DELETE'}
/api/<api_version>/districts/<district_id> {'OPTIONS', 'HEAD', 'GET', 'DELETE'}
/api/<api_version>/districts/from-country/<country_id> {'OPTIONS', 'HEAD', 'GET', 'DELETE'}
/api/<api_version>/documents {'OPTIONS', 'HEAD', 'GET', 'POST', 'PUT'}
/api/<api_version>/documents/<doc_id> {'OPTIONS', 'HEAD', 'GET', 'DELETE'}
/api/<api_version>/documents/<doc_id>/annotations {'OPTIONS', 'HEAD', 'GET', 'POST', 'PUT'}
/api/<api_version>/documents/<doc_id>/annotations/<zone_id> {'HEAD', 'GET', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/annotations/<zone_id>/from-user/<user_id> {'OPTIONS', 'HEAD', 'GET', 'DELETE'}
/api/<api_version>/documents/<doc_id>/annotations/from-user/<user_id> {'OPTIONS', 'DELETE'}
/api/<api_version>/documents/<doc_id>/annotations/from-user/<user_id>/list {'HEAD', 'GET', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/annotations/list {'HEAD', 'GET', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/commentaries {'OPTIONS', 'PUT', 'HEAD', 'GET', 'POST', 'DELETE'}
/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id> {'OPTIONS', 'HEAD', 'GET', 'DELETE'}
/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id>/and-type/<type_id> {'OPTIONS', 'HEAD', 'GET', 'DELETE'}
/api/<api_version>/documents/<doc_id>/commentaries/notes {'OPTIONS', 'HEAD', 'GET', 'POST', 'PUT'}
/api/<api_version>/documents/<doc_id>/commentaries/notes/<note_id> {'HEAD', 'GET', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/commentaries/notes/<note_id>/from-user/<user_id> {'OPTIONS', 'DELETE'}
/api/<api_version>/documents/<doc_id>/commentaries/notes/from-user/<user_id> {'OPTIONS', 'HEAD', 'GET', 'DELETE'}
/api/<api_version>/documents/<doc_id>/commentaries/of-type/<type_id> {'OPTIONS', 'HEAD', 'GET', 'DELETE'}
/api/<api_version>/documents/<doc_id>/commentaries/reference {'HEAD', 'GET', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/commentaries/reference/notes {'HEAD', 'GET', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/commentaries/reference/of-type/<type_id> {'HEAD', 'GET', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/first-canvas {'HEAD', 'GET', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/manifest {'HEAD', 'GET', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/notes {'HEAD', 'GET', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/notes/<note_id> {'HEAD', 'GET', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/notes/from-user/<user_id> {'HEAD', 'GET', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/transcriptions {'OPTIONS', 'HEAD', 'GET', 'POST', 'PUT'}
/api/<api_version>/documents/<doc_id>/transcriptions/from-user/<user_id> {'OPTIONS', 'HEAD', 'GET', 'DELETE'}
/api/<api_version>/documents/<doc_id>/transcriptions/from-user/<user_id>/list {'HEAD', 'GET', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/transcriptions/list {'HEAD', 'GET', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/transcriptions/notes {'OPTIONS', 'HEAD', 'GET', 'POST', 'PUT'}
/api/<api_version>/documents/<doc_id>/transcriptions/notes/<note_id> {'HEAD', 'GET', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/transcriptions/notes/<note_id>/from-user/<user_id> {'OPTIONS', 'DELETE'}
/api/<api_version>/documents/<doc_id>/transcriptions/notes/from-user/<user_id> {'OPTIONS', 'HEAD', 'GET', 'DELETE'}
/api/<api_version>/documents/<doc_id>/transcriptions/reference {'HEAD', 'GET', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/transcriptions/reference/notes {'HEAD', 'GET', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/transcriptions/users {'HEAD', 'GET', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/translations {'OPTIONS', 'HEAD', 'GET', 'POST', 'PUT'}
/api/<api_version>/documents/<doc_id>/translations/from-user/<user_id> {'OPTIONS', 'HEAD', 'GET', 'DELETE'}
/api/<api_version>/documents/<doc_id>/translations/notes {'OPTIONS', 'HEAD', 'GET', 'POST', 'PUT'}
/api/<api_version>/documents/<doc_id>/translations/notes/<note_id> {'HEAD', 'GET', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/translations/notes/<note_id>/from-user/<user_id> {'OPTIONS', 'DELETE'}
/api/<api_version>/documents/<doc_id>/translations/notes/from-user/<user_id> {'OPTIONS', 'HEAD', 'GET', 'DELETE'}
/api/<api_version>/documents/<doc_id>/translations/reference {'HEAD', 'GET', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/translations/reference/notes {'HEAD', 'GET', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/translations/users {'HEAD', 'GET', 'OPTIONS'}
/api/<api_version>/editors {'OPTIONS', 'PUT', 'HEAD', 'GET', 'POST', 'DELETE'}
/api/<api_version>/editors/<editor_id> {'OPTIONS', 'HEAD', 'GET', 'DELETE'}
/api/<api_version>/institutions {'OPTIONS', 'PUT', 'HEAD', 'GET', 'POST', 'DELETE'}
/api/<api_version>/institutions/<institution_id> {'OPTIONS', 'HEAD', 'GET', 'DELETE'}
/api/<api_version>/languages {'OPTIONS', 'PUT', 'HEAD', 'GET', 'POST', 'DELETE'}
/api/<api_version>/languages/<language_code> {'OPTIONS', 'HEAD', 'GET', 'DELETE'}
/api/<api_version>/note-types {'HEAD', 'GET', 'OPTIONS'}
/api/<api_version>/notes {'HEAD', 'GET', 'POST', 'OPTIONS'}
/api/<api_version>/speech-part-types {'OPTIONS', 'PUT', 'HEAD', 'GET', 'POST', 'DELETE'}
/api/<api_version>/speech-part-types/<speech_part_type_id> {'OPTIONS', 'HEAD', 'GET', 'DELETE'}
/api/<api_version>/test/auth/<doc_id> {'POST', 'OPTIONS', 'DELETE'}
/api/<api_version>/traditions {'OPTIONS', 'PUT', 'HEAD', 'GET', 'POST', 'DELETE'}
/api/<api_version>/traditions/<tradition_id> {'OPTIONS', 'HEAD', 'GET', 'DELETE'}
/api/<api_version>/user {'HEAD', 'GET', 'OPTIONS'}
/api/<api_version>/users/<user_id> {'HEAD', 'GET', 'OPTIONS'}
/api/user-role {'HEAD', 'GET', 'OPTIONS'}
