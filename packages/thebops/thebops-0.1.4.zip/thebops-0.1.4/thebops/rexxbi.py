#!/usr/bin/env python
# -*- coding: latin1 -*- vim: ts=8 sts=4 sw=4 si et tw=79
"""\
rexxbi - selected functions like those built-in in the REXX language

These functions are *not fully* compatible to the original Rexx ones,
since Rexx doesn't distinguish between numbers and strings which *look like*
numbers.  The logic should be the same, however; for full compability, you may
use wrapper functions which perform the necessary argument conversions.
Besides, Rexx ignores case when it comes to variables and (almost all) function
names, which Python does not ...

Thus, don't expect this to suffice to build a Rexx interpreter;
however, some Rexx functions might be of some use:

>>> translate('ij.fg.abcd', '2012-12-31', 'abcdefghij')
'31.12.2012'

(look for the doctests, and try the commandline demo rexxbi_demo.py)
"""
# examples: <http://www.kyla.co.uk/other/rexx2.htm>,
#   <http://www.scoug.com/OPENHOUSE/REXXINTRO/RXBISTTR1.4.HTML>,
#   <http://www.kilowattsoftware.com/tutorial/rexx/bitranslate.htm>
# TODO: wordlength

__author__ = "Tobias Herp <tobias.herp@gmx.net>"
VERSION = (0,
           4,	# integrated demo moved to -> rexxbi_demo.py
           2,	# overlay
           1,	# docstrings, incl. doctests (regression tests)
           'rev-%s' % '$Rev: 938 $'[6:-2],
           )
__version__ = '.'.join(map(str, VERSION))
__all__ = [# general-use utilities:
           'left',
           'right',
           'center', 'centre',
           'overlay',
           'substr', 'delstr',
           'translate',
           'compare',
           'verify',
           # word functions:
           'word', 'words', 'wordpos',
           'subword', 'delword',
           'wordindex',
           # no part of Rexx, but needed e.g. for demo:
           'even', 'odd',
           # exceptions:
           'RexxError',
           'RexxArgumentError',
           ]

DEBUG = 0
class RexxError(Exception):
    def __str__(self):
        return self.msg

class RexxArgumentError(RexxError):
    def __init__(self, arg, fname):
        self.arg = arg
        self.fname = fname
        self.msg = ('invalid argument %(arg)r'
                    'to function %(fname)r'
                    ) % locals()

def right(s, width, fillchar=' '):
    """
    like the Rexx built-in function RIGHT:
    return the last <width> characters of the given string,
    filled up with <fillchar>

    >>> right('foo', 5)
    '  foo'
    >>> right('foo', 5, '*')
    '**foo'
    >>> right('foo', 2)
    'oo'
    """
    assert width >= 0
    if width == 0:
        return ''
    length = len(s)
    if length > width:
        return s[-width:]
    else:
        return s.rjust(width, fillchar)

def left(s, width, fillchar=' '):
    """
    like the Rexx built-in function LEFT:
    return the first <width> characters of the given string,
    filled up with <fillchar>

    >>> left('foo', 5)
    'foo  '
    >>> left('foo', 5, '*')
    'foo**'
    >>> left('foo', 1)
    'f'
    """
    assert width >= 0
    length = len(s)
    if length > width:
        return s[:width]
    else:
        return s.ljust(width, fillchar)

def center(s, width, fillchar=' '):
    """
    like the Rexx built-in function CENTER (or CENTRE):
    return the middle <width> characters of the given string,
    filled up with <fillchar>.

    NOTE that for odd widths greater than the odd length of the
    given string, Rexx doesn't behave like Python's center method!

    >>> center('ham', 5, '-')
    '-ham-'
    >>> center('ham', 6, ' ')
    ' ham  '
    >>> center('abcde', 2)
    'bc'
    >>> centre('spam', 7)
    ' spam  '
    """
    assert width >= 0
    assert len(fillchar) == 1
    length = len(s)
    if length > width:
        head, rest = divmod(length-width, 2)
        return s[head:-(head+rest)]
    elif odd(width) and even(length):
        return s.center(width-1, fillchar) + fillchar
    else:
        return s.center(width, fillchar)
centre = center

def substr(s, start, width=None, fillchar=' '):
    """
    like the Rexx built-in function SUBSTR:

    >>> substr('abcde', 3)
    'cde'
    >>> substr('abcde', 3, 5)
    'cde  '
    >>> substr('abcde', 3, 5, '*')
    'cde**'
    >>> substr('abcde', 3, 0)
    ''
    """
    assert start >= 1
    if width is None:
        return s[start-1:]
    elif width == 0:
        return ''
    assert width > 0
    return left(s[start-1:], width, fillchar)

