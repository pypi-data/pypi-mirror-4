# vi: fileencoding=utf-8
import unittest


class MappingTests(unittest.TestCase):
    def Mapping(self, *a, **kw):
        from s4u.sqlalchemy.mapping import Mapping
        return Mapping(*a, **kw)

    def test_load_dialect_impl_postgresql(self):
        from sqlalchemy.dialects.postgresql.base import dialect
        from sqlalchemy.dialects.postgresql import HSTORE
        mapping = self.Mapping()
        impl = mapping.load_dialect_impl(dialect())
        self.assertTrue(isinstance(impl, HSTORE))

    def test_load_dialect_impl_sqlite(self):
        from sqlalchemy.dialects.sqlite.base import dialect
        from sqlalchemy.types import VARCHAR
        mapping = self.Mapping()
        impl = mapping.load_dialect_impl(dialect())
        self.assertTrue(isinstance(impl, VARCHAR))

    def test_process_bind_param_postgresql_passthrough(self):
        from sqlalchemy.dialects.postgresql.base import dialect
        mapping = self.Mapping()
        input = object()
        output = mapping.process_bind_param(input, dialect())
        self.assertTrue(output is input)

    def test_process_bind_param_other_dialect_none(self):
        from sqlalchemy.dialects.sqlite.base import dialect
        mapping = self.Mapping()
        self.assertEqual(mapping.process_bind_param(None, dialect()), None)

    def test_process_bind_param_other_dialect_with_data(self):
        from sqlalchemy.dialects.sqlite.base import dialect
        mapping = self.Mapping()
        input = {u'foo': u'bâz'}
        output = mapping.process_bind_param(input, dialect())
        self.assertTrue(isinstance(output, str))
        self.assertEqual(output, '{"foo": "b\\u00e2z"}')

    def test_process_result_postgresql_passthrough(self):
        from sqlalchemy.dialects.postgresql.base import dialect
        mapping = self.Mapping()
        input = object()
        output = mapping.process_result_value(input, dialect())
        self.assertTrue(output is input)

    def test_process_result_value_other_dialect_none(self):
        from sqlalchemy.dialects.sqlite.base import dialect
        mapping = self.Mapping()
        self.assertEqual(mapping.process_result_value(None, dialect()), None)

    def test_process_result_value_other_dialect_with_data(self):
        from sqlalchemy.dialects.sqlite.base import dialect
        mapping = self.Mapping()
        input = '{"foo": "b\\u00e2z"}'
        output = mapping.process_result_value(input, dialect())
        self.assertEqual(output, {u'foo': u'bâz'})
