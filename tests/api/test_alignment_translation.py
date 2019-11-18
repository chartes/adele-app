from os.path import join

from tests.base_server import TestBaseServer, PROF1_USER, STU1_USER, STU2_USER, json_loads


class TestAlignmentTranslationAPI(TestBaseServer):
    FIXTURES = [
        join(TestBaseServer.FIXTURES_PATH, "documents", "doc_21.sql"),
        join(TestBaseServer.FIXTURES_PATH, "transcriptions", "transcription_doc_21_prof1.sql"),
        join(TestBaseServer.FIXTURES_PATH, "notes", "notes_transcription_doc_21_prof1.sql"),
        join(TestBaseServer.FIXTURES_PATH, "transcriptions", "transcription_doc_21_stu1.sql"),
        join(TestBaseServer.FIXTURES_PATH, "notes", "notes_transcription_doc_21_stu1.sql"),
        join(TestBaseServer.FIXTURES_PATH, "transcriptions", "transcription_doc_21_stu2.sql"),
        join(TestBaseServer.FIXTURES_PATH, "notes", "notes_transcription_doc_21_stu2.sql"),
    ]

    # prod: id = 4
    FIXTURES_TRANSLATION_PROF = [
        join(TestBaseServer.FIXTURES_PATH, "translations", "translation_doc_21_prof1.sql"),
        join(TestBaseServer.FIXTURES_PATH, "notes", "notes_translation_doc_21_prof1.sql"),
    ]

    # eleve: id = 5
    FIXTURES_TRANSLATION_STU1 = [
        join(TestBaseServer.FIXTURES_PATH, "translations", "translation_doc_21_stu1.sql"),
        join(TestBaseServer.FIXTURES_PATH, "notes", "notes_translation_doc_21_stu1.sql"),
    ]

    FIXTURES_ALIGNMENT_STU1 = [
        join(TestBaseServer.FIXTURES_PATH, "alignments_translation", "alignments_translation_doc_21_stu1.sql"),
    ]

    FIXTURES_ALIGNMENT_PROF1 = [
        join(TestBaseServer.FIXTURES_PATH, "alignments_translation", "alignments_translation_doc_21_prof1.sql"),
    ]

    def test_get_alignment_from_user(self):
        self.load_fixtures(TestAlignmentTranslationAPI.FIXTURES)

        self.assert403("/adele/api/1.0/documents/21/transcriptions/alignments/from-user/4")
        self.assert403("/adele/api/1.0/documents/21/transcriptions/alignments/from-user/7", **STU1_USER)
        self.assert404("/adele/api/1.0/documents/21/transcriptions/alignments/from-user/5", **STU1_USER)
        self.assert404("/adele/api/1.0/documents/21/transcriptions/alignments/from-user/4", **PROF1_USER)

        self.load_fixtures(TestAlignmentTranslationAPI.FIXTURES_TRANSLATION_STU1)
        self.assert404("/adele/api/1.0/documents/21/transcriptions/alignments/from-user/5", **STU1_USER)

        self.load_fixtures(TestAlignmentTranslationAPI.FIXTURES_ALIGNMENT_STU1)

        self.assert404("/adele/api/1.0/documents/21/transcriptions/alignments/from-user/5", **STU1_USER)
        self.assert403("/adele/api/1.0/documents/21/transcriptions/alignments/from-user/5", **STU2_USER)

        # now that the transcription is validated, users can get the alignments
        self.assert200("/adele/api/1.0/documents/21/validate-transcription", **PROF1_USER)
        r = self.assert200("/adele/api/1.0/documents/21/transcriptions/alignments/from-user/5", **STU1_USER)
        r = json_loads(r.data)['data']
        self.assertEqual(5, len(r))

        # if teacher has his own translation, users can still get their own alignments through the API
        self.load_fixtures(TestAlignmentTranslationAPI.FIXTURES_TRANSLATION_PROF)
        self.assert200("/adele/api/1.0/documents/21/transcriptions/alignments/from-user/5", **STU1_USER)
        self.assert200("/adele/api/1.0/documents/21/validate-translation", **PROF1_USER)
        self.assert200("/adele/api/1.0/documents/21/transcriptions/alignments/from-user/5", **STU1_USER)

        self.load_fixtures(TestAlignmentTranslationAPI.FIXTURES_ALIGNMENT_PROF1)
        r = self.assert200("/adele/api/1.0/documents/21/transcriptions/alignments/from-user/5", **STU1_USER)
        r = json_loads(r.data)['data']
        self.assertEqual(5, len(r))
        # and teacher can get his own translation
        r = self.assert200("/adele/api/1.0/documents/21/transcriptions/alignments/from-user/4", **PROF1_USER)
        r = json_loads(r.data)['data']
        self.assertEqual(3, len(r))
        # and yet teacher can get the user's translation too
        r = self.assert200("/adele/api/1.0/documents/21/transcriptions/alignments/from-user/5", **PROF1_USER)
        r = json_loads(r.data)['data']
        self.assertEqual(5, len(r))

        #r = self.assert200("/adele/documents/21/view/transcription-alignment")
        #print(r.data)

    def test_get_alignment_reference(self):
        self.load_fixtures(TestAlignmentTranslationAPI.FIXTURES)
        self.assert404("/adele/api/1.0/documents/21/transcriptions/alignments")
        self.assert404("/adele/api/1.0/documents/21/transcriptions/alignments", **STU1_USER)
        self.assert404("/adele/api/1.0/documents/21/transcriptions/alignments", **PROF1_USER)

        self.load_fixtures(TestAlignmentTranslationAPI.FIXTURES_TRANSLATION_STU1)
        self.load_fixtures(TestAlignmentTranslationAPI.FIXTURES_TRANSLATION_PROF)
        self.load_fixtures(TestAlignmentTranslationAPI.FIXTURES_ALIGNMENT_STU1)
        self.load_fixtures(TestAlignmentTranslationAPI.FIXTURES_ALIGNMENT_PROF1)

        self.assert404("/adele/api/1.0/documents/21/transcriptions/alignments")
        self.assert404("/adele/api/1.0/documents/21/transcriptions/alignments", **STU1_USER)
        self.assert404("/adele/api/1.0/documents/21/transcriptions/alignments", **PROF1_USER)

        self.assert200("/adele/api/1.0/documents/21/validate-translation", **PROF1_USER)

        r = self.assert200("/adele/api/1.0/documents/21/transcriptions/alignments")
        r = json_loads(r.data)['data']
        self.assertEqual(3, len(r))
        r = self.assert200("/adele/api/1.0/documents/21/transcriptions/alignments", **STU1_USER)
        r = json_loads(r.data)['data']
        self.assertEqual(3, len(r))
        r = self.assert200("/adele/api/1.0/documents/21/transcriptions/alignments", **PROF1_USER)
        r = json_loads(r.data)['data']
        self.assertEqual(3, len(r))

    def test_post_alignment_for_user(self):
        raise NotImplementedError

    def test_put_alignment_for_user(self):
        raise NotImplementedError

    def test_clone_alignment_from_user(self):
        # ???
        raise NotImplementedError

    def test_delete_alignemnt_for_user(self):
        raise NotImplementedError
