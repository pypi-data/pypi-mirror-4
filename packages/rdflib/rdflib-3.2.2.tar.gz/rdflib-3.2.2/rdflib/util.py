"""
Some utility functions.

Miscellaneous utilities

* list2set
* first
* uniq
* more_than

Term characterisation and generation

* to_term
* from_n3

Date/time utilities

* date_time
* parse_date_time

Statement and component type checkers

* check_context
* check_subject
* check_predicate
* check_object
* check_statement
* check_pattern

"""

from calendar import timegm
from time import altzone
#from time import daylight
from time import gmtime
from time import localtime
from time import time
from time import timezone

try:
    cmp
except NameError:
    def sign(n):
        if n < 0: return -1
        if n > 0: return 1
        return 0
else:
    def sign(n): return cmp(n, 0)

from rdflib.exceptions import ContextTypeError
from rdflib.exceptions import ObjectTypeError
from rdflib.exceptions import PredicateTypeError
from rdflib.exceptions import SubjectTypeError
from rdflib.graph import Graph
from rdflib.graph import QuotedGraph
from rdflib.term import BNode
from rdflib.term import Literal
from rdflib.term import URIRef

__all__ = ['list2set', 'first', 'uniq', 'more_than', 'to_term', 'from_n3','date_time', 'parse_date_time', 'check_context', 'check_subject', 'check_predicate', 'check_object', 'check_statement', 'check_pattern']

def list2set(seq):
    """
    Return a new list without duplicates. 
    Preserves the order, unlike set(seq)
    """
    seen = set()
    return [ x for x in seq if x not in seen and not seen.add(x)]

def first(seq):
    for result in seq:
        return result
    return None

def uniq(sequence, strip=0):
    """removes duplicate strings from the sequence."""
    if strip:
        return set(s.strip() for s in sequence)
    else:
        return set(sequence)

def more_than(sequence, number):
    "Returns 1 if sequence has more items than number and 0 if not."
    i = 0
    for item in sequence:
        i += 1
        if i > number:
            return 1
    return 0

def to_term(s, default=None):
    """
    Creates and returns an Identifier of type corresponding 
    to the pattern of the given positional argument string ``s``:

    '' returns the ``default`` keyword argument value or ``None``

    '<s>' returns ``URIRef(s)`` (i.e. without angle brackets)

    '"s"' returns ``Literal(s)`` (i.e. without doublequotes)

    '_s' returns ``BNode(s)`` (i.e. without leading underscore)

    """
    if not s:
        return default
    elif s.startswith("<") and s.endswith(">"):
        return URIRef(s[1:-1])
    elif s.startswith('"') and s.endswith('"'):
        return Literal(s[1:-1])
    elif s.startswith("_"):
        return BNode(s)
    else:
        msg = "Unrecognised term syntax: '%s'" % s
        raise Exception(msg)

def from_n3(s, default=None, backend=None):
    r'''
    Creates the Identifier corresponding to the given n3 string. 
    
        >>> from_n3('<http://ex.com/foo>') == URIRef('http://ex.com/foo')
        True
        >>> from_n3('"foo"@de') == Literal('foo', lang='de')
        True
        >>> from_n3('"""multi\nline\nstring"""@en') == Literal('multi\nline\nstring', lang='en')
        True
        >>> from_n3('42') == Literal(42)
        True
        
    '''
    # TODO: should be able to handle prefixes given as opt. argument maybe: from_n3('rdfs:label')
    if not s:
        return default
    if s.startswith('<'):
        return URIRef(s[1:-1])
    elif s.startswith('"'):
        if s.startswith('"""'):
            quotes = '"""'
        else:
            quotes =  '"'
        value, rest = s.rsplit(quotes, 1)
        value = value[len(quotes):] # strip leading quotes
        datatype = None
        language = None
        
        # as a given datatype overrules lang-tag check for it first
        dtoffset = rest.rfind('^^')
        if dtoffset >= 0:
            # found a datatype
            # datatype has to come after lang-tag so ignore everything before
            # see: http://www.w3.org/TR/2011/WD-turtle-20110809/#prod-turtle2-RDFLiteral
            datatype = rest[dtoffset+2:]
        else:
            if rest.startswith("@"):
                language = rest[1:] # strip leading at sign
        
        value = value.replace(r'\"', '"').replace('\\\\', '\\')
        # Hack: this should correctly handle strings with either native unicode
        # characters, or \u1234 unicode escapes.
        value = value.encode("raw-unicode-escape").decode("unicode-escape")
        return Literal(value, language, datatype)
    elif s == 'true' or s == 'false':
        return Literal(s == 'true')
    elif s.isdigit():
        return Literal(int(s))
    elif s.startswith('{'):
        identifier = from_n3(s[1:-1])
        return QuotedGraph(backend, identifier)
    elif s.startswith('['):
        identifier = from_n3(s[1:-1])
        return Graph(backend, identifier)
    else:
        if s.startswith("_:"):
            return BNode(s[2:])
        else:
            return BNode(s)

