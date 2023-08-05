Usage
=====

The ORM base class is available as :py:class:`s4u.sqlalchemy.meta.BaseObject`
and can be included directly:

.. code-block:: python

   from s4u.sqlalchemy.meta import BaseObject

   class Account(BaseObject):
       __tablename__ = 'account'
       # Define your columns and methods here.


When you need to build a query you can use the
:py:obj:`s4u.sqlalchemy.meta.Session` session factory. Note that ``Session``
can not be imported directly: if you import it before
:py:func:`s4u.sqlalchemy.init_model` is called it is still set to None. Instead
import the ``meta`` module:

.. code-block:: python

   from s4u.sqlalchemy import meta

   account = meta.Session.query(Account).first()

When writing methods in a model it is recommended to use
:py:func:`sqlalchemy.orm.session.object_session` instead:

.. code-block:: python

   from sqlalchemy.orm.session import object_session

   class Account(BaseObject):
       def favourites(self):
           "Return all the recent favourite articles."""
           session = object_session(self)
           return session.query(Article).all()