def delstr(s, start, width=None):
    """
    like the Rexx built-in function DELSTR:

    >>> delstr('abcde', 3)
    'ab'
    >>> delstr('abcde', 3, 1)
    'abde'
    >>> delstr('abcde', 3, 0)
    'abcde'
    """
    assert start >= 1
    start -= 1
    if width is None:
        return s[:start]
    elif width == 0:
        return s
    tmp = list(s)
    del tmp[start:start+width]
    return ''.join(tmp)

def _fillingzip(s1, s2, fillchar):
    """
    assymmetrical zip function; if the 1st sequence is shorter than the 2nd, it
    is filled up with the fillchar.

    >>> list(_fillingzip('abc', 'ABCDE', '*'))
    [('a', 'A'), ('b', 'B'), ('c', 'C'), ('*', 'D'), ('*', 'E')]
    >>> list(_fillingzip('abcde', 'ABC', '*'))
    [('a', 'A'), ('b', 'B'), ('c', 'C')]
    """
    for tup in zip(s1, s2):
        yield tup
    if len(s1) < len(s2):
        for ch in s2[len(s1):]:
            yield (fillchar, ch)

def translate(s, new=None, old=None, fillchar=None):
    """
    s -- a string (required)

    new -- a string (or sequence of characters)

    old -- like new

    fillchar -- used if old is longer than new

    This function serves two purposes:

    1) if only a string is given, returns s.upper()

    2) the more interesting form allows to "reorder" strings:
       each character in s, if contained in old, is replaced by the respective
       character in new.

    >>> translate('abc')
    'ABC'
    >>> translate('abcdef', '1', 'abcd')
    '1   ef'
    >>> translate('ij.fg.abcd', '2012-12-31', 'abcdefghij')
    '31.12.2012'
    """
    if (new, old, fillchar) == (None, None, None):
        return s.upper()
    if fillchar is None:
        fillarg = ''
        fillchar = ' '
    else:
        assert len(fillchar) == 1
    themap = {}
    if old is None:
        for ch in s:
            themap[ch] = fillchar
    else:
        for (val, key) in _fillingzip(new or '', old or '', fillchar):
            themap[key] = val
    res = []
    for ch in s:
        try:
            res.append(themap[ch])
        except KeyError:
            res.append(ch)
    return ''.join(res)

def match_arg(s):
    """
    interpret Rexx-conforming 3rd arguments to verify
    and return 0 or 1

    ObjectRexx interprets 'mismatch' like 'match', which
    is counter-intuitive; thus, this value is disallowed!

    >>> match_arg('match')
    1
    >>> match_arg('M')
    1
    >>> match_arg('n')
    0
    >>> match_arg('nOma')
    0
    >>> match_arg('nnnn')
    0
    """
    assert isinstance(s, str)
    assert s, 'empty strings are not allowed'
    la = s.lower()
    longstrings = ('nomatch', 'match')
    for i in range(2):
        if longstrings[i].startswith(la):
            return i
    # sic! Getestet mit ooRexx_4.0.1(MT):
    for i in range(2):
        if la.startswith(longstrings[i][0]):
            return i
    raise RexxArgumentError(s, 'verify')

def verify(s, ref, mode=0):
    """
    return the 1-based position in s which is *not* present in ref (nomatch
    mode, default), or which *is* present in s (match mode)

    s -- the inspected string

    ref -- the reference set of characters; in Rexx also given as a string

    mode -- 'nomatch' or 0 (default), or 'match' or 1; case is ignored

    Currently, there the following calling syntax differences to the Rexx
    version:
    - Rexx supports (case-insensitive) abbreviations of 'match' and 'nomatch'
      as well; this is not implemented (yet?)
    - instead, this function allows to use selected boolean values,
      where False means 'NOMATCH'

    >>> verify('abc', 'a')
    2
    >>> verify('abc', 'a', 'nomatch')
    2
    >>> verify('abc', 'a', 0)
    2
    >>> verify('abc', 'a', 'match')
    1
    >>> verify('abc', 'c', 1)
    3
    >>> verify('follow the white rabbit', 'abcdefhilortwxyz')
    7
    """
    if mode not in (0, 1, False, True):
        mode = match_arg(mode)
    nr = 1
    refset = set(ref)
    if mode:
        for ch in s:
            if ch in refset:
                return nr
            nr += 1
    else:
        for ch in s:
            if ch not in refset:
                return nr
            nr += 1
    return 0

