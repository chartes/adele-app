
from os.path import join
from tests.base_server import TestBaseServer, json_loads, ADMIN_USER, STU1_USER, PROF1_USER, PROF2_USER


class TestDocumentValidationAPI(TestBaseServer):
    FIXTURES = [
        join(TestBaseServer.FIXTURES_PATH, "documents", "doc_21.sql")
    ]
    FIXTURES_TRANSCRIPTION_PROF_1 = [
        join(TestBaseServer.FIXTURES_PATH, "transcriptions", "transcription_doc_21_prof1.sql"),
        join(TestBaseServer.FIXTURES_PATH, "notes", "notes_transcription_doc_21_prof1.sql"),
    ]
    FIXTURES_TRANSLATION_PROF_1 = [
        join(TestBaseServer.FIXTURES_PATH, "translations", "translation_doc_21_prof1.sql"),
        join(TestBaseServer.FIXTURES_PATH, "notes", "notes_translation_doc_21_prof1.sql"),
    ]
    FIXTURES_TRANSCRIPTION_STU_1 = [
        join(TestBaseServer.FIXTURES_PATH, "transcriptions", "transcription_doc_21_stu1.sql"),
        join(TestBaseServer.FIXTURES_PATH, "notes", "notes_transcription_doc_21_stu1.sql"),
    ]
    FIXTURES_TRANSLATION_STU_1 = [
        join(TestBaseServer.FIXTURES_PATH, "translations", "translation_doc_21_stu1.sql"),
        join(TestBaseServer.FIXTURES_PATH, "notes", "notes_translation_doc_21_stu1.sql"),
    ]
    FIXTURES_FACSIMILE = [
        join(TestBaseServer.FIXTURES_PATH, "alignments_image", "alignments_image_doc_21_prof1.sql"),
    ]
    FIXTURES_COMMENTARIES = [
        join(TestBaseServer.FIXTURES_PATH, "commentaries", "commentary_doc_21.sql"),
    ]
    FIXTURES_SPEECHPARTS_PROF_1 = [
        join(TestBaseServer.FIXTURES_PATH, "alignments_discours", "alignments_discours_doc_21_prof1.sql"),
    ]

    def test_validation_transcription(self):
        self.load_fixtures(self.FIXTURES)
        # when there's no transcription at all
        self.assert404("/api/1.0/documents/21/validate-transcription", **PROF1_USER)
        self.load_fixtures(self.FIXTURES_TRANSCRIPTION_STU_1)
        # when there's no teacher transcription but user ones
        self.assert404("/api/1.0/documents/21/validate-transcription", **PROF1_USER)
        # cannot validate as student
        self.assert403("/api/1.0/documents/21/validate-transcription", **STU1_USER)
        # when there's teacher trancription
        self.load_fixtures(self.FIXTURES_TRANSCRIPTION_PROF_1)
        self.assert200("/api/1.0/documents/21/validate-transcription", **PROF1_USER)
        # test unvalidation
        # cannot validate as student
        self.assert403("/api/1.0/documents/21/unvalidate-transcription", **STU1_USER)
        self.assert200("/api/1.0/documents/21/unvalidate-transcription", **PROF1_USER)
        # test when you delete the transcription
        self.assert200("/api/1.0/documents/21/transcriptions/from-user/4", method="DELETE", **PROF1_USER)
        self.assert404("/api/1.0/documents/21/validate-transcription", **PROF1_USER)
        self.assert404("/api/1.0/documents/21/unvalidate-transcription", **PROF1_USER)

    def test_validation_translation(self):
        self.load_fixtures(self.FIXTURES)
        # when there's no transcription at all
        self.assert403("/api/1.0/documents/21/validate-translation", **PROF1_USER)
        # when there's no translation at all
        self.load_fixtures(self.FIXTURES_TRANSCRIPTION_PROF_1)
        self.assert403("/api/1.0/documents/21/validate-translation", **PROF1_USER)

        self.load_fixtures(self.FIXTURES_TRANSLATION_PROF_1)
        self.load_fixtures(self.FIXTURES_TRANSCRIPTION_STU_1)
        self.load_fixtures(self.FIXTURES_TRANSLATION_STU_1)
        # cannot validate as student
        self.assert403("/api/1.0/documents/21/validate-translation", **STU1_USER)
        # when there's teacher translation
        self.assert200("/api/1.0/documents/21/validate-transcription", **PROF1_USER)
        self.assert200("/api/1.0/documents/21/validate-translation", **PROF1_USER)

        # when the transcription is unvalidated
        self.assert200("/api/1.0/documents/21/unvalidate-translation", **PROF1_USER)
        self.assert200("/api/1.0/documents/21/unvalidate-transcription", **PROF1_USER)
        self.assert403("/api/1.0/documents/21/validate-translation", **PROF1_USER)
        self.assert200("/api/1.0/documents/21/validate-transcription", **PROF1_USER)
        self.assert200("/api/1.0/documents/21/validate-translation", **PROF1_USER)

        # test unvalidation
        # cannot validate as student
        self.assert403("/api/1.0/documents/21/unvalidate-translation", **STU1_USER)
        self.assert200("/api/1.0/documents/21/unvalidate-translation", **PROF1_USER)

        # test when you delete the translation
        self.assert200("/api/1.0/documents/21/translations/from-user/4", method="DELETE", **PROF1_USER)
        self.assert404("/api/1.0/documents/21/validate-translation", **PROF1_USER)
        self.assert404("/api/1.0/documents/21/unvalidate-translation", **PROF1_USER)

        self.load_fixtures(self.FIXTURES_TRANSLATION_PROF_1)

        # test when you delete the transcription
        self.assert200("/api/1.0/documents/21/transcriptions/from-user/4", method="DELETE", **PROF1_USER)
        self.assert403("/api/1.0/documents/21/validate-translation", **PROF1_USER)
        self.assert403("/api/1.0/documents/21/unvalidate-translation", **PROF1_USER)

    def test_validation_commentaries(self):
        self.load_fixtures(self.FIXTURES)
        # when there's no transcription at all
        self.assert403("/api/1.0/documents/21/validate-commentaries", **PROF1_USER)

        # when there's no commentaries at all
        self.load_fixtures(self.FIXTURES_TRANSCRIPTION_PROF_1)
        self.assert200("/api/1.0/documents/21/validate-transcription", **PROF1_USER)
        # 403 cuz student
        self.assert403("/api/1.0/documents/21/validate-commentaries", **STU1_USER)
        self.load_fixtures(self.FIXTURES_COMMENTARIES)
        self.assert200("/api/1.0/documents/21/validate-commentaries", **PROF1_USER)

        # test when you delete the commentaries
        self.assert200("/api/1.0/documents/21/commentaries", method="DELETE", **PROF1_USER)
        self.assert404("/api/1.0/documents/21/validate-commentaries", **PROF1_USER)
        self.assert404("/api/1.0/documents/21/unvalidate-commentaries", **PROF1_USER)

        self.load_fixtures(self.FIXTURES_COMMENTARIES)
        # test unvalidation
        # when the transcription is unvalidated
        self.assert200("/api/1.0/documents/21/unvalidate-commentaries", **PROF1_USER)
        self.assert200("/api/1.0/documents/21/unvalidate-transcription", **PROF1_USER)
        self.assert403("/api/1.0/documents/21/validate-commentaries", **PROF1_USER)
        self.assert200("/api/1.0/documents/21/validate-transcription", **PROF1_USER)
        self.assert200("/api/1.0/documents/21/validate-commentaries", **PROF1_USER)

        # cannot validate as student
        self.assert403("/api/1.0/documents/21/unvalidate-commentaries", **STU1_USER)

        # test when you delete the commentaries
        self.assert200("/api/1.0/documents/21/commentaries", method="DELETE", **PROF1_USER)
        self.assert404("/api/1.0/documents/21/validate-commentaries", **PROF1_USER)
        self.assert404("/api/1.0/documents/21/unvalidate-commentaries", **PROF1_USER)

        # test when you delete the transcription
        self.assert200("/api/1.0/documents/21/transcriptions/from-user/4", method="DELETE", **PROF1_USER)
        self.assert403("/api/1.0/documents/21/validate-commentaries", **PROF1_USER)
        self.assert403("/api/1.0/documents/21/unvalidate-commentaries", **PROF1_USER)

    def test_validation_facsimile_pt1(self):
        self.load_fixtures(self.FIXTURES)
        # when there's no transcription at all
        self.assert403("/api/1.0/documents/21/validate-facsimile", **PROF1_USER)

        # when there's no speechparts at all
        self.load_fixtures(self.FIXTURES_TRANSCRIPTION_PROF_1)
        self.assert200("/api/1.0/documents/21/validate-transcription", **PROF1_USER)
        self.assert403("/api/1.0/documents/21/validate-facsimile", **STU1_USER)
        self.load_fixtures(self.FIXTURES_FACSIMILE)
        self.assert200("/api/1.0/documents/21/validate-facsimile", **PROF1_USER)

        # test when you delete the speechparts
        self.assert200("/api/1.0/documents/21/facsimile", method="DELETE", **PROF1_USER)
        self.assert404("/api/1.0/documents/21/validate-facsimile", **PROF1_USER)
        self.assert404("/api/1.0/documents/21/unvalidate-facsimile", **PROF1_USER)

    def test_validation_facsimile_pt2(self):
        self.load_fixtures(self.FIXTURES)
        self.load_fixtures(self.FIXTURES_TRANSCRIPTION_PROF_1)
        self.load_fixtures(self.FIXTURES_FACSIMILE)
        self.assert200("/api/1.0/documents/21/validate-transcription", **PROF1_USER)
        self.assert200("/api/1.0/documents/21/validate-facsimile", **PROF1_USER)
        # test unvalidation
        # when the transcription is unvalidated
        self.assert200("/api/1.0/documents/21/unvalidate-facsimile", **PROF1_USER)
        self.assert200("/api/1.0/documents/21/unvalidate-transcription", **PROF1_USER)
        self.assert403("/api/1.0/documents/21/validate-facsimile", **PROF1_USER)
        self.assert200("/api/1.0/documents/21/validate-transcription", **PROF1_USER)
        self.assert200("/api/1.0/documents/21/validate-facsimile", **PROF1_USER)

        # cannot validate as student
        self.assert403("/api/1.0/documents/21/unvalidate-facsimile", **STU1_USER)

        # test when you delete the facsimile alignemnt
        self.assert200("/api/1.0/documents/21/facsimile", method="DELETE", **PROF1_USER)
        self.assert404("/api/1.0/documents/21/validate-facsimile", **PROF1_USER)
        self.assert404("/api/1.0/documents/21/unvalidate-facsimile", **PROF1_USER)

        # test when you delete the transcription
        self.assert200("/api/1.0/documents/21/transcriptions/from-user/4", method="DELETE", **PROF1_USER)
        self.assert403("/api/1.0/documents/21/validate-facsimile", **PROF1_USER)
        self.assert403("/api/1.0/documents/21/unvalidate-facsimile", **PROF1_USER)

    def test_validation_speechparts(self):
        self.load_fixtures(self.FIXTURES)
        # when there's no transcription at all
        self.assert403("/api/1.0/documents/21/validate-speech-parts", **PROF1_USER)

        # when there's no speechparts at all
        self.load_fixtures(self.FIXTURES_TRANSCRIPTION_PROF_1)
        self.assert200("/api/1.0/documents/21/validate-transcription", **PROF1_USER)
        self.assert403("/api/1.0/documents/21/validate-speech-parts", **STU1_USER)
        self.load_fixtures(self.FIXTURES_SPEECHPARTS_PROF_1)
        self.assert200("/api/1.0/documents/21/validate-speech-parts", **PROF1_USER)

        # test when you delete the speechparts
        self.assert200("/api/1.0/documents/21/speech-parts/from-user/4", method="DELETE", **PROF1_USER)
        self.assert404("/api/1.0/documents/21/validate-speech-parts", **PROF1_USER)
        self.assert404("/api/1.0/documents/21/unvalidate-speech-parts", **PROF1_USER)

        self.load_fixtures(self.FIXTURES_SPEECHPARTS_PROF_1)
        # test unvalidation
        # when the transcription is unvalidated
        self.assert200("/api/1.0/documents/21/unvalidate-speech-parts", **PROF1_USER)
        self.assert200("/api/1.0/documents/21/unvalidate-transcription", **PROF1_USER)
        self.assert403("/api/1.0/documents/21/validate-speech-parts", **PROF1_USER)
        self.assert200("/api/1.0/documents/21/validate-transcription", **PROF1_USER)
        self.assert200("/api/1.0/documents/21/validate-speech-parts", **PROF1_USER)

        # cannot validate as student
        self.assert403("/api/1.0/documents/21/unvalidate-speech-parts", **STU1_USER)

        # test when you delete the speechparts
        self.assert200("/api/1.0/documents/21/speech-parts/from-user/4", method="DELETE", **PROF1_USER)
        self.assert404("/api/1.0/documents/21/validate-speech-parts", **PROF1_USER)
        self.assert404("/api/1.0/documents/21/unvalidate-speech-parts", **PROF1_USER)

        # test when you delete the transcription
        self.assert200("/api/1.0/documents/21/transcriptions/from-user/4", method="DELETE", **PROF1_USER)
        self.assert403("/api/1.0/documents/21/validate-speech-parts", **PROF1_USER)
        self.assert403("/api/1.0/documents/21/unvalidate-speech-parts", **PROF1_USER)

    def test_parallel_validations(self):
        self.load_fixtures(self.FIXTURES)
        self.load_fixtures(self.FIXTURES_TRANSCRIPTION_PROF_1)
        self.load_fixtures(self.FIXTURES_TRANSLATION_PROF_1)
        self.load_fixtures(self.FIXTURES_COMMENTARIES)
        self.load_fixtures(self.FIXTURES_FACSIMILE)
        self.load_fixtures(self.FIXTURES_SPEECHPARTS_PROF_1)
        # test you can get all the validation flags at the same time

        self.assert200("/api/1.0/documents/21/validate-transcription", **PROF1_USER)
        self.assert200("/api/1.0/documents/21/validate-translation", **PROF1_USER)
        self.assert200("/api/1.0/documents/21/validate-commentaries", **PROF1_USER)
        self.assert200("/api/1.0/documents/21/validate-facsimile", **PROF1_USER)
        self.assert200("/api/1.0/documents/21/validate-speech-parts", **PROF1_USER)

        r = self.assert200("/api/1.0/documents/21/validation-flags", **PROF1_USER)
        r = json_loads(r.data)["data"]

        self.assertTrue(r['notice'])
        self.assertTrue(r['transcription'])
        self.assertTrue(r['translation'])
        self.assertTrue(r['facsimile'])
        self.assertTrue(r['speech-parts'])
        self.assertTrue(r['commentaries'])

