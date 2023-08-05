import unittest
from sqlalchemy import create_engine
from s4u.sqlalchemy import init_sqlalchemy
from s4u.sqlalchemy import meta
import transaction


class DatabaseTestCase(unittest.TestCase):
    """Base class for tests which require a database.
    """
    create_tables = True
    db_uri = 'sqlite://'

    def setUp(self):
        self.engine = create_engine(self.db_uri)
        init_sqlalchemy(self.engine)
        if self.create_tables:
            meta.metadata.create_all()

    def tearDown(self):
        transaction.abort()
        if self.create_tables:
            meta.metadata.drop_all()
        self.engine.dispose()
