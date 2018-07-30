import sys
import json
from flask_testing import LiveServerTestCase

from app import create_app, db

if sys.version_info < (3, 6):
    json_loads = lambda s: json_loads(s.decode("utf-8")) if isinstance(s, bytes) else json.loads(s)
else:
    json_loads = json.loads


class TestBaseServer(LiveServerTestCase):

    def create_app(self):
        self.app = create_app("test")
        return self.app

    BASE_FIXTURES = [
        "tests/data/fixtures/users/default_users.sql",
        "tests/data/fixtures/refs.sql",
    ]

    def setUp(self):
        with self.app.app_context():
            self.clear_data()

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

