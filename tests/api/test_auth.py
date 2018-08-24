
from tests.base_server import TestBaseServer, json_loads, ADMIN_USER


class TestAuthAPI(TestBaseServer):

    FIXTURES = [
    ]

    def test_get_auth_token(self):
        self.assert403("/adele/api/1.0/token")

        r = self.get_with_auth("/adele/api/1.0/token", **ADMIN_USER)
        self.assertIn("token", json_loads(r.data))
