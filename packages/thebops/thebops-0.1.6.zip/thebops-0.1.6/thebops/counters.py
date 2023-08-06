#!/usr/bin/python
# -*- coding: latin-1 -*- äöü vim: ts=8 sts=4 et si sw=4 tw=79 
"""
Python module counters                            (c) Tobias Herp 2005,2012
~~~~~~~~~~~~~~~~~~~~~~
Provides utility functions to count several things, e.g. errors or warnings.

Typical usage:

    from thebops.counters import error, count, register_counters, all_counters
    register_counters(dirs='director[y|ies] skipped',
                      read='file[s] read')
    for f in glob.glob('*'):
        if os.path.isdir(f):
            count('dirs')
        try:
            fil = open(f, 'r')
            count('read')
        except IOError, info:
            error(info, 'read')
            continue
        ...
    all_counters()

Counting functions:

count(key)             increase the counter for the given key
error(text [,subkey])  print a text to stderr, increase the error counter,
                       and (if given) the error:subkey counter as well
warning(text [,subkey])  like error(), but affects the warning counter
register_counters()    tell all_counters (see below) about the description
                       strings to use

Output your results:

counted(key, text)     print a line for the given counter, if it is > 0;
                       the text may contain "[a singular|plural] version[s]"
all_counters([key])    print a line for every counter whose value is > 0;
                       the numbers will be nicely adjusted
all_counted_strings([key])  use this if you want to use the results for
                       something else than printing
counted_string(key[, text])  returns the string which would be printed by
                       all_counters() or '' otherwise

Error handling, inspired by the 'errors' module:

check_errors([text[, code]])  Terminate the program, if any errors have
                       occurred already
fatal(text, code, tell, count, help, subtype)   (all arguments optional)
                       Terminates the program (for fatal errors), with
                       some smart defaults

Adjust the module's operation:

recursion(boo)         switch recursive counting operation off (default)
                       or on
reset(key[, resetmax])  resets the counter of the given key (and all of
                       its subkeys) to 0; by default doesn't touch _MAXCOUNT
reset_all([resetmax])  resets all counters; by default, resets _MAXCOUNT
                       as well

Helper functions:

freezeText(text, plu)  parses the given text and returns the singular or
                       plural version
digits(i)              returns the number of digits needed for decimal
                       representation 

Variables:

ERR_FILE      The file (or file-like object) error() and warning()
              print to, by default: sys.stderr
FILE          The file (or file-like object) counted() and all_counters()
              print to, by default: sys.stdout
TEXT_SUBTYPE  A string used for unregistered subkeys of registered keys,
              default: ', subtype: '
SEPARATOR     the separator character for keys given as strings, default:
              ':'

Keys are (key, [subkey,][..]) tuples of strings internally; for convenience,
they can be specified as 'key[:subkey][..]' strings. E.g.,

    error("couldn't read file %s" % filename, 'io:read')

will increase the counters ('error',) and ('error', 'io', 'read') and,
if recursion is switched on ("recursion(True)"), ('error', 'io') as well.

When called by itself, displays a little demo, counting the characters
given in the argument string.
"""
# TODO:
# - alle Funktionen dokumentieren
# - ... und systematisieren
# - (einzelne) Strings für 0-Werte
# - type-Aufrufe durch isinstance ersetzen

VERSION = '.'.join(map(str,
                       (0,
                        4, # modinfo integriert
                        'rev-%s' % '$Rev: 961 $'[6:-2],
                        )))
from types import StringType, TupleType, ListType
import sys

# you may set these to any open file-like object:
ERR_FILE = sys.stderr  # used by error(), warning()
FILE =     sys.stdout  # used by counted(), and thus implicitely by all_counters()

from thebops.errors import RC_ERROR, RC_OK, RC_HELP, RC_CANCEL, RC_ABORT, \
        set_progname, progname
set_progname('counters')
try: _
except NameError:
    def _(s): return s

COUNTER = {}
try:
    True, False
except NameError:
    False = not 1
    True  = not False

# if True, count('one:two') will increase the counters 'one' and 'one:two';
# change via --> switch_recursion(boo)
_RECURSE = False

