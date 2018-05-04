/api/<api_version>/acte-types {'POST', 'DELETE', 'PUT', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/acte-types/<acte_type_id> {'DELETE', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/alignments/translation/<transcription_id>/<translation_id> {'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/commentary-types {'POST', 'DELETE', 'PUT', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/commentary-types/<commentary_type_id> {'DELETE', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/countries {'POST', 'DELETE', 'PUT', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/countries/<country_id> {'DELETE', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/districts {'POST', 'DELETE', 'PUT', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/districts/<district_id> {'DELETE', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/districts/from-country/<country_id> {'DELETE', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents {'POST', 'PUT', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id> {'DELETE', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/annotations {'POST', 'PUT', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/annotations/<zone_id> {'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/annotations/<zone_id>/from-user/<user_id> {'DELETE', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/annotations/from-user/<user_id> {'DELETE', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/annotations/from-user/<user_id>/list {'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/annotations/list {'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/commentaries {'POST', 'DELETE', 'PUT', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id> {'DELETE', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id>/and-type/<type_id> {'DELETE', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/commentaries/notes {'POST', 'PUT', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/commentaries/notes/<note_id> {'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/commentaries/notes/<note_id>/from-user/<user_id> {'DELETE', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/commentaries/notes/from-user/<user_id> {'DELETE', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/commentaries/of-type/<type_id> {'DELETE', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/commentaries/reference {'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/commentaries/reference/notes {'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/commentaries/reference/of-type/<type_id> {'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/first-canvas {'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/images {'POST', 'DELETE', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/manifest {'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/notes {'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/notes/<note_id> {'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/notes/from-user/<user_id> {'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/transcriptions {'POST', 'PUT', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments {'POST', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments/discours {'POST', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments/discours/from-user/<user_id> {'DELETE', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments/discours/reference {'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments/from-user/<user_id> {'DELETE', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments/images {'POST', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments/images/from-user/<user_id> {'DELETE', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments/images/reference {'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments/reference {'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/transcriptions/from-user/<user_id> {'DELETE', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/from-user/<user_id>/list {'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/transcriptions/list {'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/transcriptions/notes {'POST', 'PUT', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/notes/<note_id> {'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/transcriptions/notes/<note_id>/from-user/<user_id> {'DELETE', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/transcriptions/notes/from-user/<user_id> {'DELETE', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/transcriptions/reference {'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/transcriptions/reference/notes {'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/transcriptions/users {'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/translations {'POST', 'PUT', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/translations/from-user/<user_id> {'DELETE', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/translations/notes {'POST', 'PUT', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/translations/notes/<note_id> {'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/translations/notes/<note_id>/from-user/<user_id> {'DELETE', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/translations/notes/from-user/<user_id> {'DELETE', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/documents/<doc_id>/translations/reference {'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/translations/reference/notes {'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/translations/users {'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/editors {'POST', 'DELETE', 'PUT', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/editors/<editor_id> {'DELETE', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/institutions {'POST', 'DELETE', 'PUT', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/institutions/<institution_id> {'DELETE', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/languages {'POST', 'DELETE', 'PUT', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/languages/<language_code> {'DELETE', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/note-types {'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/notes {'POST', 'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/speech-part-types {'POST', 'DELETE', 'PUT', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/speech-part-types/<speech_part_type_id> {'DELETE', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/test/auth/<doc_id> {'POST', 'DELETE', 'OPTIONS'}
/api/<api_version>/token {'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/traditions {'POST', 'DELETE', 'PUT', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/traditions/<tradition_id> {'DELETE', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/user {'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/users/<user_id> {'DELETE', 'OPTIONS', 'HEAD', 'GET'}
/api/<api_version>/users/<user_id>/roles {'POST', 'DELETE', 'OPTIONS', 'HEAD', 'GET'}
/api/user-role {'GET', 'HEAD', 'OPTIONS'}
