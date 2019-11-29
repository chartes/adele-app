from os.path import join

import unittest

from tests.base_server import TestBaseServer, json_loads, ADMIN_USER, PROF1_USER, STU1_USER


class TestUsersAPI(TestBaseServer):

    FIXTURES = [
        join(TestBaseServer.FIXTURES_PATH, "documents", "doc_20.sql")
    ]

    def test_get_current_user(self):
        self.assert401("/api/1.0/user")

        r = self.get_with_auth("/api/1.0/user", **ADMIN_USER)
        self.assertEqual("AdminJulien", json_loads(r.data)["data"][0]["username"])
        r = self.get_with_auth("/api/1.0/user", **PROF1_USER)
        self.assertEqual("Professeur1", json_loads(r.data)["data"][0]["username"])

    def test_get_user_from_id(self):
        self.assert401("/api/1.0/users/1")
        self.assert404("/api/1.0/users/100", **ADMIN_USER)
        self.assert403("/api/1.0/users/100", **STU1_USER)

        r = self.assert401("/api/1.0/users/1")
        r = self.get_with_auth("/api/1.0/users/4", **PROF1_USER)
        self.assertEqual("Professeur1", json_loads(r.data)["data"][0]["username"])

    def test_get_user_roles(self):
        self.assert401("/api/1.0/users/4/roles")
        self.assert403("/api/1.0/users/4/roles", **STU1_USER)
        self.assert404("/api/1.0/users/100/roles", **ADMIN_USER)

        r = self.get_with_auth("/api/1.0/users/5/roles", **STU1_USER)

        role_names = [role["name"] for role in json_loads(r.data)["data"]]
        self.assertEqual(1, len(role_names))
        self.assertIn("student", role_names)

        r = self.get_with_auth("/api/1.0/users/4/roles", **PROF1_USER)
        role_names = [role["name"] for role in json_loads(r.data)["data"]]
        self.assertEqual(1, len(role_names))
        self.assertIn("teacher", role_names)

        r = self.get_with_auth("/api/1.0/users/1/roles", **ADMIN_USER)
        role_names = [role["name"] for role in json_loads(r.data)["data"]]
        self.assertEqual(3, len(role_names))
        self.assertIn("admin", role_names)
        self.assertIn("teacher", role_names)
        self.assertIn("student", role_names)

    def test_add_role_to_user(self):
        self.assert401("/api/1.0/users/4/roles", data={"data": [{"name": "student"}]}, method="POST")
        self.assert403("/api/1.0/users/4/roles", data={"data": [{"name": "student"}]}, method="POST", **STU1_USER)

        resp = self.assert200("/api/1.0/users/4/roles", **ADMIN_USER)

        role_names = [role["name"] for role in json_loads(resp.data)["data"]]
        self.assertNotIn("student", role_names)
        self.assertIn("teacher", role_names)

        # add student role to user 4
        self.post_with_auth("/api/1.0/users/4/roles",
                            data={"data": [{"name": "student"}]}, **ADMIN_USER)

        resp = self.get_with_auth("/api/1.0/users/4/roles", **ADMIN_USER)
        role_names = [role["name"] for role in json_loads(resp.data)["data"]]

        self.assertIn("student", role_names)
        self.assertIn("teacher", role_names)

    def test_delete_user(self):
        self.assert401("/api/1.0/users/4", method="DELETE")
        self.assert403("/api/1.0/users/4", method="DELETE", **STU1_USER)
        self.assert403("/api/1.0/users/1", method="DELETE", **PROF1_USER)
        self.assert404("/api/1.0/users/100", method="DELETE", **ADMIN_USER)

        r = self.get_with_auth("/api/1.0/users/4", **PROF1_USER)
        self.assertEqual("Professeur1", json_loads(r.data)["data"][0]["username"])

        self.delete_with_auth("/api/1.0/users/4", **ADMIN_USER)
        self.assert404("/api/1.0/users/4", **ADMIN_USER)

    def test_delete_user_roles(self):
        self.assert401("/api/1.0/users/5/roles", method="DELETE")
        self.assert403("/api/1.0/users/4/roles", method="DELETE", **STU1_USER)
        self.assert404("/api/1.0/users/100/roles", method="DELETE", **ADMIN_USER)

        self.post_with_auth("/api/1.0/users/5/roles",
                            data={"data": [{"name": "teacher"}]}, **PROF1_USER)

        self.delete_with_auth("/api/1.0/users/5/roles", **PROF1_USER)

        r = self.get_with_auth("/api/1.0/users/5/roles", **PROF1_USER)
        role_names = [role["name"] for role in json_loads(r.data)["data"]]
        self.assertEqual(1, len(role_names))
        self.assertIn("student", role_names)

    def test_get_whitelist(self):
        self.assert404("/api/1.0/whitelists/100", **PROF1_USER)
        self.assert403("/api/1.0/whitelists/1", **STU1_USER)
        self.assert401("/api/1.0/whitelists/1")

        r = self.get_with_auth("/api/1.0/whitelists/1", **PROF1_USER)
        self.assertEqual("Master 1 TNAH 2018", json_loads(r.data)["data"][0]["label"])

    def test_add_whitelist(self):
        self.assert401("/api/1.0/whitelists",
                       data={"data": [{"whitelist_name": "WL1"}]},
                       method="POST")
        self.assert403("/api/1.0/whitelists",
                       data={"data": [{"whitelist_name": "WL1"}]},
                       method="POST", **STU1_USER)

        r = self.assert200("/api/1.0/whitelists", method="POST",
                                data={"data": [{"whitelist_name": "WL1"}]}, **PROF1_USER)
        # As of today, 14 is the next generated id
        self.assertEqual(14, json_loads(r.data)["data"][0]["id"])

    def test_delete_whitelist(self):
        self.load_fixtures(self.FIXTURES)

        self.assert401("/api/1.0/whitelists/1", method="DELETE")
        self.assert403("/api/1.0/whitelists/1", method="DELETE", **STU1_USER)
        self.assert404("/api/1.0/whitelists/100", method="DELETE", **ADMIN_USER)

        # bind the whitelist 1 to the doc
        self.post_with_auth("/api/1.0/documents/20/whitelist",
                        data={"data": [{"whitelist_id": "1"}]}, **PROF1_USER)
        r = self.get("/api/1.0/documents/20")
        self.assertEqual(1, json_loads(r.data)["data"]["whitelist"]["id"])

        # delete the whitelist then check the document again
        self.assert200("/api/1.0/whitelists/1", method="DELETE", **ADMIN_USER)
        r = self.get("/api/1.0/documents/20")
        self.assertIsNone(json_loads(r.data)["data"]["whitelist"])

        # try to get the whitelist
        self.assert404("/api/1.0/whitelists/1", method="DELETE", **ADMIN_USER)

    def test_add_user_to_whitelist(self):
        self.assert401("/api/1.0/whitelists/1/add-users", data={}, method="POST")
        self.assert403("/api/1.0/whitelists/1/add-users", data={}, method="POST", **STU1_USER)

        def get_ids(r):
            return [u['id'] for u in json_loads(r.data)["data"][0]["users"]]
        # check that users 1 and 2 are not in the list
        r = self.get_with_auth("/api/1.0/whitelists/1", **PROF1_USER)
        ids = get_ids(r)
        self.assertNotIn(1, ids)
        self.assertNotIn(2, ids)
        # add users 1 and 2
        r = self.post_with_auth("/api/1.0/whitelists/1/add-users",
                            data={"data": {"user_id": [1, 2]}}, **PROF1_USER)
        ids = get_ids(r)
        self.assertIn(1, ids)
        self.assertIn(2, ids)

        # be sure you can't add duplicates
        r = self.post_with_auth("/api/1.0/whitelists/1/add-users",
                            data={"data": {"user_id": [1, 2]}}, **PROF1_USER)
        ids_wo_ducplicates = get_ids(r)
        self.assertEqual(len(ids), len(ids_wo_ducplicates))

    def test_remove_user_from_whitelist(self):
        self.assert401("/api/1.0/whitelists/1/remove-user/1", method="DELETE")
        self.assert403("/api/1.0/whitelists/1/remove-user/1", method="DELETE", **STU1_USER)

        def get_ids(r):
            return [u['id'] for u in json_loads(r.data)["data"][0]["users"]]

        # add users 1 and 2
        r = self.post_with_auth("/api/1.0/whitelists/1/add-users",
                            data={"data": {"user_id": [1, 2]}}, **PROF1_USER)
        ids = get_ids(r)

        # be sure you can't add duplicates
        self.delete_with_auth("/api/1.0/whitelists/1/remove-user/1", **PROF1_USER)
        r = self.get_with_auth("/api/1.0/whitelists/1", **PROF1_USER)
        ids_wo_user_1 = get_ids(r)

        self.assertNotIn(1, ids_wo_user_1)
        self.assertEqual(len(ids) - 1, len(ids_wo_user_1))
