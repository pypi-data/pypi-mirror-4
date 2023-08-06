#!/usr/bin/env python
# -*- coding: latin1 -*- vim: ts=8 sts=4 sw=4 si et tw=79
"""\
optparse options
"""

__author__ = "Tobias Herp <tobias.herp@gmx.net>"
VERSION = (0,
           2,   # add_glob_options, add_verbosity_options
           3,   # 'main' function
           'rev-%s' % '$Rev: 947 $'[6:-2],
           )
__version__ = '.'.join(map(str, VERSION))

__all__ = ['add_date_options',
           'add_glob_options',
           'add_help_option',
           'add_verbosity_options',
           'add_version_option',
           # helpers: 
           'cb_decrease',
           'cb_simplefunc',
           # TODO: 
           # 'cb_negations', # siehe wget.py, negations; auch für wobinich.py
           ]

from optparse import OptionConflictError
from time import mktime, localtime

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
    # - autosplit to two options if a int. constant for --help is given
    # - ... 
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
    since the signature might change!

    Options are:

    dest -- propagated to option constructors
    default -- dto., default: 0
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
        verbose_help = _('be verbose (-vv: even more verbose)')
    elif not verbose_help:
        verbose_help = None
    # processing: 
    pog.add_option('-v', '--verbose',
                   dest=dest,
                   default=default,
                   action='count',
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

def main():
    try:
        from thebops.enhopa import OptionParser, OptionGroup
    except ImportError:
        from optparse import OptionParser, OptionGroup
    from thebops.errors import err, info, check_errors
    p = OptionParser(description=_('A Python module which provides useful '
                     'optparse options'),
                     usage='\n    '.join(('',
                         'from optparse import OptionParser',   
                         'from opo import add_date_options, '
                                          'add_version_option',
                         'p = OptionParser()',   
                         'add_date_options(p)',
                         'add_version_option(p, version=(1, 0))',
                         'o, a = p.parse_args()',
                         'print o.date',
                         )),
                     add_help_option=0)

    g = OptionGroup(p, _("Demo for date options"))
    add_date_options(g, metavar='d.[m.[y]]')
    p.add_option_group(g)

    g = OptionGroup(p, _("Demo for verbosity options"))
    add_verbosity_options(g, default=2)
    p.add_option_group(g)

    g = OptionGroup(p, _("Everyday options"))
    add_help_option(g)
    add_version_option(g, version=VERSION)
    p.add_option_group(g)

    o, a = p.parse_args()

    for arg in a:
        err(_('Argument %s ignored') % arg)
    if o.date:
        info(_('Date: %s') % str(o.date[:3]))
    info(_('Verbosity: %r') % o.verbose)
    check_errors()

if __name__ == '__main__':
    main()
