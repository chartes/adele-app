from os.path import join
from tests.base_server import TestBaseServer, json_loads, ADMIN_USER, STU1_USER, PROF1_USER, PROF2_USER


class TestEditorTypesAPI(TestBaseServer):

    def test_get_editors(self):
        self.assert404("/api/1.0/editors/100")

        r = self.assert200('/api/1.0/editors')
        r = json_loads(r.data)["data"]
        self.assertEqual(1, len(r))

        r = self.assert200('/api/1.0/editors/1')
        r = json_loads(r.data)["data"]
        self.assertEqual(1, r[0]["id"])

    def test_delete_editors(self):
        self.assert401("/api/1.0/editors", method="DELETE")
        self.assert403("/api/1.0/editors", method="DELETE", **STU1_USER)

        self.delete_with_auth("/api/1.0/editors/1", **ADMIN_USER)
        self.assert404("/api/1.0/editors/1")

        r = self.assert200('/api/1.0/editors')
        r = json_loads(r.data)["data"]
        self.assertEqual(0, len(r))

    def test_put_editors(self):
        self.assert401("/api/1.0/editors", data={"data": [{}]},  method="PUT")
        self.assert403("/api/1.0/editors", data={"data": [{}]},  method="PUT", **STU1_USER)
        self.assert409("/api/1.0/editors", data={"data": [{"id": 100}]},  method="PUT", **ADMIN_USER)

        self.assert200("/api/1.0/editors", data={"data": [{"id": 1, "ref": "PapeTest"}]}, method="PUT", **ADMIN_USER)
        r = self.assert200('/api/1.0/editors/1')
        r = json_loads(r.data)["data"]
        self.assertEqual("PapeTest", r[0]["ref"])

        self.assert200("/api/1.0/editors", data={"data": [{"id": 1, "name": "Desc2"}]}, method="PUT", **ADMIN_USER)
        r = self.assert200('/api/1.0/editors/1')
        r = json_loads(r.data)["data"]
        self.assertEqual("Desc2", r[0]["name"])

        # put conflicting data
        self.assert409("/api/1.0/editors",
                       data={"data": [{"id": -1, "ref": "EDITOR-TYPT-500", "name": "DESC-500"}]}, method="PUT",
                       **ADMIN_USER)
        self.assert409("/api/1.0/editors",
                       data={"data": [{"id": 1, "ref": "EDITOR-TYPT-501", "name": "DESC-501"},
                                      {"id": 500, "ref": "EDITOR-TYPT-502", "name": "DESC-502"}]}, method="PUT",
                       **PROF1_USER)

        # put multiple data
        self.assert200("/api/1.0/editors",
                       data={"data": [{"id": 500, "ref": "EDITOR-TYPT-500", "name": "DESC-500"}]}, method="POST",
                       **ADMIN_USER)

        self.assert200("/api/1.0/editors",
                       data={"data": [{"id": 1, "ref": "EDITOR-TYPT-1", "name": "DESC-1"},
                                      {"id": 500, "ref": "EDITOR-TYPT-5XX", "name": "DESC-XXX"}]}, method="PUT",
                       **PROF1_USER)

    def test_api_post_editor(self):
        self.assert401("/api/1.0/editors", data={"data": [{}]},  method="POST")
        self.assert403("/api/1.0/editors", data={"data": [{}]},  method="POST", **STU1_USER)
        self.assert409("/api/1.0/editors", data={"data": [{"champ bidon": 100}]}, method="POST", **ADMIN_USER)

        self.assert200("/api/1.0/editors",
                       data={"data": [{"id": 500, "ref": "EDITOR-TYPT-500", "name": "DESC-500"}]}, method="POST", **ADMIN_USER)

        r = self.assert200('/api/1.0/editors/500')
        r = json_loads(r.data)["data"]
        self.assertEqual(500, r[0]["id"])

        # post conflicting data
        self.assert409("/api/1.0/editors",
                       data={"data": [{"id": 500, "ref": "EDITOR-TYPT-500", "name": "DESC-500"}]}, method="POST",
                       **ADMIN_USER)

        # post multiple data
        self.assert200("/api/1.0/editors",
                       data={"data": [{"id": 501, "ref": "EDITOR-TYPT-501", "name": "DESC-501"},
                                      {"id": 502, "ref": "EDITOR-TYPT-502", "name": "DESC-502"}]}, method="POST",
                       **PROF1_USER)
        self.assert200('/api/1.0/editors/501')
        self.assert200('/api/1.0/editors/502')
