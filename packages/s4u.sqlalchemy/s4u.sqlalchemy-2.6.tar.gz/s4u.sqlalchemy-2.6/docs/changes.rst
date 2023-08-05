Changelog
=========

2.6 - January 8, 2013
-----------------------

- First public release.


2.5 - December 10, 2012
-----------------------

- Modify upgrade content provider to always mark the transaction as changed so
  DDL is flushed in a commit. Again - this change got lost somewhere.


2.4 - December 10, 2012
-----------------------

- Do not create multiple engines when our upgrade context provider is used
  multiple times.


2.3 - February 28, 2012
-----------------------

- Modify upgrade content provider to always mark the transaction as
  changed so DDL is flushed in a commit.
  [wichert]

- Make database URL used in DatabaseTestCase configurable via a new
  ``db_uri`` class variable.
  [wichert]

- Abort transaction earlier during test breakdown so we do not try to
  drop tables while another connection is open within a transaction.
  [wichert]


2.2 - January 31, 2012
----------------------

- Update alembic 0.2.0 release which changed its API especially for us.
  [wichert]


2.1 - January 4, 2011
---------------------

- Update DatabaseTestCase to abort any open transaction. This clears out all
  open SQL connections.
  [wichert]


2.0 - January 3, 2011
---------------------

- Setup an `alembic <http://pypi.python.org/pypi/alembic>`_ context
  as part of the upgrade context.
  [wichert]


1.8 - December 28, 2011
-----------------------

- Make creation of database tables optional in DatabaseTestCase.


1.7 - December 28, 2011
-----------------------

- Remove bad docstring from DatabaseTestCase class.

- Expose SQLAlchemy engine in test class as `engine` attribute,
  and fully dispose of the engine on test teardown.


1.6 - November 9, 2011
----------------------

- Move dummy test class inside of test class so it does not pollute
  metadata of real applications.

- Add an INET type to handle IPv4 and IPv6 networks and addresses.
  On the Python side these are handled as IPy.IP instances.


1.5 - September 19, 2011
------------------------

- Add :py:func:`day_difference <s4u.sqlalchemy.func.day_difference>`
  SQL function.


1.4 - September 14, 2011
------------------------

- Include (very minimal) GUID documentation.

- Add :py:func:`least <s4u.sqlalchemy.func.least>` and
  :py:func:`least <s4u.sqlalchemy.func.greatest>` SQL functions.


1.3 - August 31, 2011
---------------------

- Add basic s4u.upgrade integration.


1.2 - August 4, 2011
--------------------

- Fix Pyramid ``includeme`` support.


1.1 - August 4, 2011
--------------------

- Loosen SQLAlchemy dependency to > 0.6.

- Add a uuid column type.


1.0 - August 2, 2011
--------------------

- First version.
