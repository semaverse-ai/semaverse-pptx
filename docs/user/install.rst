.. _install:

Installing
==========

|pp| is hosted on PyPI, so installing with `pip` is simple::

    pip install semaverse-pptx

|pp| depends on the ``lxml`` package and ``Pillow``, the modern version of
the Python Imaging Library (``PIL``). The charting features depend on
``XlsxWriter``. ``pip`` will install these dependencies automatically.

Currently |pp| requires Python 3.9 or later. The tests are run against Python 3.9
through 3.13.

Dependencies
------------

* Python 3.9 or later
* lxml
* Pillow
* XlsxWriter (to use charting features)
