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

        self.assert401("/api/1.0/documents/21/transcriptions/alignments/from-user/4")
        self.assert403("/api/1.0/documents/21/transcriptions/alignments/from-user/7", **STU1_USER)
        self.assert404("/api/1.0/documents/21/transcriptions/alignments/from-user/5", **STU1_USER)
        self.assert404("/api/1.0/documents/21/transcriptions/alignments/from-user/4", **PROF1_USER)

        self.load_fixtures(TestAlignmentTranslationAPI.FIXTURES_TRANSLATION_STU1)
        self.assert404("/api/1.0/documents/21/transcriptions/alignments/from-user/5", **STU1_USER)

        self.load_fixtures(TestAlignmentTranslationAPI.FIXTURES_ALIGNMENT_STU1)

        self.assert404("/api/1.0/documents/21/transcriptions/alignments/from-user/5", **STU1_USER)
        self.assert403("/api/1.0/documents/21/transcriptions/alignments/from-user/5", **STU2_USER)

        # now that the transcription is validated, users can get the alignments
        self.assert200("/api/1.0/documents/21/validate-transcription", **PROF1_USER)
        r = self.assert200("/api/1.0/documents/21/transcriptions/alignments/from-user/5", **STU1_USER)
        r = json_loads(r.data)['data']
        self.assertEqual(5, len(r))

        # if teacher has his own translation, users can still get their own alignments through the API
        self.load_fixtures(TestAlignmentTranslationAPI.FIXTURES_TRANSLATION_PROF)
        self.assert200("/api/1.0/documents/21/transcriptions/alignments/from-user/5", **STU1_USER)
        self.assert200("/api/1.0/documents/21/validate-translation", **PROF1_USER)
        self.assert200("/api/1.0/documents/21/transcriptions/alignments/from-user/5", **STU1_USER)

        self.load_fixtures(TestAlignmentTranslationAPI.FIXTURES_ALIGNMENT_PROF1)
        r = self.assert200("/api/1.0/documents/21/transcriptions/alignments/from-user/5", **STU1_USER)
        r = json_loads(r.data)['data']
        self.assertEqual(5, len(r))
        # and teacher can get his own translation
        r = self.assert200("/api/1.0/documents/21/transcriptions/alignments/from-user/4", **PROF1_USER)
        r = json_loads(r.data)['data']
        self.assertEqual(3, len(r))
        # and yet teacher can get the user's translation too
        r = self.assert200("/api/1.0/documents/21/transcriptions/alignments/from-user/5", **PROF1_USER)
        r = json_loads(r.data)['data']
        self.assertEqual(5, len(r))

        #r = self.assert200("/adele/documents/21/view/transcription-alignment")
        #print(r.data)

    def test_get_alignment_reference(self):
        self.load_fixtures(TestAlignmentTranslationAPI.FIXTURES)
        self.assert404("/api/1.0/documents/21/transcriptions/alignments")
        self.assert404("/api/1.0/documents/21/transcriptions/alignments", **STU1_USER)
        self.assert404("/api/1.0/documents/21/transcriptions/alignments", **PROF1_USER)

        self.load_fixtures(TestAlignmentTranslationAPI.FIXTURES_TRANSLATION_STU1)
        self.load_fixtures(TestAlignmentTranslationAPI.FIXTURES_TRANSLATION_PROF)
        self.load_fixtures(TestAlignmentTranslationAPI.FIXTURES_ALIGNMENT_STU1)
        self.load_fixtures(TestAlignmentTranslationAPI.FIXTURES_ALIGNMENT_PROF1)

        self.assert404("/api/1.0/documents/21/transcriptions/alignments")
        self.assert404("/api/1.0/documents/21/transcriptions/alignments", **STU1_USER)
        self.assert404("/api/1.0/documents/21/transcriptions/alignments", **PROF1_USER)

        self.assert200("/api/1.0/documents/21/validate-transcription", **PROF1_USER)
        self.assert200("/api/1.0/documents/21/validate-translation", **PROF1_USER)

        r = self.assert200("/api/1.0/documents/21/transcriptions/alignments")
        r = json_loads(r.data)['data']
        self.assertEqual(3, len(r))
        r = self.assert200("/api/1.0/documents/21/transcriptions/alignments", **STU1_USER)
        r = json_loads(r.data)['data']
        self.assertEqual(3, len(r))
        r = self.assert200("/api/1.0/documents/21/transcriptions/alignments", **PROF1_USER)
        r = json_loads(r.data)['data']
        self.assertEqual(3, len(r))

    def test_post_alignment_for_user(self):
        self.assert401("/api/1.0/documents/21/transcriptions/alignments/from-user/5",
                       method="POST", data={"data": []})
        self.assert403("/api/1.0/documents/21/transcriptions/alignments/from-user/5",
                       method="POST", data={"data": []}, **STU2_USER)
        self.assert404("/api/1.0/documents/21/transcriptions/alignments/from-user/5",
                       method="POST", data={"data": []}, **STU1_USER)

        self.load_fixtures(TestAlignmentTranslationAPI.FIXTURES)
        self.assert404("/api/1.0/documents/21/transcriptions/alignments/from-user/5",
                       method="POST", data={"data": []}, **STU1_USER)
        self.load_fixtures(TestAlignmentTranslationAPI.FIXTURES_TRANSLATION_STU1)

        # cannot post when the transcription validation flag is False
        self.assert404("/api/1.0/documents/21/transcriptions/alignments/from-user/5",
                       method="POST", data={"data": []}, **STU1_USER)

        self.assert200("/api/1.0/documents/21/validate-transcription", **PROF1_USER)
        #send nothing
        self.assert200("/api/1.0/documents/21/transcriptions/alignments/from-user/5",
                       method="POST", data={"data": []}, **STU1_USER)
        # still nothing on the reference content side
        self.assert404("/api/1.0/documents/21/transcriptions/alignments", **STU1_USER)
        # but user has alignments now
        r = self.assert200("/api/1.0/documents/21/transcriptions/alignments/from-user/5", **STU1_USER)
        r = json_loads(r.data)['data']
        self.assertEqual(0, len(r))

        # send ptrs
        ptrs = [(3, 15, 4, 11), (15, 16, 4, 11), (16, 25, 4, 11)]
        self.assert200("/api/1.0/documents/21/transcriptions/alignments/from-user/5",
                       method="POST", data={"data": ptrs}, **STU1_USER)
        r = self.assert200("/api/1.0/documents/21/transcriptions/alignments/from-user/5", **STU1_USER)
        r = json_loads(r.data)['data']
        self.assertEqual(3, len(r))

        # test integrity
        # TODO

        # test continuity
        # TODO

        # test truncate and replace
        ptrs = [(3, 15, 4, 11), (15, 16, 4, 11)]
        self.assert200("/api/1.0/documents/21/transcriptions/alignments/from-user/5",
                       method="POST", data={"data": ptrs}, **STU1_USER)
        r = self.assert200("/api/1.0/documents/21/transcriptions/alignments/from-user/5", **STU1_USER)
        r = json_loads(r.data)['data']
        self.assertEqual(2, len(r))

        # on TEACHER side
        self.load_fixtures(TestAlignmentTranslationAPI.FIXTURES_TRANSLATION_PROF)
        ptrs = [(3, 15, 4, 11), (15, 16, 4, 11), (16, 25, 4, 11), (25, 36, 4, 11)]
        self.assert200("/api/1.0/documents/21/transcriptions/alignments/from-user/4",
                       method="POST", data={"data": ptrs}, **PROF1_USER)
        r = self.assert200("/api/1.0/documents/21/transcriptions/alignments/from-user/4", **PROF1_USER)
        r = json_loads(r.data)['data']
        self.assertEqual(4, len(r))

        r = self.assert200("/api/1.0/documents/21/transcriptions/alignments/from-user/5", **PROF1_USER)
        r = json_loads(r.data)['data']
        self.assertEqual(2, len(r))

        self.assert200("/api/1.0/documents/21/unvalidate-transcription", **PROF1_USER)
        self.assert404("/api/1.0/documents/21/transcriptions/alignments/from-user/5",
                       method="POST", data={"data": ptrs}, **STU1_USER)
        self.assert404("/api/1.0/documents/21/transcriptions/alignments/from-user/4",
                       method="POST", data={"data": ptrs}, **PROF1_USER)

    def test_delete_alignment_for_user(self):
        self.assert403("/api/1.0/documents/21/transcriptions/alignments/from-user/5",
                       method="DELETE", **STU2_USER)
        self.assert401("/api/1.0/documents/21/transcriptions/alignments/from-user/5",
                       method="DELETE")
        self.assert404("/api/1.0/documents/21/transcriptions/alignments/from-user/5",
                       method="DELETE", **STU1_USER)

        self.load_fixtures(TestAlignmentTranslationAPI.FIXTURES)
        self.load_fixtures(TestAlignmentTranslationAPI.FIXTURES_TRANSLATION_STU1)

        self.assert200("/api/1.0/documents/21/validate-transcription", **PROF1_USER)
        self.load_fixtures(TestAlignmentTranslationAPI.FIXTURES_ALIGNMENT_STU1)

        r = self.assert200("/api/1.0/documents/21/transcriptions/alignments/from-user/5", **PROF1_USER)
        r = json_loads(r.data)['data']
        self.assertEqual(5, len(r))

        self.assert200("/api/1.0/documents/21/transcriptions/alignments/from-user/5", method="DELETE", **STU1_USER)
        r = self.assert200("/api/1.0/documents/21/transcriptions/alignments/from-user/5", **PROF1_USER)
        r = json_loads(r.data)['data']
        self.assertEqual(0, len(r))

        self.load_fixtures(TestAlignmentTranslationAPI.FIXTURES_ALIGNMENT_STU1)
        self.assert200("/api/1.0/documents/21/transcriptions/alignments/from-user/5", method="DELETE", **PROF1_USER)
        r = self.assert200("/api/1.0/documents/21/transcriptions/alignments/from-user/5", **PROF1_USER)
        r = json_loads(r.data)['data']
        self.assertEqual(0, len(r))
