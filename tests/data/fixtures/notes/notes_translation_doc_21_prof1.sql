INSERT INTO note (id, type_id, user_id, content) VALUES (100004, 0, 4, '<p>NOTE 1 PROF1</p>');
INSERT INTO note (id, type_id, user_id, content) VALUES (100005, 0, 4, '<p>NOTE 2 PROF1</p>');
INSERT INTO note (id, type_id, user_id, content) VALUES (100006, 0, 4, '<p>NOTE 3 PROF1</p>');

INSERT INTO translation_has_note (translation_id, note_id, ptr_start, ptr_end) VALUES (21, 100004, 3, 5);
INSERT INTO translation_has_note (translation_id, note_id, ptr_start, ptr_end) VALUES (21, 100005, 9, 10);
INSERT INTO translation_has_note (translation_id, note_id, ptr_start, ptr_end) VALUES (21, 100006, 15, 17);
