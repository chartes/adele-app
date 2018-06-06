/api/<api_version>/acte-types {'HEAD', 'DELETE', 'PUT', 'POST', 'OPTIONS', 'GET'}
/api/<api_version>/acte-types/<acte_type_id> {'HEAD', 'DELETE', 'OPTIONS', 'GET'}
/api/<api_version>/alignments/translation/<transcription_id>/<translation_id> {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/commentary-types {'HEAD', 'DELETE', 'PUT', 'POST', 'OPTIONS', 'GET'}
/api/<api_version>/commentary-types/<commentary_type_id> {'HEAD', 'DELETE', 'OPTIONS', 'GET'}
/api/<api_version>/countries {'HEAD', 'DELETE', 'PUT', 'POST', 'OPTIONS', 'GET'}
/api/<api_version>/countries/<country_id> {'HEAD', 'DELETE', 'OPTIONS', 'GET'}
/api/<api_version>/districts {'HEAD', 'DELETE', 'PUT', 'POST', 'OPTIONS', 'GET'}
/api/<api_version>/districts/<district_id> {'HEAD', 'DELETE', 'OPTIONS', 'GET'}
/api/<api_version>/districts/from-country/<country_id> {'HEAD', 'DELETE', 'OPTIONS', 'GET'}
/api/<api_version>/documents {'HEAD', 'PUT', 'POST', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id> {'HEAD', 'DELETE', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/annotations {'HEAD', 'PUT', 'POST', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/annotations/<zone_id> {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/annotations/<zone_id>/from-user/<user_id> {'HEAD', 'DELETE', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/annotations/from-user/<user_id> {'DELETE', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/annotations/from-user/<user_id>/list {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/annotations/list {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/commentaries {'HEAD', 'DELETE', 'PUT', 'POST', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id> {'HEAD', 'DELETE', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id>/and-type/<type_id> {'HEAD', 'DELETE', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/commentaries/notes {'HEAD', 'PUT', 'POST', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/commentaries/notes/<note_id> {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/commentaries/notes/<note_id>/from-user/<user_id> {'DELETE', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/commentaries/notes/from-user/<user_id> {'HEAD', 'DELETE', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/commentaries/of-type/<type_id> {'HEAD', 'DELETE', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/commentaries/reference {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/commentaries/reference/notes {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/commentaries/reference/of-type/<type_id> {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/first-canvas {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/images {'HEAD', 'DELETE', 'POST', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/manifest {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/notes {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/notes/<note_id> {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/notes/from-user/<user_id> {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions {'HEAD', 'PUT', 'POST', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments {'HEAD', 'POST', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments/discours {'HEAD', 'POST', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments/discours/from-user/<user_id> {'HEAD', 'DELETE', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments/discours/reference {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments/from-user/<user_id> {'HEAD', 'DELETE', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments/images {'HEAD', 'POST', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments/images/from-user/<user_id> {'HEAD', 'DELETE', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments/images/reference {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments/reference {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/from-user/<user_id> {'HEAD', 'DELETE', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/from-user/<user_id>/list {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/list {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/notes {'HEAD', 'PUT', 'POST', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/notes/<note_id> {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/notes/<note_id>/from-user/<user_id> {'DELETE', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/transcriptions/notes/from-user/<user_id> {'HEAD', 'DELETE', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/reference {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/reference/notes {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/users {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/translations {'HEAD', 'PUT', 'POST', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/translations/from-user/<user_id> {'HEAD', 'DELETE', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/translations/notes {'HEAD', 'PUT', 'POST', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/translations/notes/<note_id> {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/translations/notes/<note_id>/from-user/<user_id> {'DELETE', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/translations/notes/from-user/<user_id> {'HEAD', 'DELETE', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/translations/reference {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/translations/reference/notes {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/translations/users {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/editors {'HEAD', 'DELETE', 'PUT', 'POST', 'OPTIONS', 'GET'}
/api/<api_version>/editors/<editor_id> {'HEAD', 'DELETE', 'OPTIONS', 'GET'}
/api/<api_version>/institutions {'HEAD', 'DELETE', 'PUT', 'POST', 'OPTIONS', 'GET'}
/api/<api_version>/institutions/<institution_id> {'HEAD', 'DELETE', 'OPTIONS', 'GET'}
/api/<api_version>/languages {'HEAD', 'DELETE', 'PUT', 'POST', 'OPTIONS', 'GET'}
/api/<api_version>/languages/<language_code> {'HEAD', 'DELETE', 'OPTIONS', 'GET'}
/api/<api_version>/note-types {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/notes {'POST', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/speech-part-types {'HEAD', 'DELETE', 'PUT', 'POST', 'OPTIONS', 'GET'}
/api/<api_version>/speech-part-types/<speech_part_type_id> {'HEAD', 'DELETE', 'OPTIONS', 'GET'}
/api/<api_version>/test/auth/<doc_id> {'DELETE', 'POST', 'OPTIONS'}
/api/<api_version>/token {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/traditions {'HEAD', 'DELETE', 'PUT', 'POST', 'OPTIONS', 'GET'}
/api/<api_version>/traditions/<tradition_id> {'HEAD', 'DELETE', 'OPTIONS', 'GET'}
/api/<api_version>/user {'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/users/<user_id> {'HEAD', 'DELETE', 'OPTIONS', 'GET'}
/api/<api_version>/users/<user_id>/roles {'HEAD', 'DELETE', 'POST', 'OPTIONS', 'GET'}
/api/user-role {'OPTIONS', 'HEAD', 'GET'}