def compare(s1, s2, pad=None):
    """
    >>> compare('abc', 'abc ')
    4
    >>> compare('abc', 'abc ', ' ')
    0
    >>> compare('abc', 'xyz')
    1
    >>> compare('abc', 'abc  e', ' ')
    6
    """
    pos = 1
    for (a, b) in zip(s1, s2):
        if a != b:
            return pos
        pos += 1
    if len(s1) == len(s2):
        return 0
    if pad is None:
        return pos
    for ch in s1[pos-1:] or s2[pos-1:]:
        if ch != pad:
            return pos
        pos += 1
    return 0

def copies(s, count):
    """
    >>> copies('abc', 0)
    ''
    >>> copies('ga', 2)
    'gaga'
    """
    assert isinstance(s, basestring)
    assert count >= 0
    return s * count

def overlay(s, target, start=1, count=None, fillchar=' '):
    """
    >>> overlay('a', 'bbb', 1)
    'abb'
    >>> overlay('a', 'bbb', 5)
    'bbb a'
    >>> overlay('a', 'bbb', 5, 2)
    'bbb a '
    >>> overlay('a', 'bbb', 2, 5)
    'ba    '
    >>> overlay('a', 'bbb', 5, 2, '-')
    'bbb-a-'
    >>> overlay('a', 'bbb', 2, 5, '-')
    'ba----'
    >>> overlay('', 'bbb', 5, None, '-')
    'bbb-'
    >>> overlay('', 'bbb', 5, 0, '-')
    'bbb-'
    """
    if count is None:
        count = len(s)
    else:
        assert count >= 0
        if count != len(s):
            s = left(s, count, fillchar)
    if len(target) < start + count - 1:
        target = left(target, start + count - 1, fillchar)
    liz = list(target)
    si = start - 1
    for ch in s:
        liz[si] = ch
        si += 1
    return ''.join(liz)


def odd(n):
    """
    >>> odd(2)
    False
    >>> odd(1)
    True
    """
    assert isinstance(n, int)
    return bool(n % 2)

def even(n):
    """
    >>> even(2)
    True
    >>> even(1)
    False
    """
    return not odd(n)

def word(s, pos):
    """
    >>> word('  ', 1)
    ''
    >>> word('   eins zwei  ', 2)
    'zwei'
    >>> word('eins.zwei', 2)
    ''
    >>> word('eins\tzwei', 2)
    'zwei'
    """
    assert pos > 0
    try:
        return s.split()[pos-1]
    except IndexError:
        return ''

def words(s):
    """
    Return the number of whitespace-divided words

    >>> words('  ')
    0
    >>> words('   eins zwei  ')
    2
    >>> words('eins.zwei')
    1
    >>> words('eins\tzwei')
    2
    """
    return len(s.split())

def wordpos(w, s):
    """
    Return the number of the given word in the given string

    >>> wordpos('zwei', '  ')
    0
    >>> wordpos('zwei', '   eins zwei  ')
    2
    >>> wordpos('zwei', 'eins.zwei')
    0
    >>> wordpos('zwei', 'eins\tzwei')
    2
    >>> wordpos('  follow  ', '  follow the white rabbit')
    1
    """
    try:
        return s.split().index(w.strip()) + 1
    except ValueError:
        return 0

import string

def wordindex(s, nr):
    """
    Return the 1-based position of the 1st character of the nth word

    >>> wordindex('  ', 1)
    0
    >>> wordindex('   eins zwei  ', 1)
    4
    >>> wordindex('eins\tzwei', 2)
    6
    """
    pos = 0
    sofar = 0
    inword = 0
    for ch in s:
        pos += 1
        if ch in string.whitespace:
            if inword:
                inword = 0
        else:
            if not inword:
                sofar += 1
                if sofar == nr:
                    return pos
                inword = 1
    return 0

def _wordborders(s):
    """
    helper for subword and delword;
    the number of yielded indexes is always even

    >>> list(_wordborders('single'))
    [0, 6]
    >>> list(_wordborders(' two words '))
    [1, 4, 5, 10]
    >>> list(_wordborders('eins\tzwei'))
    [0, 4, 5, 9]
    """
    if not s:
        return
    idx = 0
    def isblanc(ch):
        return ch in string.whitespace
    def noblanc(ch):
        return ch not in string.whitespace
    funcs = (noblanc, isblanc)
    funcidx = 0 # 1st search for non-blanks
    prev = 0
    for ch in s:
        this = funcs[funcidx](ch)
        if this != prev:
            funcidx = not funcidx
            yield idx
        idx += 1
    if funcidx:
        yield idx
    yield idx
    yield idx

