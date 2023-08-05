# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name='pydhcp-ldap-schema',
    version='0.1alpha',
    author='Dariusz Górecki',
    author_email='darek.krk@gmail.com',
    url='https://github.com/canni/pydhcp-ldap-schema',
    description='ISC-DHCP LDAP Schema manipulation helper',
    py_modules=['pydhcp_ldap_schema'],
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP',
    ],
)
