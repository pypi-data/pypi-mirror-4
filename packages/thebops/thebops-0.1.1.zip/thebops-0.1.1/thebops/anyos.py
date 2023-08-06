# -*- coding: latin1 -*- a Python module - vim: ts=8 sts=4 sw=4 si et
r"""
anyos -- provide some os functionality for any operating system
~~~~~--------------------------------------~~~-~---------~-----

1) link creation
----------------
For Windows(tm) systems, the os module lacks some very useful functions:

link -- create a hard link
symlink -- create a symbolic link

It is *possible*, however, to do such things on Windows systems
(on WinNT-based systems with NTFS drives, at least).
This module imports the original function, if possible, and otherwise
provides a workaround;  to do this, it looks for suitable executables,
using the find_progs function (which is wrapped for convenience in the likeix
module).

Furthermore, the os.symlink does't support a force argument
(like ln -s -f) to overwrite existing symlinks; thus, a symlink_forced
function is provided which fills this gap.

2) find_progs
-------------
A lot of useful commandline tools known from Linux are available for Windows
too; however, they are somewhat hard to find:

- you need to get them yourself
- there is no standard directory for such stuff
- the 'which' program doesn't find Windows executables if given w/o extension
- sometimes their location is not added to the PATH during installation
  (true even for the Python interpreter!)
- there might be different versions to choose from
- you might prefer to avoid wrapper batch files which are written suboptimally
  by other people and rather use the wrapped program directly

And *no*, you don't want to scan your entire hard disk.

The find_progs function allows you to ferret out all occurrences
on the system, using a smart strategy:
0. (for configuration files; typically not used for executables)
   searches a directory and all of its *parents* (not: children!)
1. searches a specified set of directories.
   Some tools install on Win* in some directory somewhere below
   %ProgramFiles% which are not available in the PATH.
   find_progs optionally takes a sequence of directory specs which
   may contain environment variable names in Python's dict comprehension
   syntax; if the variable is unknown, the entry is ignored.
   (Of course, this is way faster than searching an entire harddisk.)
   If is even possible to specify versioned directories (e.g. C:\...\vim73)
   and automatically get the highest version.
2. Searches the PATH.
   When doing this, some directories can be excluded (the xroots argument)
   which very likely contain programs which don't behave like the desired
   POSIX tool at all, e.g. %(SystemRoot)%.

The likeix module contains some wrappers to this function, collecting
knowledge about how to find certain programs.

The find_progs function is intended to allow for portable programs; the seeked
tools should *of course* be found on Linux systems as well, where they are
located in a small set of directories (/bin, /usr/bin and the like).
The PATH search (active by default) should take care of that;
it has not been thoroughly tested yet, though.

Prerequisites
-------------
Python 2.4 is needed because of the subprocess module;
for Python 2.4, the missing parts are amended.

$Id: anyos.py 906 2013-03-30 16:00:17Z Tobias $
"""

__author__ = "Tobias Herp <tobias.herp@gmx.net>"
VERSION = (0,
           4, # Bugfix f�r Linux (keine PATHEXT-Variable)
              # (scanpath-Baustelle noch ge�ffnet?)
           1, # isunix is used by fancyhash
           'rev-%s' % '$Rev: 906 $'[6:-2],
           )
__version__ = '.'.join((map(str, VERSION)))

from subprocess import Popen, PIPE, call
try:
    from subprocess import CalledProcessError
except ImportError:
    class CalledProcessError(Exception):
        """
        taken from Python 2.7 version.
        This exception is raised when a process run by check_call() or
        check_output() returns a non-zero exit status.
        The exit status will be stored in the returncode attribute;
        check_output() will also store the output in the output attribute.
        """
        def __init__(self, returncode, cmd, output=None):
            self.returncode = returncode
            self.cmd = cmd
            self.output = output
        def __str__(self):
            return "Command '%s' returned non-zero exit status %d" \
                    % (self.cmd, self.returncode)


