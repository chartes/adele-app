import os
import sys
import json

from flask_testing import TestCase
from os.path import join

from app import create_app, db

if sys.version_info < (3, 6):
    json_loads = lambda s: json_loads(s.decode("utf-8")) if isinstance(s, bytes) else json.loads(s)
else:
    json_loads = json.loads


def make_auth_headers(username):
    from app.api.auth import create_tokens
    from app.models import User
    data, access_token, refresh_token = create_tokens(User.query.filter(User.username == username).first())
    return {
        'content-type': 'application/json',
        'Authorization': "Bearer {}".format(access_token)
    }


_app = create_app("test")

# for convenience
ADMIN_USER = {"username": "AdminJulien"}
PROF1_USER = {"username": "Professeur1"}
PROF2_USER = {"username": "Professeur2"}
PROF3_USER = {"username": "Professeur3"}
STU1_USER = {"username": "Eleve1"}
STU2_USER = {"username": "Eleve2"}

class TestBaseServer(TestCase):

    FIXTURES_PATH = join(os.path.dirname(os.path.abspath(__file__)), 'data', 'fixtures')

    BASE_FIXTURES = [
        join(FIXTURES_PATH, "users", "default_users.sql"),
        join(FIXTURES_PATH, "refs.sql"),
    ]

    def setUp(self):
        with self.app.app_context():
            self.clear_data()
            self.load_fixtures(self.BASE_FIXTURES)

    def create_app(self):
        with _app.app_context():
            db.create_all()
            self.client = _app.test_client(allow_subdomain_redirects=True)
            _app.test_server = self
        return _app

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    @staticmethod
    def clear_data():
        meta = db.metadata
        for table in reversed(meta.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()

    def load_fixtures(self, fixtures):
        with self.app.app_context(), db.engine.connect() as connection:
            for fixture in fixtures:
                with open(fixture) as f:
                    for _s in f.readlines():
                        trans = connection.begin()
                        connection.execute(_s, multi=True)
                        trans.commit()

    def get(self, url, **kwargs):
        return self.client.get(url, follow_redirects=True, **kwargs)

    def get_with_auth(self, url, username):
        return self.get(url, headers=make_auth_headers(username))

    def post(self, url, data, **kwargs):
        return self.client.post(url, data=json.dumps(data), follow_redirects=True, **kwargs)

    def post_with_auth(self, url, data, username):
        return self.post(url, data, headers=make_auth_headers(username))

    def put(self, url, data, **kwargs):
        return self.client.put(url, data=json.dumps(data), follow_redirects=True, **kwargs)

    def put_with_auth(self, url, data, username):
        return self.put(url, data, headers=make_auth_headers(username))

    def delete(self, url, **kwargs):
        return self.client.delete(url, follow_redirects=True, **kwargs)

    def delete_with_auth(self, url, username):
        return self.delete(url, headers=make_auth_headers(username))

    def assertStatusCode(self, status_code, url, method="GET", **kwargs):
        with_auth = 'username' in kwargs
        if method == "GET":
            if with_auth:
                r = self.get_with_auth(url, username=kwargs["username"])
            else:
                r = self.get(url)
        elif method == "POST":
            if with_auth:
                r = self.post_with_auth(url, data=kwargs.get('data', {}), username=kwargs["username"])
            else:
                r = self.post(url, data=kwargs.get('data', {}))
        elif method == "DELETE":
            if with_auth:
                r = self.delete_with_auth(url, username=kwargs["username"])
            else:
                r = self.delete(url)
        elif method == "PUT":
            if with_auth:
                r = self.put_with_auth(url, data=kwargs.get('data', {}), username=kwargs["username"])
            else:
                r = self.put(url, data=kwargs.get('data', {}))
        else:
            raise NotImplementedError

        self.assertStatus(r, status_code)
        return r

    def assert200(self, url, method='GET', **kwargs):
        return self.assertStatusCode(200, url, method, **kwargs)

    def assert403(self, url, method='GET', **kwargs):
        return self.assertStatusCode(403, url, method, **kwargs)

    def assert401(self, url, method='GET', **kwargs):
        return self.assertStatusCode(401, url, method, **kwargs)

    def assert409(self, url, method='GET', **kwargs):
        return self.assertStatusCode(409, url, method, **kwargs)

    def assert404(self, url, method='GET', **kwargs):
        return self.assertStatusCode(404, url, method, **kwargs)

    def assert400(self, url, method='GET', **kwargs):
        return self.assertStatusCode(400, url, method, **kwargs)

    def assertPtr(self, text, ptr_start, ptr_end, expected_fragment):
        self.assertEqual(expected_fragment, text[ptr_start:ptr_end])

    """
    def check_integrity(self, text, a, b, root="div"):
        print("testing integrity from", a, "to", b, "of:", text, "({0})".format(text[a:b]))
        data = StringIO(r"<root>{0}</root>".format(text[a:b], root, root))
        tree = etree.parse(data, etree.XMLParser(recover=False))
        result = etree.tostring(tree.getroot(), pretty_print=True, method="html")
        print(result)
        return result
    """