# override with --> register_counters():
TEXT = {('error',): 'error[s]',
        ('warning',): 'warning[s]',
        }
TEXT_SUBTYPE = ', subtype: '
# is as wide (in decimal presentation) as the largest counter:
_MAXCOUNT = 9
__all__ = ['count', 'counted',
           'freezeText',
           'used_counters', 'all_counters', 'register_counters',
           'error', 'warning',
           ]
SEPARATOR = ':' # e.g. 'error:fileio' instead of ('error', 'fileio'); convenience

def _getProgName():
    from os.path import splitext, split
    from sys import argv
    return splitext(split(argv[0])[1])[0]

PROG = _getProgName() or 'Python Shell'
MASK = None

def _getMask():
    MASK = globals()['MASK']
    if MASK is None:
        MASK = ''.join(('%', str(digits(globals()['_MAXCOUNT'])), 'd %s'))
    return MASK

def _isTupleOfStrings(seq):
    """
    >>> _isTupleOfStrings(('eins', 'zwei'))
    True
    >>> _isTupleOfStrings(['eins', 'zwei'])
    False
    >>> _isTupleOfStrings(('eins', 2))
    False
    """
    if not type(seq) is TupleType:
        return False
    for topic in seq:
        if not type(topic) is StringType:
            return False
    return True
       
def _isListOfStrings(seq):
    """
    >>> _isListOfStrings(('eins', 'zwei'))
    False
    >>> _isListOfStrings(['eins', 'zwei'])
    True
    >>> _isListOfStrings(['eins', 2])
    False
    """
    if not type(seq) is ListType:
        return False
    for topic in seq:
        if not type(topic) is StringType:
            return False
    return True
        
def _normalizeKey(key):
    """
    takes a string or a sequence; returns a tuple.

    >>> _normalizeKey('eins:zwei')
    ('eins', 'zwei')
    >>> _normalizeKey('eins')
    ('eins',)
    >>> _normalizeKey('eins:')
    ('eins',)
    >>> _normalizeKey(None)
    ()
    """
    if type(key) is TupleType:
        assert _isTupleOfStrings(key)
        return key
    elif key is None:
        return ()
    elif type(key) is StringType:
        if SEPARATOR in key:
            return tuple([s for s in key.split(SEPARATOR)
                          if s])
        else:
            return (key,)
    elif type(key) is ListType:
        assert _isListOfStrings(key)
        return tuple(key)
    else:
        raise TypeError('tuple or string expected (%s; %s)'
                        % (str(key), type(key)))

def _count_raw(key):
    """
    working horse for count() and count_all();
    don't use it directly!
    """
    if COUNTER.has_key(key):
        COUNTER[key] += 1
        if COUNTER[key] > globals()['_MAXCOUNT']:
            globals()['_MAXCOUNT'] = globals()['_MAXCOUNT'] * 10 + 9
            if globals()['MASK']:
                globals()['MASK'] = None
    else:
        COUNTER[key] = 1

def count(key):
    """
    increase the counter with the given (normalized) key
    >>> count('eins:zwei')
    >>> counted_value(('eins', 'zwei'))
    1
    >>> count('eins:zwei')
    >>> counted_value(('eins', 'zwei'))
    2
    """
    key = _normalizeKey(key)
    _count_raw(key)
count_simple = count

def count_all(key):
    """
    like count_simple(key), but increases the 'parent' keys as well
    """
    key = _normalizeKey(key)
    for l in range(1, len(key)+1):
        _count_raw(key[:l])

def counted(key, text, zero=0, reset=0):
    """
    print a line of text, if count(key) has been called before
    """
    key = _normalizeKey(key)
    if COUNTER.has_key(key):
        val = COUNTER[key]
        if val or zero:
            print >> FILE, (_getMask()
                            % (val,
                               freezeText(text, COUNTER[key] != 1)))
        if val and reset:
            COUNTER[key] = 0

def counted_value(key):
    """
    return the counted value for the given key, or 0
    """
    key = _normalizeKey(key)
    if COUNTER.has_key(key):
        return COUNTER[key]
    else:
        return 0

