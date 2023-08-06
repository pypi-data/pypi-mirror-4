PyCNB
======
Access cnb.cz daily rates with the comfort of your command line

CLI and Twisted protocol for `Czech National Bank daily rates <http://www.cnb.cz/cs/index.html>`_.

Usage
=====

from shell::

    $ pycnb
    USD 19.835
    IDR 2.042
    BGN 13.229
    ILS 5.468
    GBP 30.268
    DKK 3.471
    CAD 19.365
    JPY 20.153
    …

lists all the available rates in format::

     CURRENCY, " ", RATE

or interactive (with tab-completion)::

    $ pycnb -i
    Python 2.7.3 (default, Mar 23 2013, 00:49:43)
    [GCC 4.6.3] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    PyCNB v0.0.4
    >>> USD * 20
    Decimal('396.700')
    >>> USD * D('10.4')
    Decimal('206.2840')

from code::

    from pycnb.protocol import get_rates
    d = get_rates(reactor)
    d.addCallback(process_rates)
