#!/usr/bin/env python2.3

'''
py-Asterisk distutils script.
'''

__author__ = 'David M. Wilson <dw-py-Asterisk-setup.py@botanicus.net>'
__id__ = '$Id: setup.py 77 2004-09-24 15:39:56Z dw $'

from distutils.core import setup




setup(
    name =          'py-Asterisk',
	version =       '0.1a1',
	description =   'Asterisk Manager API Python interface.',
	author =        'David M. Wilson',
	author_email =  'dw-py-Asterisk-setup.py@botanicus.net',
	license =       'LGPL',
	url =           'http://botanicus.net/dw/',
	download_url =  'http://botanicus.net/dw/py-asterisk.php',
	packages =      [ 'Asterisk' ],
	scripts =       [ 'asterisk-dump', 'py-asterisk' ],
    data_files =    [ ('/etc/asterisk', ['conf/py-asterisk.conf.sample']) ]
)
