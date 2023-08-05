Command line
============

The :program:`pypel` script is the main tool of the :mod:`pypel` package. It
simplifies receipts management providing several commands.

Command line usage
------------------

::

    $ pypel --help
    usage: pypel [-h] [-v] {show,set,del,sum,gpg} ...

    Easy receipts management.

    positional arguments:
      {show,set,del,sum,gpg}
                            commands
        show                Show receipts' metadata
        set                 Set receipts' metadata
        del                 Delete receipts' metadata
        sum                 Sum receipts' price
        gpg                 Sign or verify receipts

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit

:program:`pypel` commands
-------------------------

- **show**: :ref:`command-show`
- **set**: :ref:`command-set`
- **del**: :ref:`command-del`
- **sum**: :ref:`command-sum`
- **gpg**: :ref:`command-gpg`

.. note:: Receipts' supported extensions are: jpg, jpeg, png, eps.

.. _command-show:

Show receipts' metadata
^^^^^^^^^^^^^^^^^^^^^^^

::

    pypel show [-h] [-v] [-c] receipt [receipt ...]

.. program:: pypel show

.. cmdoption:: -c, --color

   Colorize the output. Useful only if you use ``--verify`` option.

   .. note:: `Pygments <http://pygments.org/>`_ version 1.5 or superior is
              required.

.. cmdoption:: -v, --verify

   Verify receipts.

   .. note:: `python-gnupg <http://code.google.com/p/python-gnupg/>`_  version
              0.3.0 or superior  is required.

.. _command-set:

Set receipts' metadata
^^^^^^^^^^^^^^^^^^^^^^

::

    pypel set [-h] [-p PRICE] [-r RETAILER] receipt [receipt ...]

.. program:: pypel set

.. cmdoption:: -p PRICE, --price PRICE

   Set receipt's price to ``PRICE``.

.. cmdoption:: -r RETAILER, --retailer RETAILER

   Set receipt's retailer to ``RETAILER``.

.. _command-del:

Delete receipts' metadata
^^^^^^^^^^^^^^^^^^^^^^^^^

::

    pypel del [-h] [-p] [-r] receipt [receipt ...]

.. program:: pypel del

.. cmdoption:: -p, --price

   Delete receipt's price.

.. cmdoption:: -r, --retailer

   Delete receipt's retailer.

.. _command-sum:

Sum receipts' price
^^^^^^^^^^^^^^^^^^^

Sum receipts' price and print the result.

::

    pypel sum [-h] receipt [receipt ...]


.. _command-gpg:

Sign or verify receipts
^^^^^^^^^^^^^^^^^^^^^^^

.. note:: `python-gnupg <http://code.google.com/p/python-gnupg/>`_  version
          0.3.0 or superior  is required.

The GPG Key :program:`pypel` will use is specified by the ``PYPELKEY``
environment variable.

::

    pypel gpg [-h] [-s | -v] receipt [receipt ...]

.. program:: pypel gpg

.. cmdoption:: -s, --sign

   Sign receipts.

.. cmdoption:: -v, --verify

   Verify receipts.
