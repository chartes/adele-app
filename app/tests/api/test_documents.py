import pprint

from app.tests.base_server import TestBaseServer, json_loads


class TestDocumentsAPI(TestBaseServer):

    FIXTURES = [
        "data/fixtures/documents/doc_20.sql"
    ]

    def test_get_document_20(self):
        self.load_fixtures(self.BASE_FIXTURES + self.FIXTURES)

        with self.app.test_client() as c:
            resp = c.get("/adele/api/1.0/documents/20")
            self.assertEqual(resp.status_code, 200)
            r = json_loads(resp.data)
            self.assertIn("data", r)
