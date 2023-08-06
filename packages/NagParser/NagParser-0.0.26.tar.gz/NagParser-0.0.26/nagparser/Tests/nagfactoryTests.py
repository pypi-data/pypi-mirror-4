import unittest

from nagparser import parse
from nagparser.Model import Nag

from NagConfigTests import buildtestnagconfig


def nagfromtestdata():
    return parse(buildtestnagconfig())


class nagfactoryTests(unittest.TestCase):
    def test_build_nag_instance_from_test_config(self):
        self.assertTrue(isinstance(nagfromtestdata(), Nag))


if __name__ == '__main__':
    unittest.main()
