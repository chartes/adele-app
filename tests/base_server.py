import sys
import json
from flask_testing import LiveServerTestCase, TestCase
from os.path import join
from os import getcwd
from app import create_app, db

import base64


if sys.version_info < (3, 6):
    json_loads = lambda s: json_loads(s.decode("utf-8")) if isinstance(s, bytes) else json.loads(s)
else:
    json_loads = json.loads


def make_auth_headers(username, password):
    s = bytes("{}:{}".format(username, password), 'utf-8')
    return {
        'content-type': 'application/json',
        'Authorization': "Basic {}".format(base64.b64encode(s).decode('ascii'))
    }


_app = create_app("test")


class TestBaseServer(TestCase):

    FIXTURES_PATH = join(getcwd(), 'data', 'fixtures')

    BASE_FIXTURES = [
        join(FIXTURES_PATH, "users", "default_users.sql"),
        join(FIXTURES_PATH, "refs.sql"),
    ]

    def setUp(self):
        with self.app.app_context():
            self.clear_data()

    def create_app(self):
        with _app.app_context():
            db.create_all()
            self.client = _app.test_client()
        return _app

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

    def post(self, url, data, **kwargs):
        return self.client.post(url, data=json.dumps(data), follow_redirects=True, **kwargs)

    def post_with_auth(self, url, data, username, password):
        return self.post(url, data, headers=make_auth_headers(username, password))

    def get(self, url):
        return self.client.get(url, follow_redirects=True)

    def get_with_auth(self, url, username, password):
        return self.client.get(url, headers=make_auth_headers(username, password))
