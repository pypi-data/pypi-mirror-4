import unittest


class INETTests(unittest.TestCase):
    def INET(self, *a, **kw):
        from s4u.sqlalchemy.inet import INET
        return INET(*a, **kw)

    def test_load_dialect_impl_postgresql(self):
        from sqlalchemy.dialects.postgresql.base import dialect
        from sqlalchemy.dialects.postgresql import INET
        inet = self.INET()
        impl = inet.load_dialect_impl(dialect())
        self.assertTrue(isinstance(impl, INET))

    def test_load_dialect_impl_sqlite(self):
        from sqlalchemy.dialects.sqlite.base import dialect
        from sqlalchemy.types import CHAR
        inet = self.INET()
        impl = inet.load_dialect_impl(dialect())
        self.assertTrue(isinstance(impl, CHAR))

    def test_process_bind_param_none(self):
        inet = self.INET()
        self.assertEqual(inet.process_bind_param(None, None), None)

    def test_process_bind_param_ip_for_postgres(self):
        import IPy
        from sqlalchemy.dialects.postgresql.base import dialect
        inet = self.INET()
        input = IPy.IP('127.0.0.1')
        output = inet.process_bind_param(input, dialect())
        self.assertTrue(isinstance(output, str))
        self.assertEqual(output, str(input))

    def test_process_bind_param_str_for_postgres(self):
        from sqlalchemy.dialects.postgresql.base import dialect
        inet = self.INET()
        output = inet.process_bind_param('127.1.2.3', dialect())
        self.assertTrue(isinstance(output, str))
        self.assertEqual(output, '127.1.2.3')

    def test_process_bind_param_ip_for_sqlite(self):
        import IPy
        from sqlalchemy.dialects.sqlite.base import dialect
        inet = self.INET()
        input = IPy.IP('::1')
        output = inet.process_bind_param(input, dialect())
        self.assertTrue(isinstance(output, str))
        self.assertEqual(output, '::1')

    def test_process_bind_param_str_for_sqlite(self):
        from sqlalchemy.dialects.sqlite.base import dialect
        inet = self.INET()
        output = inet.process_bind_param('10', dialect())
        self.assertTrue(isinstance(output, str))
        self.assertEqual(output, '10.0.0.0')

    def test_process_result_value_none(self):
        inet = self.INET()
        self.assertEqual(inet.process_result_value(None, None), None)

    def test_process_result_value_str_value(self):
        import IPy
        inet = self.INET()
        output = inet.process_result_value('::1', None)
        self.assertTrue(isinstance(output, IPy.IP))
        self.assertEqual(str(output), '::1')
