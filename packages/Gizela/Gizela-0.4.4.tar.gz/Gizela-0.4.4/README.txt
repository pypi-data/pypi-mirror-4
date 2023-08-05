Gizela
******

`Homepage <https://pypi.python.org/pypi/Gizela/>`_

Gizela provides
===============
* reading adjustment of geodetic network from program 
  gama-local v. 1.9 (xml results) with covariance matrix
* computing statistical quantities for coordinate displacement
  test
* drawing error ellipses and displacement ellipses


Install from source
===================
Git clone: ::

    git://github.com/gizela/gizela.git

Build Python package: ::

    cd gizela
    python setup.py sdist

Install package: ::

    easy_install dist/Gizela-_version_-tar.gz


Install with ``easy_install``
=============================
Go to `Gizela project page <http://pypi.python.org/pypi/Gizela/>`_. Download tarball and install: ::

    easy_install Gizela-_version_.tar.gz

Or simply use ``easy_install`` without previous download: ::

    easy_install Gizela


For coordinate displacement testing use script
==============================================
::

    bin/gama-data-adj.py
