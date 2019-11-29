import unittest
from os.path import join

from app.models import Commentary
from tests.base_server import TestBaseServer, json_loads, ADMIN_USER, STU1_USER, PROF1_USER, PROF2_USER, STU2_USER


@unittest.skip
class TestCommentariesAPI(TestBaseServer):
    FIXTURES = [
        join(TestBaseServer.FIXTURES_PATH, "documents", "doc_20.sql"),
        join(TestBaseServer.FIXTURES_PATH, "commentaries", "commentary_doc_20.sql"),

        join(TestBaseServer.FIXTURES_PATH, "documents", "doc_21.sql"),
        join(TestBaseServer.FIXTURES_PATH, "transcriptions", "transcription_doc_21_prof1.sql"),
        join(TestBaseServer.FIXTURES_PATH, "commentaries", "commentary_doc_21.sql"),

        join(TestBaseServer.FIXTURES_PATH, "documents", "doc_22.sql"),
        join(TestBaseServer.FIXTURES_PATH, "documents", "doc_23.sql"),
    ]

    def reload_fixtures(self):
        self.clear_data()
        self.load_fixtures(TestBaseServer.BASE_FIXTURES)
        self.load_fixtures(TestCommentariesAPI.FIXTURES)

    def test_get_commentaries(self):
        self.load_fixtures(TestCommentariesAPI.FIXTURES)

        self.assert404("/api/1.0/documents/20/commentaries/-1")

        # being anonymous
        self.assert403('/api/1.0/documents/20/commentaries/from-user/4')
        self.assert403('/api/1.0/documents/20/commentaries/from-user/5/and-type/1')

        # being student
        # -- access to other ppl coms
        self.assert403('/api/1.0/documents/20/commentaries/from-user/4', **STU1_USER)
        self.assert403('/api/1.0/documents/20/commentaries/from-user/4/and-type/1', **STU1_USER)
        self.assert403('/api/1.0/documents/20/commentaries/from-user/7', **STU1_USER)

        # -- access to my own coms
        r = self.assert200('/api/1.0/documents/20/commentaries/from-user/5', **STU1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(2, len(r))
        r = self.assert200('/api/1.0/documents/20/commentaries/from-user/5/and-type/1', **STU1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(1, len(r))
        self.assertEqual(1, r[0]["type"]["id"])

        # being teacher
        # -- access to other ppl coms
        self.assert200('/api/1.0/documents/20/commentaries/from-user/5', **PROF1_USER)
        self.assert200('/api/1.0/documents/20/commentaries/from-user/5/and-type/1', **PROF1_USER)
        self.assert200('/api/1.0/documents/20/commentaries/from-user/7', **PROF1_USER)

        r = self.assert200('/api/1.0/documents/20/commentaries/from-user/-1', **PROF1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(0, len(r))

        # -- access to my own coms
        r = self.assert200('/api/1.0/documents/20/commentaries/from-user/4', **PROF1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(1, len(r))
        r = self.assert200('/api/1.0/documents/20/commentaries/from-user/4/and-type/1', **PROF1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(1, len(r))
        self.assertEqual(r[0]["type"]["id"], 1)

        # being admin
        self.assert200('/api/1.0/documents/20/commentaries/from-user/5', **ADMIN_USER)
        self.assert200('/api/1.0/documents/20/commentaries/from-user/5/and-type/1', **ADMIN_USER)
        self.assert200('/api/1.0/documents/20/commentaries/from-user/4', **ADMIN_USER)

    def test_get_reference_commentaries(self):
        self.load_fixtures(TestCommentariesAPI.FIXTURES)
        self.assert200("/api/1.0/documents/21/validate-commentaries", **PROF1_USER)

        # doc 20 : without reference transcription (so no ref comms)
        r = self.assert200('/api/1.0/documents/20/commentaries/reference')
        r = json_loads(r.data)["data"]
        self.assertEqual(0, len(r))
        r = self.assert200('/api/1.0/documents/20/commentaries/reference', **PROF1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(0, len(r))
        r = self.assert200('/api/1.0/documents/20/commentaries/reference', **STU1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(0, len(r))

        # doc 21 : with reference transcription
        # must get PROF1's comms
        r = self.assert200('/api/1.0/documents/21/commentaries/reference')
        r = json_loads(r.data)["data"]
        self.assertEqual(1, len(r))
        self.assertEqual(r[0]["id"], 21)

        # must get his own comms
        r = self.assert200('/api/1.0/documents/21/commentaries/reference', **PROF1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(1, len(r))
        self.assertEqual(r[0]["id"], 21)

        # must get PROF1's comms
        r = self.assert200('/api/1.0/documents/21/commentaries/reference', **STU1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(1, len(r))
        self.assertEqual(r[0]["id"], 21)

        # get comm reference of type
        r = self.assert200('/api/1.0/documents/21/commentaries/reference/of-type/1', **STU1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(1, len(r))
        r = self.assert200('/api/1.0/documents/21/commentaries/reference/of-type/2', **STU1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(0, len(r))

    def test_post_commentary_ano(self):
        self.load_fixtures(TestCommentariesAPI.FIXTURES)

        # being anonymous
        self.assert403("/api/1.0/documents/20/commentaries",
                       data={"data": [{"type_id": 4, "content": "COMM 1"}]}, method="POST")

    def test_post_commentary_stu(self):
        self.load_fixtures(TestCommentariesAPI.FIXTURES)

        # being a student
        #   - on a doc without transcription
        self.assert400("/api/1.0/documents/23/commentaries",
                       data={"data": [{"type_id": 3, "content": "COMM 1"}]}, method="POST", **STU1_USER)
        #   - on my own transcription
        r = self.assert200("/api/1.0/documents/21/commentaries",
                           data={"data": [{"type_id": 4, "content": "COMM 21_STU1"}]}, method="POST", **STU1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(1, len(r))

        self.assertEqual(r[0]["content"], "COMM 21_STU1")
        #   - on another ppl behalf
        self.assert403("/api/1.0/documents/21/commentaries",
                       data={"data": [{"type_id": 3, "content": "COMM 1", "user_id": 4}]}, method="POST", **STU1_USER)
        #   - on an unverified transcription
        self.assert400("/api/1.0/documents/23/commentaries",
                       data={"data": [{"type_id": 3, "content": "COMM 1", "user_id": 5}]}, method="POST", **STU1_USER)
        #   - multiple coms
        r = self.assert200("/api/1.0/documents/21/commentaries",
                           data={"data": [{"type_id": 3, "content": "COMM 21_STU1"},
                                          {"type_id": 5, "content": "COMM 21_STU1"}]}, method="POST", **STU1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(2, len(r))
        #   - post a commentary with bad data
        self.assert400("/api/1.0/documents/23/commentaries",
                       data={"data": [{"type": 3, "content": "COMM 1"}]}, method="POST", **STU1_USER)
        #   - post a duplicate com (twice the same com type)
        self.assert400("/api/1.0/documents/21/commentaries",
                       data={"data": [{"type_id": 4, "content": "COMM 21_STU1"}]}, method="POST", **STU1_USER)

    def test_post_commentary_teacher(self):
        self.load_fixtures(TestCommentariesAPI.FIXTURES)

        # being a teacher
        #   - on a doc without transcription
        self.assert400("/api/1.0/documents/23/commentaries",
                       data={"data": [{"type_id": 3, "content": "COMM 1"}]}, method="POST", **PROF1_USER)
        #   - on my own transcription
        r = self.assert200("/api/1.0/documents/21/commentaries",
                           data={"data": [{"type_id": 4, "content": "COMM 21_PROF1"}]}, method="POST", **PROF1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(1, len(r))

        self.assertEqual(r[0]["content"], "COMM 21_PROF1")
        #   - on another ppl behalf
        r = self.assert200("/api/1.0/documents/21/commentaries",
                           data={"data": [{"type_id": 3, "content": "COMM 1", "user_id": 5}]}, method="POST", **PROF1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(1, len(r))
        #   - on an unverified transcription
        self.assert400("/api/1.0/documents/23/commentaries",
                       data={"data": [{"type_id": 3, "content": "COMM 1"}]}, method="POST", **PROF1_USER)
        #   - multiple coms
        r = self.assert200("/api/1.0/documents/21/commentaries",
                           data={"data": [{"type_id": 3, "content": "COMM 21_STU1"},
                                          {"type_id": 5, "content": "COMM 21_STU1"}]}, method="POST", **PROF1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(2, len(r))
        #   - post a commentary with bad data
        self.assert400("/api/1.0/documents/23/commentaries",
                       data={"data": [{"type": 3, "content": "COMM 1"}]}, method="POST", **PROF1_USER)
        #   - post a duplicate com (twice the same com type)
        self.assert400("/api/1.0/documents/21/commentaries",
                       data={"data": [{"type_id": 4, "content": "COMM 21_PROF1"}]}, method="POST", **PROF1_USER)

    def test_post_commentary_admin(self):
        self.load_fixtures(TestCommentariesAPI.FIXTURES)

        # being an admin
        #   - on a doc without transcription
        self.assert400("/api/1.0/documents/23/commentaries",
                       data={"data": [{"type_id": 3, "content": "COMM 1"}]}, method="POST", **ADMIN_USER)
        #   - on my own transcription
        r = self.assert200("/api/1.0/documents/21/commentaries",
                           data={"data": [{"type_id": 4, "content": "COMM 21_ADMIN"}]}, method="POST", **ADMIN_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(1, len(r))

        self.assertEqual(r[0]["content"], "COMM 21_ADMIN")
        #   - on another ppl behalf
        r = self.assert200("/api/1.0/documents/21/commentaries",
                           data={"data": [{"type_id": 3, "content": "COMM 1", "user_id": 5}]}, method="POST",
                           **ADMIN_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(1, len(r))
        #   - on an unverified transcription
        self.assert400("/api/1.0/documents/23/commentaries",
                       data={"data": [{"type_id": 3, "content": "COMM 1"}]}, method="POST", **ADMIN_USER)
        #   - multiple coms
        r = self.assert200("/api/1.0/documents/21/commentaries",
                           data={"data": [{"type_id": 3, "content": "COMM 21_ADMIN"},
                                          {"type_id": 5, "content": "COMM 21_ADMIN"}]}, method="POST", **ADMIN_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(2, len(r))
        #   - post a commentary with bad data
        self.assert400("/api/1.0/documents/23/commentaries",
                       data={"data": [{"type": 3, "content": "COMM 1"}]}, method="POST", **ADMIN_USER)
        #   - post a duplicate com (twice the same com type)
        self.assert400("/api/1.0/documents/21/commentaries",
                       data={"data": [{"type_id": 4, "content": "COMM 21_PROF1"}]}, method="POST", **ADMIN_USER)

    def test_put_commentary_ano(self):
        self.load_fixtures(TestCommentariesAPI.FIXTURES)
        # being anonymous
        self.assert403("/api/1.0/documents/20/commentaries",
                       data={"data": [{
                           "doc_id": 20,
                           "user_id": 4,
                           "type_id": 2,
                           "content": "This is a commentary"
                       }]}, method="PUT")

    def test_put_commentary_stu(self):
        self.load_fixtures(TestCommentariesAPI.FIXTURES)

        # being a student
        #   - on my own transcription
        r = self.assert200("/api/1.0/documents/21/commentaries",
                           data={"data": [{"type_id": 4, "content": "COMM 21_STU1"}]}, method="POST", **STU1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(1, len(r))
        self.assertEqual(r[0]["content"], "COMM 21_STU1")
        r = self.assert200("/api/1.0/documents/21/commentaries",
                           data={"data": [{"type_id": 4, "content": "MODIFIED"}]}, method="PUT", **STU1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(1, len(r))
        self.assertEqual(r[0]["content"], "MODIFIED")

        #   - on another ppl behalf
        self.assert403("/api/1.0/documents/21/commentaries",
                       data={"data": [{"type_id": 3, "content": "COMM 1", "user_id": 4}]}, method="PUT", **STU1_USER)
        #   - multiple coms
        r = self.assert200("/api/1.0/documents/21/commentaries",
                           data={"data": [{"type_id": 1, "content": "MODIFIED 1"},
                                          {"type_id": 2, "content": "MODIFIED 2"}]}, method="PUT", **STU1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(2, len(r))
        #   - put a commentary with bad data
        self.assert400("/api/1.0/documents/23/commentaries",
                       data={"data": [{"type": 3, "content": "COMM 1"}]}, method="PUT", **STU1_USER)

    def test_put_commentary_teacher(self):
        self.load_fixtures(TestCommentariesAPI.FIXTURES)

        # being a teacher
        #   - on my own transcription
        r = self.assert200("/api/1.0/documents/21/commentaries",
                           data={"data": [{"type_id": 4, "content": "COMM 21_PROF1"}]}, method="POST", **PROF1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(1, len(r))
        self.assertEqual(r[0]["content"], "COMM 21_PROF1")
        r = self.assert200("/api/1.0/documents/21/commentaries",
                           data={"data": [{"type_id": 4, "content": "MODIFIED"}]}, method="PUT", **PROF1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(1, len(r))
        self.assertEqual(r[0]["content"], "MODIFIED")

        #   - on another ppl behalf
        r = self.assert200("/api/1.0/documents/21/commentaries",
                       data={"data": [{"type_id": 1, "content": "COMM 1 MODIFIED", "user_id": 5}]}, method="PUT", **PROF1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(1, len(r))
        self.assertEqual(r[0]["user_id"], 5)

        #   - multiple coms
        r = self.assert200("/api/1.0/documents/21/commentaries",
                           data={"data": [{"type_id": 1, "content": "MODIFIED 1", "user_id": 5},
                                          {"type_id": 2, "content": "MODIFIED 2", "user_id": 5}]}, method="PUT", **PROF1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(2, len(r))
        for rd in r:
            self.assertEqual(rd["user_id"], 5)

    def test_put_commentary_admin(self):
        self.load_fixtures(TestCommentariesAPI.FIXTURES)

        # being an admin

        #   - on another ppl behalf
        r = self.assert200("/api/1.0/documents/21/commentaries",
                           data={"data": [{"type_id": 1, "content": "COMM 1 MODIFIED", "user_id": 5}]}, method="PUT",
                           **ADMIN_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(1, len(r))
        self.assertEqual(r[0]["user_id"], 5)

        #   - multiple coms
        r = self.assert200("/api/1.0/documents/21/commentaries",
                           data={"data": [{"type_id": 1, "content": "MODIFIED 1", "user_id": 5},
                                          {"type_id": 2, "content": "MODIFIED 2", "user_id": 5}]}, method="PUT",
                           **ADMIN_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(2, len(r))
        for rd in r:
            self.assertEqual(rd["user_id"], 5)

    def test_delete_commentary_ano(self):
        self.load_fixtures(TestCommentariesAPI.FIXTURES)
        self.assert403("/api/1.0/documents/20/commentaries", method="DELETE")
        self.assert403("/api/1.0/documents/20/commentaries/from-user/5", method="DELETE")
        self.assert403("/api/1.0/documents/20/commentaries/of-type/2", method="DELETE")
        self.assert403("/api/1.0/documents/20/commentaries/from-user/5/and-type/2", method="DELETE")

    def test_delete_commentary_stu(self):
        self.load_fixtures(TestCommentariesAPI.FIXTURES)
        # - when there is no com
        self.assert200("/api/1.0/documents/23/commentaries", method="DELETE", **STU1_USER)
        # - on other ppl behalf
        self.assert403("/api/1.0/documents/20/commentaries/from-user/4", method="DELETE", **STU1_USER)

        self.reload_fixtures()
        r = self.assert200('/api/1.0/documents/20/commentaries/from-user/5', **STU1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(2, len(r))
        # delete only type_id = 2
        self.assert200("/api/1.0/documents/20/commentaries/of-type/2", method="DELETE", **STU1_USER)
        r = self.assert200('/api/1.0/documents/20/commentaries/from-user/5', **STU1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(1, len(r))

        self.reload_fixtures()
        r = self.assert200('/api/1.0/documents/20/commentaries/from-user/5', **STU1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(2, len(r))
        self.assert200("/api/1.0/documents/20/commentaries/from-user/5/and-type/2", method="DELETE", **STU1_USER)
        r = self.assert200('/api/1.0/documents/20/commentaries/from-user/5', **STU1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(1, len(r))

    def test_delete_commentary_teacher(self):
        self.load_fixtures(TestCommentariesAPI.FIXTURES)
        # - when there is no com
        self.assert200("/api/1.0/documents/23/commentaries", method="DELETE", **PROF1_USER)
        # - on other ppl behalf
        self.assert200("/api/1.0/documents/20/commentaries/from-user/4", method="DELETE", **PROF1_USER)

        self.reload_fixtures()
        r = self.assert200('/api/1.0/documents/20/commentaries/from-user/5', **PROF1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(2, len(r))
        self.assert200("/api/1.0/documents/20/commentaries/of-type/2", method="DELETE", **PROF1_USER)
        r = self.assert200('/api/1.0/documents/20/commentaries/from-user/5', **PROF1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(1, len(r))

        self.reload_fixtures()
        r = self.assert200('/api/1.0/documents/20/commentaries/from-user/5', **PROF1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(2, len(r))
        self.assert200("/api/1.0/documents/20/commentaries/from-user/5/and-type/2", method="DELETE", **PROF1_USER)
        r = self.assert200('/api/1.0/documents/20/commentaries/from-user/5', **PROF1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(1, len(r))

    def test_delete_commentary_admin(self):
        self.load_fixtures(TestCommentariesAPI.FIXTURES)
        # - when there is no com
        self.assert200("/api/1.0/documents/23/commentaries", method="DELETE", **ADMIN_USER)
        # - on other ppl behalf
        self.assert200("/api/1.0/documents/20/commentaries/from-user/4", method="DELETE", **ADMIN_USER)

        self.reload_fixtures()
        r = self.assert200('/api/1.0/documents/20/commentaries/from-user/5', **ADMIN_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(2, len(r))
        self.assert200("/api/1.0/documents/20/commentaries/of-type/2", method="DELETE", **ADMIN_USER)
        r = self.assert200('/api/1.0/documents/20/commentaries/from-user/5', **ADMIN_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(1, len(r))

        self.reload_fixtures()
        r = self.assert200('/api/1.0/documents/20/commentaries/from-user/5', **ADMIN_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(2, len(r))
        self.assert200("/api/1.0/documents/20/commentaries/from-user/5/and-type/2", method="DELETE", **ADMIN_USER)
        r = self.assert200('/api/1.0/documents/20/commentaries/from-user/5', **ADMIN_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(1, len(r))
