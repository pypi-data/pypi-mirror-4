Using dataflake.fakeldap
========================

The class :class:`ldap.fakeldap.FakeLDAPConnection` can be used 
as a replacement for the various connection-modeling classes 
in the module :mod:`ldap.ldapobject`.

If the connection class used by your code can be provided at 
runtime, simply use the replacement:

.. code-block:: python

    from dataflake.fakeldap import FakeLDAPConnection

    class MyClass(object):

        def __init__(self, connection_class, uri):
            self.connection = connection_class(uri)

    ...

    my_object = MyClass(connection_class=FakeLDAPConnection)


If your code imports one of the different LDAP connection classes
inside the :mod:`ldap.ldapobject` module directly, you can simply 
patch in the :class:`ldap.fakeldap.FakeLDAPConnection` class:

.. code-block:: python

    class MyTests(unittest.TestCase):

        def setUp(self):
            from dataflake.fakeldap import FakeLDAPConnection
            from ldap import ldapobject
            self.old_connection_class = ldapobject.LDAPObject
            ldapobject.LDAPObject = FakeLDAPConnection

        def tearDown(self):
            from ldap import ldapobject
            ldapobject.LDAPObject = self.old_connection_class

        def test_something(self):
            ...


