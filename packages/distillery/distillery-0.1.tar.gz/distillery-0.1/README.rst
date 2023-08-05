Distillery
==========

.. image:: https://secure.travis-ci.org/jeanphix/distillery.png

``distillery`` is another `fatory_girl <https://github.com/thoughtbot/factory_girl>`_ like for python ORMs.


Installation
------------

``pip install distillery``


Defining distilleries
---------------------

Each distillery has a ``__model__`` and a set of attributes and methods. The ``__model__`` is the ORM model class from which instance will be produced::

    class UserDistillery(MyOrmDistillery):
        __model__ = User


Attributes
~~~~~~~~~~

A distillery class attribute defines default values for specific model field::

    class UserDistillery(MyOrmDistillery):
        __model__ = User

        username = "defaultusername"

All new ``User`` outputted from ``UserDistillery`` will have ``defaultusername`` as ``username`` field value while there's no override.


Methods (a.k.a. "lazy attributes")
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A distillery class method allow to build dinamic value for specific field::

    from distillery import lazy


    class UserDistillery(MyOrmDistillery):
        __model__ = User

        username = "defaultusername"

        @lazy
        def email_address(cls, instance, sequence):
            return "%s@%s" % (instance.username, instance.company.domain)

All new ``User`` outputted from ``UserDistillery`` will have an ``email_address`` computed from his username and his company domain.

Note: all lazies received an ``instance`` and a ``sequence`` that are respectively the object instance and an auto incremented sequence.


Using distilleries
------------------


Distillery.init()
~~~~~~~~~~~~~~~~~

Inits and populates an instance::

    user = UserDistillery.init()
    assert user.username == "defaultusername"
    assert user.id is None

    user = UserDistillery.create(username="overriddenusername")
    assert user.username == "overriddenusername"
    assert user.id is None


Distillery.create()
~~~~~~~~~~~~~~~~~~~

Inits, populates and persists an instance::

    user = UserDistillery.create()
    assert user.username == "defaultusername"
    assert user.id is not None


Datasets
--------

``distillery`` provides a ``Set`` class that act as a fixture container.

A ``Set`` needs a ``__distillery__`` class member from where all instances will born::

    from distillery import Set


    class UserSet(Set):
        __distillery__ = UserDistillery

        class jeanphix:
            username = 'jeanphix'


Then simply instanciate the ``UserSet`` to access the fixture object::

    users = UserSet()
    assert users.jeanphix.username == 'jeanphix'


Cross ``Set`` relations are also allowed::

    from distillery import Set


    class CompanySet(Set):
        __distillery__ = CompanyDistillery

        class my_company:
            name = "My company"


    class UserSet(Set):
        __distillery__ = UserDistillery

        class jeanphix:
            username = 'jeanphix'
            company = CompanySet.company


    users = UserSet()
    assert users.jeanphix.company == 'My company'


``Set`` can also create fixture instances on demand when they are accessed by setting ``on_demand`` constructor parameter::

    users = UserSet(on_demand=True)
    users.jeanphix  # jeanphix will be created here.


ORMs
----

Django
~~~~~~

Django models could be distilled using ``DjangoDistillery`` that only requires a ``__model__`` class member::

    from distillery import DjangoDistillery

    from django.auth.models import User

    class UserDistillery(DjangoDistillery):
        __model__ = User

        #  ...


SQLAlchemy
~~~~~~~~~~

SQLAlchemy distilleries require a ``__model__`` and a ``__session__`` class members::

    from distillery import SQLAlchemyDistillery

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine('sqlite://', echo=False)
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    Base = declarative_base()

    class User(Base):
        #  ...


    class UserDistillery(SQLAlchemyDistillery):
        __model__ = User
        __session__ = session

        #  ...
