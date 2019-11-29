from tests.base_server import TestBaseServer, json_loads, ADMIN_USER, STU1_USER, PROF1_USER


class TestCountrysAPI(TestBaseServer):

    def test_get_countries(self):
        self.assert404("/api/1.0/countries/100")

        r = self.assert200('/api/1.0/countries')
        r = json_loads(r.data)["data"]
        self.assertEqual(4, len(r))

        r = self.assert200('/api/1.0/countries/1')
        r = json_loads(r.data)["data"]
        self.assertEqual("France", r[0]["label"])

    def test_delete_countries(self):
        self.assert401("/api/1.0/countries", method="DELETE")
        self.assert403("/api/1.0/countries", method="DELETE", **STU1_USER)
        self.assert200("/api/1.0/countries/126436", method="DELETE", **ADMIN_USER)

        self.assert200("/api/1.0/countries/1", method="DELETE", **ADMIN_USER)

        r = self.assert200('/api/1.0/countries')
        r = json_loads(r.data)["data"]
        self.assertEqual(3, len(r))

    def test_put_countries(self):
        self.assert401("/api/1.0/countries", data={"data": {}},  method="PUT")
        self.assert403("/api/1.0/countries", data={"data": {}},  method="PUT", **STU1_USER)
        self.assert409("/api/1.0/countries", data={"data": [{"id": 100}]},  method="PUT", **ADMIN_USER)

        self.assert200("/api/1.0/countries", data={"data": [{"id": 1, "label": "PapeTest"}]}, method="PUT", **ADMIN_USER)
        r = self.assert200('/api/1.0/countries/1')
        r = json_loads(r.data)["data"]
        self.assertEqual("PapeTest", r[0]["label"])

        self.assert200("/api/1.0/countries", data={"data": [{"id": 1, "ref": "Desc2"}]}, method="PUT", **ADMIN_USER)
        r = self.assert200('/api/1.0/countries/1')
        r = json_loads(r.data)["data"]
        self.assertEqual("Desc2", r[0]["ref"])

        # put conflicting data
        self.assert409("/api/1.0/countries",
                       data={"data": [{"id": -1, "label": "ACTE-TYPT-500", "ref": "DESC-500"}]}, method="PUT",
                       **ADMIN_USER)
        self.assert409("/api/1.0/countries",
                       data={"data": [{"id": 1, "label": "ACTE-TYPT-501", "ref": "DESC-501"},
                                      {"id": 500, "label": "ACTE-TYPT-502", "ref": "DESC-502"}]}, method="PUT",
                       **PROF1_USER)

        # put multiple data
        self.assert200("/api/1.0/countries",
                       data={"data": [{"id": 500, "label": "ACTE-TYPT-500", "ref": "DESC-500"}]}, method="POST",
                       **ADMIN_USER)

        self.assert200("/api/1.0/countries",
                       data={"data": [{"id": 1, "label": "ACTE-TYPT-1", "ref": "DESC-1"},
                                      {"id": 500, "label": "ACTE-TYPT-5XX", "ref": "DESC-XXX"}]}, method="PUT",
                       **PROF1_USER)

    def test_api_post_country(self):
        self.assert401("/api/1.0/countries", data={"data": [{}]},  method="POST")
        self.assert403("/api/1.0/countries", data={"data": [{}]},  method="POST", **STU1_USER)
        self.assert400("/api/1.0/countries", data={"data": [{"champ bidon": 100}]}, method="POST", **ADMIN_USER)

        self.assert200("/api/1.0/countries",
                       data={"data": [{"id": 500, "label": "ACTE-TYPT-500", "ref": "DESC-500"}]}, method="POST", **ADMIN_USER)

        r = self.assert200('/api/1.0/countries/500')
        r = json_loads(r.data)["data"]
        self.assertEqual(500, r[0]["id"])

        # post conflicting data
        self.assert400("/api/1.0/countries",
                       data={"data": [{"id": 500, "label": "ACTE-TYPT-500", "ref": "DESC-500"}]}, method="POST",
                       **ADMIN_USER)

        # post multiple data
        self.assert200("/api/1.0/countries",
                       data={"data": [{"id": 501, "label": "ACTE-TYPT-501", "ref": "DESC-501"},
                                      {"id": 502, "label": "ACTE-TYPT-502", "ref": "DESC-502"}]}, method="POST",
                       **PROF1_USER)
        self.assert200('/api/1.0/countries/501')
        self.assert200('/api/1.0/countries/502')
