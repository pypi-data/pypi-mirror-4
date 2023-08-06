import unittest
import urllib2

from smssluzbacz_api import Transport


class TestTransport(unittest.TestCase):

    def setUp(self):
        self.url = 'https://smsgateapi.sluzba.cz/apipost20/sms'
        self.transport = Transport(self.url)

    def test_transport_no_params(self):
        response, contents = self.transport.process()
        self.assertEqual(response.code, 200)
        self.assertEqual(contents, '<status><id>400</id><message>Neznama akce</message></status>')

    def test_transport_params(self):
        params = (
            ('msg', 'message'),
            ('msisdn', '123456789'),
            ('act', 'send'),
            ('login', 'login'),
            ('auth', 'auth')
        )
        response, contents = self.transport.process(params=params)
        self.assertEqual(response.code, 200)
        self.assertEqual(contents, '<status><id>401</id><message>Chybne prihlaseni</message></status>')

    def test_transport_no_url(self):
        with self.assertRaises(ValueError):
            self.transport.url = ''
            self.transport.process()

    def test_transport_invalid_url(self):
        with self.assertRaises(urllib2.URLError):
            self.transport.url = 'http://test'
            self.transport.process()

    def test_transport_timeout_error(self):
        with self.assertRaises(urllib2.URLError):
            self.transport.timeout = 0
            self.transport.process()

    def test_transport_http_error(self):
        with self.assertRaises(urllib2.HTTPError):
            self.transport.url += 'a' * 4
            self.transport.process()


if __name__ == '__main__':
    unittest.main()