def subword(s, first, count=None):
    r"""
    Return max. count (or all remaining) subwords of the given string,
    beginning with word #<first>.

    The returned string ends with the end of the last contained
    word, with trailing whitespace stripped.

    >>> subword('follow the white rabbit', 1)
    'follow the white rabbit'
    >>> subword('follow the white rabbit', 1, 1)
    'follow'
    >>> subword('  follow the white rabbit  ', 3, 2)
    'white rabbit'
    >>> subword('  follow the white  rabbit', 3, 2)
    'white  rabbit'
    >>> subword('  ', 1)
    ''
    >>> subword('   eins   zwei  drei  ', 1, 2)
    'eins   zwei'
    >>> subword('   eins   zwei  drei  ', 1)
    'eins   zwei  drei'
    >>> subword('eins\tzwei', 1, 2)
    'eins\tzwei'
    >>> subword('eins\tzwei', 2)
    'zwei'
    >>> subword('eins\tzwei', 2, 1)
    'zwei'
    >>> subword('eins\tzwei', 3, 1)
    ''
    >>> subword('follow the white rabbit', 2, 1)
    'the'
    """
    assert isinstance(first, int)
    assert first >= 1
    sidx = (first - 1) * 2
    if count is not None:
        assert isinstance(count, int)
        if count == 0:
            return ''
        assert count > 0
        eidx = (first + count - 2) * 2 + 1
    else:
        eidx = None
    ii = 0
    indexes = _wordborders(s)
    for spos in indexes:
        if ii == sidx:
            if count is None:
                return s.rstrip()[spos:]
            else:
                ii += 1
                break
        ii += 1
    # too few words: 
    if ii == 0:
        return ''
    for epos in indexes:
        if ii == eidx:
            return s[spos:epos]
        elawo = epos
        ii += 1
    return s.rstrip()[spos:]

def pvars(ns, *args):
    """
    ns -- namespace (e.g. 'locals()')
    args -- variable names (from ns)
    """
    if not DEBUG:
        return
    assert isinstance(ns, dict)
    liz = ['%s=%%(%s)r' % (item, item)
           for item in args]
    print ('; '.join(liz)) % ns

def p(s):
    if DEBUG: print(s)

def delword(s, first, count=None):
    """
    Return the given string with max. <count> words removed
    (or all remaining), beginning with subword #<first>;

    trailing whitespace is removed if the last word is removed;
    the space before the first deleted word is preserved.

    >>> delword('follow the white rabbit', 1)
    ''
    >>> delword('  follow   the white rabbit ', 2, 2)
    '  follow    rabbit '
    >>> delword('  follow   the white rabbit ', 2, 10)
    '  follow     '
    >>> delword('follow the white rabbit', 1, 4)
    ''
    >>> delword('follow the white rabbit', 1, 5)
    ''
    >>> delword('follow the white rabbit', 2)
    'follow '
    >>> delword('follow the white rabbit', 2, 3)
    'follow '
    >>> delword('follow the white rabbit', 2, 5)
    'follow '
    >>> delword('follow the white rabbit', 3)
    'follow the '
    >>> delword('follow the white rabbit', 3, 2)
    'follow the '
    >>> delword('follow the white rabbit', 3, 5)
    'follow the '
    >>> delword('follow the white rabbit', 4)
    'follow the white '
    >>> delword('follow the white rabbit', 4, 1)
    'follow the white '
    >>> delword('follow the white rabbit', 4, 5)
    'follow the white '
    >>> delword('follow the white rabbit', 5)
    'follow the white rabbit'
    >>> delword('follow the white rabbit', 5, 1)
    'follow the white rabbit'
    >>> delword('follow the white rabbit', 5, 5)
    'follow the white rabbit'
    """
    assert isinstance(first, int)
    assert first >= 1
    sidx = (first - 1) * 2
    if count is not None:
        assert isinstance(count, int)
        if count == 0:
            return s
        assert count > 0
        eidx = (first + count - 1) * 2
    else:
        eidx = None
    p('delword(%r, %d, %s)' % (s, first, count))
    pvars(locals(), 'sidx', 'eidx')
    ii = 0
    indexes = _wordborders(s)
    for spos in indexes:
        pvars(locals(), 'spos', 'ii')
        if ii == sidx:
            if count is None:
                return s[:spos]
            else:
                ii += 1
                break
        ii += 1
    # too few words: 
    if ii == 0:
        return s
    pvars(locals(), 'ii', 'spos')
    p('s[spos:]=%r' % s[spos:])
    for epos in indexes:
        pvars(locals(), 'ii', 'epos')
        if ii == eidx:
            if list(indexes):
                return ''.join((s[:spos], s[epos:]))
            else:
                return ''.join((s[:spos], s[epos:].rstrip()))
        elawo = epos
        ii += 1
        # too few words: 
    return s[:spos]
    return s.rstrip()[spos:]

if __name__ == '__main__':
    from thebops.modinfo import main as modinfo
    modinfo(version=__version__)
