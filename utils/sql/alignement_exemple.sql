
-- Transcription vs Translation
SELECT
  substr(transcription.content, ptr_transcription_start, ptr_transcription_end - ptr_transcription_start) as transcription,
  substr(translation.content, ptr_translation_start, ptr_translation_end - ptr_translation_start) as translation
FROM
  transcription
  JOIN alignment_translation
    on transcription.transcription_id = alignment_translation.transcription_id
  JOIN  translation
    ON alignment_translation.translation_id = translation.translation_id
;
