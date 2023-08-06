import unittest

import pickle

from nagparser.Model.NagCommands import NagCommands

from nagfactoryTests import nagfromtestdata
from expectedresults import expectedresultsfolder

#Fully hydrated nag object with test data
nag = nagfromtestdata()


class BaseTests(unittest.TestCase):
    def test_commands_property_is_NagCommands_instance(self):
        self.assertTrue(isinstance(nag.commands, NagCommands))

    def test_attributes_property_is_correct(self):
        with open(expectedresultsfolder + '/nag_attributes.pickle') as f:
            self.assertEqual(nag.attributes, pickle.load(f))

    def test_getbad(self):
        print nag.status

if __name__ == '__main__':
    unittest.main()
