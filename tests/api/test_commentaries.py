from os.path import join
from tests.base_server import TestBaseServer, json_loads, ADMIN_USER, STU1_USER, PROF1_USER, PROF2_USER, STU2_USER


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

    def test_get_commentaries(self):
        self.load_fixtures(TestCommentariesAPI.FIXTURES)

        self.assert404("/adele/api/1.0/documents/20/commentaries/-1")

        # being anonymous
        self.assert403('/adele/api/1.0/documents/20/commentaries/from-user/4')
        self.assert403('/adele/api/1.0/documents/20/commentaries/from-user/5/and-type/1')

        # being student
        # -- access to other ppl coms
        self.assert403('/adele/api/1.0/documents/20/commentaries/from-user/4', **STU1_USER)
        self.assert403('/adele/api/1.0/documents/20/commentaries/from-user/4/and-type/1', **STU1_USER)
        self.assert403('/adele/api/1.0/documents/20/commentaries/from-user/7', **STU1_USER)

        # -- access to my own coms
        r = self.assert200('/adele/api/1.0/documents/20/commentaries/from-user/5', **STU1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(len(r), 2)
        r = self.assert200('/adele/api/1.0/documents/20/commentaries/from-user/5/and-type/1', **STU1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]["type"]["id"], 1)

        # being teacher
        # -- access to other ppl coms
        self.assert200('/adele/api/1.0/documents/20/commentaries/from-user/5', **PROF1_USER)
        self.assert200('/adele/api/1.0/documents/20/commentaries/from-user/5/and-type/1', **PROF1_USER)
        self.assert200('/adele/api/1.0/documents/20/commentaries/from-user/7', **PROF1_USER)

        r = self.assert200('/adele/api/1.0/documents/20/commentaries/from-user/-1', **PROF1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(len(r), 0)

        # -- access to my own coms
        r = self.assert200('/adele/api/1.0/documents/20/commentaries/from-user/4', **PROF1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(len(r), 1)
        r = self.assert200('/adele/api/1.0/documents/20/commentaries/from-user/4/and-type/1', **PROF1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]["type"]["id"], 1)

        # being admin
        self.assert200('/adele/api/1.0/documents/20/commentaries/from-user/5', **ADMIN_USER)
        self.assert200('/adele/api/1.0/documents/20/commentaries/from-user/5/and-type/1', **ADMIN_USER)
        self.assert200('/adele/api/1.0/documents/20/commentaries/from-user/4', **ADMIN_USER)

    def test_get_reference_commentaries(self):
        self.load_fixtures(TestCommentariesAPI.FIXTURES)

        # doc 20 : without reference transcription (so no ref comms)
        r = self.assert200('/adele/api/1.0/documents/20/commentaries/reference')
        r = json_loads(r.data)["data"]
        self.assertEqual(len(r), 0)
        r = self.assert200('/adele/api/1.0/documents/20/commentaries/reference', **PROF1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(len(r), 0)
        r = self.assert200('/adele/api/1.0/documents/20/commentaries/reference', **STU1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(len(r), 0)

        # doc 21 : with reference transcription
        # must get PROF1's comms
        r = self.assert200('/adele/api/1.0/documents/21/commentaries/reference')
        r = json_loads(r.data)["data"]
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]["id"], 21)

        # must get his own comms
        r = self.assert200('/adele/api/1.0/documents/21/commentaries/reference', **PROF1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]["id"], 21)

        # must get PROF1's comms
        r = self.assert200('/adele/api/1.0/documents/21/commentaries/reference', **STU1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]["id"], 21)

    def test_post_commentary(self):
        self.load_fixtures(TestCommentariesAPI.FIXTURES)

        # being anonymous
        self.assert403("/adele/api/1.0/documents/20/commentaries",
                       data={"data": [{"type_id": 4, "content": "COMM 1"}]}, method="POST")

        # being a student
        #   - on a doc without transcription
        self.assert409("/adele/api/1.0/documents/23/commentaries",
                       data={"data": [{"type_id": 3, "content": "COMM 1"}]}, method="POST", **STU1_USER)
        #   - on my own transcription
        r = self.assert200("/adele/api/1.0/documents/21/commentaries",
                           data={"data": [{"type_id": 4, "content": "COMM 21_STU1"}]}, method="POST", **STU1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(len(r), 1)

        self.assertEqual(r[0]["content"], "COMM 21_STU1")
        #   - on another ppl behalf
        self.assert403("/adele/api/1.0/documents/23/commentaries",
                       data={"data": [{"type_id": 3, "content": "COMM 1", "user_id": 4}]}, method="POST", **STU1_USER)
        #   - on an unverified transcription
        self.assert409("/adele/api/1.0/documents/23/commentaries",
                       data={"data": [{"type_id": 3, "content": "COMM 1", "user_id": 5}]}, method="POST", **STU1_USER)
        #   - multiple coms
        r = self.assert200("/adele/api/1.0/documents/21/commentaries",
                           data={"data": [{"type_id": 3, "content": "COMM 21_STU1"},
                                          {"type_id": 5, "content": "COMM 21_STU1"}]}, method="POST", **STU1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(len(r), 2)
        #   - post a commentary with bad data
        self.assert409("/adele/api/1.0/documents/23/commentaries",
                       data={"data": [{"type": 3, "content": "COMM 1"}]}, method="POST", **STU1_USER)
        #   - post a duplicate com (twice the same com type)
        self.assert409("/adele/api/1.0/documents/21/commentaries",
                       data={"data": [{"type_id": 4, "content": "COMM 21_STU1"}]}, method="POST", **STU1_USER)
        # being a teacher
        #   - on a doc without transcription
        #   - on my own transcription
        #   - on another ppl behalf
        #   - on an unverified transcription
        #   - multiple coms
        #   - post a commentary with bad data
        #   - post a duplicate com (twice the same com type)

        # being and admin
        #   - on a doc without transcription
        #   - on my own transcription
        #   - on another ppl behalf
        #   - on an unverified transcription
        #   - multiple coms
        #   - post a commentary with bad data
        #   - post a duplicate com (twice the same com type)

#
#    def test_delete_acte_types(self):
#        self.assert403("/adele/api/1.0/acte-types", method="DELETE")
#        self.assert403("/adele/api/1.0/acte-types", method="DELETE", **STU1_USER)
#        self.assert404("/adele/api/1.0/acte-types/126436", method="DELETE", **ADMIN_USER)
#
#        self.delete_with_auth("/adele/api/1.0/acte-types/19", **ADMIN_USER)
#        self.assert404("/adele/api/1.0/acte-types/19")
#
#        r = self.get('/adele/api/1.0/acte-types')
#        r = json_loads(r.data)["data"]
#        self.assertEqual(len(r), 20)
#
#    def test_put_acte_types(self):
#        self.assert403("/adele/api/1.0/acte-types", data={"data": {}},  method="PUT")
#        self.assert403("/adele/api/1.0/acte-types", data={"data": {}},  method="PUT", **STU1_USER)
#        self.assert409("/adele/api/1.0/acte-types", data={"data": [{"id": 100}]},  method="PUT", **ADMIN_USER)
#
#        self.put_with_auth("/adele/api/1.0/acte-types",
#                           data={"data": [{"id": 19, "label": "PapeTest"}]}, **ADMIN_USER)
#        r = self.get('/adele/api/1.0/acte-types/19')
#        r = json_loads(r.data)["data"]
#        self.assertEqual("PapeTest", r[0]["label"])
#
#        self.put_with_auth("/adele/api/1.0/acte-types",
#                           data={"data": [{"id": 19, "description": "Desc2"}]}, **ADMIN_USER)
#        r = self.get('/adele/api/1.0/acte-types/19')
#        r = json_loads(r.data)["data"]
#        self.assertEqual("Desc2", r[0]["description"])
#
#        # put conflicting data
#        self.assert409("/adele/api/1.0/acte-types",
#                       data={"data": [{"id": -1, "label": "ACTE-TYPT-500", "description": "DESC-500"}]}, method="PUT",
#                       **ADMIN_USER)
#        self.assert409("/adele/api/1.0/acte-types",
#                       data={"data": [{"id": 19, "label": "ACTE-TYPT-501", "description": "DESC-501"},
#                                      {"id": 500, "label": "ACTE-TYPT-502", "description": "DESC-502"}]}, method="PUT",
#                       **PROF1_USER)
#
#        # put multiple data
#        self.assert200("/adele/api/1.0/acte-types",
#                       data={"data": [{"id": 500, "label": "ACTE-TYPT-500", "description": "DESC-500"}]}, method="POST",
#                       **ADMIN_USER)
#
#        self.assert200("/adele/api/1.0/acte-types",
#                       data={"data": [{"id": 19, "label": "ACTE-TYPT-19", "description": "DESC-19"},
#                                      {"id": 500, "label": "ACTE-TYPT-5XX", "description": "DESC-XXX"}]}, method="PUT",
#                       **PROF1_USER)
#
#    def test_api_post_acte_type(self):
#        self.assert403("/adele/api/1.0/acte-types", data={"data": {}},  method="POST")
#        self.assert403("/adele/api/1.0/acte-types", data={"data": {}},  method="POST", **STU1_USER)
#        self.assert409("/adele/api/1.0/acte-types", data={"data": [{"champ bidon": 100}]}, method="POST", **ADMIN_USER)
#
#        self.assert200("/adele/api/1.0/acte-types",
#                       data={"data": [{"id": 500, "label": "ACTE-TYPT-500", "description": "DESC-500"}]}, method="POST", **ADMIN_USER)
#
#        r = self.assert200('/adele/api/1.0/acte-types/500')
#        r = json_loads(r.data)["data"]
#        self.assertEqual(500, r[0]["id"])
#
#        # post conflicting data
#        self.assert409("/adele/api/1.0/acte-types",
#                       data={"data": [{"id": 500, "label": "ACTE-TYPT-500", "description": "DESC-500"}]}, method="POST",
#                       **ADMIN_USER)
#
#        # post multiple data
#        self.assert200("/adele/api/1.0/acte-types",
#                       data={"data": [{"id": 501, "label": "ACTE-TYPT-501", "description": "DESC-501"},
#                                      {"id": 502, "label": "ACTE-TYPT-502", "description": "DESC-502"}]}, method="POST",
#                       **PROF1_USER)
#        self.assert200('/adele/api/1.0/acte-types/501')
#        self.assert200('/adele/api/1.0/acte-types/502')
#
