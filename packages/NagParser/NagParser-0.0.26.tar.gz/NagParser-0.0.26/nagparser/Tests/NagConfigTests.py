import unittest

from nagparser.Model.NagConfig import NagConfig, basicgetpermissions


def fakegetpermissions():
    return ['fakepermission']


def buildtestnagconfig():
    basedir = './testdata/'
    files = [basedir + 'test_objects.cache', basedir + 'test_status.dat']
    nagconfig = NagConfig(files)
    nagconfig.APIKEYS = ['abc123', '123abc']

    return nagconfig


class NagConfigTests(unittest.TestCase):

    def setUp(self):
        self.nagconfig = buildtestnagconfig()

    def test_nagconfig_is_Config_instance(self):
        self.assertTrue(isinstance(self.nagconfig, NagConfig))

    def test_fake_files_raise_exception(self):
        files = ['fakefile.cache', 'fakefile.dat']
        self.assertRaises(IOError, NagConfig, files)

    def test_getpermissions_function_set_to_default(self):
        self.assertTrue(self.nagconfig.getpermissions is basicgetpermissions)

    def test_set_getpermissions_function(self):
        self.nagconfig._set_getpermissionsfunction(fakegetpermissions)
        self.assertTrue(self.nagconfig.getpermissions() == ['fakepermission'])

    def test_can_set_and_get_basic_apikeys(self):
        #see setUp for inital set
        self.assertEqual(self.nagconfig.APIKEYS, ['abc123', '123abc'])

        #Test that passing str will result in APIKEYS returning the str as single item list
        self.nagconfig.APIKEYS = 'abc123'
        self.assertEqual(self.nagconfig.APIKEYS, ['abc123'])

    def test_can_use_default_getpermissions(self):
        self.assertTrue(self.nagconfig.getpermissions('abc123') == ['access granted'])
        self.assertTrue(self.nagconfig.getpermissions('123abc') == ['access granted'])
        self.assertTrue(self.nagconfig.getpermissions('fakekey') == [])


if __name__ == '__main__':
    unittest.main()
