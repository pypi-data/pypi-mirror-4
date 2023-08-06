import unittest
from unittest import TestCase
from dm.util.password import generate

def suite():
    suites = [
            unittest.makeSuite(TestPassword),
        ]
    return unittest.TestSuite(suites)

class TestPassword(TestCase):

    def test_generate(self):
        password = generate()
        self.failUnless(len(password) == 8)

    def test_generate_size(self):
        size = 10
        password = generate(size)
        self.failUnless(len(password) == size)

