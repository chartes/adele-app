import pprint
from flask import json
from os.path import join
from tests.base_server import TestBaseServer, json_loads


class TestDocumentsAPI(TestBaseServer):

    FIXTURES = [
        join(TestBaseServer.FIXTURES_PATH, "documents", "doc_20.sql")
    ]

    def test_get_document(self):
        self.load_fixtures(self.BASE_FIXTURES + self.FIXTURES)

        # document found
        resp = self.get("/adele/api/1.0/documents/20")
        self.assertEqual(200, resp.status_code)
        r = json_loads(resp.data)
        self.assertIn("data", r)
        self.assertEqual(20, r["data"]["id"])

        # document not found
        resp = self.get("/adele/api/1.0/documents/999")
        self.assertEqual(200, resp.status_code)
        r = json_loads(resp.data)
        self.assertIn("errors", r)

    def test_post_document(self):
        self.load_fixtures(self.BASE_FIXTURES + self.FIXTURES)
        login_info = {"username": "AdminJulien", "password": "AdeleAdmin2018"}

        resp = self.post_with_auth(
            "/adele/api/1.0/documents",
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
            **login_info)

        resp = self.get("/adele/api/1.0/documents/21")
        r = json_loads(resp.data)
        self.assertEqual(21, r["data"]["id"])
        self.assertEqual(1, r["data"]["user_id"])
        #print(r)
