
from os.path import join
from tests.base_server import TestBaseServer, json_loads, ADMIN_USER, STU1_USER, PROF1_USER, PROF2_USER


class TestDocumentValidationAPI(TestBaseServer):
    FIXTURES = [
        join(TestBaseServer.FIXTURES_PATH, "documents", "doc_21.sql")
    ]
    FIXTURES_TRANSCRIPTION = [
        join(TestBaseServer.FIXTURES_PATH, "transcriptions", "transcription_doc_21_prof1.sql"),
        join(TestBaseServer.FIXTURES_PATH, "notes", "notes_transcription_doc_21_prof1.sql"),
    ]
    FIXTURES_TRANSLATION = [
        join(TestBaseServer.FIXTURES_PATH, "translations", "translation_doc_21_prof1.sql"),
        join(TestBaseServer.FIXTURES_PATH, "notes", "notes_translation_doc_21_prof1.sql"),
    ]
    FIXTURES_FACSIMILE = [
    ]
    FIXTURES_COMMENTARIES = [
    ]
    FIXTURES_SPEECHPARTS = [
        join(TestBaseServer.FIXTURES_PATH, "alignments_discours", "alignments_discours_doc_21_prof1.sql"),
    ]

    def test_validation_transcription(self):
        self.load_fixtures(self.FIXTURES)

        # when there's no transcription at all

        self.load_fixtures(self.FIXTURES_TRANSCRIPTION)
        # when there's no teacher transcription but user ones

        # when there's teacher trancription

        # test unvalidation

        # test when you delete the transcription

        raise NotImplementedError

    def test_validation_translation(self):
        self.load_fixtures(self.FIXTURES)
        self.load_fixtures(self.FIXTURES_TRANSCRIPTION)

        # when there's no translation at all

        self.load_fixtures(self.FIXTURES_TRANSLATION)
        # when there's no teacher translation but user ones

        # when there's teacher translation

        # test unvalidation

        # test when you modify the translation

        # test when you modify the transcription

        # test when you delete the translation

        # test when you delete the transcription

        raise NotImplementedError

    def test_validation_commentaries(self):
        self.load_fixtures(self.FIXTURES)
        self.load_fixtures(self.FIXTURES_TRANSCRIPTION)

        # when there's no commentaries at all

        self.load_fixtures(self.FIXTURES_COMMENTARIES)
        # when there's no teacher commentaries but user ones

        # when there's teacher commentaries

        # test unvalidation

        # test when you modify the commentaries

        # test when you modify the transcription

        # test when you delete the commentaries

        # test when you delete the transcription

        raise NotImplementedError

    def test_validation_facsimile(self):
        self.load_fixtures(self.FIXTURES)
        self.load_fixtures(self.FIXTURES_TRANSCRIPTION)

        # when there's no facsimile alignments at all

        self.load_fixtures(self.FIXTURES_FACSIMILE)
        # when there's no teacher facsimile alignments but user ones

        # when there's teacher facsimile alignments

        # test unvalidation

        # test when you modify the facsimile alignments

        # test when you modify the transcription

        # test when you delete the facsimile alignments

        # test when you delete the transcription

        raise NotImplementedError

    def test_validation_speechparts(self):
        self.load_fixtures(self.FIXTURES)
        self.load_fixtures(self.FIXTURES_TRANSCRIPTION)

        # when there's no speechparts alignments at all

        self.load_fixtures(self.FIXTURES_SPEECHPARTS)
        # when there's no teacher speechparts alignments but user ones

        # when there's teacher speechparts alignments

        # test unvalidation

        # test when you modify the speechparts alignments

        # test when you modify the transcription

        # test when you delete the speechparts alignments

        # test when you delete the transcription

        raise NotImplementedError

    def test_parallel_validations(self):
        self.load_fixtures(self.FIXTURES)
        self.load_fixtures(self.FIXTURES_TRANSCRIPTION)
        self.load_fixtures(self.FIXTURES_TRANSLATION)
        self.load_fixtures(self.FIXTURES_COMMENTARIES)
        self.load_fixtures(self.FIXTURES_FACSIMILE)
        self.load_fixtures(self.FIXTURES_SPEECHPARTS)
        # test you can get all the validation flags at the same time

        raise NotImplementedError
