=============
 Development
=============

Getting the source code
=======================
The source code is maintained in the Dataflake Git 
repository. To check out the trunk:

.. code-block:: sh

  $ git clone https://git.dataflake.org/git/dataflake.fakeldap

You can also browse the code online at 
http://git.dataflake.org/cgit/dataflake.fakeldap


Bug tracker
===========
For bug reports, suggestions or questions please use the 
Launchpad bug tracker at 
https://bugs.launchpad.net/dataflake.fakeldap .


Sharing Your Changes
====================

.. note::

   Please ensure that all tests are passing before you submit your code.
   If possible, your submission should include new tests for new features
   or bug fixes, although it is possible that you may have tested your
   new code by updating existing tests.

If you got a read-only checkout from the Git repository, and you
have made a change you would like to share, the best route is to let
Git help you make a patch file:

.. code-block:: sh

   $ git diff > dataflake.fakeldap-cool_feature.patch

You can then upload that patch file as an attachment to a Launchpad bug
report.

Running the tests in a ``virtualenv``
=====================================
If you use the ``virtualenv`` package to create lightweight Python
development environments, you can run the tests using nothing more
than the ``python`` binary in a virtualenv.  First, create a scratch
environment:

.. code-block:: sh

   $ /path/to/virtualenv --no-site-packages /tmp/virtualpy

Next, get this package registered as a "development egg" in the
environment:

.. code-block:: sh

   $ /tmp/virtualpy/bin/python setup.py develop

Finally, run the tests using the build-in ``setuptools`` testrunner:

.. code-block:: sh

   $ /tmp/virtualpy/bin/python setup.py test
   running test
   ...
   test_search_startswithendswith_wildcard (dataflake.fakeldap.tests.test_fakeldap_search.FakeLDAPSearchTests) ... ok
   
   ----------------------------------------------------------------------
   Ran 56 tests in 0.033
   
   OK

If you have the :mod:`nose` package installed in the virtualenv, you can
use its testrunner too:

.. code-block:: sh

   $ /tmp/virtualpy/bin/easy_install nose
   ...
   $ /tmp/virtualpy/bin/python setup.py nosetests
   running nosetests
   ....................................................
   ----------------------------------------------------------------------
   Ran 57 tests in 0.049s

   OK

or:

.. code-block:: sh

   $ /tmp/virtualpy/bin/nosetests
   .....................................................
   ----------------------------------------------------------------------
   Ran 63 tests in 0.072s

   OK

If you have the :mod:`coverage` package installed in the virtualenv,
you can see how well the tests cover the code:

.. code-block:: sh

   $ /tmp/virtualpy/bin/easy_install nose coverage
   ...
   $ /tmp/virtualpy/bin/python setup.py nosetests \
       --with-coverage --cover-package=dataflake.fakeldap
   running nosetests
   ...
   .........................................................
   Name                 Stmts   Miss  Cover   Missing
   --------------------------------------------------
   dataflake.fakeldap     397     45    89%   ...
   ----------------------------------------------------------------------
   Ran 57 tests in 0.071s

   OK

Building the documentation in a ``virtualenv``
==============================================

:mod:`dataflake.fakeldap` uses the nifty :mod:`Sphinx` documentation system
for building its docs.  Using the same virtualenv you set up to run the
tests, you can build the docs:

.. code-block:: sh

   $ /tmp/virtualpy/bin/easy_install Sphinx pkginfo
   ...
   $ cd docs
   $ PATH=/tmp/virtualpy/bin:$PATH make html
   sphinx-build -b html -d _build/doctrees   . _build/html
   ...
   build succeeded.

   Build finished. The HTML pages are in _build/html.


Running the tests using  :mod:`zc.buildout`
===========================================

:mod:`dataflake.fakeldap` ships with its own :file:`buildout.cfg` file and
:file:`bootstrap.py` for setting up a development buildout:

.. code-block:: sh

  $ python bootstrap.py
  ...
  Generated script '.../bin/buildout'
  $ bin/buildout
  ...

Once you have a buildout, the tests can be run as follows:

.. code-block:: sh

   $ bin/test 
   Running tests at level 1
   Running zope.testrunner.layer.UnitTests tests:
     Set up zope.testrunner.layer.UnitTests in 0.000 seconds.
     Running:
   ..............................................................
     Ran 62 tests with 0 failures and 0 errors in 0.043 seconds.
   Tearing down left over layers:
     Tear down zope.testrunner.layer.UnitTests in 0.000 seconds.


Building the documentation using :mod:`zc.buildout`
===================================================

The :mod:`dataflake.fakeldap` buildout installs the Sphinx 
scripts required to build the documentation, including testing 
its code snippets:

.. code-block:: sh

    $ bin/docbuilder.sh
    rm -rf _build/*
    sphinx-build -b html -d _build/doctrees   . _build/html
    Making output directory...
    Running Sphinx v1.1.3
    ...
    build succeeded.

    Build finished. The HTML pages are in .../docs/_build/html.

To build the documentation as PDF you first need to ensure your system 
has a latex2pdf binary installed.

.. code-block:: sh

    $ bin/pdfbuilder.sh
    sphinx-build -b latex -d _build/doctrees   . _build/latex
    Making output directory...
    Running Sphinx v1.1.3
    ...
    Output written on dataflake.fakeldap.pdf (15 pages, 96151 bytes).
    Transcript written on dataflake.fakeldap.log.


Making a release
================

These instructions assume that you have a development sandbox set 
up using :mod:`zc.buildout` as the scripts used here are generated 
by the buildout.

The first thing to do when making a release is to check that the ReST
to be uploaded to PyPI is valid:

.. code-block:: sh

  $ bin/docpy setup.py --long-description | bin/rst2 html \
    --link-stylesheet \
    --stylesheet=http://www.python.org/styles/styles.css > desc.html

Once you're certain everything is as it should be, the following will
build the distribution, upload it to PyPI, register the metadata with
PyPI and upload the Sphinx documentation to PyPI:

.. code-block:: sh

  $ bin/buildout -o
  $ bin/docbuilder.sh
  $ bin/pdfbuilder.sh
  $ bin/docpy setup.py sdist register upload upload_sphinx \
        --upload-dir=docs/_build/html

The ``bin/buildout`` step will make sure the correct package information 
is used.