try:
    from subprocess import check_call
except ImportError:
    def check_call(*popenargs, **kwargs):
        """
        taken from Python 2.7 version; see
        <http://docs.python.org/library/subprocess.html#subprocess.check_call>
        """
        retcode = call(*popenargs, **kwargs)
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise CalledProcessError(retcode, cmd)
        return 0

# _hier_ wird importiert:
from os.path import isfile, isdir, \
        sep, join, split, dirname, splitext, \
        normcase, normpath, abspath, \
        pathsep
from os import utime, stat, environ
from time import time
from sys import platform
from string import digits, punctuation
from glob import glob

__all__ = ['link', 'symlink',
           'symlink_forced',
           'touch',
           'quoted_seq',
           # see the likeix module for wrappers and a demo:
           'find_progs',
           # parse version info from directory names:
           'vsplit_digits', 'vdir_digits',
           'vsplit_delim',  'vdir_delim',
           'isunix',  # see usage comments
           'gen_expanded_strings',
           'gen_parents',
           'np',
           # 'escape_char',
           # data:
           'SHELL_ESCAPE',
           # exception classes:
           'Error',
           'ForceNeeded',
           'CommandFailed',
           'ProgramNotFound',
           'VersionConstrained',
           'VersionsUnknown',
           # callable classes:
           'Command',
           'Link',
           'Symlink',
           'Symlink_forced',
           # 'ask' removed from __all__ (use shtools version!)
           ]

DEBUG = 0

class Error(Exception):
    """
    Base class for anyos Exeptions
    """
class ForceNeeded(Error):
    """
    the requested command would have needed to be 'force'd
    """
    def __init__(self, cmd, returncode=None, force_option=None):
        self.cmd = cmd
        self.returncode = returncode
        self.force_option = force_option
    def __str__(self):
        cmd = quoted_arg(self.cmd)
        info = []
        if self.force_option:
            info.append(self.force_option)
        if self.returncode is not None:
            info.append(_('returncode: %s') % self.returncode)
        if info:
            info = _(' (%s)') % _('; ').join(info)
        else:
            info = ''
        return _('command %(cmd)s would have needed '
                 'to be forced%(info)s'
                 ) % locals()

class CommandFailed(CalledProcessError, Error, OSError):
    """
    the requested command failed; this class works around the problem
    that subprocess.CalledProcessError doesn't inherit OSError
    """
    # methods _almost_ like inherited from CalledProcessError:
    def __init__(self, cmd, returncode, output=None):
        self.cmd = cmd
        self.returncode = returncode
        self.output = output
    def __str__(self):
        return "Command %s returned non-zero exit status %d" \
                % (quoted_arg(self.cmd), self.returncode)

class ProgramNotFound(Error):
    """
    The given program was not found
    """
    def __init__(self, cmd):
        self.returncode = None
        self.cmd = cmd
        self.output = None
        self.msg = ("Program %s not found"
                    ) % quoted_arg(self.cmd)
    def __str__(self):
        return self.msg

class VersionConstrained(ProgramNotFound):
    """
    The program was found, but the version constraints were not met
    """
    def __init__(self, prog):
        self.prog = prog
        self.msg = ('The program %r was found, but the version constraints'
                    ' were not met' % prog)

class VersionsUnknown(VersionConstrained):
    """
    The program was found, but the version could not be determined
    """
    def __init__(self, prog):
        self.prog = prog
        self.msg = ('The program %r was found, but the version is unknown'
                    % prog)

class Command(object):
    # the worker method:
    _worker = None
    def __init__(self):
        pass
    @classmethod
    def __call__(cls, *args, **kwargs):
        if cls._worker is None:
            # print cls.__name__+': get_worker()'
            cls.get_worker()
        return cls._worker(*args, **kwargs)

