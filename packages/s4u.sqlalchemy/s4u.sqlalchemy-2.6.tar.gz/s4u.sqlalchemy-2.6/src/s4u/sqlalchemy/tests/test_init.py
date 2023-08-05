import unittest


class test_init_sqlalchemy(unittest.TestCase):
    def init_sqlalchemy(self, *a, **kw):
        from s4u.sqlalchemy import init_sqlalchemy
        return init_sqlalchemy(*a, **kw)

    def test_basic_sqlite(self):
        from sqlalchemy import create_engine
        from s4u.sqlalchemy import meta
        engine = create_engine('sqlite://')
        self.init_sqlalchemy(engine)
        self.assertTrue(meta.Session.bind is engine)


class includeme_tests(unittest.TestCase):
    def includeme(self, *a, **kw):
        from s4u.sqlalchemy import includeme
        return includeme(*a, **kw)

    def test_sqlite_config(self):
        from s4u.sqlalchemy import meta

        class Registry:
            settings = {'sqlalchemy.url': 'sqlite://'}

        class Config:
            registry = Registry

        config = Config()
        self.includeme(config)
        self.assertEqual(str(meta.Session.bind.url), 'sqlite://')
