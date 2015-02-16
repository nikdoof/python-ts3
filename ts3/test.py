
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import socket
import threading
import time
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
from ts3.protocol import TS3Proto, ConnectionError, NoConnectionError


class TS3ProtoTest(unittest.TestCase):
    """ Tests the TS3Proto class """

    def setUp(self):

        self.ts3 = TS3Proto()

    def testCharacterEscaping(self):

        teststr = '|/ abcdefg| |'
        expected = r'\p\/\sabcdefg\p\s\p'

        res = self.ts3._escape_str(teststr)
        self.assertEqual(res, expected)

    def testControlEscaping(self):

        teststr = "\n\r\t"
        expected = r'\n\r\t'

        self.assertEqual(self.ts3._escape_str(teststr), expected)
        self.assertEqual(self.ts3._escape_str(1), '1')

    def testCharacterUnEscaping(self):

        teststr = r'\p\/\sabcdefg\p\s\p'
        expected = '|/ abcdefg| |'

        self.assertEqual(self.ts3._unescape_str(teststr), expected)
        self.assertEqual(self.ts3._unescape_str('1'), '1')
        self.assertEqual(self.ts3._unescape_str(1), '1')

    def testFullCircle(self):

        teststr = '|/ abcdefg| |'
        res = self.ts3._unescape_str(self.ts3._escape_str(teststr))

        self.assertEqual(res, teststr)

    def testConstructBasic(self):
        self.assertEqual(self.ts3.construct_command('testcommand'), 'testcommand')
        self.assertEqual(self.ts3.construct_command('testcommand', opts=['test']), 'testcommand -test')
        self.assertEqual(self.ts3.construct_command('testcommand', opts=['test1', 'test2', 'test3']), 'testcommand -test1 -test2 -test3')
        self.assertEqual(self.ts3.construct_command('testcommand', keys=OrderedDict([('key1', 'test')])), 'testcommand key1=test')
        self.assertEqual(self.ts3.construct_command('testcommand', keys=OrderedDict([('key1', 'test'), ('key2', 'test')])), 'testcommand key1=test key2=test')
        self.assertEqual(self.ts3.construct_command('testcommand', keys=OrderedDict([('key1', 'test'), ('key2', [1,2,3])])), 'testcommand key1=test key2=1|key2=2|key2=3')
        self.assertEqual(self.ts3.construct_command('testcommand', keys=OrderedDict([('key1', 'test'), ('key2', 'test')]), opts=['test']), 'testcommand key1=test key2=test -test')
    
    def testParseData(self):
        # some response examples taken from http://media.teamspeak.com/ts3_literature/TeamSpeak%203%20Server%20Query%20Manual.pdf

        data = 'timestamp=1259356318 level=4 channel=Query msg=query\sfrom\s87.163.52.195:9\sissued:\slogview\slimitcount=30|timestamp=1259356148'
        parsed = [{'msg': 'query from 87.163.52.195:9 issued: logview limitcount=30', 'timestamp': '1259356318', 'channel': 'Query', 'level': '4'}, {'timestamp': '1259356148'}]

        self.assertEqual(self.ts3.parse_data(data), parsed)

        data = 'cid=2 cldbid=9 cgid=9|cid=2 cldbid=24 cgid=9|cid=2 cldbid=47 cgid=9'
        parsed = [{'cgid': '9', 'cldbid': '9', 'cid': '2'}, {'cgid': '9', 'cldbid': '24', 'cid': '2'}, {'cgid': '9', 'cldbid': '47', 'cid': '2'}]

        self.assertEqual(self.ts3.parse_data(data), parsed)

        data = 'client_unique_identifier=P5H2hrN6+gpQI4n\/dXp3p17vtY0= client_nickname=Rabe85 client_version=3.0.0-alpha24\s[Build:\s8785]\s(UI:\s8785)'
        parsed = {'client_unique_identifier': 'P5H2hrN6+gpQI4n/dXp3p17vtY0=', 'client_version': '3.0.0-alpha24 [Build: 8785] (UI: 8785)', 'client_nickname': 'Rabe85'}

        self.assertEqual(self.ts3.parse_data(data), parsed)


def dummy_ts3(event, sock):
    """
    A simple dummy TS3 server to run tests against
    """
    sock.listen(5)
    event.set()
    try:
        conn, addr = sock.accept()
        conn.send(b"TS3\n\r")
    except socket.timeout:
        pass
    finally:
        sock.close()
        event.set()


class TS3ProtoNetworkTests(unittest.TestCase):

    def setUp(self):
        self.evt = threading.Event()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(3)
        self.sock.bind(('127.0.0.1', 0))
        self.port = self.sock.getsockname()[1]
        threading.Thread(target=dummy_ts3, args=(self.evt, self.sock)).start()
        self.evt.wait()
        self.evt.clear()
        time.sleep(.1)
        self.ts3 = TS3Proto()

    def tearDown(self):
        self.evt.wait()
        if hasattr(self.ts3._telnet, 'sock'):
            self.ts3._telnet.sock.close()

    def testConnect(self):
        self.assertTrue(self.ts3.connect('127.0.0.1', self.port))
        self.assertTrue(self.ts3.is_connected())
        self.assertIsNone(self.ts3.check_connection())

    def testConnectFail(self):
        self.assertRaises(ConnectionError, self.ts3.connect, '127.0.0.1', 9911)

    def testNoConnection(self):
        self.assertFalse(self.ts3.is_connected())
        self.assertRaises(NoConnectionError, self.ts3.check_connection())


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TS3ProtoTest))
    suite.addTest(unittest.makeSuite(TS3ProtoNetworkTests))
    return suite

if __name__ == '__main__':
    unittest.main()
