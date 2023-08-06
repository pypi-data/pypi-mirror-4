import re
import logging
import urllib

from smssluzbacz_api import Transport, TelephoneNumberError, MessageError, ActionError, LoginError, CreditError,\
    GateError, TRUNCATE_LIMIT


log = logging.getLogger(__name__)


class SmsGateApi(object):
    """Implements 'Lite' version of sms.sluzba.cz HTTP API.

    The only possibility of lite version is to send POST/GET request to send SMS
    with no advanced options and operations.

    """
    URL = 'http://smsgateapi.sluzba.cz/apilite20/sms'
    URL_SSL = 'https://smsgateapi.sluzba.cz/apilite20/sms'

    def __init__(self, login, password, timeout=2, use_ssl=True):
        """Initializes SmsGateApi class.

        :param login: sms.sluzba.cz login
        :rtype login: string
        :param password: password to sms.sluzba.cz
        :rtype password: string
        :param timeout: http connection timeout in seconds
        :rtype timeout: int
        :param use_ssl: whether to use ssl via http or not
        :rtype use_ssl: bool
        :returns: SmsGateApi instance
        :rtype: smssluzbacz_api.lite.SmsGateApi

        """
        self.login = login
        self.password = password
        self.timeout = timeout
        self.use_ssl = use_ssl


    def send(self, tel_number, message, use_post=True):
        """Sends SMS via sms.sluzba.cz.

        :param tel_number: telephone number of SMS receiver
        :rtype tel_number: string
        :param message: text body of SMS
        :rtype message: string
        :param use_post: whether to use GET or POST http method
        :rtype use_post: bool
        :returns: True is SMS was successfully sent
        :rtype: bool
        :raises: ValueError, urllib2.URLError, urllib2.HTTPError, GateError
        :raises: TelephoneNumberError, MessageError, ActionError, LoginError
        :raises: CreditError

        """
        if message is not None and len(message) > TRUNCATE_LIMIT:
            log.warn('Message text exceeds %d characters and will be automatically truncated', TRUNCATE_LIMIT)
        params = (
            ('login', self.login),
            ('password', self.password),
            ('number', tel_number),
            ('text', message)
        )
        log.debug('Params built: %s', params)
        log.info('Sending SMS to number: %s, message text: %s', tel_number, message)
        if use_post:
            transport = Transport(SmsGateApi.URL_SSL if self.use_ssl else SmsGateApi.URL, timeout=self.timeout)
            response, contents = transport.process(params=params)
        else:
            encoded_params = urllib.urlencode(params)
            encoded_url = '?'.join([SmsGateApi.URL_SSL, encoded_params]) if self.use_ssl else '?'.join([SmsGateApi.URL, encoded_params])
            transport = Transport(encoded_url, timeout=self.timeout)
            response, contents = transport.process()
        if response.code != 200:
            raise GateError
        if re.match(r'^{0}'.format(TelephoneNumberError.code), contents) is not None:
            raise TelephoneNumberError
        elif re.match(r'^{0}'.format(MessageError.code), contents) is not None:
            raise MessageError
        elif contents[:3] == ActionError.code:
            raise ActionError
        elif contents[:3] == LoginError.code:
            raise LoginError
        elif contents[:3] == CreditError.code:
            raise CreditError
        elif contents[:3] == GateError.code:
            raise GateError
        elif contents[:3] == '200':
            log.info('SMS message successfully sent to %s.', tel_number)
            return True

