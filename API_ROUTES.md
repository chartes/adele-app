/api/<api_version>/acte-types {'POST', 'GET', 'HEAD', 'OPTIONS', 'DELETE', 'PUT'}
/api/<api_version>/acte-types/<acte_type_id> {'GET', 'HEAD', 'OPTIONS', 'DELETE'}
/api/<api_version>/alignments/translation/<transcription_id>/<translation_id> {'OPTIONS', 'GET', 'HEAD'}
/api/<api_version>/commentary-types {'POST', 'GET', 'HEAD', 'OPTIONS', 'DELETE', 'PUT'}
/api/<api_version>/commentary-types/<commentary_type_id> {'GET', 'HEAD', 'OPTIONS', 'DELETE'}
/api/<api_version>/countries {'POST', 'GET', 'HEAD', 'OPTIONS', 'DELETE', 'PUT'}
/api/<api_version>/countries/<country_id> {'GET', 'HEAD', 'OPTIONS', 'DELETE'}
/api/<api_version>/districts {'POST', 'GET', 'HEAD', 'OPTIONS', 'DELETE', 'PUT'}
/api/<api_version>/districts/<district_id> {'GET', 'HEAD', 'OPTIONS', 'DELETE'}
/api/<api_version>/districts/from-country/<country_id> {'GET', 'HEAD', 'OPTIONS', 'DELETE'}
/api/<api_version>/documents {'POST', 'GET', 'HEAD', 'OPTIONS', 'PUT'}
/api/<api_version>/documents/<doc_id> {'GET', 'HEAD', 'OPTIONS', 'DELETE'}
/api/<api_version>/documents/<doc_id>/annotations {'POST', 'GET', 'HEAD', 'OPTIONS', 'PUT'}
/api/<api_version>/documents/<doc_id>/annotations/<zone_id> {'OPTIONS', 'GET', 'HEAD'}
/api/<api_version>/documents/<doc_id>/annotations/<zone_id>/from-user/<user_id> {'GET', 'HEAD', 'OPTIONS', 'DELETE'}
/api/<api_version>/documents/<doc_id>/annotations/from-user/<user_id> {'OPTIONS', 'DELETE'}
/api/<api_version>/documents/<doc_id>/annotations/from-user/<user_id>/list {'OPTIONS', 'GET', 'HEAD'}
/api/<api_version>/documents/<doc_id>/annotations/list {'OPTIONS', 'GET', 'HEAD'}
/api/<api_version>/documents/<doc_id>/commentaries {'POST', 'GET', 'HEAD', 'OPTIONS', 'DELETE', 'PUT'}
/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id> {'GET', 'HEAD', 'OPTIONS', 'DELETE'}
/api/<api_version>/documents/<doc_id>/commentaries/from-user/<user_id>/and-type/<type_id> {'GET', 'HEAD', 'OPTIONS', 'DELETE'}
/api/<api_version>/documents/<doc_id>/commentaries/notes {'POST', 'GET', 'HEAD', 'OPTIONS', 'PUT'}
/api/<api_version>/documents/<doc_id>/commentaries/notes/<note_id> {'OPTIONS', 'GET', 'HEAD'}
/api/<api_version>/documents/<doc_id>/commentaries/notes/<note_id>/from-user/<user_id> {'OPTIONS', 'DELETE'}
/api/<api_version>/documents/<doc_id>/commentaries/notes/from-user/<user_id> {'GET', 'HEAD', 'OPTIONS', 'DELETE'}
/api/<api_version>/documents/<doc_id>/commentaries/of-type/<type_id> {'GET', 'HEAD', 'OPTIONS', 'DELETE'}
/api/<api_version>/documents/<doc_id>/commentaries/reference {'OPTIONS', 'GET', 'HEAD'}
/api/<api_version>/documents/<doc_id>/commentaries/reference/notes {'OPTIONS', 'GET', 'HEAD'}
/api/<api_version>/documents/<doc_id>/commentaries/reference/of-type/<type_id> {'OPTIONS', 'GET', 'HEAD'}
/api/<api_version>/documents/<doc_id>/first-canvas {'OPTIONS', 'GET', 'HEAD'}
/api/<api_version>/documents/<doc_id>/images {'POST', 'GET', 'HEAD', 'OPTIONS', 'DELETE'}
/api/<api_version>/documents/<doc_id>/manifest {'OPTIONS', 'GET', 'HEAD'}
/api/<api_version>/documents/<doc_id>/notes {'OPTIONS', 'GET', 'HEAD'}
/api/<api_version>/documents/<doc_id>/notes/<note_id> {'OPTIONS', 'GET', 'HEAD'}
/api/<api_version>/documents/<doc_id>/notes/from-user/<user_id> {'OPTIONS', 'GET', 'HEAD'}
/api/<api_version>/documents/<doc_id>/transcriptions {'POST', 'GET', 'HEAD', 'OPTIONS', 'PUT'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments {'POST', 'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments/discours {'POST', 'GET', 'HEAD', 'OPTIONS'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments/discours/from-user/<user_id> {'GET', 'HEAD', 'OPTIONS', 'DELETE'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments/discours/reference {'OPTIONS', 'GET', 'HEAD'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments/from-user/<user_id> {'GET', 'HEAD', 'OPTIONS', 'DELETE'}
/api/<api_version>/documents/<doc_id>/transcriptions/alignments/reference {'OPTIONS', 'GET', 'HEAD'}
/api/<api_version>/documents/<doc_id>/transcriptions/from-user/<user_id> {'GET', 'HEAD', 'OPTIONS', 'DELETE'}
/api/<api_version>/documents/<doc_id>/transcriptions/from-user/<user_id>/list {'OPTIONS', 'GET', 'HEAD'}
/api/<api_version>/documents/<doc_id>/transcriptions/list {'OPTIONS', 'GET', 'HEAD'}
/api/<api_version>/documents/<doc_id>/transcriptions/notes {'POST', 'GET', 'HEAD', 'OPTIONS', 'PUT'}
/api/<api_version>/documents/<doc_id>/transcriptions/notes/<note_id> {'OPTIONS', 'GET', 'HEAD'}
/api/<api_version>/documents/<doc_id>/transcriptions/notes/<note_id>/from-user/<user_id> {'OPTIONS', 'DELETE'}
/api/<api_version>/documents/<doc_id>/transcriptions/notes/from-user/<user_id> {'GET', 'HEAD', 'OPTIONS', 'DELETE'}
/api/<api_version>/documents/<doc_id>/transcriptions/reference {'OPTIONS', 'GET', 'HEAD'}
/api/<api_version>/documents/<doc_id>/transcriptions/reference/notes {'OPTIONS', 'GET', 'HEAD'}
/api/<api_version>/documents/<doc_id>/transcriptions/users {'OPTIONS', 'GET', 'HEAD'}
/api/<api_version>/documents/<doc_id>/translations {'POST', 'GET', 'HEAD', 'OPTIONS', 'PUT'}
/api/<api_version>/documents/<doc_id>/translations/from-user/<user_id> {'GET', 'HEAD', 'OPTIONS', 'DELETE'}
/api/<api_version>/documents/<doc_id>/translations/notes {'POST', 'GET', 'HEAD', 'OPTIONS', 'PUT'}
/api/<api_version>/documents/<doc_id>/translations/notes/<note_id> {'OPTIONS', 'GET', 'HEAD'}
/api/<api_version>/documents/<doc_id>/translations/notes/<note_id>/from-user/<user_id> {'OPTIONS', 'DELETE'}
/api/<api_version>/documents/<doc_id>/translations/notes/from-user/<user_id> {'GET', 'HEAD', 'OPTIONS', 'DELETE'}
/api/<api_version>/documents/<doc_id>/translations/reference {'OPTIONS', 'GET', 'HEAD'}
/api/<api_version>/documents/<doc_id>/translations/reference/notes {'OPTIONS', 'GET', 'HEAD'}
/api/<api_version>/documents/<doc_id>/translations/users {'OPTIONS', 'GET', 'HEAD'}
/api/<api_version>/editors {'POST', 'GET', 'HEAD', 'OPTIONS', 'DELETE', 'PUT'}
/api/<api_version>/editors/<editor_id> {'GET', 'HEAD', 'OPTIONS', 'DELETE'}
/api/<api_version>/institutions {'POST', 'GET', 'HEAD', 'OPTIONS', 'DELETE', 'PUT'}
/api/<api_version>/institutions/<institution_id> {'GET', 'HEAD', 'OPTIONS', 'DELETE'}
/api/<api_version>/languages {'POST', 'GET', 'HEAD', 'OPTIONS', 'DELETE', 'PUT'}
/api/<api_version>/languages/<language_code> {'GET', 'HEAD', 'OPTIONS', 'DELETE'}
/api/<api_version>/note-types {'OPTIONS', 'GET', 'HEAD'}
/api/<api_version>/notes {'POST', 'OPTIONS', 'GET', 'HEAD'}
/api/<api_version>/speech-part-types {'POST', 'GET', 'HEAD', 'OPTIONS', 'DELETE', 'PUT'}
/api/<api_version>/speech-part-types/<speech_part_type_id> {'GET', 'HEAD', 'OPTIONS', 'DELETE'}
/api/<api_version>/test/auth/<doc_id> {'OPTIONS', 'DELETE', 'POST'}
/api/<api_version>/traditions {'POST', 'GET', 'HEAD', 'OPTIONS', 'DELETE', 'PUT'}
/api/<api_version>/traditions/<tradition_id> {'GET', 'HEAD', 'OPTIONS', 'DELETE'}
/api/<api_version>/user {'OPTIONS', 'GET', 'HEAD'}
/api/<api_version>/users/<user_id> {'GET', 'HEAD', 'OPTIONS', 'DELETE'}
/api/<api_version>/users/<user_id>/roles {'POST', 'GET', 'HEAD', 'OPTIONS', 'DELETE'}
/api/user-role {'OPTIONS', 'GET', 'HEAD'}
