INSERT INTO note (id, type_id, user_id, content) VALUES (52001, 0, 7, '<p>USER 2 NOTE</p>');

INSERT INTO translation_has_note (translation_id, note_id, ptr_start, ptr_end) VALUES (50, 52001, 3, 5);
