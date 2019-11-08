INSERT INTO note (id, type_id, user_id, content) VALUES (500001, 0, 5, '<p>NOTE 1 STU1</p>');
INSERT INTO note (id, type_id, user_id, content) VALUES (500002, 0, 5, '<p>NOTE 2 STU1</p>');
INSERT INTO note (id, type_id, user_id, content) VALUES (500003, 0, 5, '<p>NOTE 3 STU1</p>');


INSERT INTO transcription_has_note (transcription_id, note_id, ptr_start, ptr_end) VALUES (22, 500001, 3, 5);
INSERT INTO transcription_has_note (transcription_id, note_id, ptr_start, ptr_end) VALUES (22, 500002, 9, 10);
INSERT INTO transcription_has_note (transcription_id, note_id, ptr_start, ptr_end) VALUES (22, 500003, 15, 17);
