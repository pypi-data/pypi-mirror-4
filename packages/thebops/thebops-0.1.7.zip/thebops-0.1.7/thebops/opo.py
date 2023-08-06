#!/usr/bin/env python
# -*- coding: latin1 -*- vim: ts=8 sts=4 sw=4 si et tw=79
"""\
opo: optparse options
"""

__author__ = "Tobias Herp <tobias.herp@gmx.net>"
VERSION = (0,
           3,   # add_trace_option, DEBUG
           2,   # add_verbosity_options: action
           'rev-%s' % '$Rev: 970 $'[6:-2],
           )
__version__ = '.'.join(map(str, VERSION))

__all__ = ['add_date_options',
           'add_glob_options',
           'add_help_option',
           'add_verbosity_options',
           'add_version_option',
           # to be used together:
           'add_trace_option', 'DEBUG',
           # callback functions:
           'cb_decrease',
           'cb_simplefunc',
           'cb_counting_sidekick',
           # other helpers:
           'get_the_parser',
           # TODO:
           # 'cb_negations', # siehe wget.py, negations; auch für wobinich.py
           ]

from optparse import OptionConflictError
from time import mktime, localtime
pdb = None  # see DEBUG, cb_counting_sidekick, dbg_... functions

from thebops.shtools import DateCalculator
from thebops.anyos import isunix

try:
    _
except NameError:
    def _(s):
        return s

def cb_simplefunc(option, opt_str, value, parser, func, *args):
    """
    Simple callback function: apply the given function

    If the calling option takes a value, it is inserted
    as the 1st argument to the given function.
    """
    liz = list(args)
    if value is not None:
        liz.insert(0, value)
    setattr(parser.values, option.dest, func(*tuple(liz)))

def cb_decrease(option, opt_str, value, parser, floor=0, *args):
    """
    Simple callback function: decrease the given value by 1
    """
    val = getattr(parser.values, option.dest, 0)
    if value is None:
        val -= 1
    else:
        # can only happen if requested by calling option:
        val -= value
    assert None < -100
    if val < floor:
        val = floor
    setattr(parser.values, option.dest, val)

def splitdate_european(s, div='.', order='dmy'):
    """
    split a european-style date specification

    >>> splitdate_european('1.10.')
    {'day': 1, 'month': 10, 'year': None}
    """
    keys = ['day', 'month', 'year']
    res = {}
    for k in keys:
        res[k] = None
    assert order in ('dmy', 'ymd')
    if order == 'ymd':
        keys.reverse()
    liz = s.split(div)
    while liz:
        v = liz.pop(0)
        k = keys.pop(0)
        if v:
            res[k] = int(v)
    if liz:
        raise ValueError(liz)
    return res

