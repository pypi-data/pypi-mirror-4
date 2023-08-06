Upgrades
========

s4u.sqlalchemy supports using ``s4u.upgrade`` to manage migrations.
It provides a ``sql`` upgrade context which configures the SQLAlchemy
context. It also supports use of `alembic <http://alembic.readthedocs.org>`_
to make modifications in the database.

The upgrade context exposes two keys in the upgrade environment:

``sql-engine``
  The SQLAlchemy engine object.

``alembic``
  An alembic `Operations
  <http://alembic.readthedocs.org/en/latest/ops.html#alembic.operations.Operations>`_
  object.

A default upgrade step which creates all missing tables and indices
is registered. If you need to modify existing tables you can create
a new upgrade step which introspects the current database and makes
any necessary changes.

.. code-block:: python

    @upgrade_step(requires=['sql'])
    def add_auth_source_column(environment):
        engine = environment['sql-engine']
        inspector = Inspector.from_engine(engine)
        if 'auth_source' in get_columns(User.__table__.name):
            return
        log.info('Adding auth_source column to user table.')
        alembic = environment['alembic']
        alembic.add_column(User.__table__, User.__table__.c['auth_source'])
