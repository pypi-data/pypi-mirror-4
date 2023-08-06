#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys, code, readline
from decimal import Decimal
from rlcompleter import Completer

from cement.core import foundation, handler, controller
from twisted.internet import reactor

from .protocol import get_rates
from pycnb import version

class MainController(controller.CementBaseController):
    class Meta:
        description = 'Access cnb.cz daily rates with the comfort of your command line'
        arguments = [
            (['-i', '--interactive'], dict(action='store_true')),
            (['-v', '--version'], dict(action='store_true')),
        ]

    def get_callbacks(self):
        if self.pargs.interactive:
            return [self.create_namespace, self.interact]
        else:
            return [self.print_all]

    def version(self):
        print(version)

    @controller.expose()
    def default(self):
        if self.pargs.version:
            return self.version()

        d = get_rates(reactor)
        for cb in self.get_callbacks():
            d.addCallback(cb)

        d.addBoth(lambda x: reactor.stop())
        reactor.run()

    def create_namespace(self, ns):
        ns['D'] = Decimal
        return ns

    def _get_banner(self):
        cprt = 'Type "help", "copyright", "credits" or "license" for more information.'
        banner = "Python %s on %s\n%s\n" % (sys.version, sys.platform,
            cprt)
        # ^ standard banner made by `code.interact`
        banner += "PyCNB v{0}".format(version)
        return banner

    def interact(self, ns):
        c = Completer(ns)
        readline.set_completer(c.complete)
        readline.parse_and_bind("tab: complete")
        code.interact(self._get_banner(), local=ns)

    def print_all(self, rates):
        for c,r in rates.items():
            print("{currency} {rate}".format(currency=c, rate=r))

class PyCNBApp(foundation.CementApp):
    class Meta:
        label = 'pycnb'
        base_controller = MainController

def main():
    app = PyCNBApp()
    app.setup()
    app.run()
