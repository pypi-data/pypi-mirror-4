import unittest

import rfc3161

class Rfc3161(unittest.TestCase):
    PUBLIC_TSA_SERVER = 'http://time.certum.pl'

    def test_timestamp(self):
        try:
            value, substrate = rfc3161.RemoteTimestamper(self.PUBLIC_TSA_SERVER)(data='xx')
        except rfc3161.TimestampingError:
            return
        self.assertNotEqual(value, None)
        self.assertEqual(substrate, '')
