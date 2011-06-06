import unittest
from __init__ import TS3Proto

class TS3ProtoTest(unittest.TestCase):
    """ Tests the TS3Proto class """

    def setUp(self):

        self.ts3 = TS3Proto()

    def testCharacterEscaping(self):

        teststr = '|/ abcdefg| |'
        expected = r'\p\/\sabcdefg\p\s\p'

        res = self.ts3._escape_str(teststr)
        self.assertTrue(res == expected)

    def testControlEscaping(self):

        teststr = "\n\r\t"
        expected = r'\n\r\t'

        self.assertTrue(self.ts3._escape_str(teststr) == expected)

    def testCharacterUnEscaping(self):

        teststr = r'\p\/\sabcdefg\p\s\p'
        expected = '|/ abcdefg| |'

        self.assertTrue(self.ts3._unescape_str(teststr) == expected)

    def testFullCircle(self):

        teststr = '|/ abcdefg| |'
        res = self.ts3._unescape_str(self.ts3._escape_str(teststr))

        self.assertTrue(res == teststr)

    def testConstructBasic(self):

        self.assertTrue(self.ts3.construct_command('testcommand'), 'testcommand')
        self.assertTrue(self.ts3.construct_command('testcommand', opts=['test']), 'testcommand -test')
        self.assertTrue(self.ts3.construct_command('testcommand', keys={'key1': 'test'}), 'testcommand key1=test')
        self.assertTrue(self.ts3.construct_command('testcommand', keys={'key1': 'test', 'key2': 'test'}), 'testcommand key1=test|key2=test')
        self.assertTrue(self.ts3.construct_command('testcommand', keys={'key1': 'test', 'key2': 'test'}, opts=['test']), 'testcommand key1=test|key2=test -test')

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TS3ProtoTest))
    return suite

if __name__ == '__main__':
    unittest.main()
