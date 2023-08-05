from zope.sqlalchemy import ZopeTransactionExtension
from s4u.sqlalchemy import meta
from sqlalchemy import orm
from sqlalchemy import engine_from_config


def init_sqlalchemy(engine):
    """Initialise the SQLAlchemy models. This must be called before using
    using any of the SQLAlchemy managed the tables or classes in the model."""

    sm = orm.sessionmaker(bind=engine, extension=ZopeTransactionExtension())
    meta.Session = orm.scoped_session(sm)
    meta.metadata.bind = engine


def includeme(config):
    """'Convenience method to initialise all components of this
    :mod:`s4u.sqlalchemy` package from a pyramid applicaiton.
    """
    engine = engine_from_config(config.registry.settings, 'sqlalchemy.')
    init_sqlalchemy(engine)


__all__ = ['init_model']
