import unittest

from tests.base_server import TestBaseServer, json_loads, ADMIN_USER, PROF1_USER, STU1_USER


class TestUsersAPI(TestBaseServer):

    FIXTURES = [
    ]

    def setUp(self):
        super().setUp()
        self.load_fixtures(self.BASE_FIXTURES)

    def test_get_auth_token(self):
        self.assert403("/adele/api/1.0/token")

        r = self.get_with_auth("/adele/api/1.0/token", **ADMIN_USER)
        self.assertIn("token", json_loads(r.data))

    def test_get_current_user(self):
        self.assert403("/adele/api/1.0/user")

        r = self.get_with_auth("/adele/api/1.0/user", **ADMIN_USER)
        self.assertEqual("AdminJulien", json_loads(r.data)["data"]["username"])
        r = self.get_with_auth("/adele/api/1.0/user", **PROF1_USER)
        self.assertEqual("Professeur1", json_loads(r.data)["data"]["username"])

    def test_get_user_from_id(self):
        self.assert403("/adele/api/1.0/users/1")
        self.assert404("/adele/api/1.0/users/100", **ADMIN_USER)

        r = self.assert403("/adele/api/1.0/users/1")
        r = self.get_with_auth("/adele/api/1.0/users/4", **PROF1_USER)
        self.assertEqual("Professeur1", json_loads(r.data)["data"]["username"])

    def test_get_user_roles(self):
        self.assert403("/adele/api/1.0/users/4/roles")
        self.assert403("/adele/api/1.0/users/4/roles", **STU1_USER)
        self.assert404("/adele/api/1.0/users/100/roles", **ADMIN_USER)

        r = self.get_with_auth("/adele/api/1.0/users/5/roles", **STU1_USER)
        role_names = [role["name"] for role in json_loads(r.data)["data"]]
        self.assertEqual(1, len(role_names))
        self.assertIn("student", role_names)

        r = self.get_with_auth("/adele/api/1.0/users/4/roles", **PROF1_USER)
        role_names = [role["name"] for role in json_loads(r.data)["data"]]
        self.assertEqual(1, len(role_names))
        self.assertIn("teacher", role_names)

        r = self.get_with_auth("/adele/api/1.0/users/1/roles", **ADMIN_USER)
        role_names = [role["name"] for role in json_loads(r.data)["data"]]
        self.assertEqual(3, len(role_names))
        self.assertIn("admin", role_names)
        self.assertIn("teacher", role_names)
        self.assertIn("student", role_names)

    def test_add_role_to_user(self):
        self.assert403("/adele/api/1.0/users/4/roles", data={"data": {"name": "student"}}, method="POST")

        resp = self.get_with_auth("/adele/api/1.0/users/4/roles", **ADMIN_USER)
        role_names = [role["name"] for role in json_loads(resp.data)["data"]]
        self.assertNotIn("student", role_names)
        self.assertIn("teacher", role_names)

        # add student role to user 4
        self.post_with_auth("/adele/api/1.0/users/4/roles",
                            data={"data": {"name": "student"}}, **ADMIN_USER)

        resp = self.get_with_auth("/adele/api/1.0/users/4/roles", **ADMIN_USER)
        role_names = [role["name"] for role in json_loads(resp.data)["data"]]

        self.assertIn("student", role_names)
        self.assertIn("teacher", role_names)

    def test_delete_user(self):
        self.assert403("/adele/api/1.0/users/4", method="DELETE")
        self.assert403("/adele/api/1.0/users/4", method="DELETE", **STU1_USER)
        self.assert403("/adele/api/1.0/users/1", method="DELETE", **PROF1_USER)
        self.assert404("/adele/api/1.0/users/100", method="DELETE", **ADMIN_USER)

        r = self.get_with_auth("/adele/api/1.0/users/4", **PROF1_USER)
        self.assertEqual("Professeur1", json_loads(r.data)["data"]["username"])

        self.delete_with_auth("/adele/api/1.0/users/4", **ADMIN_USER)
        self.assert404("/adele/api/1.0/users/4", **ADMIN_USER)

    def test_delete_user_roles(self):
        self.assert403("/adele/api/1.0/users/5/roles", method="DELETE")
        self.assert404("/adele/api/1.0/users/100/roles", method="DELETE", **ADMIN_USER)

        self.post_with_auth("/adele/api/1.0/users/5/roles",
                            data={"data": {"name": "teacher"}}, **PROF1_USER)

        self.delete_with_auth("/adele/api/1.0/users/5/roles", **PROF1_USER)

        r = self.get_with_auth("/adele/api/1.0/users/5/roles", **PROF1_USER)
        role_names = [role["name"] for role in json_loads(r.data)["data"]]
        self.assertEqual(1, len(role_names))
        self.assertIn("student", role_names)

    def test_get_whitelist(self):
        self.assert404("/adele/api/1.0/whitelists/100", **PROF1_USER)
        self.assert403("/adele/api/1.0/whitelists/1")

        r = self.get_with_auth("/adele/api/1.0/whitelists/1", **PROF1_USER)
        self.assertEqual("Master 1 TNAH 2018", json_loads(r.data)["data"]["label"])

    def test_add_whitelist(self):
        self.assert403("/adele/api/1.0/whitelists",
                       data={"data": {"whitelist_name": "WL1"}},
                       method="POST")

        r = self.post_with_auth("/adele/api/1.0/whitelists",
                                data={"data": {"whitelist_name": "WL1"}}, **PROF1_USER)
        # As of today, 14 is the next generated id
        self.assertEqual(14, json_loads(r.data)["data"]["id"])

    @unittest.skip("NotImplemented")
    def test_delete_whitelist(self):
        self.assert403("/adele/api/1.0/whitelists/1", method="DELETE")
        self.assert404("/adele/api/1.0/whitelists/100", method="DELETE", **ADMIN_USER)
        # TODO: test bind/unbind to document

    @unittest.skip("NotImplemented")
    def test_add_user_to_whitelist(self):
        pass

    @unittest.skip("NotImplemented")
    def test_remove_user_from_whitelist(self):
        pass


