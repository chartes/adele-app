import pprint
from flask import json
from os.path import join
from tests.base_server import TestBaseServer, json_loads


class TestDocumentsAPI(TestBaseServer):

    FIXTURES = [
        join(TestBaseServer.FIXTURES_PATH, "documents/doc_20.sql")
    ]

    def test_get_document(self):
        self.load_fixtures(self.BASE_FIXTURES + self.FIXTURES)

        # document found
        resp = self.get("/adele/api/1.0/documents/20")
        self.assertEqual(resp.status_code, 200)
        r = json_loads(resp.data)
        self.assertIn("data", r)
        print(r)

        # document not found
        resp = self.get("/adele/api/1.0/documents/999")
        self.assertEqual(resp.status_code, 200)
        r = json_loads(resp.data)
        self.assertIn("errors", r)

    def test_post_document(self):
        self.load_fixtures(self.BASE_FIXTURES)

        resp = self.post_with_auth("adele/api/1.0/documents", data={"foor": "bar"}, username="AdminJulien", password="AdeleAdmin2018")

        print(resp.data)