def mkdate_simple(s, func=splitdate_european):
    dic = func(s)
    liz = _dd2list(dic)
    today_l = list(localtime())
    if liz[0] is not None and liz[0] < 100:
        liz[0] += (today_l[0] // 100) * 100
    today_l[3:6] = [12, 0, 0]
    for i in range(len(liz)):
        if liz[i] is not None:
            today_l[i] = liz[i]
    return localtime(mktime(today_l))

def _dd2list(dic):
    """
    date dictionary to list
    """
    return [dic['year'], dic['month'], dic['day']]

def add_date_options(pog,
                     dest='date',
                     today_args=None,
                     tomorrow_args=None,
                     yesterday_args=None,
                     parsedval_args=None,
                     parsedval_func=None,
                     metavar=None,
                     default=0):
    """
    pog -- parser or group
    """
    adddays = DateCalculator()
    cbargs = [adddays, None]
    kwargs = {'dest': dest,
              'action': 'callback',
              'callback': cb_simplefunc,
              'callback_args': None,    # replaced by tuple, see below
              }
    if default is not None:
        if isinstance(default, int) and default < 10000:
            default = adddays(default)
        elif isinstance(default, (int, float)):
            default = localtime(default)
        kwargs['default'] = default

    if today_args is None:
        today_args = ['--today',
                      '--heute',
                      ]
    if today_args:
        cbargs[1] = 0
        kwargs['callback_args'] = tuple(cbargs)
        pog.add_option(*tuple(today_args), **kwargs)
    if yesterday_args is None:
        yesterday_args = ['--yesterday',
                          '--gestern',
                          ]
    if yesterday_args:
        cbargs[1] = -1
        kwargs['callback_args'] = tuple(cbargs)
        pog.add_option(*tuple(yesterday_args), **kwargs)
    if tomorrow_args is None:
        tomorrow_args = ['--tomorrow',
                         '--morgen',
                         ]
    if tomorrow_args:
        cbargs[1] = 1
        kwargs['callback_args'] = tuple(cbargs)
        pog.add_option(*tuple(tomorrow_args), **kwargs)
    if parsedval_args is None:
        parsedval_args = ['--date',
                          '--datum',
                          ]
    if parsedval_args:
        if parsedval_func is None:
            parsedval_func = mkdate_simple
        del kwargs['callback_args']
        if metavar is None:
            metavar = getattr(parsedval_func, 'metavar', None)
        kwargs.update({'callback': cb_simplefunc,
                       'callback_args': (parsedval_func,),
                       'type': 'string',
                       'metavar': metavar,
                       })
        pog.add_option(*tuple(parsedval_args), **kwargs)

def add_help_option(pog, *args, **kwargs):
    """
    Add a --help option to the given OptionParser or OptionGroup object
    (possible only if not already done during creation of the OptionParser
    object; to suppress this, create it with 'add_help_option=0').

    All options but the "parser or group" are optional; by default, the only
    difference to the non-suppressed --help option is the additional '-?'
    option string (and your free choice to put it into an option group).
    """
    # TODO:
    # - autosplit to two options if an integer constant for --help is given
    # - ... perpaps introduce "add_..._options" for this purpose
    if not args:
        args = ('-h', '-?', '--help')
    keys = kwargs.keys()
    if 'action' not in keys:
        kwargs['action'] = 'help'
    if 'help' not in keys:
        kwargs['help'] = _('show this help message and exit')
    pog.add_option(*args, **kwargs)

def add_version_option(pog, *args, **kwargs):
    """
    Add a --version option to the given OptionParser or OptionGroup object
    (possible only if not already done during creation of the OptionParser
    object; to suppress this, create it without the 'version' argument
    and give this argument to this function instead).

    Important argument:

    version -- the program version, e.g. a string, or a tuple of integers. You
               *must* specify this, unless you change the default 'version'
               action to something else, e.g. 'count', and build your version
               information facility yourself.

    All arguments to add_option are supported; by default, the only difference
    to the non-default --version option is the additional '-V' option string
    (and your free choice to put it into an option group).
    """
    if not args:
        args = ('-V', '--version')
    keys = kwargs.keys()
    if 'version' in keys:
        version = kwargs.pop('version')
        if isinstance(version, (int, float)):
            version = '%%prog %s' % version
        elif isinstance(version, (list, tuple)):
            version = ' '.join(('%prog',
                                '.'.join(map(str, version))))
        elif isinstance(version, basestring):
            pass
        else:
            version = '%%prog %s' % (version,)
        pa = pog
        while hasattr(pa, 'parser'):
            pa = getattr(pa, 'parser')
        pa.version = version

    if 'action' not in keys:
        kwargs['action'] = 'version'
    if 'help' not in keys:
        kwargs['help'] = _("show program's version number and exit")
    pog.add_option(*args, **kwargs)

def add_verbosity_options(pog,
                          dest='verbose',
                          default=0,
                          action='count',
                          complement=None,
                          verbose_help=None,
                          q_help=None,
                          quiet_help=None,
                          q_args=None,
                          q_kwargs=None):
    """
    Add counting -v/--verbose option, under certain conditions
    accompanied with --quiet and a decreasing -q.

    This function is work in progress; please specify keyword arguments,
    since the exact signature might change!

    Options are:

    dest -- propagated to option constructors
    default -- dto., default: 0
    action -- 'count' (default) or 'store_true'
    complement -- whether to create the complementary options
                  -q and --quiet. Default is yes, if the default value
                  is != 0, else no.
    verbose_help -- your own help string for the -v/--verbose option;
                    specify a non-None false value to suppress the default help
    q_help -- your own help string for the -q option (dto.)
    quiet_help -- dto., for the --quiet option
    q_args -- unnamed arguments to complement function (currently used only
              if complement = 1)
    q_kwargs -- kwargs to the cb_decrease callback function which is used
                by '-q'. By default, this won't ever set the verbosity value to
                a number below zero; to change this, you might use {'floor':
                None}.
    """
    # help strings:
    if verbose_help is None:
        if action == 'count':
            verbose_help = _('be verbose (-vv: even more verbose)')
        else:
            verbose_help = _('be verbose')
    elif not verbose_help:
        verbose_help = None
    # processing:
    pog.add_option('-v', '--verbose',
                   dest=dest,
                   default=default,
                   action=action,
                   help=verbose_help)
    if complement is None:
        complement = int(default != 0)
        if default >= 2:
            complement = 2
    if not complement:
        return
    # more help strings:
    if quiet_help is None:
        quiet_help = _('switch extra output off')
    elif not quiet_help:
        quiet_help = None
    if complement < 2:
        kwargs = dict( dest=dest,
                       action='store_const',
                       const=0,
                       help=quiet_help)
        if q_args is None:
            q_args = ('--quiet', '-q')
        pog.add_option(*q_args, **kwargs)
        return
    if q_help is None:
        q_help = _('decrease verbosity')
    elif not q_help:
        q_help = None
    if quiet_help is None:
        quiet_help = _('switch extra output off')
    elif not quiet_help:
        quiet_help = None
    try:
        pog.add_option('-q',
                       dest=dest,
                       action='callback',
                       callback=cb_decrease,
                       callback_kwargs=q_kwargs,
                       help=q_help)
    except OptionConflictError:
        pass
    pog.add_option('--quiet',
                   dest=dest,
                   action='store_const',
                   const=0,
                   help=quiet_help)

def add_glob_options(pog,
                     dest=None,
                     default=None):
    """
    add --glob and --no-glob options to tell a program to evaluate
    or not shell-style regular expressions for commandline-given
    file (or directory..., whatever you need) arguments.

    On Linux operating systems and alike, usually the shell does the expansion;
    on DOS-descended operating systems (including Windows(tm) and OS/2(tm)),
    this is done by the programs themselves.

    dest - propagated to the option constructor, default: 'glob'
    default - give a non-None value to override the calculation from the
              anyos module
    """
    s = ('', _(' (default on this platform)'))
    if default is None:
        default = not isunix()
    else:
        default = bool(default)
    pog.add_option('--glob',
                   dest=dest or 'glob',
                   default=default,
                   action='store_true',
                   help=_('evaluate shell-style regular expressions%s'
                   ) % s[default])
    pog.add_option('--no-glob',
                   dest=dest or 'glob',
                   action='store_false',
                   help=_('leave regular expression expansion to the shell%s'
                   ) % s[not default])

def cb_counting_sidekick(option, opt_str, value, parser,
                         *funcs):
    """
    combines counting to calling functions:
    at first call, the first function is called,
    at second call the second.

    Used for add_trace_option/DEBUG.
    """
    val = getattr(parser.values, option.dest, 0)
    if value is None:
        value = 1
    if val is None:
        val = 1
    else:
        # can only happen if requested by calling option:
        val += value
    setattr(parser.values, option.dest, val)
    if val <= len(funcs):
        funcs[val-1]()

_DEBUG_KEY = 'dummy'
def DEBUG(func=None, *args, **kwargs):
    """
    For development purposes, simplifies the usage of pdb.set_trace.
    No need for

      if 0:
          import pdb; pdb.set_trace()

    everywhere in the code anymore.

    To be used together with add_trace_option.

    If called with arguments, the first one is checked for callability;
    if it evaluates to a True value, the processing is continued.

    If the first argument is not callable, no **kwargs are allowed.
    Otherwise, all *args are checked for their boolean value.
    """
    global pdb, _DEBUG_KEY
    if _DEBUG_KEY == 'dummy':
        return
    else:
        if callable(func) and not func(*args, **kwargs):
            return
        elif kwargs:
            assert not kwargs, (
                    'keyword args require a callable first argument'
                    ' (DEBUG(%r, %s, %s)'
                    ) % (func, args, kwargs)
        check = func is not None or args
        if check:
            for item in (func,) + args:
                if item:
                    check = 0
                    break
            if check:
                return

        if _DEBUG_KEY == 'init':
            import pdb
            _DEBUG_KEY = 'trace'
        elif _DEBUG_KEY == 'trace':
            return pdb.set_trace()  # -TT

def _dbg_import():
    # DEBUG can be used anywhere in application code;
    # no need to import pdb
    global pdb, _DEBUG_KEY
    import pdb
    _DEBUG_KEY = 'init'

def _dbg_start():
    # DEBUG will pdb.set_trace() when called after options evaluation;
    # see add_trace_option, cb_counting_sidekick
    global pdb, _DEBUG_KEY
    import pdb
    _DEBUG_KEY = 'trace'

def _dbg_options():
    # allows to debug options evaluation;
    # see add_trace_option, cb_counting_sidekick
    return DEBUG()

def add_trace_option(pog, *args, **kwargs):
    """
    Usage:

      from thebops.opo import add_trace_option, DEBUG
      # ...
      p = OptionParser(...)
      add_trace_option(p)   # counting option, -T
      # ...
      o, a = p.parse_args()
      DEBUG()               # calls set_trace, if -TT

    If the trace option is not given, every call to the DEBUG function will
    simply do nothing.
    If it is given once (-T), pdb is imported, and the first call to DEBUG will do
    nothing (but "awake" it)
    If it is given twice (-TT), the first call will execute pdb.set_trace().
    If it is given three times (-TTT), pdb.set_trace() is executed immediately,
    thus allowing to debug options evaluation.

    """
    KEYS = {'dest': 'trace',
            'action': 'callback',
            'callback': cb_counting_sidekick,
            'callback_args': (_dbg_import,
                              _dbg_start,
                              _dbg_options,
                              ),
            }
    KEYS.update(kwargs)
    if 'help' in KEYS:
        if not KEYS['help'].strip():
            del KEYS['help']
    else:
        KEYS['help'] = _('increase debugging level: '
                'with -T, DEBUG anywhere in the code; '
                'with -TT, start debugging after options evaluation; '
                'with -TTT, debugging starts *immediately* during '
                'options evaluation.')
    if not args:
        args = ('-T',)
    pog.add_option(*args, **KEYS)

def get_the_parser(parser):
    """
    take an OptionParser or OptionGroup object
    and return the (root) OptionParser object
    """
    use = parser    # don't change the given object!
    while 1:
        try:
            use = use.parser
        except AttributeError:
            return use

if __name__ == '__main__':
    from thebops.modinfo import main as modinfo
    modinfo(version=__version__)

