Tooth.paste: Shiny new Python packages!
=======================================

Tooth.paste creates shiny new Python packages. Start your new packages with a prepared
Sphinx documentation section, a test folder for your unit tests and a Makefile containing
all the tools needed to keep your Python code clean.


Get started
-----------

Create a virtualenv and activate it::

    $ virtualenv --no-site-packages trytoothpaste
    $ cd trytoothpaste
    $ source ./bin/activate
 
Install tooth.paste in your virtualenv::
 
    $ pip install tooth.paste


Creating a new package
----------------------

Create shiny new Python package::

    $ ./bin/templer tooth_basic_namespace my.project


.. note::

   Right now only basic namespace packages are supported. These contain one dot in the
   name. Basic packages without a dot will be added soon, as well as packges with a 
   nested namespace (2 dots in name).


Get started with the new package
--------------------------------

Prepare everything for development by running ``make build``::

    $ cd my.project
    $ make build

Document your package
---------------------

Once you have created your new package, you can directly write some documentation
in the following reStructuredText document::

    docs/source/index.rst

Consult `The Quick reStructuredText <http://docutils.sourceforge.net/docs/user/rst/quickref.html>`_ 
reference to get started with reStructuredText.

Build the html Sphinx documentation
-----------------------------------

Run ``make docs`` to generate the Sphinx documentation in HTML::

    $ make docs

Open the HTML documentation in your browser and verify that the layout looks good::

    docs/build/html/index.html 

Write some code
---------------

You can start adding code::

    cd my/project
    vim __init__.py

Write some tests
----------------

You can start adding code::

    tests/test_project.py

Run the tests
-------------

Run the unit tests::

    $ make test

Run the coverage
----------------

Run the coverage tool::
   
    $ make coverage

You can then have a look at the coverage in the generated HTML pages::

    htmlcov/index.html

Run pylint
----------

Run the pylint tool:: 

    $ make pylint

Run flake8
----------

Runt the flake8 tool::

    $ make flake8

Run pep8:
---------

Run the pep8 tool::

    $ make pep8


Travis-CI:
----------

`Activate the Travis Service hook for Github <http://travis-ci.org/profile>`_

Read the docs:
--------------

`Add a web hook for Read the docs <http://read-the-docs.readthedocs.org/en/latest/webhooks.html>`_

Contents:

.. toctree::
   :maxdepth: 2

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
