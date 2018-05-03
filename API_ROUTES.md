/api/<api_version>/acte-types {'DELETE', 'PUT', 'GET', 'HEAD', 'OPTIONS', 'POST'}
/api/<api_version>/acte-types/<acte_type_id> {'DELETE', 'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/alignments/translation/<transcription_id>/<translation_id> {'HEAD', 'OPTIONS', 'GET'}
/api/<api_version>/commentary-types {'DELETE', 'PUT', 'GET', 'HEAD', 'OPTIONS', 'POST'}
/api/<api_version>/commentary-types/<commentary_type_id> {'DELETE', 'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/countries {'DELETE', 'PUT', 'GET', 'HEAD', 'OPTIONS', 'POST'}
/api/<api_version>/countries/<country_id> {'DELETE', 'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/districts {'DELETE', 'PUT', 'GET', 'HEAD', 'OPTIONS', 'POST'}
/api/<api_version>/districts/<district_id> {'DELETE', 'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/districts/from-country/<country_id> {'DELETE', 'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents {'PUT', 'GET', 'HEAD', 'OPTIONS', 'POST'}
/api/<api_version>/documents/<doc_id> {'DELETE', 'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/annotations {'PUT', 'GET', 'HEAD', 'OPTIONS', 'POST'}
/api/<api_version>/documents/<doc_id>/annotations/<zone_id> {'HEAD', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/annotations/<zone_id>/from-user/<user_id> {'DELETE', 'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/annotations/from-user/<user_id> {'OPTIONS', 'DELETE'}
/api/<api_version>/documents/<doc_id>/annotations/from-user/<user_id>/list {'HEAD', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/annotations/list {'HEAD', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/commentaries {'DELETE', 'PUT', 'GET', 'HEAD', 'OPTIONS', 'POST'}
/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id> {'DELETE', 'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id>/and-type/<type_id> {'DELETE', 'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/commentaries/notes {'PUT', 'GET', 'HEAD', 'OPTIONS', 'POST'}
/api/<api_version>/documents/<doc_id>/commentaries/notes/<note_id> {'HEAD', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/commentaries/notes/<note_id>/from-user/<user_id> {'OPTIONS', 'DELETE'}
/api/<api_version>/documents/<doc_id>/commentaries/notes/from-user/<user_id> {'DELETE', 'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/commentaries/of-type/<type_id> {'DELETE', 'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/commentaries/reference {'HEAD', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/commentaries/reference/notes {'HEAD', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/commentaries/reference/of-type/<type_id> {'HEAD', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/first-canvas {'HEAD', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/images {'DELETE', 'GET', 'HEAD', 'OPTIONS', 'POST'}
/api/<api_version>/documents/<doc_id>/manifest {'HEAD', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/notes {'HEAD', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/notes/<note_id> {'HEAD', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/notes/from-user/<user_id> {'HEAD', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions {'PUT', 'GET', 'HEAD', 'OPTIONS', 'POST'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments {'GET', 'HEAD', 'OPTIONS', 'POST'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments/discours {'GET', 'HEAD', 'OPTIONS', 'POST'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments/discours/from-user/<user_id> {'DELETE', 'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments/discours/reference {'HEAD', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments/from-user/<user_id> {'DELETE', 'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments/images {'GET', 'HEAD', 'OPTIONS', 'POST'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments/images/from-user/<user_id> {'DELETE', 'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments/images/reference {'HEAD', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments/reference {'HEAD', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/from-user/<user_id> {'DELETE', 'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/transcriptions/from-user/<user_id>/list {'HEAD', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/list {'HEAD', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/notes {'PUT', 'GET', 'HEAD', 'OPTIONS', 'POST'}
/api/<api_version>/documents/<doc_id>/transcriptions/notes/<note_id> {'HEAD', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/notes/<note_id>/from-user/<user_id> {'OPTIONS', 'DELETE'}
/api/<api_version>/documents/<doc_id>/transcriptions/notes/from-user/<user_id> {'DELETE', 'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/transcriptions/reference {'HEAD', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/reference/notes {'HEAD', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/users {'HEAD', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/translations {'PUT', 'GET', 'HEAD', 'OPTIONS', 'POST'}
/api/<api_version>/documents/<doc_id>/translations/from-user/<user_id> {'DELETE', 'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/translations/notes {'PUT', 'GET', 'HEAD', 'OPTIONS', 'POST'}
/api/<api_version>/documents/<doc_id>/translations/notes/<note_id> {'HEAD', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/translations/notes/<note_id>/from-user/<user_id> {'OPTIONS', 'DELETE'}
/api/<api_version>/documents/<doc_id>/translations/notes/from-user/<user_id> {'DELETE', 'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/translations/reference {'HEAD', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/translations/reference/notes {'HEAD', 'OPTIONS', 'GET'}
/api/<api_version>/documents/<doc_id>/translations/users {'HEAD', 'OPTIONS', 'GET'}
/api/<api_version>/editors {'DELETE', 'PUT', 'GET', 'HEAD', 'OPTIONS', 'POST'}
/api/<api_version>/editors/<editor_id> {'DELETE', 'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/institutions {'DELETE', 'PUT', 'GET', 'HEAD', 'OPTIONS', 'POST'}
/api/<api_version>/institutions/<institution_id> {'DELETE', 'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/languages {'DELETE', 'PUT', 'GET', 'HEAD', 'OPTIONS', 'POST'}
/api/<api_version>/languages/<language_code> {'DELETE', 'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/note-types {'HEAD', 'OPTIONS', 'GET'}
/api/<api_version>/notes {'HEAD', 'OPTIONS', 'POST', 'GET'}
/api/<api_version>/speech-part-types {'DELETE', 'PUT', 'GET', 'HEAD', 'OPTIONS', 'POST'}
/api/<api_version>/speech-part-types/<speech_part_type_id> {'DELETE', 'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/test/auth/<doc_id> {'POST', 'OPTIONS', 'DELETE'}
/api/<api_version>/traditions {'DELETE', 'PUT', 'GET', 'HEAD', 'OPTIONS', 'POST'}
/api/<api_version>/traditions/<tradition_id> {'DELETE', 'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/user {'HEAD', 'OPTIONS', 'GET'}
/api/<api_version>/users/<user_id> {'DELETE', 'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/users/<user_id>/roles {'DELETE', 'GET', 'HEAD', 'OPTIONS', 'POST'}
/api/user-role {'HEAD', 'OPTIONS', 'GET'}
