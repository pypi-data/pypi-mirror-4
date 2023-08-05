Installation
============

You will need `Python <http://python.org>`_ version 2.4 or better to
run :mod:`dataflake.fakeldap`.  Development of 
:mod:`dataflake.fakeldap` is done primarily under Python 2.7, so 
that version is recommended.

.. warning:: To successfully install :mod:`dataflake.fakeldap`, 
   you will need :term:`setuptools` installed on your Python system 
   in order to run the ``easy_install`` command.

It is advisable to install :mod:`dataflake.fakeldap` into a
:term:`virtualenv` in order to obtain isolation from any "system"
packages you've got installed in your Python version (and likewise, 
to prevent :mod:`dataflake.fakeldap` from globally installing 
versions of packages that are not compatible with your system Python).

After you've got the requisite dependencies installed, you may install
:mod:`dataflake.fakeldap` into your Python environment using the 
following command::

  $ easy_install dataflake.fakeldap

If you use :mod:`zc.buildout` you can add :mod:`dataflake.fakeldap`
to the necessary ``eggs`` section to have it pulled in automatically.

When you ``easy_install`` :mod:`dataflake.fakeldap`, the
:term:`python-ldap` libraries are installed if they are not present.
