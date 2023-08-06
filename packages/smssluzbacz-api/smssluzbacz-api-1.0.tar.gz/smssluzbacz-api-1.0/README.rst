smssluzbacz-api
===============

smssluzba-api is API for sending SMS via sms.sluzba.cz HTTP service.
It allows you to send SMS (short text messages) from python applications.
In order to use this API you have to register to http://sms.sluzba.cz/ service.
There is restriction on sms.sluzba.cz that will block your account after
several invalid login attempts. Length of one SMS is restricted to 459 characters.


Note
----

There is known bug in authentication in post API making it unable to authenticate properly.
sms.sluzba.cz service is working on resolving this issue.


Requirements
------------

- python 2.7+


Installation
------------

Install via *pip* or copy this module into your project or into your PYTHON_PATH.

::

 $ pip install smssluzbacz-api


Examples
--------

**Example 1**

Using lite API

::

 from smssluzbacz_api.lite import SmsGateApi

 api = SmsGateApi('login', 'password', timeout=2, use_ssl=True)
 api.send('123456789', 'my SMS message', use_post=True)


**Example 2**

Using post API

::

 from smssluzbacz_api.post import SmsGateApi

 api = SmsGateApi('login', 'password', timeout=2, use_ssl=True)
 api.send('123456789', 'my SMS message')


Tests
-----

**Tested on environment**

- Xubuntu Linux 12.04 LTS precise 64-bit
- python 2.7.3
- python unittest

**Running tests**

To run the unit tests run command: ::

 $ python test.py
 $ python setup.py test


**Running integration tests for lite API**

To run integration tests for lite API run command: ::

 $ python integration_test_lite.py <login> <password> <tel_number>

To list all command line options run command: ::

 $ python integration_test_lite.py --help


**Running integration tests for post API**

To run integration tests for post API run command: ::

 $ python integration_test_post.py <login> <password> <tel_number>

To list all command line options run command: ::

 $ python integration_test_post.py --help



Authors
-------

| Jozef Sevcik, CodeScale s.r.o.
| char0n (Vladimir Gorej, CodeScale s.r.o.)
| email: info@codescale.net
| web: http://www.codescale.net


References
----------

- http://sms.sluzba.cz
- http://sms.sluzba.cz/downloads/SMS_Gate_API_LITE_20.pdf
- http://sms.sluzba.cz/downloads/SMS_Gate_API_POST_20.pdf
- http://github.com/jsk/python-smssluzbacz-api
- http://pypi.python.org/pypi/smssluzbacz-api/
- http://www.codescale.net/en/community#smssluzbacz-api