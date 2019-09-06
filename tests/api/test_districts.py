from tests.base_server import TestBaseServer, json_loads, ADMIN_USER, STU1_USER, PROF1_USER


class TestDistrictsAPI(TestBaseServer):

    def test_get_districts(self):
        self.assert404("/adele/api/1.0/districts/100")
        self.assert404("/adele/api/1.0/districts/from-country/100")

        r = self.assert200('/adele/api/1.0/districts/from-country/1')
        r = json_loads(r.data)["data"]
        self.assertEqual(20, len(r))

        r = self.assert200('/adele/api/1.0/districts/8/from-country/1')
        r = json_loads(r.data)["data"]
        self.assertEqual("Limousin", r[0]["label"])

    def test_delete_districts(self):
        self.assert403("/adele/api/1.0/districts/from-country/1", method="DELETE")
        self.assert403("/adele/api/1.0/districts/from-country/1", method="DELETE", **STU1_USER)

        self.assert200("/adele/api/1.0/districts/1/from-country/1", **PROF1_USER)
        self.assert200("/adele/api/1.0/districts/1/from-country/1", method="DELETE", **PROF1_USER)
        self.assert404("/adele/api/1.0/districts/1/from-country/1", **PROF1_USER)
        self.assert200("/adele/api/1.0/districts/2/from-country/1", **PROF1_USER)
        self.assert200("/adele/api/1.0/districts/from-country/1", method="DELETE", **PROF1_USER)
        r = self.assert200("/adele/api/1.0/districts/from-country/1", **PROF1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(0, len(r))

    def test_put_districts(self):
        self.assert403("/adele/api/1.0/districts", data={"data": {}},  method="PUT")
        self.assert403("/adele/api/1.0/districts", data={"data": {}},  method="PUT", **STU1_USER)
        self.assert409("/adele/api/1.0/districts", data={"data": [{"id": 100}]},  method="PUT", **ADMIN_USER)

        self.assert200("/adele/api/1.0/districts", data={"data": [{"id": 1, "label": "PapeTest"}]}, method="PUT", **ADMIN_USER)
        r = self.assert200('/adele/api/1.0/districts/1')
        r = json_loads(r.data)["data"]
        self.assertEqual("PapeTest", r[0]["label"])

        self.assert200("/adele/api/1.0/districts", data={"data": [{"id": 1, "label": "Desc2"}]}, method="PUT", **ADMIN_USER)
        r = self.assert200('/adele/api/1.0/districts/1')
        r = json_loads(r.data)["data"]
        self.assertEqual("Desc2", r[0]["ref"])

        # put conflicting data
        self.assert409("/adele/api/1.0/districts",
                       data={"data": [{"id": -1, "label": "ACTE-TYPT-500"}]}, method="PUT",
                       **ADMIN_USER)
        self.assert409("/adele/api/1.0/districts",
                       data={"data": [{"id": 1, "label": "ACTE-TYPT-501"},
                                      {"id": 500, "label": "ACTE-TYPT-502"}]}, method="PUT",
                       **PROF1_USER)

        # put multiple data
        self.assert200("/adele/api/1.0/districts",
                       data={"data": [{"id": 500, "label": "ACTE-TYPT-500", "ref": "DESC-500"}]}, method="POST",
                       **ADMIN_USER)

        self.assert200("/adele/api/1.0/districts",
                       data={"data": [{"id": 1, "label": "ACTE-TYPT-1", "ref": "DESC-1"},
                                      {"id": 500, "label": "ACTE-TYPT-5XX", "ref": "DESC-XXX"}]}, method="PUT",
                       **PROF1_USER)

    def test_api_post_district(self):
        self.assert403("/adele/api/1.0/districts", data={"data": [{}]},  method="POST")
        self.assert403("/adele/api/1.0/districts", data={"data": [{}]},  method="POST", **STU1_USER)
        self.assert409("/adele/api/1.0/districts", data={"data": [{"champ bidon": 100}]}, method="POST", **ADMIN_USER)

        self.assert200("/adele/api/1.0/districts",
                       data={"data": [{"id": 500, "label": "ACTE-TYPT-500", "ref": "DESC-500"}]}, method="POST", **ADMIN_USER)

        r = self.assert200('/adele/api/1.0/districts/500')
        r = json_loads(r.data)["data"]
        self.assertEqual(500, r[0]["id"])

        # post conflicting data
        self.assert409("/adele/api/1.0/districts",
                       data={"data": [{"id": 500, "label": "ACTE-TYPT-500", "ref": "DESC-500"}]}, method="POST",
                       **ADMIN_USER)

        # post multiple data
        self.assert200("/adele/api/1.0/districts",
                       data={"data": [{"id": 501, "label": "ACTE-TYPT-501", "ref": "DESC-501"},
                                      {"id": 502, "label": "ACTE-TYPT-502", "ref": "DESC-502"}]}, method="POST",
                       **PROF1_USER)
        self.assert200('/adele/api/1.0/districts/501')
        self.assert200('/adele/api/1.0/districts/502')
