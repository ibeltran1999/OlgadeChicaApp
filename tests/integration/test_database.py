import unittest

from app import create_app, db

class DatabaseTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"]  = "sqlite:///:memory:"

        self.app.app_context().push()

    def test_database_connection(self):
            result = db.session.execute(db.text("SELECT 1"))

            self.assertEqual(result.scalar(), 1)

    def tearDown(self):
        db.session.remove()
        self.app = None
