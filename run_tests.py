#!/usr/bin/env python3
import doctest
import inspect
import unittest

import helpers

# helpers use doctest for their tests, but we convert doctest to unittest since unittest has nicer output
testSuite = unittest.TestSuite()

for member in dir(helpers):
    mod = getattr(helpers, member)
    if inspect.ismodule(mod):
        testSuite.addTests(doctest.DocTestSuite(mod))


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(testSuite)
