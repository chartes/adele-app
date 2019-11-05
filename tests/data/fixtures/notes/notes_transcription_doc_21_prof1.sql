INSERT INTO note (id, type_id, user_id, content) VALUES (100001, 0, 4, '<p>NOTE 1 PROF1</p>');
INSERT INTO note (id, type_id, user_id, content) VALUES (100002, 0, 4, '<p>NOTE 2 PROF1</p>');
INSERT INTO note (id, type_id, user_id, content) VALUES (100003, 0, 4, '<p>NOTE 3 PROF1</p>');

INSERT INTO transcription_has_note (transcription_id, note_id, ptr_start, ptr_end) VALUES (21, 100001, 3, 5);
INSERT INTO transcription_has_note (transcription_id, note_id, ptr_start, ptr_end) VALUES (21, 100002, 9, 10);
INSERT INTO transcription_has_note (transcription_id, note_id, ptr_start, ptr_end) VALUES (21, 100003, 15, 17);
