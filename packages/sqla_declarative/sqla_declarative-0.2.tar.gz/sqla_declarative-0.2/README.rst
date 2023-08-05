sqla_declarative
================

This package provides an extended Base class for your SQLAlchemy classes.
What this class proposes:
    * the __tablename__ to create/use for the class is automatically defined by class.__name__.lower().
    * it adds a property pk_id which returns the value of the primary key for the object.
    * it attaches a query object to the class which is a shortcut to session.query(class).
    * Function which returns all the DB entry in a HTML table
    * Function to edit/add new entry as a HTML form


Example of usage::

    import sqlalchemy as sa
    from sqlalchemy.orm import (
        scoped_session,
        sessionmaker,
        )
    from zope.sqlalchemy import ZopeTransactionExtension
    from sqla_declarative import extended_declarative_base

    session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
    Base = extended_declarative_base(
        session,
        metadata=sa.MetaData('sqlite:///:memory:'))

    class Test1(Base):
        id = sa.Column(sa.Integer, primary_key=True)
        name = sa.Column(sa.String(50))

    bob = Test1(name='Bob')
    session.add(bob)

    # pk_id detects automatically the primary key and returns it value
    bob.pk_id == 1
    # Easy querying. For example:
    Test1.query.one() == bob

    # To see all the existing entry as HTML
    Test1.view_all()

    # To add/update a new entry as HTML
    widget = Test1.edit_form()
    widget.display()


Build Status
------------

.. |master| image:: https://secure.travis-ci.org/LeResKP/sqla_declarative.png?branch=master
   :alt: Build Status - master branch
   :target: https://travis-ci.org/#!/LeResKP/sqla_declarative

.. |develop| image:: https://secure.travis-ci.org/LeResKP/sqla_declarative.png?branch=develop
   :alt: Build Status - develop branch
   :target: https://travis-ci.org/#!/LeResKP/sqla_declarative

+----------+-----------+
| Branch   | Status    |
+==========+===========+
| master   | |master|  |
+----------+-----------+
| develop  | |develop| |
+----------+-----------+
