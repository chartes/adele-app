INSERT INTO image (manifest_url, canvas_idx, img_idx, doc_id) VALUES ('https://iiif.chartes.psl.eu/manifests/adele/man21.json', 0, 0, 21);

INSERT INTO image_zone (zone_id, manifest_url, canvas_idx, img_idx, user_id, zone_type_id, coords, note) VALUES (111, 'https://iiif.chartes.psl.eu/manifests/adele/man21.json', 0, 0, 4, 1, '188,487,587,507', null);
INSERT INTO image_zone (zone_id, manifest_url, canvas_idx, img_idx, user_id, zone_type_id, coords, note) VALUES (112, 'https://iiif.chartes.psl.eu/manifests/adele/man21.json', 0, 0, 4, 1, '587,482,787,509', null);
INSERT INTO image_zone (zone_id, manifest_url, canvas_idx, img_idx, user_id, zone_type_id, coords, note) VALUES (113, 'https://iiif.chartes.psl.eu/manifests/adele/man21.json', 0, 0, 4, 1, '186,512,509,536', null);

INSERT INTO alignment_image VALUES (21,	4,	111, 'https://iiif.chartes.psl.eu/manifests/adele/man21.json',	0,	0,	3,	84);
INSERT INTO alignment_image VALUES (21,	4,	112, 'https://iiif.chartes.psl.eu/manifests/adele/man21.json',	0,	0,	84,	189);
INSERT INTO alignment_image VALUES (21,	4,	113, 'https://iiif.chartes.psl.eu/manifests/adele/man21.json',	0,	0,	189, 237);