class Link(Command):
    @classmethod
    def options(cls):
        return []
    @classmethod
    def doit(cls, source, link_name):
        try:
            cmd = [cls._program, source, link_name]
            i = 1
            for o in cls.options():
                cmd.insert(i, o)
                i += 1
            if DEBUG:
                print cmd
            check_call(cmd)
        except CalledProcessError, e:
            raise CommandFailed(e.returncode, e.cmd, e.output)
    @classmethod
    def get_worker(cls):
        from thebops.likeix import get_1st
        cls._program = get_1st('ln')
        cls._worker = cls.doit

class Symlink(Link):
    @classmethod
    def options(cls):
        return Link.options() + ['-s']

class Symlink_forced(Symlink):
    @classmethod
    def options(cls):
        return Symlink.options() + ['-f']

SHELL_ESCAPE = None
def escape_char(reset=0):
    """
    gib das Escape-Zeichen zurueck, das dem folgenden Zeichen seine
    Sonderbedeutung fuer die Shell nimmt
    """
    # sollte stimmen f�r:
    # - Windows, OS/2...
    # - Linux
    # Noch ungekl�rt:
    # - MacOS
    # - CygWin
    # - ...
    def compute_anew():
        if sep == '\\':
            return '^'
        else:
            return '\\'
    global SHELL_ESCAPE
    if SHELL_ESCAPE is None or reset:
        SHELL_ESCAPE = compute_anew()
    return SHELL_ESCAPE

def isunix():
    # - wildcards usually expanded from shell
    return platform in ('linux',
                        'linux2',
                        'cygwin',
                        )

SHELL_ESCAPE = escape_char()
SHELL_WILDCARDS = set('*?')
SHELL_SINGLETONS = set('(!;)')

if isunix():
    SHELL_QUOTES = list('\'"')
    SHELL_SPECIAL = set(" \t$()[]{}^=;!',`~")    # TODO: pr�fen
    SHELL_ESCAPE_UNQUOTED = SHELL_SPECIAL.union(SHELL_QUOTES)
    def quote_this(ch, qu=None):
        if ch == SHELL_ESCAPE:
            return 1
        elif qu is None:
            if ch in SHELL_ESCAPE_UNQUOTED:
                return 1
        elif ch == qu:
            return 1
        elif qu == "'":
            return ch == '$'
        return 0

else:   # windows
    SHELL_QUOTES = list('"')
    # Windows 7, cmd /?:
    SHELL_SPECIAL = set(" \t()[]{}^=;!'+,`~")    # TODO: pr�fen
    SHELL_ESCAPE_UNQUOTED = SHELL_SPECIAL.union(SHELL_QUOTES)
    def quote_this(ch, qu=None):
        if ch == SHELL_ESCAPE:
            return 1
        elif qu is None:
            if ch in SHELL_ESCAPE_UNQUOTED:
                return 1
        elif ch == qu:
            return 1
        return 0

def quoted_seq(seq):
    """
    nimm eine zur direkten Ausfuehrung (ohne Shell) geeignete Sequenz
    und gib eine Version zurueck, die als ein Befehlsstring einer
    Shell uebergeben werden koennte
    """
    assert not isinstance(seq, (str, unicode))
    for elem in seq:
        if elem in SHELL_SINGLETONS:
            yield SHELL_ESCAPE + elem
            continue
        eset = set(elem)
        if eset.intersection(SHELL_WILDCARDS):
            yield quoted_arg(elem)
        elif eset.intersection(SHELL_SPECIAL):
            yield quoted_arg(elem)
        else:
            yield elem

def quoted_arg(s):
    u"""
    nimm einen String entgegen und versieh ihn mit Anf�hrungszeichen
    """
    for qu in SHELL_QUOTES:
        if not qu in s:
            return qu + s + qu
    res = []
    qu = SHELL_QUOTES[0]
    res.append(qu)
    for ch in s:
        if quote_this(ch, qu):
            res.append(SHELL_ESCAPE)
        res.append(ch)
    res.append(qu)
    return ''.join(res)


