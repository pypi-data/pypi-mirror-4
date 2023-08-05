# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name                = 'pyxmli',
    packages            = ['pyxmli'],
    version             = open('VERSION').read(),
    author              = u'Greendizer',
    author_email        = 'developers@xmli.com',
    install_requires    = ['pycrypto >= 2.6',
                           'lxml >= 2.3'],
    url                 = 'http://github.com/Greendizer/PyXMLi',
    license             = open('LICENCE').read(),
    description         = 'Create XMLi 2.0 compliant invoices in Python.',
    long_description    = open('README.markdown').read(),
    zip_safe            = True,
)