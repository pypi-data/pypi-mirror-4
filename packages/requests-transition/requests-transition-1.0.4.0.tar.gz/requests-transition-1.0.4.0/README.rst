requests-transition: Python HTTP for busy people who don't have time to port all their code yet
===============================================================================================

The ``requests`` library is a useful and well-written HTTP library for Python,
by Kenneth Reitz.

In December 2012, Reitz released version 1.0 of requests and decided that it
would break backward compatibility with the 0.x versions. This is a valid
thing to do -- after all, that's what major version numbers are for.

Unfortunately, the state of Python packaging is pretty bad about managing
multiple versions of the same library. There's lots of code out there that
depends on Requests 0.x, and it can't all be instantly updated to 1.0.

Some libraries have been declaring a dependency on "requests < 1.0" using
setuptools, which allows them to keep working if you use setuptools right. But
the problem there is that you can't *ever* upgrade to 1.x while using such
code.

We want to make it possible to move to the shiny new Requests 1.x code.  But we
also want our code stack to keep working in the present.  That's the purpose of
``requests-transition``. All it does is it installs both versions of
``requests`` as two different packages with different names.
    
To use Requests 0.14:

.. code-block:: python

    import requests0 as requests

To use Requests 1.0:

.. code-block:: python

    import requests1 as requests

Installation
------------

To install this distribution, simply:

.. code-block:: bash

    $ pip install requests-transition

For once it's actually relevant that Python distributions can have multiple
packages in them. This will install two packages, ``requests0`` and
``requests1``.

It will not install anything as a package named ``requests``;
that name still belongs to the real distribution of requests, whichever version
of it you choose to install.