def find_progs(progname,
               parentsof=None,
               indirs=None,
               scanpath=None,
               xroots=None,
               pathvar='PATH',
               vdirs=None,
               vfunc=None,
               inroots=None):
    ur"""
    Finde ein geeignetes Programm, das m�glicherweise im PATH steht -
    vielleicht aber auch nicht! ;-)

    progname -- Name des zu suchenden Programms, z.B. 'find'.  Die Angabe
                soll keine Verzeichniskomponente enthalten; was dann passiert,
                w�re undefiniert

    Alle weiteren Argumente bitte *immer* benannt �bergeben, da sich die
    Reihenfolge �ndern k�nnte:

    parentsof -- ein Verzeichnis, dessen �bergeordnete Verzeichnisse ebenfalls
                 durchsucht werden.
                 F�r lokale Konfigurationsdateien, die Defaults in
                 allgemeineren Verzeichnissen �bersteuern; daher als erstes
                 ausgewertet

    indirs -- Sequenz von zu durchsuchenden Verzeichnissen; Umgebungsvariablen
              d�rfen in Python-Syntax angegeben werden ('%(name)s')

    vdirs -- versionierte Verzeichnisse, wie z.B. von Vim-Installationen

    vfunc -- Funktion, die aus den vdirs-Verzeichnisnamen die jeweilige
             Version extrahiert und als Tupel zur�ckgibt; Verzeichnisse, f�r
             die diese Funktion None zur�ckgibt, werden ignoriert

    scanpath -- Soll der PATH durchsucht werden?
                Default: wenn pathvar (default: PATH) leer ist, nein;
                wenn xroots angegeben, ja;
                wenn weder indirs noch inroots angegeben, ja

    xroots -- Auszuschlie�ende Wurzelverzeichnisse, z.B. r'c:\Windows'
              (weil sich darunter Programme finden, die nicht passen,
              weil z.B. das 'find.exe' von Windows etwas v�llig anderes
              tut)

    pathvar -- �blicherweise PATH (default)

    inroots -- Sequenz von Wurzelverzeichnissen, deren Unterverzeichnisse
               durchsucht werden (noch nicht implementiert)

    Die ...dirs- und ...roots-Argumente sind Sequenzen von Strings, die
    die Namen von Umgebungsvariablen enthalten d�rfen, z.B. '%(windir)s'
    anstelle von r'c:\Windows'

    """
    indirs = indirs and list(gen_expanded_strings(indirs, environ)) or []
    inroots = inroots and list(gen_expanded_strings(inroots, environ)) or []
    xroots = xroots and list(gen_expanded_strings(xroots, environ)) or []
    vdirs = vdirs and list(gen_expanded_strings(vdirs, environ)) or []

    progname, extensions = splitext(progname)
    if not extensions:
        try:
            extensions = map(normcase, environ['PATHEXT'].split(pathsep))
        except KeyError:
            pass
        if not extensions:
            extensions = ['']
    else:
        extensions = [extensions or '']
    # parents of (f�r lokale Konfigurationsdateien):
    if parentsof:
        for d in gen_parents(parentsof):
            for e in extensions:
                fn = join(d, progname+e)
                if isfile(fn):
                    yield fn

    # direkt angegebene Verzeichnisse:
    for d in indirs:
        if not isdir(d):
            continue
        d = normpath(d)
        for e in extensions:
            fn = join(d, progname+e)
            if isfile(fn):
                yield fn

    # Versionsverzeichnisse
    if vdirs:
        if vfunc is None:
            vfunc = vsplit_digits
        found = []
        for vdir in vdirs:
            for d in glob(vdir):
                ver = vfunc(d)
                if ver is not None:
                    for e in extensions:
                        fn = join(d, progname+e)
                        if isfile(fn):
                            found.append((ver, fn))
        if found:
            found.sort()
            found.reverse() # h�here Versionen zuerst
            for tup in found:
                yield tup[1]

    oricase = {}
    # PATH:
    if scanpath is None:    # default
        if not pathvar:
            scanpath = 0
        elif xroots:
            scanpath = 1
        elif not (indirs or inroots):   # keine andere positive Angabe
            scanpath = 1
    if scanpath:
        path_tups = [tup
                     for tup in _gen_absdir_tuples(
                         environ[pathvar].split(pathsep),
                         oricase)]
        if not path_tups:
            scanpath = 0
    if scanpath:
        if xroots:
            xroots_dic = {}
            list(_gen_absdir_tuples(xroots, xroots_dic))
            for t in path_tups:
                if stored_below_any_dirtup(t, xroots_dic):
                    continue
                for e in extensions:
                    t2 = t + (progname+e,)
                    fn = _rejoin(t2)
                    if isfile(fn):
                        yield fn
        else:
            for t in path_tups:
                for e in extensions:
                    t2 = t + (progname+e,)
                    fn = _rejoin(t2)
                    if isfile(fn):
                        yield fn