def check_context(c):
    if not (isinstance(c, URIRef) or \
            isinstance(c, BNode)):
        raise ContextTypeError("%s:%s" % (c, type(c)))

def check_subject(s):
    """ Test that s is a valid subject identifier."""
    if not (isinstance(s, URIRef) or isinstance(s, BNode)):
        raise SubjectTypeError(s)

def check_predicate(p):
    """ Test that p is a valid predicate identifier."""
    if not isinstance(p, URIRef):
        raise PredicateTypeError(p)

def check_object(o):
    """ Test that o is a valid object identifier."""
    if not (isinstance(o, URIRef) or \
            isinstance(o, Literal) or \
            isinstance(o, BNode)):
        raise ObjectTypeError(o)

def check_statement(triple):
    (s, p, o) = triple
    if not (isinstance(s, URIRef) or isinstance(s, BNode)):
        raise SubjectTypeError(s)

    if not isinstance(p, URIRef):
        raise PredicateTypeError(p)

    if not (isinstance(o, URIRef) or \
            isinstance(o, Literal) or \
            isinstance(o, BNode)):
        raise ObjectTypeError(o)

def check_pattern(triple):
    (s, p, o) = triple
    if s and not (isinstance(s, URIRef) or isinstance(s, BNode)):
        raise SubjectTypeError(s)

    if p and not isinstance(p, URIRef):
        raise PredicateTypeError(p)

    if o and not (isinstance(o, URIRef) or \
                  isinstance(o, Literal) or \
                  isinstance(o, BNode)):
        raise ObjectTypeError(o)

def date_time(t=None, local_time_zone=False):
    """http://www.w3.org/TR/NOTE-datetime ex: 1997-07-16T19:20:30Z

    >>> date_time(1126482850)
    '2005-09-11T23:54:10Z'

    @@ this will change depending on where it is run
    #>>> date_time(1126482850, local_time_zone=True)
    #'2005-09-11T19:54:10-04:00'

    >>> date_time(1)
    '1970-01-01T00:00:01Z'

    >>> date_time(0)
    '1970-01-01T00:00:00Z'
    """
    if t is None:
        t = time()

    if local_time_zone:
        time_tuple = localtime(t)
        if time_tuple[8]:
            tz_mins = altzone // 60
        else:
            tz_mins = timezone // 60
        tzd = "-%02d:%02d" % (tz_mins // 60, tz_mins % 60)
    else:
        time_tuple = gmtime(t)
        tzd = "Z"

    year, month, day, hh, mm, ss, wd, y, z = time_tuple
    s = "%0004d-%02d-%02dT%02d:%02d:%02d%s" % ( year, month, day, hh, mm, ss, tzd)
    return s

def parse_date_time(val):
    """always returns seconds in UTC

    # tests are written like this to make any errors easier to understand
    >>> parse_date_time('2005-09-11T23:54:10Z') - 1126482850.0
    0.0

    >>> parse_date_time('2005-09-11T16:54:10-07:00') - 1126482850.0
    0.0

    >>> parse_date_time('1970-01-01T00:00:01Z') - 1.0
    0.0

    >>> parse_date_time('1970-01-01T00:00:00Z') - 0.0
    0.0
    >>> parse_date_time("2005-09-05T10:42:00") - 1125916920.0
    0.0
    """

    if "T" not in val:
        val += "T00:00:00Z"

    ymd, time = val.split("T")
    hms, tz_str = time[0:8], time[8:]

    if not tz_str or tz_str=="Z":
        time = time[:-1]
        tz_offset = 0
    else:
        signed_hrs = int(tz_str[:3])
        mins = int(tz_str[4:6])
        secs = (sign(signed_hrs) * mins + signed_hrs * 60) * 60
        tz_offset = -secs

    year, month, day = ymd.split("-")
    hour, minute, second = hms.split(":")

    t = timegm((int(year), int(month), int(day), int(hour),
                int(minute), int(second), 0, 0, 0))
    t = t + tz_offset
    return t

def test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    # try to make the tests work outside of the time zone they were written in
    #import os, time
    #os.environ['TZ'] = 'US/Pacific'
    #try:
    #    time.tzset()
    #except AttributeError, e:
    #    print e
        #pass
        # tzset missing! see
        # http://mail.python.org/pipermail/python-dev/2003-April/034480.html
    test()  # pragma: no cover
