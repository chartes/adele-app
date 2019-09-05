import unittest
from os.path import join
from tests.base_server import TestBaseServer, json_loads, ADMIN_USER, STU1_USER, PROF1_USER, PROF2_USER


class TestActeTypesAPI(TestBaseServer):

    FIXTURES = [
        join(TestBaseServer.FIXTURES_PATH, "documents", "doc_20.sql")
    ]

    def test_get_acte_types(self):
        self.assert404("/adele/api/1.0/acte-types/100")

        r = self.get('/adele/api/1.0/acte-types')
        r = json_loads(r.data)["data"]
        self.assertEqual(len(r), 21)

        r = self.get('/adele/api/1.0/acte-types/19')
        r = json_loads(r.data)["data"]
        self.assertEqual(19, r[0]["id"])

    def test_delete_acte_types(self):
        self.assert403("/adele/api/1.0/acte-types", method="DELETE")
        self.assert403("/adele/api/1.0/acte-types", method="DELETE", **STU1_USER)
        self.assert404("/adele/api/1.0/acte-types/126436", method="DELETE", **ADMIN_USER)

        self.delete_with_auth("/adele/api/1.0/acte-types/19", **ADMIN_USER)
        self.assert404("/adele/api/1.0/acte-types/19")

        r = self.get('/adele/api/1.0/acte-types')
        r = json_loads(r.data)["data"]
        self.assertEqual(len(r), 20)

    def test_put_acte_types(self):
        self.assert403("/adele/api/1.0/acte-types", data={"data": {}},  method="PUT")
        self.assert403("/adele/api/1.0/acte-types", data={"data": {}},  method="PUT", **STU1_USER)
        self.assert404("/adele/api/1.0/acte-types", data={"data": [{"id": 100}]},  method="PUT", **ADMIN_USER)

        self.put_with_auth("/adele/api/1.0/acte-types",
                           data={"data": [{"id": 19, "label": "PapeTest"}]}, **ADMIN_USER)
        r = self.get('/adele/api/1.0/acte-types/19')
        r = json_loads(r.data)["data"]
        self.assertEqual("PapeTest", r[0]["label"])

        self.put_with_auth("/adele/api/1.0/acte-types",
                           data={"data": [{"id": 19, "description": "Desc2"}]}, **ADMIN_USER)
        r = self.get('/adele/api/1.0/acte-types/19')
        r = json_loads(r.data)["data"]
        self.assertEqual("Desc2", r[0]["description"])

    def test_api_post_acte_type(self):
        self.assert403("/adele/api/1.0/acte-types", data={"data": {}},  method="POST")
        self.assert403("/adele/api/1.0/acte-types", data={"data": {}},  method="POST", **STU1_USER)
        self.assert409("/adele/api/1.0/acte-types", data={"data": [{"champ bidon": 100}]}, method="POST", **ADMIN_USER)

        self.assert200("/adele/api/1.0/acte-types",
                       data={"data": [{"id": 500, "label": "ACTE-TYPT-500", "description": "DESC-500"}]}, method="POST", **ADMIN_USER)

        r = self.assert200('/adele/api/1.0/acte-types/500')
        r = json_loads(r.data)["data"]
        self.assertEqual(500, r[0]["id"])
