# -*- coding: utf-8 -*-

from distutils.core import setup

import pydhcp_ldap_schema

setup(
    name='pydhcp-ldap-schema',
    version=pydhcp_ldap_schema.__version__,
    author='Dariusz Górecki',
    author_email='darek.krk@gmail.com',
    url='https://github.com/canni/pydhcp-ldap-schema',
    description='ISC-DHCP LDAP Schema manipulation helper',
    py_modules=['pydhcp_ldap_schema'],
    keywords=['dhcp', 'ldap', 'schema'],
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP',
    ],
)
