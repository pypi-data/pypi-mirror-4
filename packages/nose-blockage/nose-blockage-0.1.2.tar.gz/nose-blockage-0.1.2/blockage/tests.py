import smtplib
import unittest
import urllib

from plugins import MockHTTPCall, MockSMTPCall, NoseBlockage


class Test(unittest.TestCase):

    def setUp(self):
        self.plugin = NoseBlockage()
        self.plugin.whitelists = {'http': 'www.mozilla.org', 'smtp': ''}
        self.plugin.begin()

    def test_http(self):
        urllib.urlopen('http://www.mozilla.org')
        with self.assertRaises(MockHTTPCall):
            urllib.urlopen('http://foo.org')

    def test_smtp(self):
        with self.assertRaises(MockSMTPCall):
            smtplib.SMTP('localhost')
