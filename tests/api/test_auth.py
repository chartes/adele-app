import pprint
from flask import json
from os.path import join
from tests.base_server import TestBaseServer, json_loads


class TestAuthAPI(TestBaseServer):

    FIXTURES = [
    ]

    def test_auth(self):
        self.load_fixtures(self.BASE_FIXTURES)

        resp = self.get_with_auth("/adele/api/1.0/user", username="AdminJulien", password="AdeleAdmin2018")
        r = json_loads(resp.data)
        self.assertEqual('AdminJulien', r["data"]["username"])
