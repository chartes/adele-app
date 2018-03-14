from app import db

ALIGNMENT_STMT = lambda doc_id, transcription_id : """
   -- Transcription vs Translation
   SELECT
     transcription.transcription_id,
     translation.translation_id,
     substr(transcription.content, ptr_transcription_start, 
       ptr_transcription_end - ptr_transcription_start) as transcription,
     substr(translation.content, ptr_translation_start, 
       ptr_translation_end - ptr_translation_start) as translation
   FROM
     transcription
     JOIN alignment_translation
       on transcription.transcription_id = alignment_translation.transcription_id
     JOIN  translation
       ON alignment_translation.translation_id = translation.translation_id
   WHERE
     transcription.transcription_id = {t_id} 
     and
     transcription.doc_id = {doc_id} 
     and 
     translation.doc_id = {doc_id}
   ;
   """.format(t_id=transcription_id, doc_id=doc_id)

"""
"""
def align_translation(doc_id, transcription_id):
    stmt = ALIGNMENT_STMT(doc_id, transcription_id)
    rows = db.execute(stmt).fetchall()
    for row in [row for row in rows]:
        print(row)

    return [row for row in rows]

