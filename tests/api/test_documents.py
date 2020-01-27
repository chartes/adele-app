import unittest
from os.path import join
from tests.base_server import TestBaseServer, json_loads, ADMIN_USER, STU1_USER, PROF1_USER, PROF2_USER


class TestDocumentsAPI(TestBaseServer):

    FIXTURES = [
        join(TestBaseServer.FIXTURES_PATH, "documents", "doc_20.sql")
    ]

    def test_get_document(self):
        self.load_fixtures(self.FIXTURES)

        # document not found
        self.assert404("/api/1.0/documents/999")
        # document found
        resp = self.get("/api/1.0/documents/20")
        self.assertEqual(20, json_loads(resp.data)["data"]["id"])

    def test_post_document(self):
        self.load_fixtures(self.FIXTURES)
        self.assert403("/api/1.0/documents", data={"data": {}},  method="POST", **STU1_USER)

        self.post_with_auth(
            "/api/1.0/documents",
            data={
                "data":
                    {
                      "title":  "My new title",
                      "subtitle": "My new subtitle",
                      "argument": "<p>L’infante Urra</p>",
                      "creation": 1400,
                      "creation_lab": "1400",
                      "copy_year": "[1409-1420 ca.]",
                      "copy_cent": 15,
                      "institution_id":  1,
                      "pressmark": "J 340, n° 21",
                      "editor_id": [1, 2],
                      "country_id": [1, 2, 3],
                      "district_id": [1, 2, 3],
                      "acte_type_id": [1],
                      "language_code": "fro",
                      "tradition_id": [1],
                      "linked_document_id": [20]
                    }
            },
            **ADMIN_USER)

        resp = self.get("/api/1.0/documents/21")
        r = json_loads(resp.data)
        self.assertEqual(21, r["data"]["id"])
        self.assertEqual(1, r["data"]["user_id"])

    def test_publish_document(self):
        self.load_fixtures(self.FIXTURES)
        self.assert401("/api/1.0/documents/20/publish", method="GET",)
        self.assert403("/api/1.0/documents/20/publish", method="GET", **STU1_USER)
        self.assert403("/api/1.0/documents/20/publish", method="GET", **PROF2_USER)
        self.assert404("/api/1.0/documents/100/publish", method="GET", **ADMIN_USER)

        self.get_with_auth("/api/1.0/documents/20/unpublish", **ADMIN_USER)
        resp = self.get_with_auth("/api/1.0/documents/20/publish", **PROF1_USER)
        self.assertTrue(json_loads(resp.data)["data"]["is_published"])

    def test_unpublish_document(self):
        self.load_fixtures(self.FIXTURES)
        self.assert401("/api/1.0/documents/20/unpublish", method="GET")
        self.assert403("/api/1.0/documents/20/unpublish", method="GET", **STU1_USER)
        self.assert403("/api/1.0/documents/20/unpublish", method="GET", **PROF2_USER)
        self.assert404("/api/1.0/documents/100/unpublish", method="GET", **ADMIN_USER)

        self.get_with_auth("/api/1.0/documents/20/publish", **PROF1_USER)
        resp = self.get_with_auth("/api/1.0/documents/20/unpublish", **PROF1_USER)
        self.assertFalse(json_loads(resp.data)["data"]["is_published"])

    def test_list_document(self):
        self.post_with_auth("/api/1.0/documents/add",
                            data={"data": {"title": "Title1", "subtitle": "Subtitle1"}},
                            **PROF1_USER)
        r = self.get("/api/1.0/documents")
        self.assertEqual(1, len(json_loads(r.data)["data"]))

        self.post_with_auth("/api/1.0/documents/add",
                            data={"data": {"title": "Title2", "subtitle": "Subtitle2"}},
                            **ADMIN_USER)

        self.post_with_auth("/api/1.0/documents/add",
                            data={"data": {"title": "Title3", "subtitle": "Subtitle3"}},
                            **ADMIN_USER)

        r = self.get("/api/1.0/documents")
        self.assertEqual(3, len(json_loads(r.data)["data"]))

        self.delete_with_auth("/api/1.0/documents/3", **ADMIN_USER)
        r = self.get("/api/1.0/documents")
        self.assertEqual(2, len(json_loads(r.data)["data"]))

    def test_delete_document(self):
        self.load_fixtures(self.FIXTURES)
        self.assert401("/api/1.0/documents/20", method="DELETE")
        self.assert403("/api/1.0/documents/20", method="DELETE", **STU1_USER)
        self.assert403("/api/1.0/documents/20", method="DELETE", **PROF2_USER)

        self.delete_with_auth("/api/1.0/documents/20", **ADMIN_USER)
        self.assert404("/api/1.0/documents/20")

    def test_change_document_whitelist(self):
        self.load_fixtures(self.FIXTURES)
        self.assert401("/api/1.0/documents/20/whitelist", data={}, method="POST")
        self.assert403("/api/1.0/documents/20/whitelist", data={}, method="POST", **STU1_USER)
        self.assert403("/api/1.0/documents/20/whitelist", data={}, method="POST", **PROF2_USER)

        r = self.post_with_auth("/api/1.0/documents/20/whitelist",
                                data={"data": {"whitelist_id": 1}},
                                **PROF1_USER)

        self.assertEqual(1, json_loads(r.data)["data"]["whitelist"]["id"])

        r = self.post_with_auth("/api/1.0/documents/20/whitelist",
                                data={"data": {}},
                                **ADMIN_USER)
        self.assertIsNone(json_loads(r.data)["data"]["whitelist"])

    def test_change_documents_closing_date(self):
        self.load_fixtures(self.FIXTURES)
        self.assert401("/api/1.0/documents/20/close", data={}, method="POST")
        self.assert403("/api/1.0/documents/20/close", data={}, method="POST", **STU1_USER)
        self.assert403("/api/1.0/documents/20/close", data={}, method="POST", **PROF2_USER)

        r = self.post_with_auth("/api/1.0/documents/20/close",
                                data={"data": {"closing_date": "15/10/2087"}},
                                **PROF1_USER)

        self.assertEqual('2087-10-15 00:00:00', json_loads(r.data)["data"]["date_closing"])

        r = self.post_with_auth("/api/1.0/documents/20/close",
                                data={"data": {}},
                                **ADMIN_USER)
        self.assertIsNone(json_loads(r.data)["data"]["date_closing"])

    def test_add_document(self):
        self.assert401("/api/1.0/documents/add", data={}, method="POST")
        self.assert403("/api/1.0/documents/add", data={}, method="POST", **STU1_USER)

        r = self.get("/api/1.0/documents")
        self.assertEqual(0, len(json_loads(r.data)["data"]))

        self.post_with_auth("/api/1.0/documents/add",
                            data={"data": {"title": "Title1", "subtitle": "Subtitle1"}},
                            **PROF1_USER)
        r = self.get("/api/1.0/documents")
        self.assertEqual(1, len(json_loads(r.data)["data"]))

        self.post_with_auth("/api/1.0/documents/add",
                            data={"data": {"title": "Title1", "subtitle": "Subtitle1"}},
                            **ADMIN_USER)
        r = self.get("/api/1.0/documents")
        self.assertEqual(2, len(json_loads(r.data)["data"]))

    def test_set_document_manifest(self):
        self.load_fixtures(self.FIXTURES)
        self.assert401("/api/1.0/documents/20/manifest", data={}, method="POST")
        self.assert403("/api/1.0/documents/20/manifest", data={}, method="POST", **STU1_USER)
        self.assert403("/api/1.0/documents/20/manifest", data={}, method="POST", **PROF2_USER)

        r = self.post_with_auth("/api/1.0/documents/20/manifest",
                            data={"data": {"manifest_url": "https://iiif.chartes.psl.eu/manifests/adele/man20.json"}},
                            **PROF1_USER)

        d = json_loads(r.data)
        self.assertEqual(1, len(d["data"]))

        r = self.post_with_auth("/api/1.0/documents/20/manifest",
                            data={"data": {"manifest_url": "https://iiif.chartes.psl.eu/manifests/adele/man109.json"}},
                            **ADMIN_USER)
        d = json_loads(r.data)
        self.assertEqual(2, len(d["data"]))
