#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
log = logging.getLogger(__name__)

from cement.core import foundation, handler, controller
from pprint import pprint
from .protocol import get_rates

class MainController(controller.CementBaseController):
    class Meta:
        description = 'PyCNB entry point'

    @controller.expose()
    def default(self):
        get_rates(self._gotRates)

    def _gotRates(self, rates):
        [pprint(i) for i in rates.items()
            if i[0] in ["EUR", "USD"]]

class PyCNBApp(foundation.CementApp):
    class Meta:
        label = 'pycnb'
        base_controller = MainController

def main():
    app = PyCNBApp()
    app.setup()
    app.run()
