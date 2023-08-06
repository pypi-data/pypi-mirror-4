This module provides a function to calculate tripcodes:

    >>> from tripcode import tripcode
    >>> tripcode('tea')
    'WokonZwxw2'
    >>> tripcode(u'ｋａｍｉ')
    'yGAhoNiShI'

It's notable only in that it also provides a (slow) pure-Python ``crypt(3)``
implementation, which it uses as a fall-back on platforms that don't have
one of their own (e.g. Windows):

   >>> from tripcode import _crypt
   >>> _crypt('encrapt', 'xy')
   'xyk2vcIZuU2vU'
