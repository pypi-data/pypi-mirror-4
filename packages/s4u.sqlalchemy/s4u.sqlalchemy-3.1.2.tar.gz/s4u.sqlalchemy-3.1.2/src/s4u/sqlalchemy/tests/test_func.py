import unittest


class greatest_tests(unittest.TestCase):
    def greatest(self, *a, **kw):
        from s4u.sqlalchemy.func import greatest
        return greatest(*a, **kw)

    def test_default_compile(self):
        self.assertEqual(
                str(self.greatest(1, 2).compile()),
                'greatest(:greatest_1, :greatest_2)')

    def test_sqlite_uses_max(self):
        from sqlalchemy.dialects.sqlite.base import dialect
        sqlite = dialect()
        self.assertEqual(
                str(self.greatest(1, 2).compile(dialect=sqlite)),
                'MAX(?, ?)')


class least_tests(unittest.TestCase):
    def least(self, *a, **kw):
        from s4u.sqlalchemy.func import least
        return least(*a, **kw)

    def test_default_compile(self):
        self.assertEqual(
                str(self.least(1, 2).compile()),
                'least(:least_1, :least_2)')

    def test_sqlite_uses_max(self):
        from sqlalchemy.dialects.sqlite.base import dialect
        sqlite = dialect()
        self.assertEqual(
                str(self.least(1, 2).compile(dialect=sqlite)),
                'MIN(?, ?)')


class day_difference_tests(unittest.TestCase):
    def day_difference(self, *a, **kw):
        from s4u.sqlalchemy.func import day_difference
        return day_difference(*a, **kw)

    def test_default_compile(self):
        import datetime 
        start = datetime.date(2011, 9, 1)
        end = datetime.date(2011, 9, 6)
        self.assertEqual(
                str(self.day_difference(start, end).compile()),
                'EXTRACT(day FROM :day_difference_1 - :day_difference_2)')

    def test_default_needs_two_arguments(self):
        self.assertRaises(ValueError,
                self.day_difference(1, 2, 3).compile)

    def test_sqlite_uses_juliandates(self):
        import datetime 
        from sqlalchemy.dialects.sqlite.base import dialect
        start = datetime.date(2011, 9, 1)
        end = datetime.date(2011, 9, 6)
        sqlite = dialect()
        self.assertEqual(
                str(self.day_difference(start, end).compile(dialect=sqlite)),
                'CAST(julianday(?) - julianday(?) AS INT)')

    def test_sqlite_needs_two_arguments(self):
        from sqlalchemy.dialects.sqlite.base import dialect
        sqlite = dialect()
        self.assertRaises(ValueError,
                self.day_difference(1, 2, 3).compile, dialect=sqlite)
