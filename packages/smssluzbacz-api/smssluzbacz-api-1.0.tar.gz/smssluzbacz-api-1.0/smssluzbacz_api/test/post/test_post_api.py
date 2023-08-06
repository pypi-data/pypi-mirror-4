import unittest

import smssluzbacz_api.post
from smssluzbacz_api.test import TransportMock, HttpResponseMock
from smssluzbacz_api import TelephoneNumberError, MessageError, ActionError, LoginError, CreditError,\
    GateError


class TestSmsGateApiPost(unittest.TestCase):

    def setUp(self):
        smssluzbacz_api.post.Transport = TransportMock

    def test_non_200_response_code(self):
        with self.assertRaises(GateError):
            response = HttpResponseMock()
            response.code = 1000
            TransportMock.process_returns((response, ''))
            api = smssluzbacz_api.post.SmsGateApi('login', 'pass')
            api.send('123456789', 'message')

    def test_telephone_number_error(self):
        with self.assertRaises(TelephoneNumberError):
            response = HttpResponseMock()
            response.code = 200
            TransportMock.process_returns((response,
                                           '<status><id>{0}</id><message></message></status>'.format(TelephoneNumberError.code)))
            api = smssluzbacz_api.post.SmsGateApi('login', 'pass')
            api.send('12345-6789', 'message')

    def test_message_error(self):
        with self.assertRaises(MessageError):
            response = HttpResponseMock()
            response.code = 200
            TransportMock.process_returns((response,
                                           '<status><id>{0}</id><message></message></status>'.format(MessageError.code)))
            api = smssluzbacz_api.post.SmsGateApi('login', 'pass')
            api.send('123456789', '')

    def test_action_error(self):
        with self.assertRaises(ActionError):
            response = HttpResponseMock()
            response.code = 200
            TransportMock.process_returns((response,
                                           '<status><id>{0}</id><message></message></status>'.format(ActionError.code)))
            api = smssluzbacz_api.post.SmsGateApi('login', 'pass')
            api.send('123456789', 'message')

    def test_login_error(self):
        with self.assertRaises(LoginError):
            response = HttpResponseMock()
            response.code = 200
            TransportMock.process_returns((response,
                                           '<status><id>{0}</id><message></message></status>'.format(LoginError.code)))
            api = smssluzbacz_api.post.SmsGateApi('login', 'pass')
            api.send('123456789', 'message')

    def test_credit_error(self):
        with self.assertRaises(CreditError):
            response = HttpResponseMock()
            response.code = 200
            TransportMock.process_returns((response,
                                           '<status><id>{0}</id><message></message></status>'.format(CreditError.code)))
            api = smssluzbacz_api.post.SmsGateApi('login', 'pass')
            api.send('123456789', 'message')

    def test_gate_error(self):
        with self.assertRaises(GateError):
            response = HttpResponseMock()
            response.code = 200
            TransportMock.process_returns((response,
                                           '<status><id>{0}</id><message></message></status>'.format(GateError.code)))
            api = smssluzbacz_api.post.SmsGateApi('login', 'pass')
            api.send('123456789', 'message')

    def test_no_error(self):
        response = HttpResponseMock()
        response.code = 200
        TransportMock.process_returns((response, '<status><id>200</id><message></message></status>'))
        api = smssluzbacz_api.post.SmsGateApi('login', 'pass')
        result = api.send('123456789', 'message')
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()