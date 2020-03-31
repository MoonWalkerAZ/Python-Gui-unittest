import unittest
import unittest.runner
import itertools
import collections
import time
import asyncio

class TestVisaMethods(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        pass

    @classmethod
    def tearDownClass(self):
        pass

    @unittest.skip("demonstrating skipping")
    def test_upper(self):
        time.sleep(1)

        self.assertEqual('foo2'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        time.sleep(1.2)
        s = 'hello world'
        self.assertEqual(s.split(), ['hello2', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)


if __name__ == '__main__':
    unittest.main()