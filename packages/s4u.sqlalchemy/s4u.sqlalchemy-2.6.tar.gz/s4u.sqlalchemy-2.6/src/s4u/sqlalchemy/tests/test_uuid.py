import unittest


class GUIDTests(unittest.TestCase):
    test_uuid = 'e56aeaa8-ec0e-48ad-829f-dbae94bc378f'

    def GUID(self, *a, **kw):
        from s4u.sqlalchemy.uuid import GUID
        return GUID(*a, **kw)

    def test_load_dialect_impl_postgresql(self):
        from sqlalchemy.dialects.postgresql.base import dialect
        from sqlalchemy.dialects.postgresql import UUID
        guid = self.GUID()
        impl = guid.load_dialect_impl(dialect())
        self.assertTrue(isinstance(impl, UUID))

    def test_load_dialect_impl_sqlite(self):
        from sqlalchemy.dialects.sqlite.base import dialect
        from sqlalchemy.types import CHAR
        guid = self.GUID()
        impl = guid.load_dialect_impl(dialect())
        self.assertTrue(isinstance(impl, CHAR))

    def test_process_bind_param_none(self):
        guid = self.GUID()
        self.assertEqual(guid.process_bind_param(None, None), None)

    def test_process_bind_param_uuid_for_postgres(self):
        import uuid
        from sqlalchemy.dialects.postgresql.base import dialect
        guid = self.GUID()
        input = uuid.uuid4()
        output = guid.process_bind_param(input, dialect())
        self.assertTrue(isinstance(output, str))
        self.assertEqual(output, str(input))

    def test_process_bind_param_str_for_postgres(self):
        from sqlalchemy.dialects.postgresql.base import dialect
        guid = self.GUID()
        output = guid.process_bind_param(self.test_uuid, dialect())
        self.assertTrue(isinstance(output, str))
        self.assertEqual(output, self.test_uuid)

    def test_process_bind_param_uuid_for_sqlite(self):
        import uuid
        from sqlalchemy.dialects.sqlite.base import dialect
        guid = self.GUID()
        input = uuid.uuid4()
        output = guid.process_bind_param(input, dialect())
        self.assertTrue(isinstance(output, str))
        self.assertEqual(output, str(input))

    def test_process_bind_param_str_for_sqlite(self):
        from sqlalchemy.dialects.sqlite.base import dialect
        guid = self.GUID()
        output = guid.process_bind_param(self.test_uuid, dialect())
        self.assertTrue(isinstance(output, str))
        self.assertEqual(output, self.test_uuid)

    def test_process_result_value_none(self):
        guid = self.GUID()
        self.assertEqual(guid.process_result_value(None, None), None)

    def test_process_result_value_str_value(self):
        import uuid
        guid = self.GUID()
        output = guid.process_result_value(self.test_uuid, None)
        self.assertTrue(isinstance(output, uuid.UUID))
        self.assertEqual(str(output), self.test_uuid)
