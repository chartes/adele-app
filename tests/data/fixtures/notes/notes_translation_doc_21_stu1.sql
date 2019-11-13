INSERT INTO note (id, type_id, user_id, content) VALUES (500004, 0, 5, '<p>NOTE 1 STU1</p>');
INSERT INTO note (id, type_id, user_id, content) VALUES (500005, 0, 5, '<p>NOTE 2 STU1</p>');
INSERT INTO note (id, type_id, user_id, content) VALUES (500006, 0, 5, '<p>NOTE 3 STU1</p>');


INSERT INTO translation_has_note (translation_id, note_id, ptr_start, ptr_end) VALUES (22, 500004, 3, 5);
INSERT INTO translation_has_note (translation_id, note_id, ptr_start, ptr_end) VALUES (22, 500005, 9, 10);
INSERT INTO translation_has_note (translation_id, note_id, ptr_start, ptr_end) VALUES (22, 500006, 15, 17);