def counted_string(key, text=None):
    """
    >>> counted_string(('counted', 'string'), 'Ding[sda|er]')
    ''
    >>> count('counted:string')
    >>> counted_string(('counted', 'string'), 'Ding[sda|er]')
    '1 Dingsda'
    >>> count('counted::string')
    >>> counted_string(('counted', 'string'), 'Ding[sda|er]')
    '2 Dinger'
    """
    key = _normalizeKey(key)
    if not COUNTER.has_key(key):
        return ''
    else:
        if text is None:
            text = _getText(key)
        return _getMask() % (COUNTER[key],
                             freezeText(text, COUNTER[key] != 1))

def used_counters(spec=None):
    """
    return the counter keys used (sorted and reversed; this way, e.g. with
    a variety of 'error' counters, the ('error',) counter follows all of
    the subtypes).

    Used by --> all_counters()
    """
    if spec and not type(spec) is TupleType:
        spec = _normalizeKey(spec)
    if spec:
        lis = [ k for k in COUNTER.keys()
                  if k[:len(spec)] == spec ]
    else:
        lis = COUNTER.keys()
    lis.sort()
    lis.reverse()
    return tuple(lis)

def all_counters(spec=None, zeroes=None, reset=0):
    """
    prints the messages for all counters which have been used.
    Since no text arguments are given, the function tries to
    get a registered text, and in case there is none,
    creates one using the key

    spec -- a filter

    zeroes -- show 0 values as well?

    reset -- reset every printed counter to zero
    """
    for tup in used_counters(spec):
        counted(tup, _getText(tup), zeroes, reset)

def all_counted_strings(spec=None):
    """
    returns a list of strings, containing
    the messages for all counters which have been used.
    Since no text arguments are given, the function tries to
    get a registered text, and in case there is none,
    creates one using the key
    """
    res = []
    for tup in used_counters(spec):
        s = counted_string(tup, _getText(tup))
        if s: res.append(s)
    return res

def register_counters(_dic={}, **args):
    """
    if you intend to use all_counters() to print a line for every
    counter which as been used (i.e. it is greater 0), register every
    counter you use. By default, 'error' is registered as 'error[s]',
    and 'warning' is registered as 'warning[s]'.
    If you do 
        register_counters({'error:io': 'I/O error[s]'}),
    and call
        error('io')
    at least once,
        all_counters()
    will summarize I/O errors as '{count} I/O error[s]'; otherwise,
    it will give you '{count} error[s], subtype: io'.
    
    Takes a dictionary of keys (tuples or strings, see --> _normalizeKey()).

    If the keys are valid Python identifyers, you can just use named
    arguments; for a hierarchy of counters, you must use a dictionary,
    whose keys are then normalized (i.e., e.g. 'error:fileio' is turned into
    ('error', 'fileio') etc.)
    """
    TEXT = globals()['TEXT']
    for k in _dic.keys():
        kk = _normalizeKey(k)
        TEXT[kk] = _dic[k]
    for k in args.keys():
        kk = (k,)
        TEXT[kk] = args[k]

def _getText(key):
    """
    return the registered text for a given key
    """
    assert type(key) is TupleType
    # key IS a tuple:
    if TEXT.has_key(key):
        return TEXT[key]
    else:
        tmp = range(1, len(key))
        tmp.reverse()
        for l in tmp:
            if TEXT.has_key(key[:l]):
                return TEXT_SUBTYPE.join((TEXT[key[:l]],
                                          SEPARATOR.join(key[l:])))
        return SEPARATOR.join(key)

def error(text, subtype=None):
    """
    print {program name}: {text} to (by default) stderr, and increase the
    'error' counter.  If an error subtype is specified,
    count(subtype) is called as well
    """
    print >> ERR_FILE, globals()['PROG']+':E', text
    count(('error',))
    if subtype:
        count(('error',)+_normalizeKey(subtype))
error_simple = error

def error_recursive(text, subtype=None):
    """
    print {program name}: {text} to (by default) stderr, and increase the
    'error' counter.  If an error subtype is specified,
    count(subtype) is called as well
    """
    print >> ERR_FILE, globals()['PROG']+':E', text
    count_all(('error',)+_normalizeKey(subtype))

