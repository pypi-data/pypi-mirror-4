Initialisation
==============

When using s4u.sqlalchemy in a Pyramid application you can easily configure
it by using the ``includeme`` function of the Pyramid configurator object:

.. code-block:: python

   config.include('s4u.sqlalchemy')

This will pick up any ``sqlalchemy.*`` entries from your ``.ini`` file and
use those to configure SQLAlchemy.

For non-Pyramid applications or special situations you can also use
:py:func:`s4u.sqlalchemy.init_sqlalchemy` to configure a SQLAlchemy engine
directly:

.. code-block:: python

   from sqlalchemy import create_engine
   from s4u.sqlalchemy import init_sqlalchemy

   engine = create_engine('sqlite://')
   init_sqlachemy(engine)

