import datetime
from os.path import join

from app import db
from app.models import Document, Note,  VALIDATION_TRANSCRIPTION, VALIDATION_NONE
from tests.base_server import TestBaseServer, json_loads, ADMIN_USER, STU1_USER, PROF1_USER, PROF2_USER, STU2_USER, \
    PROF3_USER


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

    # eleve: id = 7
    FIXTURES_STU2 = [
        join(TestBaseServer.FIXTURES_PATH, "transcriptions", "transcription_doc_21_stu2.sql"),
        join(TestBaseServer.FIXTURES_PATH, "notes", "notes_transcription_doc_21_stu2.sql"),
    ]

    FIXTURES_TL_STU2 = [
        join(TestBaseServer.FIXTURES_PATH, "translations", "translation_doc_21_stu2.sql"),
        join(TestBaseServer.FIXTURES_PATH, "notes", "notes_translation_doc_21_stu2.sql"),
    ]


    def test_get_transcriptions_reference(self):
        self.load_fixtures(TestTranscriptionsAPI.FIXTURES)

        # doc without transcription
        self.assert404("/api/1.0/documents/21/transcriptions")
        self.assert404("/api/1.0/documents/21/transcriptions", **STU1_USER)
        self.assert404("/api/1.0/documents/21/transcriptions", **PROF1_USER)

        # access a validated transcription
        self.load_fixtures(TestTranscriptionsAPI.FIXTURES_PROF)
        self.load_fixtures(TestTranscriptionsAPI.FIXTURES_STU1)

        self.assert200("/api/1.0/documents/21/validate-transcription", **PROF1_USER)
        r = self.assert200("/api/1.0/documents/21/transcriptions", **PROF1_USER)
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
        self.assert200("/api/1.0/documents/21/transcriptions")
        self.assert200("/api/1.0/documents/21/transcriptions", **STU1_USER)

        # -------- test validation steps ---------
        self.assert200("/api/1.0/documents/21/unvalidate-transcription", **PROF1_USER)
        self.assert404("/api/1.0/documents/21/transcriptions", **PROF1_USER)
        # needs a transcription
        self.assert200("/api/1.0/documents/21/validate-transcription", **PROF1_USER)
        self.assert200("/api/1.0/documents/21/transcriptions", **PROF1_USER)
        # needs a translation
        self.assert404("/api/1.0/documents/21/validate-translation", **PROF1_USER)
        self.assert200("/api/1.0/documents/21/transcriptions", **PROF1_USER)
        # needs a transcription
        self.assert200("/api/1.0/documents/21/validate-facsimile", **PROF1_USER)
        self.assert200("/api/1.0/documents/21/transcriptions", **PROF1_USER)
        # needs a commentary
        self.assert404("/api/1.0/documents/21/validate-commentaries", **PROF1_USER)
        self.assert200("/api/1.0/documents/21/transcriptions", **PROF1_USER)
        # needs a transcription
        self.assert200("/api/1.0/documents/21/validate-speech-parts", **PROF1_USER)
        self.assert200("/api/1.0/documents/21/transcriptions", **PROF1_USER)

    def test_get_transcriptions_from_user(self):
        self.load_fixtures(TestTranscriptionsAPI.FIXTURES)
        self.load_fixtures(TestTranscriptionsAPI.FIXTURES_STU1)

        # doc without transcription
        self.assert401("/api/1.0/documents/21/transcriptions/from-user/100")
        self.assert401("/api/1.0/documents/21/transcriptions/from-user/4")
        self.assert403("/api/1.0/documents/21/transcriptions/from-user/4", **STU1_USER)
        self.assert404("/api/1.0/documents/21/transcriptions/from-user/4", **PROF1_USER)

        # access a validated transcription
        self.load_fixtures(TestTranscriptionsAPI.FIXTURES_PROF)
        self.assert200("/api/1.0/documents/21/validate-transcription", **PROF1_USER)

        self.assert401("/api/1.0/documents/21/transcriptions/from-user/4")
        self.assert403("/api/1.0/documents/21/transcriptions/from-user/4", **STU1_USER)
        self.assert200("/api/1.0/documents/21/transcriptions/from-user/4", **PROF1_USER)

        self.assert401("/api/1.0/documents/21/transcriptions/from-user/5")
        self.assert200("/api/1.0/documents/21/transcriptions/from-user/5", **STU1_USER)
        self.assert403("/api/1.0/documents/21/transcriptions/from-user/5", **STU2_USER)
        self.assert200("/api/1.0/documents/21/transcriptions/from-user/5", **PROF1_USER)

    def test_delete_transcriptions_from_user(self):
        self.assert401("/api/1.0/documents/21/transcriptions/from-user/100", method="DELETE")
        self.assert403("/api/1.0/documents/21/transcriptions/from-user/100", method="DELETE", **STU1_USER)
        self.assert404("/api/1.0/documents/21/transcriptions/from-user/100", method="DELETE", **PROF1_USER)

        self.load_fixtures(TestTranscriptionsAPI.FIXTURES)
        self.load_fixtures(TestTranscriptionsAPI.FIXTURES_PROF)
        self.load_fixtures(TestTranscriptionsAPI.FIXTURES_STU1)

        self.assert200("/api/1.0/documents/21/validate-transcription", **PROF1_USER)
        # should not be able to delete the student transcription when the transcription has already been validated
        self.assert403("/api/1.0/documents/21/transcriptions/from-user/5", method="DELETE", **STU1_USER)
        self.assert200("/api/1.0/documents/21/unvalidate-transcription", **PROF1_USER)

        # test that bound notes are deleted when student deletes its own transcription
        self.assert200("/api/1.0/documents/21/transcriptions/from-user/5", method="DELETE", **STU1_USER)
        notes = Note.query.filter(Note.user_id == 5).all()
        self.assertEqual(0, len(notes))

        # test that bound notes are deleted too for teacher deletes its  transcription
        prof_notes = Note.query.filter(Note.user_id == 4).all()
        other_notes_cnt = len(Note.query.filter(Note.user_id != 4).all())
        self.assertNotEqual(0, len(prof_notes))

        self.assert200("/api/1.0/documents/21/validate-transcription", **PROF1_USER)
        doc = Document.query.filter(Document.id == 21).first()
        self.assertEqual(VALIDATION_TRANSCRIPTION, doc.validation_step)
        self.assert200("/api/1.0/documents/21/transcriptions/from-user/4", method="DELETE", **PROF1_USER)
        self.assertEqual(0, len(Note.query.filter(Note.user_id == 4).all()))
        self.assertEqual(other_notes_cnt, len(Note.query.filter(Note.user_id != 4).all()))

        # check that the validation step rolled back to None
        doc = Document.query.filter(Document.id == 21).first()
        self.assertEqual(VALIDATION_NONE, doc.validation_step)

        # test that the resource is not available anymore
        self.assert404("/api/1.0/documents/21/transcriptions")
        self.assert401("/api/1.0/documents/21/transcriptions/from-user/4")
        self.assert404("/api/1.0/documents/21/transcriptions/from-user/4", **PROF1_USER)

        # test when the document is closed
        doc = Document.query.filter(Document.id == 21).first()
        doc.date_closing = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        db.session.add(doc)
        db.session.commit()

        self.load_fixtures(TestTranscriptionsAPI.FIXTURES_STU1)

        self.assert403("/api/1.0/documents/21/transcriptions/from-user/5", method="DELETE", **STU1_USER)
        self.assert200("/api/1.0/documents/21/transcriptions/from-user/5", method="DELETE", **PROF1_USER)

    def test_post_transcriptions_from_user(self):
        self.load_fixtures(TestTranscriptionsAPI.FIXTURES)
        small_tr = {"data": {"content": "tr"}}
        self.assert401("/api/1.0/documents/21/transcriptions/from-user/100", data=small_tr, method="POST")
        self.assert403("/api/1.0/documents/21/transcriptions/from-user/100", data=small_tr, method="POST",
                       **STU1_USER)
        self.assert400("/api/1.0/documents/21/transcriptions/from-user/100", data=small_tr, method="POST",
                       **PROF1_USER)

        # =================== STUDENT ===================
        self.load_fixtures(TestTranscriptionsAPI.FIXTURES_PROF)
        self.assert200("/api/1.0/documents/21/validate-transcription", **PROF1_USER)
        # post when the transcription is already validated
        self.assert403("/api/1.0/documents/21/transcriptions/from-user/5",
                       data={"data": {"notes": [], "content": "test"}}, method="POST",
                       **STU1_USER)
        # clean up teacher transcription
        self.assert200("/api/1.0/documents/21/unvalidate-transcription", **PROF1_USER)
        self.assert200("/api/1.0/documents/21/transcriptions/from-user/4", method="DELETE", **PROF1_USER)

        # post notes without content
        self.assert404("/api/1.0/documents/21/transcriptions/from-user/5",
                       data={"data": {"notes": []}}, method="POST",
                       **STU1_USER)
        # post content without notes
        r = self.assert200("/api/1.0/documents/21/transcriptions/from-user/5",
                           data={"data": {"content": "new tr from user1"}}, method="POST",
                           **STU1_USER)
        r = json_loads(r.data)['data']
        self.assertEqual('new tr from user1', r['content'])
        self.assertEqual(0, len(r['notes']))
        self.assertEqual(5, r['user_id'])

        # post content with notes
        r = self.assert200("/api/1.0/documents/21/transcriptions/from-user/7",
                           data={"data": {
                               "content": "new tr from user2",
                               "notes": [{
                                   "content": "note1 from user2",
                                   "ptr_start": 0,
                                   "ptr_end": 3
                               },
                                   {
                                       "content": "note2 from user2",
                                       "ptr_start": 4,
                                       "ptr_end": 6
                                   }
                               ]
                           }}, method="POST",
                           **STU2_USER)

        r = json_loads(r.data)['data']
        self.assertEqual('new tr from user2', r['content'])
        self.assertEqual(2, len(r['notes']))
        self.assertEqual(7, r['user_id'])
        expected_fragments = ['new', 'tr']
        for i, note in enumerate(r['notes']):
            self.assertPtr(r['content'], note['ptr_start'], note['ptr_end'], expected_fragments[i])

        # =================== TEACHER ===================
        doc = Document.query.filter(Document.id == 21).first()
        doc.date_closing = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        db.session.add(doc)
        db.session.commit()
        r = self.assert200("/api/1.0/documents/21/transcriptions/from-user/4",
                           data={
                               "data": {
                                    "content": "new tr from prof1",
                                    "notes": [
                                        {
                                            "content": "note1 from prof1",
                                            "ptr_start": 0,
                                            "ptr_end": 3
                                        },
                                        {
                                             "content": "note2 from prof1",
                                             "ptr_start": 4,
                                             "ptr_end": 6
                                        }
                                    ]
                               }
                           }, method="POST",
                           **PROF1_USER)
        r = json_loads(r.data)['data']
        self.assertEqual(2, len(r['notes']))
        # ===============================================

        # post only notes with reusing of translation notes
        self.assert200("/api/1.0/documents/21/validate-transcription", **PROF1_USER)
        self.load_fixtures(TestTranscriptionsAPI.FIXTURES_TL_STU2)
        r = self.assert200("/api/1.0/documents/21/translations/from-user/7", **STU2_USER)
        # TODO: test reusing the freshly inserted notes
        # TODO: POST (id + ptrs)
        r = self.assert200("/api/1.0/documents/21/transcriptions/from-user/7", **STU2_USER)
        r = json_loads(r.data)['data']
        # the two old notes + the new one from the translation side
        self.assertEqual(3, len(r['notes']))

        # test when the document is closed for other users
        self.assert403("/api/1.0/documents/21/transcriptions/from-user/6",
                       data={"data": {"content": "tr created by stu2"}},
                       method="POST", **STU2_USER)
        self.assert403("/api/1.0/documents/21/transcriptions/from-user/8",
                       data={"data": {"content": "tr created by prof3"}},
                       method="POST", **PROF3_USER)

    def test_put_transcriptions_from_user(self):
        self.load_fixtures(TestTranscriptionsAPI.FIXTURES)

        small_tr = {"data": {"content": "tr"}}
        self.assert401("/api/1.0/documents/21/transcriptions/from-user/5", data=small_tr, method="PUT")
        self.assert404("/api/1.0/documents/21/transcriptions/from-user/5", data=small_tr, method="PUT",
                       **STU1_USER)
        self.assert404("/api/1.0/documents/21/transcriptions/from-user/5", data=small_tr, method="PUT",
                       **PROF1_USER)

        self.load_fixtures(TestTranscriptionsAPI.FIXTURES_PROF)
        self.load_fixtures(TestTranscriptionsAPI.FIXTURES_STU1)

        self.assert403("/api/1.0/documents/21/transcriptions/from-user/4",
                       data={"data": {"content": "modification from user1"}},
                       method="PUT",
                       **STU1_USER)

        r = self.assert200("/api/1.0/documents/21/transcriptions/from-user/5",
                           data={"data": {"content": "modification from user1"}},
                           method="PUT",
                           **STU1_USER)
        r = json_loads(r.data)['data']
        self.assertEqual("modification from user1", r['content'])

        r = self.assert200("/api/1.0/documents/21/transcriptions/from-user/5",
                           data={"data": {"content": "modification from prof1"}},
                           method="PUT",
                           **PROF1_USER)
        r = json_loads(r.data)['data']
        self.assertEqual("modification from prof1", r['content'])

        # let's validate the doc 21
        self.assert200("/api/1.0/documents/21/validate-transcription", **PROF1_USER)
        # teacher can modify both
        r = self.assert200("/api/1.0/documents/21/transcriptions/from-user/4",
                           data={"data": {"content": "modification from prof1 after validation"}},
                           method="PUT",
                           **PROF1_USER)
        r = json_loads(r.data)['data']
        self.assertEqual("modification from prof1 after validation", r['content'])

        r = self.assert200("/api/1.0/documents/21/transcriptions/from-user/5",
                           data={"data": {"content": "modification from prof1 after validation"}},
                           method="PUT",
                           **PROF1_USER)
        r = json_loads(r.data)['data']
        self.assertEqual("modification from prof1 after validation", r['content'])

        # user cannot modify when it's validated
        self.assert403("/api/1.0/documents/21/transcriptions/from-user/5",
                       data={"data": {"content": "modification from user& after validation"}},
                       method="PUT",
                       **STU1_USER)

        self.assert200("/api/1.0/documents/21/transcriptions/from-user/4", method="DELETE", **PROF1_USER)
        # can modify again since the teacher deleted its transcription
        self.assert200("/api/1.0/documents/21/transcriptions/from-user/5",
                       data={"data": {"content": "modification from user& after validation"}},
                       method="PUT",
                       **STU1_USER)

        # test when the document is closed
        doc = Document.query.filter(Document.id == 21).first()
        doc.date_closing = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        db.session.add(doc)
        db.session.commit()
        self.assert403("/api/1.0/documents/21/transcriptions/from-user/5",
                       data={"data": {"content": "tr modified by stu1"}},
                       method="PUT", **STU1_USER)
        self.assert200("/api/1.0/documents/21/transcriptions/from-user/5",
                       data={"data": {"content": "tr modified by prof1"}},
                       method="PUT", **PROF1_USER)

    def test_clone_transcription(self):
        self.load_fixtures(TestTranscriptionsAPI.FIXTURES)
        # access a validated transcription
        self.load_fixtures(TestTranscriptionsAPI.FIXTURES_PROF)
        self.assert200("/api/1.0/documents/21/transcriptions/from-user/4", **PROF1_USER)

        self.assert401("/api/1.0/documents/21/transcriptions/clone/from-user/100")
        self.assert404("/api/1.0/documents/21/transcriptions/clone/from-user/100", **PROF1_USER)
        self.assert404("/api/1.0/documents/2132/transcriptions/clone/from-user/100", **PROF1_USER)

        # clone student 2 tr
        self.load_fixtures(TestTranscriptionsAPI.FIXTURES_STU2)
        self.assert200("/api/1.0/documents/21/transcriptions/from-user/7", **PROF1_USER)
        self.assert200("/api/1.0/documents/21/transcriptions/clone/from-user/7", **PROF1_USER)

        # check the prof content is cloned from stu 2
        r = self.assert200("/api/1.0/documents/21/transcriptions/from-user/4", **PROF1_USER)
        r = json_loads(r.data)['data']

        self.assertEqual("transcription stu2", r["content"])
        self.assertEqual('<p>NOTE 1 STU2</p>', r['notes'][0]['content'])
        self.assertEqual('<p>NOTE 2 STU2</p>', r['notes'][1]['content'])