def vsplit_digits(s):
    ur"""
    Analysiere einen Verzeichnisnamen, der eine Informationsinformation
    enth�lt (z.B. C:\Program Files\Vim\vim73), und gib diese als Tupel zur�ck.
    Wandle jede Dezimalziffer f�r sich in eine Zahl, und brich beim ersten
    Zeichen ab, das keine Ziffer ist.

    >>> vsplit_digits(r'C:\Program Files\Vim\vim73')
    (7, 3)
    >>> vsplit_digits(r'C:\Program Files\foo\bar7.3baz/')
    (7,)
    """
    s = split(normpath(s))[1]
    pos = None
    NUMCHARS = set(digits)
    for offset in range(len(s)):
        if s[offset] in NUMCHARS:
            pos = offset
            break
    if pos is None:
        return None
    trenner = None
    for pos in range(offset+1, len(s)):
        if s[pos] in NUMCHARS:
            continue
        break
    if s[pos] in NUMCHARS:
        pos += 1
    return tuple(map(int, list(s[offset:pos])))

def vdir_digits(s):
    ur"""
    Wende vsplit_digits an auf den Verzeichnisnamen der �bergebenen Datei

    >>> vdir_digits(r'C:\Program Files\Vim\vim73\vim.exe')
    (7, 3)
    """
    return vsplit_digits(dirname(s))

def vsplit_delim(s):
    ur"""
    Analysiere einen Verzeichnisnamen, der eine Informationsinformation
    enth�lt (z.B. C:\Program Files\Vim\vim73), und gib diese als Tupel zur�ck.
    Verwende das erste Zeichen aus string.punctuation als Trenner, das auf
    Ziffern folgt; '73' ergibt also eine h�here Version als '7.3'

    >>> vsplit_delim(r'C:\Program Files\Vim\vim73')
    (73,)
    >>> vsplit_delim(r'C:\Program Files\foo\bar7.3baz/')
    (7, 3)
    """
    s = split(normpath(s))[1]
    pos = None
    NUMCHARS = set(digits)
    for offset in range(len(s)):
        if s[offset] in NUMCHARS:
            pos = offset
            break
    if pos is None:
        return None
    trenner = None
    for pos in range(offset+1, len(s)):
        if s[pos] in NUMCHARS:
            continue
        elif trenner is None:
            if s[pos] in punctuation:
                trenner = s[pos]
                NUMCHARS.add(trenner)
                continue
        break
    if s[pos] in NUMCHARS:
        pos += 1
    if trenner is not None:
        return tuple(map(int, [i
                               for i in s[offset:pos].split(trenner)
                               if i
                               ]))
    else:
        return (int(s[offset:pos]),)

