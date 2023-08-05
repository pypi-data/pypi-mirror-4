'''
Asterisk Manager API Python package.
'''

__author__ = 'David M. Wilson <dw@botanicus.net>'
__id__ = '$Id: __init__.py 61 2004-09-22 12:01:48Z dw $'

try:
    __revision__ = int('$Rev$'.split()[1])
except:
    __revision__ = None

__version__ = '0.1'
__all__ = [ 'CLI', 'Config', 'Logging', 'Manager', 'Util' ]



cause_codes = {
     0: (  0, 'UNKNOWN',        'Unkown'                    ),
     1: (  1, 'UNALLOCATED',    'Unallocated number'        ),
    16: ( 16, 'CLEAR',          'Normal call clearing'      ),
    17: ( 17, 'BUSY',           'User busy'                 ),
    18: ( 18, 'NOUSER',         'No user responding'        ),
    21: ( 21, 'REJECTED',       'Call rejected'             ),
    22: ( 22, 'CHANGED',        'Number changed'            ),
    27: ( 27, 'DESTFAIL',       'Destination out of order'  ),
    28: ( 28, 'NETFAIL',        'Network out of order'      ),
    41: ( 41, 'TEMPFAIL',       'Temporary failure'         )
}




class BaseException(Exception):
    '''
    Base class for all py-Asterisk exceptions.
    '''

    _prefix = '(Base Exception)'
    _error = '(no error)'

    def __init__(self, error):
        self._error = error

    def __str__(self):
        return '%s: %s' % (self._prefix, self._error)
