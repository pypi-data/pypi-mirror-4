import unittest

from bravo.simplex import set_seed, simplex, octaves2, octaves3

class TestOctaves(unittest.TestCase):

    def setUp(self):
        set_seed(0)

    def test_trivial(self):
        pass

    def test_identity(self):
        for i in range(512):
            self.assertEqual(simplex(i, i), octaves2(i, i, 1))
        for i in range(512):
            self.assertEqual(simplex(i, i, i), octaves3(i, i, i, 1))