def vdir_delim(s):
    ur"""
    Wende vsplit_delim an auf den Verzeichnisnamen der �bergebenen Datei

    >>> vdir_delim(r'C:\Program Files\Vim\vim73\vim.exe')
    (73,)
    """
    return vsplit_delim(dirname(s))

def gen_expanded_strings(seq, dic):
    """
    for each string of the given sequence, generate a dict-introspected
    version

    seq -- the sequence of strings

    dic -- a dictionary, e.g. os.environ

    """
    for s in seq:
        try:
            yield s % dic
        except KeyError:
            pass

def gen_parents(d):
    """
    generates the given directory (expanded to abspath) and all of its parents
    """
    d = abspath(d)  # implies normpath
    stop = 0
    while d:
        if isdir(d):
            yield d
        if stop:
            return
        d = dirname(d)
        if d[-1] == sep:    # NOTE: 'is' won't work!
            stop = 1

def _gen_absdir_tuples(seq, oridic=None):
    """
    for each item of the given sequence, yield a tuple
    (the string, split by directory separators; not normcased)

    """
    if isinstance(oridic, dict):
        for s in seq:
            a = abspath(s)
            n = normcase(a)
            t = tuple(n.split(sep))
            if t in oridic:
                continue
            else:
                # oridic[n] = a
                oridic[t] = a
                yield tuple(a.split(sep))
    else:
        dupes = set()
        for s in seq:
            a = abspath(s)
            n = normcase(a)
            if n in dupes:
                continue
            else:
                dupes.add(n)
                yield tuple(a.split(sep))


def _stored_below_dirtup(s, tup):
    """
    Check the given normalized path, whether it specifies something
    below the directory, given as a tuple

    """
    assert isinstance(s, tuple)
    l = len(tup)
    return len(s) >= l and s[:l] == tup

def _rejoin(tup):
    assert isinstance(tup, tuple)
    return sep.join(tup)


def stored_below_any_dirtup(s, tupsequence):
    """
    normalize the path, given as tuple/list/string, and look for it
    in the given sequence of tuples (which may be a dictionary with
    tuple keys as well)

    """
    if isinstance(s, tuple):
        s = tuple(map(normcase, s))
    elif isinstance(s, list):
        s = tuple(map(normcase, s))
    else:
        s = tuple(normcase(s).split(sep))
    for t in tupsequence:
        if _stored_below_dirtup(s, t):
            return 1
    return 0

def np(s):
    u"""
    gib eine normierte Fassung des �bergebenen Pfadstrings zur�ck
    """
    # abspath beinhaltet normpath
    return normcase(abspath(s))

def ask(txt):
    # TODO: deprecation warning
    from thebops.shtools import ask as fancy_ask
    fancy_ask(txt)

try:
    from os import link
except ImportError:
    if DEBUG:
        print "Can't import link"
    link = Link()

try:
    from os import symlink
except ImportError:
    if DEBUG:
        print "Can't import symlink"
    symlink = Symlink()

symlink_forced = Symlink_forced()

def _mktimestuple(atime, mtime, fname):
    """
    simple helper function to normalize the arguments for touch()
    """
    if isinstance(atime, tuple):
        assert mtime is None
        atime, mtime = atime
    if atime is None or mtime is None:
        try:
            info = stat(fname)
            return (atime or info.st_atime,
                    mtime or info.st_mtime,
                    )
        except OSError:
            return (atime or time(),
                    mtime or time(),
                    )
    return (atime, mtime)

# http://stackoverflow.com/questions/1158076/implement-touch-using-python
def touch(fname, atime=None, mtime=None):
    """
    update access and modification time of a file, creating it if necessary
    """
    times = _mktimestuple(atime, mtime, fname)
    try:
        utime(fname, times)
    except OSError:
        open(fname, 'a').close()
        utime(fname, times)
        
if __name__ == '__main__':
    from thebops.modinfo import main as modinfo
    modinfo(version='%prog '+__version__)
