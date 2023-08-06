__version__ = '1.0'

import urllib
import urllib2
import logging


log = logging.getLogger(__name__)


TRUNCATE_LIMIT = 459


class Transport(object):

    USER_AGENT = 'smssluzbacz_api'

    def __init__(self, url, timeout=2, additional_handlers=None):
        """Initializes Transport class.

        :param url: url to be requested
        :rtype url: string
        :param timeout: http connection timeout in seconds
        :rtype timeout: int
        :param additional_handlers: list of additional http handlers
        :rtype additional_handlers: list
        :returns: Transport instance
        :rtype: smssluzbacz_api.Transport

        """
        self.opener = urllib2.build_opener()
        if additional_handlers is not None:
            for handler in additional_handlers:
                self.opener.add_handler(handler)
        self.opener.addheaders = [('User-agent', self.USER_AGENT)]
        self.url = url
        self.timeout = timeout

    def process(self, params=None):
        """Processes request/response to sms.sluzba.cz.

        :param params: mapping or sequence of 2-tuples
        :rtype params: tuple or dict
        :rtype: None
        :raises: ValueError, urllib2.URLError, urllib2.HTTPError

        """
        try:
            urllib2.install_opener(self.opener)
            data = urllib.urlencode(params) if params is not None else None
            log.info('Making HTTP request to url %s', self.url)
            response = self.opener.open(self.url, timeout=self.timeout, data=data)
            contents = response.read()
            response.close()
            return response, contents
        except ValueError:
            log.exception('Url to is invalid')
            raise
        except urllib2.URLError:
            log.exception('Something went wrong while processing urllib2 handlers')
            raise
        except urllib2.HTTPError:
            log.exception('Something went wrong while requesting url %s', self.url)
            raise
        finally:
            self.opener.close()


class Error(Exception):
    """Base Error class for all package errors."""

    def __init__(self):
        super(Error, self).__init__(getattr(self, 'code'), getattr(self, 'message'))


class TelephoneNumberError(Error):

    code = '400;1'
    message = 'Telephone number is invalid.'


class MessageError(Error):

    code = '400;2'
    message = 'Message is empty.'


class ActionError(Error):

    code = '400'
    message = 'Unknown action.'


class LoginError(Error):

    code = '401'
    message = 'Invalid login credentials.'


class CreditError(Error):

    code = '402'
    message = 'Insufficient credit in your account.'


class GateError(Error):

    code = '503'
    message = 'SMS gate intercepted unknown error.'