def check_errors(text=None,
                 code=None):
    """
    ggf. zu fatal() durchgereichte Argumente:

    text -- als help-Argument durchgereicht, ein Hinweis
            auf die Hilfe (unterdrücken durch '')
    """
    if text is None:
        text = u"Aufruf mit -h oder --help für Hilfe"
    if counted_value('error'):
        fatal(code=code, tell=True, count=False, help=text)

def fatal(text=None,
          code=None,
          tell=True,
          count=None,
          help=None,
          subtype=None):
    """
    Gib einen Text aus und beende jedenfalls das Programm.
    Argumente:

    text -- der auszugebende Text

    Optional:

    code -- der Returncode; Default: die Anzahl ERRORS der bisher
            aufgetretenen Fehler, oder 1
    tell -- 1 bzw. true: Info über Anzahl bisheriger Fehler ausgeben
            2: auch Info über Anzahl bisheriger Warnungen ausgeben
            Wenn None übergeben wird, schlägt eine Automatik zu
    count -- boolean: den aktuellen Fehler mitzählen?
    subtype -- wenn angegeben (und nicht per count=False unterdrückt),
            wird gezählt

    help -- wenn übergeben, ein Hinweis auf die Hilfe
    """
    if count is None:
        count = bool(subtype)
    if count:
        if subtype is None:
            if code is not 0:
                subtype = 'fatal'
            else:
                count = 0
    if count:
        count(('errors',)+_normalizeKey(subtype or None))
    if tell is None: # Automatik
        tell = not text or not count

    if text is not None:
        print >> ERR_FILE, _PROGNAME+'!', text
    RC = code or counted_value('error') or RC_ERROR or 1
    if tell:
        all_counters('error')
        if tell > 1:
            all_counters('warning')
    if help:
        info(help)
    if tell:
        info('Beende mit RC %d' % RC, to=ERR_FILE)
    exit(RC)

def warning(text, subtype=None):
    """
    print {program name}: {text} to (by default) stderr, and increase the
    'warning' counter.  If an error subtype is specified,
    count(subtype) is called as well
    """
    print >> ERR_FILE, globals()['PROG']+':W', text
    count(('warning',))
    if subtype:
        count(('warning',)+_normalizeKey(subtype))
warning_simple = warning

def warning_recursive(text, subtype=None):
    """
    print {program name}: {text} to (by default) stderr, and increase the
    'warning' counter.  If an error subtype is specified,
    count(subtype) is called as well
    """
    print >> ERR_FILE, globals()['PROG']+':W', text
    count_all(('warning',)+_normalizeKey(subtype))

def info(text, subtype=None, count=None, to=None):
    if to is None:
        to = FILE
    if count is None:
        count = bool(subtype)
    if count:
        count(('info',)+_normalizeKey(subtype))
    print >> to, globals()['PROG']+':i', text

def digits(i):
    """
    return the number of decimal digits needed to print the given
    integer; for floats, return the number of digits before the
    decimal point

    >>> digits(123)
    3
    >>> digits(0)
    1
    """
    d = 1
    i //= 10
    while i:
        d += 1
        i //= 10
    return d

def _splitPluralSwitchableString(text):
    """
    split a string and return a 4-tuple:
    (prefix, singular, plural, suffix)

    examples:

    - 'file[s]' --> ('file', '', 's', '')

    - 'stor[y|ies] ' --> ('stor', 'y', 'ies', ' ')

    This is a helper function, used by --> freezeText(text, plural)
    """
    sf, pf = (0, 0)
    tup1 = text.split('[',1)
    if len(tup1) == 1:
        return (text, '', '', '')
    tup2 = tup1[1].split(']',1)
    if len(tup2) == 1:
        return (text, '', '', '')
    tup3 = tup2[0].split('|',1)
    if len(tup3) == 1:
        return (tup1[0], '', tup3[0], tup2[1])
    else:
        return (tup1[0], tup3[0], tup3[1], tup2[1])

