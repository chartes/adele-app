from os.path import join
from tests.base_server import TestBaseServer, json_loads, ADMIN_USER, STU1_USER, PROF1_USER, PROF2_USER


class TestTraditionTypesAPI(TestBaseServer):

    def test_get_traditions(self):
        self.assert404("/api/1.0/traditions/tradi")

        r = self.assert200('/api/1.0/traditions')
        r = json_loads(r.data)["data"]
        self.assertEqual(7, len(r))

        r = self.assert200('/api/1.0/traditions/cartulaire')
        r = json_loads(r.data)["data"]
        self.assertEqual("cartulaire", r[0]["id"])

    def test_delete_traditions(self):
        self.assert401("/api/1.0/traditions", method="DELETE")
        self.assert403("/api/1.0/traditions", method="DELETE", **STU1_USER)

        self.delete_with_auth("/api/1.0/traditions/cartulaire", **ADMIN_USER)
        self.assert404("/api/1.0/traditions/cartulaire")

        r = self.assert200('/api/1.0/traditions')
        r = json_loads(r.data)["data"]
        self.assertEqual(6, len(r))

    def test_put_traditions(self):
        self.assert401("/api/1.0/traditions", data={"data": [{}]},  method="PUT")
        self.assert403("/api/1.0/traditions", data={"data": [{}]},  method="PUT", **STU1_USER)
        self.assert409("/api/1.0/traditions", data={"data": [{"id": "test"}]},  method="PUT", **ADMIN_USER)

        self.assert200("/api/1.0/traditions", data={"data": [{"id": "cartulaire", "label": "cartu"}]}, method="PUT", **ADMIN_USER)
        r = self.assert200('/api/1.0/traditions/cartulaire')
        r = json_loads(r.data)["data"]
        self.assertEqual("cartu", r[0]["label"])

        self.assert200("/api/1.0/traditions", data={"data": [{"id": "orig", "label": "Ori"}]}, method="PUT", **ADMIN_USER)
        r = self.assert200('/api/1.0/traditions/orig')
        r = json_loads(r.data)["data"]
        self.assertEqual("Ori", r[0]["label"])

        # put conflicting data
        self.assert409("/api/1.0/traditions",
                       data={"data": [{"id": -1, "label": "EDITOR-TYPT-500"}]}, method="PUT",
                       **ADMIN_USER)
        self.assert409("/api/1.0/traditions",
                       data={"data": [{"id": 1, "label": "EDITOR-TYPT-501"},
                                      {"id": 500, "label": "EDITOR-TYPT-502"}]}, method="PUT",
                       **PROF1_USER)

        # put multiple data
        self.assert200("/api/1.0/traditions",
                       data={"data": [{"id": 500, "label": "EDITOR-TYPT-500"}]}, method="POST",
                       **ADMIN_USER)

        self.assert200("/api/1.0/traditions",
                       data={"data": [{"id": 500, "label": "EDITOR-TYPT-1"},
                                      {"id": "cartulaire", "label": "EDITOR-TYPT-5XX"}]}, method="PUT",
                       **PROF1_USER)

    def test_api_post_tradition(self):
        self.assert401("/api/1.0/traditions", data={"data": [{}]},  method="POST")
        self.assert403("/api/1.0/traditions", data={"data": [{}]},  method="POST", **STU1_USER)
        self.assert409("/api/1.0/traditions", data={"data": [{"champ bidon": 100}]}, method="POST", **ADMIN_USER)

        self.assert200("/api/1.0/traditions",
                       data={"data": [{"id": "new_tradition", "label": "EDITOR-TYPT-500"}]}, method="POST", **ADMIN_USER)

        r = self.assert200('/api/1.0/traditions/new_tradition')
        r = json_loads(r.data)["data"]
        self.assertEqual("new_tradition", r[0]["id"])

        # post conflicting data
        self.assert409("/api/1.0/traditions",
                       data={"data": [{"id": "new_tradition", "label": "EDITOR-TYPT-500"}]}, method="POST",
                       **ADMIN_USER)

        # post multiple data
        self.assert200("/api/1.0/traditions",
                       data={"data": [{"id": 501, "label": "EDITOR-TYPT-501"},
                                      {"id": 502, "label": "EDITOR-TYPT-502"}]}, method="POST",
                       **PROF1_USER)
        self.assert200('/api/1.0/traditions/501')
        self.assert200('/api/1.0/traditions/502')
