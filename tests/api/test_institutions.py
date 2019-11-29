from os.path import join
from tests.base_server import TestBaseServer, json_loads, ADMIN_USER, STU1_USER, PROF1_USER, PROF2_USER


class TestInstitutionsAPI(TestBaseServer):

    def test_get_institutions(self):
        self.assert404("/api/1.0/institutions/100")

        r = self.assert200('/api/1.0/institutions')
        r = json_loads(r.data)["data"]
        self.assertEqual(15, len(r))

        r = self.assert200('/api/1.0/institutions/12')
        r = json_loads(r.data)["data"]
        self.assertEqual("Collection privée", r[0]["name"])

    def test_delete_institutions(self):
        self.assert401("/api/1.0/institutions", method="DELETE")
        self.assert403("/api/1.0/institutions", method="DELETE", **STU1_USER)

        self.delete_with_auth("/api/1.0/institutions/10", **ADMIN_USER)
        self.assert404("/api/1.0/institutions/10")

        r = self.assert200('/api/1.0/institutions')
        r = json_loads(r.data)["data"]
        self.assertEqual(14, len(r))

    def test_put_institutions(self):
        self.assert401("/api/1.0/institutions", data={"data": [{}]},  method="PUT")
        self.assert403("/api/1.0/institutions", data={"data": [{}]},  method="PUT", **STU1_USER)
        self.assert409("/api/1.0/institutions", data={"data": [{"id": 100}]},  method="PUT", **ADMIN_USER)

        r = self.assert200("/api/1.0/institutions", data={"data": [{"id": 1, "name": "newInstitution"}]},
                       method="PUT", **ADMIN_USER)
        print(json_loads(r.data))
        r = self.assert200('/api/1.0/institutions/1')
        r = json_loads(r.data)["data"]
        self.assertEqual("newInstitution", r[0]["name"])

        self.assert200("/api/1.0/institutions", data={"data": [{"id": 1, "ref": "http://instit",
                                                                      "name": "newInstitutionModifiée"}]},
                       method="PUT", **ADMIN_USER)
        r = self.assert200('/api/1.0/institutions/1')
        r = json_loads(r.data)["data"]
        self.assertEqual("http://instit", r[0]["ref"])
        self.assertEqual("newInstitutionModifiée", r[0]["name"])
        self.assertEqual(1, r[0]["id"])

        # put multiple data
        self.assert200("/api/1.0/institutions",
                       data={"data": [{"id": 500, "ref": "INSTX", "name": "INST-500"},
                                      {"id": 501, "ref": "INSTX+1", "name": "INST-501"}]}, method="POST",
                       **ADMIN_USER)

        self.assert200("/api/1.0/institutions",
                       data={"data": [{"id": 500, "ref": "INSTX-MOD"},
                                      {"id": 501, "ref": "INSTX+1-MOD"}]}, method="PUT",
                       **PROF1_USER)

    def test_api_post_institution(self):
        self.assert401("/api/1.0/institutions", data={"data": [{}]},  method="POST")
        self.assert403("/api/1.0/institutions", data={"data": [{}]},  method="POST", **STU1_USER)
        self.assert400("/api/1.0/institutions", data={"data": [{"champ bidon": 100}]}, method="POST", **ADMIN_USER)

        self.assert200("/api/1.0/institutions",
                       data={"data": [{"id": 1000, "ref": "ACTE-TYPT-500", "name": "DESC-1000"}]}, method="POST", **ADMIN_USER)

        r = self.assert200('/api/1.0/institutions/1000')
        r = json_loads(r.data)["data"]
        self.assertEqual(1000, r[0]["id"])

        self.assert400("/api/1.0/institutions",
                       data={"data": [{"id": 1000, "ref": "ACTE-TYPT-1000-NEW", "name": "DESC-1000-NEW"}]}, method="POST",
                       **ADMIN_USER)

        # post multiple data
        self.assert404('/api/1.0/institutions/1001')
        self.assert404('/api/1.0/institutions/1002')

        self.assert200("/api/1.0/institutions",
                       data={"data": [{"id": 1001, "ref": "ACTE-TYPT-1001", "name": "DESC-1001"},
                                      {"id": 1002, "ref": "ACTE-TYPT-1002", "name": "DESC-1002"}]}, method="POST",
                       **PROF1_USER)
        self.assert200('/api/1.0/institutions/1001')
        self.assert200('/api/1.0/institutions/1002')
