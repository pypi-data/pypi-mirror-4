Installing pypel
================

``pypel`` requires `pyexiv2 <http://tilloy.net/dev/pyexiv2/>`_
version 0.3.2 or superior.

Optionally you can also install `Pygments <http://pygments.org/>`_ version 1.5
or superior (for console coloured output) and
`python-gnupg <http://code.google.com/p/python-gnupg/>`_  version 0.3.0 or
superior (for signing and verifying receipts).

You can choose to install ``pypel`` automatically or manually.

Automatic installation
----------------------

Simply install ``pypel`` using ``pip``::

    $ pip install pypel

Alternatively you can directly install from a packaged version or from the
mercurial repository using ``pip``.

For example, if you want to install version 0.1 from the mercurial repository
you have to do::

    $ pip install -e http://hg.mornie.org/pypel/@0.1#egg=pypel

Or from the packaged version::

    $ pip install http//downloads.mornie.org/pypel/pypel-0.1.tar.gz

Manual installation
-------------------

You can download packaged version from http://downloads.mornie.org/pypel
and and use Python's ``distutils`` to install.
