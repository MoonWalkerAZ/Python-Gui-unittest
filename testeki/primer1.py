import unittest
import unittest.runner
import itertools
import collections
import time
import asyncio

class TestseEn(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        pass

    @classmethod
    def tearDownClass(self):
        pass

    def test_zgoraj(self):
        time.sleep(0.5)
        self.assertEqual('foo2'.upper(), 'FOO')

    def test_alizgoraj(self):
        self.assertFalse('Foo'.isupper())

    def test_narazen(self):
        time.sleep(0.2)
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)


if __name__ == '__main__':
    unittest.main()