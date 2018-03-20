from app import db

def __get_translation_alignment(transcription_id):
    return """
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
   ;
   """.format(t_id=transcription_id)


def align_translation(transcription_id):
    """Fetches rows from alignment_translation.

        Retrieves rows from the transcription and translation tables
        using the alignment_transcription table to join data

        Args:
            transcription_id : a transcription_id
        Returns:
            A list of rows.
            Each returned row is a tuple with the following database fields:
            (transcription.transcription_id,  translation.translation_id, transcription_row, translation_row)

    """
    stmt = __get_translation_alignment(transcription_id)
    rows = db.execute(stmt).fetchall()
    for row in [row for row in rows]:
        print(row)

    return [row for row in rows]

