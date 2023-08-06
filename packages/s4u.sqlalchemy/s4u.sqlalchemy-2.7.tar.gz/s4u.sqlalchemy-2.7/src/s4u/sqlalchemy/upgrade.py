from zope.sqlalchemy import mark_changed
from s4u.upgrade import upgrade_context
from s4u.upgrade import upgrade_step
from s4u.sqlalchemy import init_sqlalchemy
from s4u.sqlalchemy import meta
from sqlalchemy import create_engine
from alembic.migration import MigrationContext
from alembic.operations import Operations


def alembic_operations():
    """Return a configure alembic operations instance.

    This assumes that the SQLAlchemy connection has already been
    configured with a call to init_sqlalchemy.
    """
    connection = meta.Session.connection()
    context = MigrationContext.configure(connection, opts={})
    return Operations(context)


_engine = None


@upgrade_context('sql', [('--db-uri',
               {'type': str, 'required': True, 'dest': 'dburi'})])
def setup_sqlalchemy(options):
    global _engine
    if _engine is None:
        _engine = create_engine(options.dburi)
        init_sqlalchemy(_engine)
    ops = alembic_operations()
    mark_changed(meta.Session())
    return {'sql-engine': _engine,
            'alembic': ops}


@upgrade_step(require=['sql'])
def add_missing(environment):
    engine = environment['sql-engine']
    meta.metadata.create_all(engine)
