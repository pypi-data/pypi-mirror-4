# -*- coding: utf-8 -*-
from setuptools import setup
import smssluzbacz_api
import os


def read(fname):
    """Utility function to read the README file.

    Used for the long_description. It's nice, because now 1) we have a top level
    README file and 2) it's easier to type in the README file than to put a raw
    string in below ...

    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='smssluzbacz-api',
    version=smssluzbacz_api.__version__,
    description='api library for sending SMS (shor text message) via sms.sluzba.cz service',
    long_description=read('README.rst'),
    author=u'Vladimír Gorej, Jozef Ševčík',
    author_email='info@codescale.net',
    url='http://www.codescale.net/en/community#smssluzbacz-api',
    download_url='https://github.com/jsk/python-smssluzbacz-api/tarball/master',
    license='BSD',
    keywords = 'sms api',
    packages=['smssluzbacz_api', 'smssluzbacz_api.lite', 'smssluzbacz_api.post',
              'smssluzbacz_api.xml', 'smssluzbacz_api.test', 'smssluzbacz_api.test.lite',
              'smssluzbacz_api.test.post', 'smssluzbacz_api.test.xml'],
    platforms='any',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
    test_suite='smssluzbacz_api.test'
)