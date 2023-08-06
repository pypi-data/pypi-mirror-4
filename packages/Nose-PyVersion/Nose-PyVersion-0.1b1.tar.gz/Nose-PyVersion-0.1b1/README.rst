Nose-PyVersion
==============

Nose-PyVersion is a plugin that excludes files from nosetests based on python filename and python version. It's useful for writing tests to test code which uses syntax that is invalid in certain python versions.

This plugins purpose is mainly to test syntax differences between python 2.x and 3.x.

Excluding files
---------------

Files are excluded based on filename. Files can be excluded for major, minor or micro version.

Filename pattern::

    [NAME][PYVERSION_SEPARATOR]py[MAJOR][MINOR]?[MICRO]?.py

The default separator is '_', it can be changed with the option `pyversion-separator`, an empty separator is allowed.

.. note:: Some separators cannot be used beacuse it messes up nose. For example a dot, `.`, cannot be used as separator.


Files not excluded for python version 2.7.3::

    somefile_py2.py
    somefile_py27.py
    somefile_py273.py

Files excluded for python version 2.7.3::

    somefile_py3.py
    somefile_py26.py
    somefile_py271.py

Usage
-----

With setup.py
-------------

Step 1: Add Nose-PyVersion to test_requires and tell nose how to find the plugin.

Example::

    setup(
        ...
        tests_require=['nose_pyversion'],
        entry_points="""
        [nose.plugins]
        pyversion=nose_pyversion:PyVersion
        """

Step 2: Enable pyversion in setup.cfg. `pyversion-separator` can also be set(optional).

Example::

    [nosetests]
    with-pyversion=1
    pyversion-separator=-


Now the tests can be run with `setup.py nosetests`. If you want `setup.py test` to use nose set `test_suite` to `nose.collector`.

Using nose for tests::

    setup(
        ...
        test_suite='nose.collector'
        ...
    )


With standalone nosetests
-------------------------

Add '--with-pyversion':

    nosetests -with-pyversion

.. note:: Running with standalone nosetests will fail if setup.cfg contains s `pyversion-separator` options. This is a bug that should be fixed but I don't know how.

Plugin options
--------------

Nose-PyVersion supports one configuration options, 'pyversion-separator'. That is the separator that is used to find files that should be excluded from tests.

Python versions
---------------

Nose-PyVersion supports python 2.7.3 and python 3.3 through `2to3`. Other versions are not tested.

Source
------

The source is hosted on `http://github.com/danielholmstrom/nose-pyversion <http://github.com/danielholmstrom/nose-pyversion>`_.

License
-------

Nose-PyVersion is released under the MIT license.

.. toctree::

