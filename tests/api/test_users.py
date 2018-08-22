import pprint
from flask import json
from os.path import join
from tests.base_server import TestBaseServer, json_loads


class TestUsersAPI(TestBaseServer):

    FIXTURES = [
    ]

    def test_add_role_to_user(self):
        self.load_fixtures(self.BASE_FIXTURES)

        resp = self.get_with_auth("/adele/api/1.0/users/4/roles", username="AdminJulien", password="AdeleAdmin2018")
        role_names = [role["name"] for role in json_loads(resp.data)["data"]]
        self.assertNotIn("student", role_names)
        self.assertIn("teacher", role_names)

        # add student role to user 4
        self.post_with_auth("/adele/api/1.0/users/4/roles", data={"data": {"name": "student"}}, username="AdminJulien", password="AdeleAdmin2018")

        resp = self.get_with_auth("/adele/api/1.0/users/4/roles", username="AdminJulien", password="AdeleAdmin2018")
        role_names = [role["name"] for role in json_loads(resp.data)["data"]]

        self.assertIn("student", role_names)
        self.assertIn("teacher", role_names)

