#!/usr/bin/env python
# -*- coding: utf-8 -*- vim: ts=8 sts=4 sw=4 si et tw=79
"""\
Demo program for the thebops.opo Python module
"""

__author__ = "Tobias Herp <tobias.herp@gmx.net>"
VERSION = (0,
           3,   # forked from opo.py 0.3.1
           3,   # add_backup_options
           'rev-%s' % '$Rev: 918 $'[6:-2],
           )
__version__ = '.'.join(map(str, VERSION))

from thebops.opo import *
from thebops.base import progname
from thebops.errors import info

try: _
except NameError:
    def _(s): return s

def demo_debug_args(tup):
    res = []
    for item in tup:
        try:
            res.append(int(item))
        except ValueError:
            res.append(item)
    if res:
        info(_('Arguments tuple converted to %s'
               ' as DEBUG(...) demo input'
               ) % res)
    return tuple(res)

def main():
    from thebops.optparse import OptionParser, OptionGroup
    from thebops.errors import err, info, check_errors
    p = OptionParser(description=_('A Python module which provides useful '
                     'optparse options'),
                     prog=progname(),
                     usage='\n    '.join(('',
                         'from optparse import OptionParser',
                         'from thebops.opo import add_date_options, '
                                          'add_version_option',
                         'p = OptionParser()',
                         'add_date_options(p)',
                         'add_version_option(p, version=(1, 0))',
                         'o, a = p.parse_args()',
                         'print o.date',
                         )),
                     add_help_option=0)

    g = OptionGroup(p, _("Demo for date options"))
    h = OptionGroup(p, 'hidden options')
    add_date_options(g, metavar='d.[m.[y]]')
    p.add_option_group(g)

    g = OptionGroup(p, _("Demo for verbosity options"))
    add_verbosity_options(g, default=2)
    p.add_option_group(g)

    g = OptionGroup(p, _("Options with optional values"))
    add_optval_option(g, '--option',
                      empty='EMPTY',
                      default='MISSING',
                      metavar='VALUE',
                      help=_('"EMPTY" if given without a value. Note: '
                      '--option or '
                      '--option=VALUE will work; --option VALUE will *not*! '
                      'Same is true for -oVALUE (will work) and '
                      '-o VALUE (won\'t)'))
    add_optval_option(h, '-o',
                      empty='EMPTY',
                      dest='option')
    add_backup_options(g)
    p.add_option_group(g)

    g = OptionGroup(p, _("Development options"))
    add_trace_option(g)
    p.add_option_group(g)

    g = OptionGroup(p, _("Everyday options"))
    add_help_option(g)
    add_version_option(g, version=VERSION)
    p.add_option_group(g)

    o, a = p.parse_args()
    DEBUG()

    if not o.trace:
        for arg in a:
            err(_('Argument %r ignored') % arg)
    DEBUG(0, *demo_debug_args(a))
    if o.date:
        info(_('Date: %s') % str(o.date[:3]))
    info(_('Verbosity: %r') % o.verbose)
    info(_('With or without value: %r') % o.option)
    info(_('Backup type: %r') % o.backup_type)
    info(_('Backup suffix: %r') % o.backup_suffix)
    check_errors()

if __name__ == '__main__':
    main()

