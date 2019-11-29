from os.path import join
from tests.base_server import TestBaseServer, json_loads, ADMIN_USER, STU1_USER, PROF1_USER, PROF2_USER


class TestCommentaryTypesAPI(TestBaseServer):

    def test_get_commentary_types(self):
        self.assert404("/api/1.0/commentary-types/100")

        r = self.assert200('/api/1.0/commentary-types')
        r = json_loads(r.data)["data"]
        self.assertEqual(6, len(r))

        r = self.assert200('/api/1.0/commentary-types/2')
        r = json_loads(r.data)["data"]
        self.assertEqual(2, r[0]["id"])

    def test_delete_commentary_types(self):
        self.assert401("/api/1.0/commentary-types", method="DELETE")
        self.assert403("/api/1.0/commentary-types", method="DELETE", **STU1_USER)

        self.delete_with_auth("/api/1.0/commentary-types/2", **ADMIN_USER)
        self.assert404("/api/1.0/commentary-types/2")

        r = self.assert200('/api/1.0/commentary-types')
        r = json_loads(r.data)["data"]
        self.assertEqual(5, len(r))

    def test_put_commentary_types(self):
        self.assert401("/api/1.0/commentary-types", data={"data": [{}]},  method="PUT")
        self.assert403("/api/1.0/commentary-types", data={"data": [{}]},  method="PUT", **STU1_USER)
        self.assert409("/api/1.0/commentary-types", data={"data": [{"id": 100}]},  method="PUT", **ADMIN_USER)

        self.assert200("/api/1.0/commentary-types",
                       data={"data": [{"id": 2, "label": "PapeTest"}]},
                       method="PUT", **ADMIN_USER)
        r = self.assert200('/api/1.0/commentary-types/2')
        r = json_loads(r.data)["data"]
        self.assertEqual("PapeTest", r[0]["label"])

        self.assert200("/api/1.0/commentary-types",
                       data={"data": [{"id": 2, "label": "Desc2"}]},
                       method="PUT", **ADMIN_USER)
        r = self.assert200('/api/1.0/commentary-types/2')
        r = json_loads(r.data)["data"]
        self.assertEqual("Desc2", r[0]["label"])

        # put conflicting data
        self.assert409("/api/1.0/commentary-types",
                       data={"data": [{"id": -1, "label": "ACTE-TYPT-500"}]},
                       method="PUT", **ADMIN_USER)
        self.assert409("/api/1.0/commentary-types",
                       data={"data": [{"id": 19, "label": "ACTE-TYPT-501"},
                                      {"id": 500, "label": "ACTE-TYPT-502"}]},
                       method="PUT", **PROF1_USER)

        # put multiple data
        self.assert200("/api/1.0/commentary-types",
                       data={"data": [{"id": 500, "label": "ACTE-TYPT-500"}]},
                       method="POST", **ADMIN_USER)
        self.assert200("/api/1.0/commentary-types",
                       data={"data": [{"id": 19, "label": "ACTE-TYPT-19"}]},
                       method="POST", **ADMIN_USER)
        self.assert200("/api/1.0/commentary-types",
                       data={"data": [{"id": 19, "label": "ACTE-TYPT-19"},
                                      {"id": 500, "label": "ACTE-TYPT-5XX"}]},
                       method="PUT", **PROF1_USER)

    def test_api_post_commentary_type(self):
        self.assert401("/api/1.0/commentary-types", data={"data": [{}]},  method="POST")
        self.assert403("/api/1.0/commentary-types", data={"data": [{}]},  method="POST", **STU1_USER)
        self.assert409("/api/1.0/commentary-types", data={"data": [{"champ bidon": 100}]}, method="POST", **ADMIN_USER)

        self.assert200("/api/1.0/commentary-types",
                       data={"data": [{"id": 500, "label": "ACTE-TYPT-500"}]}, method="POST", **ADMIN_USER)

        r = self.assert200('/api/1.0/commentary-types/500')
        r = json_loads(r.data)["data"]
        self.assertEqual(500, r[0]["id"])

        # post conflicting data
        self.assert409("/api/1.0/commentary-types",
                       data={"data": [{"id": 500, "label": "ACTE-TYPT-500"}]}, method="POST",
                       **ADMIN_USER)

        # post multiple data
        self.assert200("/api/1.0/commentary-types",
                       data={"data": [{"id": 501, "label": "ACTE-TYPT-501"},
                                      {"id": 502, "label": "ACTE-TYPT-502"}]}, method="POST",
                       **PROF1_USER)
        self.assert200('/api/1.0/commentary-types/501')
        self.assert200('/api/1.0/commentary-types/502')
