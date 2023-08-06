import unittest


class setup_sqlalchemy_tests(unittest.TestCase):
    def setup_sqlalchemy(self, *a, **kw):
        from s4u.sqlalchemy.upgrade import setup_sqlalchemy
        return setup_sqlalchemy(*a, **kw)

    def test_return_engine(self):
        from sqlalchemy.engine import Engine
        options = DummyModel(dburi='sqlite:///')
        context = self.setup_sqlalchemy(options)
        self.assertEqual(set(context), set(['sql-engine', 'alembic']))
        self.assertTrue(isinstance(context['sql-engine'], Engine))
        self.assertEqual(context['sql-engine'].name, 'sqlite')

    def test_model_initialised(self):
        from s4u.sqlalchemy import meta
        options = DummyModel(dburi='sqlite:///')
        context = self.setup_sqlalchemy(options)
        engine = context['sql-engine']
        self.assertTrue(meta.metadata.bind is engine)
        self.assertTrue(meta.Session().bind is engine)


class add_missing_tests(unittest.TestCase):
    def setUp(self):
        from sqlalchemy import schema
        from s4u.sqlalchemy import meta
        self._metadata = meta.metadata
        meta.metadata = schema.MetaData()

    def tearDown(self):
        from s4u.sqlalchemy import meta
        meta.metadata = self._metadata

    def create_table(self, name='article'):
        from sqlalchemy import schema 
        from sqlalchemy import types 
        from sqlalchemy.schema import Table
        from s4u.sqlalchemy import meta
        return Table(name, meta.metadata,
                schema.Column('id', types.Integer, primary_key=True))

    def add_missing(self, *a, **kw):
        from s4u.sqlalchemy.upgrade import add_missing
        return add_missing(*a, **kw)

    def test_add_everything(self):
        from sqlalchemy import create_engine
        from sqlalchemy.engine.reflection import Inspector
        engine = create_engine('sqlite:///')
        try:
            self.create_table()
            self.add_missing({'sql-engine': engine})
            inspector = Inspector.from_engine(engine)
            self.assertTrue('article' in inspector.get_table_names())
        finally:
            engine.dispose()


class DummyModel(object):
    def __init__(self, **kw):
        for (k, v) in kw.items():
            setattr(self, k, v)


