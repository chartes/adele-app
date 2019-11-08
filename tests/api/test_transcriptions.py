from os.path import join

from tests.base_server import TestBaseServer, json_loads, ADMIN_USER, STU1_USER, PROF1_USER, PROF2_USER, STU2_USER


class TestTranscriptionsAPI(TestBaseServer):

    FIXTURES = [
        join(TestBaseServer.FIXTURES_PATH, "documents", "doc_21.sql"),
    ]

    # prod: id = 4
    FIXTURES_PROF = [
        join(TestBaseServer.FIXTURES_PATH, "transcriptions", "transcription_doc_21_prof1.sql"),
        join(TestBaseServer.FIXTURES_PATH, "notes", "notes_transcription_doc_21_prof1.sql"),
    ]

    # eleve: id = 5
    FIXTURES_STU1 = [
        join(TestBaseServer.FIXTURES_PATH, "transcriptions", "transcription_doc_21_stu1.sql"),
        join(TestBaseServer.FIXTURES_PATH, "notes", "notes_transcription_doc_21_stu1.sql"),
    ]

    def test_get_transcriptions_reference(self):
        self.load_fixtures(TestTranscriptionsAPI.FIXTURES)

        # doc without transcription
        self.assert404("/adele/api/1.0/documents/21/transcriptions")
        self.assert404("/adele/api/1.0/documents/21/transcriptions", **STU1_USER)
        self.assert404("/adele/api/1.0/documents/21/transcriptions", **PROF1_USER)

        # access a validated transcription
        self.load_fixtures(TestTranscriptionsAPI.FIXTURES_PROF)
        self.load_fixtures(TestTranscriptionsAPI.FIXTURES_STU1)

        self.assert200("/adele/api/1.0/documents/21/validate-transcription", **PROF1_USER)
        r = self.assert200("/adele/api/1.0/documents/21/transcriptions", **PROF1_USER)
        r = json_loads(r.data)['data']
        self.assertEqual(
            '<p>Om<ex>n</ex>ib<ex>us</ex> p<ex>re</ex>sentes litt<ex>er</ex>as inspectur<ex>is</ex></p>',
            r['content']
        )
        self.assertEqual(21, r['doc_id'])
        self.assertEqual(4, r['user_id'])
        self.assertEqual(3, len(r['notes']))

        # test that notes ptr return the expected text fragment from the transcription
        expected_fragments = ['Om', 'n', 'ib']
        for i, note in enumerate(r['notes']):
            self.assertPtr(r['content'], note['ptr_start'], note['ptr_end'], expected_fragments[i])

        # available to everybody
        self.assert200("/adele/api/1.0/documents/21/transcriptions")
        self.assert200("/adele/api/1.0/documents/21/transcriptions", **STU1_USER)

        # -------- test validation steps ---------
        self.assert200("/adele/api/1.0/documents/21/unvalidate-transcription", **PROF1_USER)
        self.assert404("/adele/api/1.0/documents/21/transcriptions", **PROF1_USER)
        # needs a translation
        self.assert200("/adele/api/1.0/documents/21/validate-transcription", **PROF1_USER)
        self.assert200("/adele/api/1.0/documents/21/transcriptions", **PROF1_USER)
        # needs a translation
        self.assert404("/adele/api/1.0/documents/21/validate-translation", **PROF1_USER)
        self.assert200("/adele/api/1.0/documents/21/transcriptions", **PROF1_USER)
        # needs a transcription
        self.assert200("/adele/api/1.0/documents/21/validate-facsimile", **PROF1_USER)
        self.assert200("/adele/api/1.0/documents/21/transcriptions", **PROF1_USER)
        # needs a commentary
        self.assert404("/adele/api/1.0/documents/21/validate-commentaries", **PROF1_USER)
        self.assert200("/adele/api/1.0/documents/21/transcriptions", **PROF1_USER)
        # needs a transcription
        self.assert200("/adele/api/1.0/documents/21/validate-speech-parts", **PROF1_USER)
        self.assert200("/adele/api/1.0/documents/21/transcriptions", **PROF1_USER)

        # TODO: tester la closing_date

    def test_get_transcriptions_from_user(self):
        self.load_fixtures(TestTranscriptionsAPI.FIXTURES)
        self.load_fixtures(TestTranscriptionsAPI.FIXTURES_STU1)

        # doc without transcription
        self.assert403("/adele/api/1.0/documents/21/transcriptions/from-user/100")
        self.assert403("/adele/api/1.0/documents/21/transcriptions/from-user/4")
        self.assert403("/adele/api/1.0/documents/21/transcriptions/from-user/4", **STU1_USER)
        self.assert404("/adele/api/1.0/documents/21/transcriptions/from-user/4", **PROF1_USER)

        # access a validated transcription
        self.load_fixtures(TestTranscriptionsAPI.FIXTURES_PROF)
        self.assert200("/adele/api/1.0/documents/21/validate-transcription", **PROF1_USER)

        self.assert403("/adele/api/1.0/documents/21/transcriptions/from-user/4")
        self.assert403("/adele/api/1.0/documents/21/transcriptions/from-user/4", **STU1_USER)
        self.assert200("/adele/api/1.0/documents/21/transcriptions/from-user/4", **PROF1_USER)

        self.assert403("/adele/api/1.0/documents/21/transcriptions/from-user/5")
        self.assert200("/adele/api/1.0/documents/21/transcriptions/from-user/5", **STU1_USER)
        self.assert403("/adele/api/1.0/documents/21/transcriptions/from-user/5", **STU2_USER)
        self.assert200("/adele/api/1.0/documents/21/transcriptions/from-user/5", **PROF1_USER)

    def test_delete_transcriptions_from_user(self):
        self.assert403("/adele/api/1.0/documents/21/transcriptions/from-user/100", method="DELETE")
        self.assert403("/adele/api/1.0/documents/21/transcriptions/from-user/100", method="DELETE", **STU1_USER)
        self.assert404("/adele/api/1.0/documents/21/transcriptions/from-user/100", method="DELETE", **PROF1_USER)

        self.load_fixtures(TestTranscriptionsAPI.FIXTURES)
        self.load_fixtures(TestTranscriptionsAPI.FIXTURES_PROF)
        self.load_fixtures(TestTranscriptionsAPI.FIXTURES_STU1)
        self.assert200("/adele/api/1.0/documents/21/validate-transcription", **PROF1_USER)

        self.assert403("/adele/api/1.0/documents/21/transcriptions/from-user/4", method="DELETE", **STU1_USER)
        self.assert200("/adele/api/1.0/documents/21/transcriptions/from-user/4", method="DELETE", **PROF1_USER)

        self.assert404("/adele/api/1.0/documents/21/transcriptions")
        self.assert403("/adele/api/1.0/documents/21/transcriptions/from-user/4")
        self.assert404("/adele/api/1.0/documents/21/transcriptions/from-user/4", **PROF1_USER)

        # TODO: tester si on supprime la transcription de reference, faire reculer le flag ?
        #self.assert400("/adele/api/1.0/documents/21/validate-transcription", **PROF1_USER)

    def test_post_transcriptions_from_user(self):
        raise NotImplementedError

    def test_put_transcriptions_from_user(self):
        raise NotImplementedError
