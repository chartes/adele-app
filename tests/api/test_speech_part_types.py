from os.path import join
from tests.base_server import TestBaseServer, json_loads, ADMIN_USER, STU1_USER, PROF1_USER, PROF2_USER


class TestSpeechPartTypesAPI(TestBaseServer):

    def test_get_speech_part_types(self):
        self.assert404("/api/1.0/speech-part-types/100")

        r = self.assert200('/api/1.0/speech-part-types')
        r = json_loads(r.data)["data"]
        self.assertEqual(10, len(r))

        r = self.assert200('/api/1.0/speech-part-types/10')
        r = json_loads(r.data)["data"]
        self.assertEqual(10, r[0]["id"])

    def test_delete_speech_part_types(self):
        self.assert401("/api/1.0/speech-part-types", method="DELETE")
        self.assert403("/api/1.0/speech-part-types", method="DELETE", **STU1_USER)

        self.delete_with_auth("/api/1.0/speech-part-types/10", **ADMIN_USER)
        self.assert404("/api/1.0/speech-part-types/10")

        r = self.assert200('/api/1.0/speech-part-types')
        r = json_loads(r.data)["data"]
        self.assertEqual(9, len(r))

    def test_put_speech_part_types(self):
        self.assert401("/api/1.0/speech-part-types", data={"data": [{}]},  method="PUT")
        self.assert403("/api/1.0/speech-part-types", data={"data": [{}]},  method="PUT", **STU1_USER)
        self.assert409("/api/1.0/speech-part-types", data={"data": [{"id": 100}]},  method="PUT", **ADMIN_USER)

        self.assert200("/api/1.0/speech-part-types", data={"data": [{"id": 10, "label": "PapeTest"}]}, method="PUT", **ADMIN_USER)
        r = self.assert200('/api/1.0/speech-part-types/10')
        r = json_loads(r.data)["data"]
        self.assertEqual("PapeTest", r[0]["label"])

        self.assert200("/api/1.0/speech-part-types", data={"data": [{"id": 10, "lang_code": "oci"}]}, method="PUT", **ADMIN_USER)
        r = self.assert200('/api/1.0/speech-part-types/10')
        r = json_loads(r.data)["data"]
        print(r)
        self.assertEqual("oci", r[0]["language"]["code"])

        # put conflicting data
        self.assert409("/api/1.0/speech-part-types",
                       data={"data": [{"id": -1, "label": "SPEECH-PART-TYPT-500", "lang_code": "fre"}]}, method="PUT",
                       **ADMIN_USER)
        self.assert409("/api/1.0/speech-part-types",
                       data={"data": [{"id": 10, "label": "SPEECH-PART-TYPT-501", "lang_code": "fre"},
                                      {"id": 500, "label": "SPEECH-PART-TYPT-502", "lang_code": "fre"}]}, method="PUT",
                       **PROF1_USER)

        # put multiple data
        self.assert200("/api/1.0/speech-part-types",
                       data={"data": [{"id": 500, "label": "SPEECH-PART-TYPT-500", "lang_code": "fre"}]}, method="POST",
                       **ADMIN_USER)

        self.assert200("/api/1.0/speech-part-types",
                       data={"data": [{"id": 10, "label": "SPEECH-PART-TYPT-10", "lang_code": "fre"},
                                      {"id": 500, "label": "SPEECH-PART-TYPT-5XX", "lang_code": "oci"}]}, method="PUT",
                       **PROF1_USER)

    def test_api_post_speech_part_type(self):
        self.assert401("/api/1.0/speech-part-types", data={"data": [{}]},  method="POST")
        self.assert403("/api/1.0/speech-part-types", data={"data": [{}]},  method="POST", **STU1_USER)
        self.assert400("/api/1.0/speech-part-types", data={"data": [{"champ bidon": 100}]}, method="POST", **ADMIN_USER)

        self.assert200("/api/1.0/speech-part-types",
                       data={"data": [{"id": 500, "label": "SPEECH-PART-TYPT-500", "lang_code": "fre"}]}, method="POST", **ADMIN_USER)

        r = self.assert200('/api/1.0/speech-part-types/500')
        r = json_loads(r.data)["data"]
        self.assertEqual(500, r[0]["id"])

        self.assert400("/api/1.0/speech-part-types",
                       data={"data": [{"id": 500, "label": "SPEECH-PART-TYPT-500", "lang_code": "fre"}]}, method="POST",
                       **ADMIN_USER)

        # post multiple data
        self.assert200("/api/1.0/speech-part-types",
                       data={"data": [{"id": 501, "label": "SPEECH-PART-TYPT-501", "lang_code": "fre"},
                                      {"id": 502, "label": "SPEECH-PART-TYPT-502", "lang_code": "fre"}]}, method="POST",
                       **PROF1_USER)
        self.assert200('/api/1.0/speech-part-types/501')
        self.assert200('/api/1.0/speech-part-types/502')
