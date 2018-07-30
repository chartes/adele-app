import pprint

from tests.base_server import TestBaseServer, json_loads


class TestDocumentsAPI(TestBaseServer):

    FIXTURES = [
        "tests/data/fixtures/documents/doc_20.sql"
    ]

    def test_get_document(self):
        self.load_fixtures(self.BASE_FIXTURES + self.FIXTURES)

        with self.app.test_client() as c:
            # document found
            resp = c.get("/adele/api/1.0/documents/20")
            self.assertEqual(resp.status_code, 200)
            r = json_loads(resp.data)
            self.assertIn("data", r)
            # document not found
            resp = c.get("/adele/api/1.0/documents/999")
            self.assertEqual(resp.status_code, 200)
            r = json_loads(resp.data)
            self.assertIn("errors", r)
