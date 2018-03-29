from app import db

def __get_translation_alignment(transcription_id):
    return """
        -- Transcription vs Translation
        SELECT
          transcription.id as transcription_id,
          translation.id as translation_id,
          substr(transcription.content, ptr_transcription_start, 
            ptr_transcription_end - ptr_transcription_start) as transcription,
          substr(translation.content, ptr_translation_start, 
            ptr_translation_end - ptr_translation_start) as translation
        FROM
          transcription
          LEFT JOIN alignment_translation
            on transcription.id = alignment_translation.transcription_id
          LEFT JOIN  translation
            ON alignment_translation.translation_id = translation.id
        WHERE
          transcription.id = {transcription_id}      
        ;
        """.format(transcription_id=transcription_id)


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

    rows = db.engine.execute(stmt)

    return [row for row in rows]

