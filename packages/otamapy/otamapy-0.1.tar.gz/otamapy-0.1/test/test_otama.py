import unittest
from StringIO import StringIO
from otama import Otama


class TestOtama(unittest.TestCase):

    def setUp(self):
        self.db = Otama()

    def test_open(self):
        self.assertEqual(None, None)
