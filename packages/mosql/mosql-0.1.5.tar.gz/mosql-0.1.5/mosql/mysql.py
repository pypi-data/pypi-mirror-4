#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''It applies the MySQL-specific stuff to :mod:`mosql.util`.

Usage:

::

    import mosql.mysql

It will replace the function in :mod:`mosql.util` with it.
'''

char_escape_map = {
    # The following 7 chars is escaped in MySQL Connector/C (0.6.2)
    '\0' : r'\0',
    '\n' : r'\n',
    '\r' : r'\r',
    '\\' : r'\\',
    '\'' : r'\'',
    '\"' : r'\"',
    '\x1A' : r'\Z',
    # The following 4 chars is escaped in OWASP Enterprise Security API (1.0)
    '\b' : r'\b',
    '\t' : r'\t',
    #'%'  : r'\%',
    #'_'  : r'\_',
    # The above 2 chars shouldn't be escaped, because '\%' and '\_' evaluate
    # to string '\%' and '\_' outside of pattern-matching contexts. Programmers
    # should take responsibility for escaping them in pattern-matching contexts.
}

def escape(s):
    '''The function is designed for MySQL.

    >>> tmpl = "select * from person where person_id = '%s';"
    >>> evil_value = "' or true; --"

    >>> print tmpl % escape(evil_value)
    select * from person where person_id = '\\' or true; --';
    '''
    global char_escape_map
    return ''.join(char_escape_map.get(c) or c for c in s)

def fast_escape(s):
    '''This function only escapes the ' (single-quote) and \ (backslash).

    It is enough for security and correctness, and it is faster 50x than using
    the :func:`escape`.

    It is used for replacing the :func:`mosql.util.escape` if you import this
    moudle.
    '''
    return s.replace('\\', '\\\\').replace("'", r"\'")

import mosql.util
mosql.util.escape = fast_escape

if __name__ == '__main__':
    import doctest
    doctest.testmod()

    #from timeit import timeit
    #from functools import partial

    #timeit = partial(timeit, number=100000)
    #bytes = ''.join(chr(i) for i in range(256))

    #def _escape(s):
    #    return s.replace("'", "''")

    #print timeit(lambda: _escape(bytes))
    ## -> 0.118767976761

    #print timeit(lambda: escape(bytes))
    ## -> 7.97847890854

    #print timeit(lambda: fast_escape(bytes))
    ## -> 0.155963897705
