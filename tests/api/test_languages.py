from os.path import join
from tests.base_server import TestBaseServer, json_loads, ADMIN_USER, STU1_USER, PROF1_USER, PROF2_USER


class TestLanguageTypesAPI(TestBaseServer):

    def test_get_languages(self):
        self.assert404("/api/1.0/languages/azaza")

        r = self.assert200('/api/1.0/languages')
        r = json_loads(r.data)["data"]
        self.assertEqual(3, len(r))

        r = self.assert200('/api/1.0/languages/fre')
        r = json_loads(r.data)["data"]
        self.assertEqual("fre", r[0]["code"])

    def test_delete_languages(self):
        self.assert401("/api/1.0/languages", method="DELETE")
        self.assert403("/api/1.0/languages", method="DELETE", **STU1_USER)

        self.assert200("/api/1.0/languages/fre", method='DELETE', **ADMIN_USER)
        self.assert404("/api/1.0/languages/fre")

        r = self.assert200('/api/1.0/languages')
        r = json_loads(r.data)["data"]
        self.assertEqual(2, len(r))

    def test_put_languages(self):
        self.assert401("/api/1.0/languages", data={"data": [{}]},  method="PUT")
        self.assert403("/api/1.0/languages", data={"data": [{}]},  method="PUT", **STU1_USER)
        self.assert409("/api/1.0/languages", data={"data": [{"code": "test"}]},  method="PUT", **ADMIN_USER)

        self.assert200("/api/1.0/languages", data={"data": [{"code": "fre", "label": "PapeTest"}]}, method="PUT", **ADMIN_USER)
        r = self.assert200('/api/1.0/languages/fre')
        r = json_loads(r.data)["data"]
        self.assertEqual("PapeTest", r[0]["label"])

        self.assert200("/api/1.0/languages", data={"data": [{"code": "fre", "label": "Desc2"}]}, method="PUT", **ADMIN_USER)
        r = self.assert200('/api/1.0/languages/fre')
        r = json_loads(r.data)["data"]
        self.assertEqual("Desc2", r[0]["label"])

        # put conflicting data
        self.assert409("/api/1.0/languages",
                       data={"data": [{"code": "xyz", "label": "LANG-TYPT-500"}]}, method="PUT",
                       **ADMIN_USER)
        self.assert409("/api/1.0/languages",
                       data={"data": [{"code": "fre", "label": "LANG-TYPT-501"},
                                      {"code": "xyz", "label": "LANG-TYPT-502"}]}, method="PUT",
                       **PROF1_USER)

        # put multiple data
        self.assert200("/api/1.0/languages",
                       data={"data": [{"code": "abc", "label": "LANG-TYPT-500"}]}, method="POST",
                       **ADMIN_USER)

        self.assert200("/api/1.0/languages",
                       data={"data": [{"code": "fre", "label": "LANG-TYPT-1"},
                                      {"code": "abc", "label": "LANG-TYPT-5XX"}]}, method="PUT",
                       **PROF1_USER)

    def test_api_post_language(self):
        self.assert401("/api/1.0/languages", data={"data": [{}]},  method="POST")
        self.assert403("/api/1.0/languages", data={"data": [{}]},  method="POST", **STU1_USER)
        self.assert409("/api/1.0/languages", data={"data": [{"champ bidon": 100}]}, method="POST", **ADMIN_USER)

        self.assert200("/api/1.0/languages",
                       data={"data": [{"code": "xyz", "label": "LANG-TYPT-500"}]}, method="POST", **ADMIN_USER)

        r = self.assert200('/api/1.0/languages/xyz')
        r = json_loads(r.data)["data"]
        self.assertEqual("xyz", r[0]["code"])

        # post conflicting data
        self.assert409("/api/1.0/languages",
                       data={"data": [{"code": "fre", "label": "LANG-TYPT-500"}]}, method="POST",
                       **ADMIN_USER)

        # post multiple data
        self.assert200("/api/1.0/languages",
                       data={"data": [{"code": "erf", "label": "LANG-TYPT-501"},
                                      {"code": "dfg", "label": "LANG-TYPT-502"}]}, method="POST",
                       **PROF1_USER)
        self.assert200('/api/1.0/languages/dfg')
        self.assert200('/api/1.0/languages/erf')
