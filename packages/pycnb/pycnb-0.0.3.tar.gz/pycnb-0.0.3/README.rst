PyCNB
======

Twisted protocol for `Czech National Bank daily rates <http://www.cnb.cz/cs/index.html>`_.

Usage
=====

::

    >>> from pycnb import EUR
    >>> EUR
    Decimal('25.260')

You can use any currency identificator which is published by CNB instead of the EUR.

Also you can just run::

    $ pycnb
    ('USD', Decimal('19.279'))
    ('EUR', Decimal('25.260'))

which is hardcoded, but trivial to fix
