from tests.base_server import TestBaseServer, json_loads, ADMIN_USER, STU1_USER, PROF1_USER


class TestDistrictsAPI(TestBaseServer):

    def test_get_districts(self):
        self.assert404("/api/1.0/districts/100")
        self.assert404("/api/1.0/districts/from-country/100")

        r = self.assert200('/api/1.0/districts/from-country/1')
        r = json_loads(r.data)["data"]
        self.assertEqual(20, len(r))

        r = self.assert200('/api/1.0/districts/8/from-country/1')
        r = json_loads(r.data)["data"]
        self.assertEqual("Limousin", r[0]["label"])

    def test_delete_districts(self):
        self.assert401("/api/1.0/districts/from-country/1", method="DELETE")
        self.assert403("/api/1.0/districts/from-country/1", method="DELETE", **STU1_USER)

        self.assert200("/api/1.0/districts/1/from-country/1", **PROF1_USER)
        self.assert200("/api/1.0/districts/1/from-country/1", method="DELETE", **PROF1_USER)
        self.assert404("/api/1.0/districts/1/from-country/1", **PROF1_USER)
        self.assert200("/api/1.0/districts/2/from-country/1", **PROF1_USER)
        self.assert200("/api/1.0/districts/from-country/1", method="DELETE", **PROF1_USER)
        r = self.assert200("/api/1.0/districts/from-country/1", **PROF1_USER)
        r = json_loads(r.data)["data"]
        self.assertEqual(0, len(r))

    def test_put_districts(self):
        self.assert401("/api/1.0/districts/from-country/1", data={"data": {}},  method="PUT")
        self.assert403("/api/1.0/districts/from-country/1", data={"data": {}},  method="PUT", **STU1_USER)
        self.assert409("/api/1.0/districts/from-country/1", data={"data": [{"id": 100}]},  method="PUT", **ADMIN_USER)

        self.assert200("/api/1.0/districts/from-country/1",
                       data={"data": [{"id": 1, "label": "DistrictTest"}]},
                       method="PUT", **ADMIN_USER)
        r = self.assert200('/api/1.0/districts/1/from-country/1')
        r = json_loads(r.data)["data"]
        self.assertEqual("DistrictTest", r[0]["label"])

        # put conflicting data
        # missing district id
        self.assert409("/api/1.0/districts/from-country/1", data={"data": [{"label": "Desc2"}]}, method="PUT",
                       **ADMIN_USER)

        self.assert409("/api/1.0/districts/from-country/1",
                       data={"data": [{"id": -1, "label": "DISTRICT-500"}]}, method="PUT",
                       **ADMIN_USER)

        # put multiple data
        self.assert200("/api/1.0/districts",
                       data={"data": [{"id": 200, "label": "DISTRICT-200", "country_id": 2}]}, method="POST",
                       **ADMIN_USER)

        self.assert200("/api/1.0/districts/from-country/2",
                       data={"data": [{"id": 20, "label": "DISTRICT-20"},
                                      {"id": 200, "label": "DISTRICT-2XX"}]}, method="PUT",
                       **PROF1_USER)

    def test_api_post_district(self):
        self.assert401("/api/1.0/districts", data={"data": [{}]},  method="POST")
        self.assert403("/api/1.0/districts", data={"data": [{}]},  method="POST", **STU1_USER)
        self.assert409("/api/1.0/districts", data={"data": [{"champ bidon": 100}]}, method="POST", **ADMIN_USER)

        self.assert200("/api/1.0/districts",
                       data={"data": [{"id": 500, "label": "DISTRICT-500", "country_id": 1}]}, method="POST", **ADMIN_USER)

        r = self.assert200('/api/1.0/districts/500/from-country/1')
        r = json_loads(r.data)["data"]
        self.assertEqual(500, r[0]["id"])

        # post conflicting data
        self.assert409("/api/1.0/districts",
                       data={"data": [{"id": 500, "label": "DISTRICT-500"}]}, method="POST",
                       **ADMIN_USER)

        # post multiple data
        self.assert200("/api/1.0/districts",
                       data={"data": [{"id": 501, "label": "DISTRICT-501", "country_id": 3},
                                      {"id": 502, "label": "DISTRICT-502", "country_id": 2}]}, method="POST",
                       **PROF1_USER)
        self.assert200('/api/1.0/districts/501/from-country/3')
        self.assert200('/api/1.0/districts/502/from-country/2')