def freezeText(text, plural):
    """
    return a 'frozen' version of the given text, resolving the
    '{[sing|]plu}' expressions, depending on the 2nd parameter, which
    must be 'true' for plural versions and 'false' for singular.
    Used by --> counted(key, text)

    Examples:

    >>> freezeText('file[s] or director[y|ies]', 0)
    'file or directory'
    >>> freezeText('file[s] or director[y|ies]', 1)
    'files or directories'
    """
    res, sing, plu, suffix = _splitPluralSwitchableString(text)
    if plural:
        res = res + plu
        while suffix:
            prefix, sing, plu, suffix = _splitPluralSwitchableString(suffix)
            res = ''.join((res, prefix, plu))
    else:
        res = res + sing
        while suffix:
            prefix, sing, plu, suffix = _splitPluralSwitchableString(suffix)
            res = ''.join((res, prefix, sing))
    return res

def _nextGreater9(i):
    """
    return the least number greater than the argument
    whose decimal representation consists of nines only

    >>> _nextGreater9(123)
    999
    """
    return 10 ** digits(i)-1

def reset(key, resetmax=0):
    """
    resets all counters for key and its 'subkeys'
    """
    if resetmax:
        uc = used_counters(key)
        mx = 9
        for k, v in COUNTER.items():
            if k in uc:
                del COUNTER[k]
            elif v > mx:
                mx = _nextGreater9(v)
        _MAXCOUNT = mx
        MASK = None
    else:
        for k in used_counters(key):
            del COUNTER[k]

def reset_all(resetmax=1):
    """
    resets all counters; by default, resets _MAXCOUNT as well
    """
    COUNTER.clear()
    if resetmax:
        _MAXCOUNT = 9
        MASK = None

def recursion(boo=None):
    """
    switch recursion mode on or off, or return an informational string
    """
    if boo is None:
        return 'recursion is switched %s' % _RECURSE and 'ON' or 'OFF'
    g = globals()
    if boo:
        g['count']=count_all
        g['error']=error_recursive
        g['warning']=warning_recursive
        g['_RECURSE']=True
    else:
        g['count']=count_simple
        g['error']=error_simple
        g['warning']=warning_simple
        g['_RECURSE']=False

if _RECURSE:
    recursion(True)

set_progname(progname())

if __name__ == '__main__':
    try:
        from thebops.optparse import OptionParser, OptionGroup
    except ImportError:
        from optparse import OptionParser, OptionGroup
        
    p = OptionParser(prog=progname(),
                     usage="from thebops.counters import count, error, "
                     'register_counters, all_counters',
                     add_help_option=0)
    p.set_description(_('A python module for all counting needs; '
                        'read the docstring for details'))
    g = OptionGroup(p, _('Demo options'))
    g.add_option('-r', '--recursive',
                 action='store_true',
                 help=_("every count('key:subkey') implies "
                 "count('error:key')"))
    g.add_option('--subtype-text',
                 metavar=_('STRING'),
                 action='store',
                 help=_('used for unregistered counter subtypes, '
                 'default: ", subtype: "'))
    p.add_option_group(g)
    VERSION = '%prog ' + VERSION
    try:
        from thebops.modinfo import main
        (o, args) = main(version=VERSION,
                         parser=p)
    except ImportError:
        g = OptionGroup(p, _('Everyday options'))
        g.add_option('--help', '-h', '-?',
                     action='help',
                     help=_('Display this help message and exit'))
        p.version = VERSION
        g.add_option('--version', '-V',
                     action='version',
                     help=_('Display the module version and exit'))
        p.add_option_group(g)
        (o, args) = p.parse_args()
    if o.recursive:
        recursion(True)
        
    if o.subtype_text:
        TEXT_SUBTYPE = o.subtype_text

    register_counters({'char:digit': 'decimal digit[s]',
                       'char': 'characters',
                       ('char','alpha'): 'letter[s]',
                       ('char','alpha', 'vowel'): 'vowel[s]',
                       ('char','misc'): '[|misc. ]other character[s]',
                       })
    for s in args:
        for ch in s:
            if ch.isalpha():
                if ch in 'aeiouAEIOU':
                    count('char:alpha:vowel')
                elif ch in 'yY':
                    count('char:alpha:misc')
                elif ch.islower():
                    count('char:alpha:consonant:lower')
                else:
                    count('char:alpha:consonant:upper')
            elif ch.isdigit():
                count('char:digit:%s' % ch)
            else:
                count(('char', 'misc', ch))
    all_counters()

