INSERT INTO note (id, type_id, user_id, content) VALUES (570001, 0, 5, '<p>NOTE 1 STU2</p>');
INSERT INTO note (id, type_id, user_id, content) VALUES (570002, 0, 5, '<p>NOTE 2 STU2</p>');


INSERT INTO transcription_has_note (transcription_id, note_id, ptr_start, ptr_end) VALUES (23, 570001, 3, 5);
INSERT INTO transcription_has_note (transcription_id, note_id, ptr_start, ptr_end) VALUES (23, 570002, 9, 10);
