import unittest
import doctest
import imageresizer.observable

def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(imageresizer.observable))
    return tests
