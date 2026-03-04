================
Python packaging
================

Process Steps
=============

1. Develop **pyproject.toml** and other `distribution-related files`_
#. Build and test distribution; should pass all `distribution tests`_
#. Register project with the Python Package Index (PyPI)
#. Upload distribution(s) to PyPI


.. _`distribution tests`:

Distribution tests
==================

* ``uv build`` does not raise an exception
* all expected files are included in the sdist/wheel
* ``uv run pytest`` works in install environment
* acceptance tests pass in install environment
* ``uv pip install .`` works
* ``uv sync --extra test`` works
* ``pip install semaverse-pptx`` works


Test can install with all popular methods
-----------------------------------------

* manual
* pip
* uv


.. _`distribution-related files`:

Distribution-related files
==========================

* pyproject.toml
* MANIFEST.in
* tox.ini
* uv.lock


----


Distribution user stories
=========================

... some notions about who uses these and for what ...


Roles
-----

* naive end-user


Use Cases
---------

Test build before distribution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


"Just-works" installation
^^^^^^^^^^^^^^^^^^^^^^^^^

::

   In order to enable a new capability in my computing environment
   As a naive end-user
   I would like installation to "just work" and not scare me with error
   messages that don't indicate a real problem.


Install as a dependency
^^^^^^^^^^^^^^^^^^^^^^^


Verify installation
^^^^^^^^^^^^^^^^^^^

::

   In order to verify a new installation
   As a python developer
   I want to be able to easily run the test suite without having to invest in
   any additional discovery or configuration.



Resources
=========

* `The Hitchhiker’s Guide to Packaging`_
* `Writing a Package in Python`_ by Tarek Ziadé is an extract from his PACKT
  book *Expert Python Programming* and while being somewhat dated, contains
  some useful tidbits.
* `tox documentation`_
* `uv documentation`_
* `How To Package Your Python Code`_
* `Python Packaging: Hate, hate, hate everywhere`_
* `Building and Distributing Packages with setuptools`_
* `A guide to Python packaging`_
* `Python Packaging by Tarek Ziade`_

.. _`The Hitchhiker’s Guide to Packaging`:
   http://guide.python-distribute.org/index.html

.. _`Writing a Package in Python`:
   http://zetcode.com/articles/packageinpython/

.. _`Python's Makefile`:
   http://blog.ianbicking.org/pythons-makefile.html

.. _tox documentation:
   https://tox.wiki/

.. _uv documentation:
   https://docs.astral.sh/uv/

.. _`Python Packaging: Hate, hate, hate everywhere`:
   http://lucumr.pocoo.org/2012/6/22/hate-hate-hate-everywhere/

.. _How To Package Your Python Code:
   http://www.scotttorborg.com/python-packaging/

.. _Building and Distributing Packages with setuptools:
   http://peak.telecommunity.com/DevCenter/setuptools

.. _`A guide to Python packaging`:
   http://www.ibm.com/developerworks/opensource/library/os-pythonpackaging/index.html

.. _`Python Packaging by Tarek Ziade`:
   http://www.aosabook.org/en/packaging.html
