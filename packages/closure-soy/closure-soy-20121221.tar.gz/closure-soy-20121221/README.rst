-----
Usage
-----

1. ``pip install closure-soy``
2. ``closure-soy [<flag1> <flag2> ...] --outputPathFormat <formatString> <soyFile1> <soyFile2> ...``

Note: Consider integrating this package into webassets or another such package for automatic soy template compilation.


-----
About
-----

`Closure Templates <https://developers.google.com/closure/templates/>`_ is
a client and server side templating system for building reusable HTML and UI elements.
Closure's templating system is also commonly known as Soy templates.

This is a Java-based tool. This package, based on the
`Closure Compiler <http://pypi.python.org/pypi/closure/>`_ package,
provides a simple way to install and use the the Closure Template compiler from 
Python, bundling the ``soy.jar`` with the Python package.

This package was built for integrating with `webassets`_ for automatic template compiliation.

.. _webassets: https://github.com/miracle2k/webassets


--------
Versions
--------

Version ``YYYYMMDD`` of this package will bundle the corresponding 
version of the compiler (Closure uses the build date as the version).


If you want a new version to be uploaded, open a ticket at the
`Github page <https://github.com/Emsu/python-soy>`_.
