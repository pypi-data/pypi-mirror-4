from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import Numeric


class greatest(expression.FunctionElement):
    """SQL function to return the largest number of a series.

    .. code-block:: python

       >>> session = meta.Session()
       >>> session.query(greatest(1, 3)).scalar()
       3
       >>> session.query(greatest(9, 5, 2, 4)).scalar()
       9

    This function is only supported on databases which support GREATEST
    (such as PostgreSQL) or MAX (such as SQLite).
    """
    type = Numeric()
    name = 'greatest'


@compiles(greatest)
def default_greatest(element, compiler, **kw):
    return compiler.visit_function(element)


@compiles(greatest, 'sqlite')
def max_greatest(element, compiler, **kw):
    values = [compiler.process(a) for a in element.clauses]
    return 'MAX(%s)' % ', '.join(values)


class least(expression.FunctionElement):
    """SQL function to return the smallest number of a series.

    .. code-block:: python

       >>> session = meta.Session()
       >>> session.query(least(1, 3)).scalar()
       1
       >>> session.query(greatest(9, 5, 2, 4)).scalar()
       2

    This function is only supported on databases which support LEAST
    (such as PostgreSQL) or MIN (such as SQLite).
    """
    type = Numeric()
    name = 'least'


@compiles(least)
def default_least(element, compiler, **kw):
    return compiler.visit_function(element)


@compiles(least, 'sqlite')
def min_least(element, compiler, **kw):
    values = [compiler.process(a) for a in element.clauses]
    return 'MIN(%s)' % ', '.join(values)


class day_difference(expression.FunctionElement):
    """Determine the difference in (whole) days between two dates.

    .. code-block:: python

       >>> session = meta.Session()
       >>> today = datetime.date.today()
       >>> session.query(day_different(current_timestamp(), today))
       15
    """
    type = Numeric()
    name = 'day_difference'


@compiles(day_difference)
def default_day_difference(element, compiler, **kw):
    if len(element.clauses) != 2:
        raise ValueError('default_day_differences takes two parameters')
    values = [compiler.process(a) for a in element.clauses]
    return 'EXTRACT(day FROM %s - %s)' % tuple(values)


@compiles(day_difference, 'sqlite')
def sqlite_day_difference(element, compiler, **kw):
    """SQLite always returns 0 if you try to try to do math with dates.
    The standard trick is to convert to julian dates first.
    """
    if len(element.clauses) != 2:
        raise ValueError('default_day_differences takes two parameters')
    values = [compiler.process(a) for a in element.clauses]
    return 'CAST(julianday(%s) - julianday(%s) AS INT)' % tuple(values)


__all__ = ['greatest', 'least', 'day_difference']
