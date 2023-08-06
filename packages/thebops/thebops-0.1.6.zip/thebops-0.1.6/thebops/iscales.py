# -*- coding: latin1 -*- vim: sw=4 sts=4 ts=8 et ft=python
"""
Python module for image dimensions
"""
__version__ = (0,
               6, # CSS colour parsing moved to colours module
               1, # 'main' function for iscales_demo
               'rev-%s' % '$Rev: 962 $'[6:-2],
               )

import os.path
from sys import stderr, exit

from thebops.optparse import OptionValueError, OptParseError
# TODO: replace
from thebops.errors import fatal, warning, progname
from thebops.colours import CSS_COLOURS

__all__ = ('add_scale_option', 'add_scale_helpers',
           'add_cut_option', 
           'add_resampling_option',
           'add_clockwise_option',
           'scales',
           'CSS_CLOCK',
           'importIntFromPIL',
           'outFileName',
           # factories:
           'clip_arg',
           # mirrors:
           'mirror_auto',
           'mirror_zero',
           # info/debugging:
           'clockwise_info',
           # exceptions:
           'IscalesError',
           'FormatRegistryError',
           'DuplicateKeyError',
           'InsufficientSpecsError',
           )

try:
    set
except NameError:
    from sets import Set as set

try:
    _
except NameError:
    def _(s): return s


__author__ = 'Tobias Herp <tobias.herp@gmx.de>'
__usage__ = """
Typical usage:

  from optparse import OptionParser, OptionGroup
  from %(prog)s import add_scale_option, add_scale_helpers

  parser = OptionParser()
  group_ = OptionGroup(parser, 'Interesting options')
  add_scale_option(group_)    # adds a '--scale' option
  parser.add_option_group(group_)

  group_ = OptionGroup(parser, 'Image format help')
  add_scale_helpers(group_)
  parser.add_option_group(group_)

  option, args = parser.parse_args()

  print option.scale
"""

HELP_RC = 1

class IscalesError(Exception):
    """
    root class of the exceptions hierarchy of the iscales module
    """

class InsufficientSpecsError(IscalesError, AssertionError):
    pass

class FormatRegistryError(IscalesError):
    pass

class DuplicateKeyError(FormatRegistryError):
    pass

def outFileName(inf, outf='',
                img=None, sc=None,
                force_dimensions=0,
                dimname=None):
    """
    return a (full) file name for the new image:

    inf -- the input file name (mandatory)
    
    outf -- the output file name

    img -- the image object. Needed, if the actual size of the image
           is to be used for the file name

    sc -- the scale tuple (width, height). Needed, if the maximum
          size of the image is to be used for the file name

    force_dimensions -- insert the dimensions into the name, even if
          it wouldn't be necessary to distinguish it from the input name

    dimname -- dimension name (instead of WIDTHxHEIGHT, if "forced")

    if outf is != '', use it. If outf is the name of a directory,
    append the file part of inf
    """
    if outf:
        if outf.endswith(os.path.sep):
            outf += os.path.split(inf)[1]
        elif os.path.exists(outf):
            if os.path.isdir(outf):
                outf = os.path.sep.join((outf,os.path.split(inf)[1]))
        if not force_dimensions:
            return outf
        elif not (img or sc):
            raise InsufficientSpecsError('specify image object or scale '
                                         'tuple, or drop force_dimensions')
    elif not (img or sc):
        raise InsufficientSpecsError('at least outfile, image object'
                                     ' or scale tuple needed')
    else:
        outf = inf
    if dimname:
        size_info = '-%s' % dimname
    elif img:
        size_info = '-%dx%d' % img.size
    elif sc:
        try:
            size_info = '-%dx%d' % sc
        except TypeError:
            raise InsufficientSpecsError('sc must contain exactly two integers')
    else:
        raise AssertionError('Image or scale tuple is specified, isn\'t it?!')
    return size_info.join(os.path.splitext(outf))

def reduce(z, n):
    """
    reduce a fraction by dividing both numbers by the primes 2, 3, 5, and 7
    (which is sufficient for the common screen resolutions), and return the
    reduced tuple
    
    >>> reduce(1280, 1024)
    (5, 4)
    >>> reduce(1400, 1050)
    (4, 3)
    """
    for p in (2, 3, 5, 7):
        while not (z%p or n%p):
            z, n = z//p, n//p
    return (z, n)

class StandardRatios(dict): # requires Python 2.2+
    """
    a registry of ratios; e.g. 8:5 is better known as 16:10
    """
    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            return key

normalratio = StandardRatios()
normalratio[(8, 5)] = (16, 10)

def intsb4strings(seq):
    """
    integers before strings

    >>> intsb4strings(('a', '1', 'b', '2'))
    [1, 2, 'a', 'b']
    """
    res = list()
    for i in seq:
        try:
            res.append(int(i))
        except ValueError:
            res.append(i)
    return sorted(res)

class ScaleRegistry(object):
    """
    Registry for (width, height) image dimensions
    """
    def __init__(self):
        self.ratios = dict()
        self.keys_e = dict() # explicit
        self.keys_i = dict() # implicit
        self.dims = dict()

    def register(self, width, height,
                 names=None,
                 wkey=None,
                 pxratio=1,
                 force=None):
        """
        register the given file format.

        width -- the width [Px]

        height -- the height [Px]

        names -- one or more format names. A single name can be given
                 as a string; more than one must be given as a tuple of strings

        wkey -- take the width value as a key; if None, and no names are given,
                defaults to True.

        pxratio -- width/height ratio of pixels (usually 1, for square pixels;
                   not yet used)

        force -- by default (force=False), duplicate keys yield errors;
                 specify True to make them overwrite existing keys
        """
        tup = width, height
        if wkey is None:
            wkey = not names
        else:
            if not wkey:
                if not names:
                    raise FormatRegistryError('with no name[s] given, '
                            'wkey must not be False')
            wkey = bool(wkey)
        if names:
            if isinstance(names, basestring):
                nlist = [names]
            elif isinstance(names, (list, tuple)):
                nlist = list(names)
            else:
                raise FormatRegistryError('invalid names argument %r'
                        '(%r)' % (names, type(names)))
        else:
            nlist = list()
        for n in nlist:
            if not n:
                raise FormatRegistryError('Empty names are not allowed (%r)'
                                          % n)
            elif not isinstance(n, basestring):
                raise FormatRegistryError('Some kind of string expected'
                                          ' (%r)' % n)
        if wkey:
            nlist.append(str(width))
        elif not nlist:
            raise FormatRegistryError('list of names is empty')

        # (width, height) tuple -> names:
        if tup in self.dims:
            print '-' * 79
            print self.dims[tup]
            print tup
            print nlist
            pass    # TODO: perhaps yield some kind of info or warning
        else:
            # self.dims[tup] = set(nlist)
            # a list will preserve the order information:
            self.dims[tup] = nlist

        # name -> (width, height) tuple:
        for n in nlist:
            if n in self.keys_e:
                raise DuplicateKeyError('%r -> %s collides with %s'
                                   % (n, tup, self.keys_e[n],
                                      ))
            else:
                self.keys_e[n] = tup
            un = n.upper()
            if un != n:
                self.keys_i[un] = tup

        # ratio -> list of (width, height) tuples:
        dimtup = w, h = reduce(width, height)
        # dimtup = (w, h)
        if dimtup not in self.ratios:
            self.ratios[dimtup] = list()
        self.ratios[dimtup].append(tup)

    def getRatio(self, key):
        if key in self.keys_e:
            return self.keys_e[key]
        ukey = key.upper()
        if ukey in self.keys_e:
            return self.keys_e[ukey]
        if ukey in self.keys_i:
            return self.keys_i[ukey]
        raise KeyError(key)

    def genKeyInfosRaw(self):
        for k, v in self.keys_e.items():
            try:
                yield int(k), v[0], v[1]
            except ValueError:
                yield k, v[0], v[1]

    def showKeysRaw(self):
        for z in sorted(list(scales.genKeyInfosRaw())):
            print '%s\t->%5d x%5d' % z
        exit(HELP_RC)

    def genKeyInfos(self):
        """
        generate key infos in a sortable fashion; yield tuples of equal
        length, containing sorting keys.  The last element is a string
        which can be used directly.

        The resulting sequence is *not* grouped by ratio.
        """
        for dim, keys in self.dims.items():
            num = None
            w, h = dim
            names = list()
            for k in keys:
                if num is None:
                    try:
                        num = int(k)
                        assert num == w
                        continue
                    except ValueError:
                        pass
                names.append(k)
            if names:
                names.sort()
            w1, h1 = reduce(w, h)
            rat = float(w1) / h1
            if num:
                yield (num, rat, w, h,
                       ' %5d (x%5d, %d:%d%s)' % (
                           w, h,
                           w1, h1,
                           names and '; %s' % '/'.join(names)
                                 or '',
                        ))
            else:
                yield (None, rat, w, h,
                       '  %s (%d x %d, %d:%d)' % (
                           '/'.join(names),
                           w, h,
                           w1, h1,
                           ))

    def showKeys(self):
        seq = list(self.genKeyInfos())
        seq.sort()
        sel = [tup
               for tup in seq
               if tup[0] is not None]
        if sel:
            print _('Widths with default heights:')
            for tup in sel:
                print tup[-1]
        sel = [tup
               for tup in seq
               if tup[0] is None]
        if sel:
            print _('Specify by name only:')
            for tup in sel:
                print tup[-1]
        exit(HELP_RC)

    def showKeysByRatio(self):
        seq = list(self.genKeyInfos())
        ratios_dict = dict()
        ratios_list = list()
        grouped = list()
        rest = list()
        for (rat, w, h) in self.getRatios():
            if ((w < 10 and h < 10)
                or len(self.ratios[(w, h)]) > 1):
                grouped.append((w, h))
            else:
                rest.append((w, h))
        
        def diminfo(dim, rat=None):
            res = ['  ']
            res.append('%d x %d ' % dim)
            res.append('(%s'
                       % '/'.join(map(str,
                                      intsb4strings(self.dims[dim]))))
            if rat:
                res.append('; %d:%d' % rat)
            res.append(')')
            return ''.join(res)

        for rat in grouped:
            print '%d:%d:' % normalratio[rat]
            for dim in sorted(self.ratios[rat]):
                print diminfo(dim)
        if rest:
            print 'other:'
            for rat in rest:
                dim = self.ratios[rat][0]
                print diminfo(dim, rat)
        exit(HELP_RC)

    def getRatios(self):
        """
        return a sorted list of ratio tuples (quot, width, height)
        """
        return sorted([(float(w)/h, w, h)
                       for w, h in self.ratios])

    def getKeysByDim(self, dim):
        """
        generate the non-numeric keys which yield the given dimension tuple
        """
        try:
            for key in self.dims[dim]:
                try:
                    int(key)
                except ValueError:
                    yield key
        except KeyError:
            return

    def getKeysByRatio(self):
        """
        generate the keys, grouped by ratio
        """
        for rat, w, h in scales.getRatios():
            print "%d:%d:" % (w, h)
            print '\t%s' % scales.ratios[(w, h)]
        raise NotImplementedError

    def bestFormatName(self, width, height, given=None):
        strings, numbers = list(), list()
        normal = dict()
        try:
            specs = self.dims[(width, height)]
            given = given.upper()
            for spec in specs:
                try:
                    numbers.append(int(spec))
                except ValueError:
                    if spec.upper() == given:
                        return spec
                    strings.append(spec)
            return strings[0]
        except KeyError:
            return None
        except IndexError:
            return None



def importIntValue(libname, valname):
    """
    imports a given integer value from a given module.
    Raises ImportError, if an unknown module is specified;
    catches the AttributeError, raised if the value is unknown.
    Before using this function to import from a module in a
    package, it apparently is necessary to import the package.
    """
    import PIL.Image
    try:
        modu = __import__(libname, globals(), locals(), [])
    except NameError: # doesn't work!!!
        fatal('You might need to import %s before calling importIntValue()' %
              libname.split('.')[0])
    try:
        test = eval('%s.%s' %(libname, valname))
    except AttributeError:
        raise OptionValueError('%s is not known in module %s'
                               % (valname, libname))
    if callable(test):
        fatal('%s.%s is callable!' % (libname, valname))
    elif type(test) == type(0):
        return test
    else:
        fatal('Won\'t import %s.%s %s: not an integer' % (libname, valname, type(test)))

def importIntFromPIL(name):
    return importIntValue('PIL.Image', name)

def cb_int_from_pil(option, opt_str, value, parser, known):
    """
    callback function to get an integer constant from PIL
    """
    val = value.strip().upper()
    if not val:
        raise OptionValueError('%r: invalid value for %s'
                               % (value, opt_str))
    try:
        setattr(parser.values, option.dest,
                importIntFromPIL(val))
    except ImportError, e:
        raise OptionValueError('%s: import error (%r)'
                               % (opt_str, str(e)))
    if not val in known:
        warning('Successfully imported value of unknown symbol %s'
                % val)

CSS_CLOCK = ('top', 'right', 'bottom', 'left')

def cb_clockwise(option, opt_str, value, parser,
                 sep, factory, mirror=None, mirror2=None):
    """
    optparse callback function for clockwise options
    """
    if not value:
        raise OptionValueError('%s: empty value not allowed'
                               % opt_str)
    try:
        liz = map(factory, value.split(sep))
    except ValueError, e:
        raise OptionValueError((str(e)))
    if len(liz) > 4:
        raise OptionValueError('%s takes at most 4 values %s'
                               % (opt_str, tuple(liz)))
    if mirror is None:
        mirror = lambda x: x
    if mirror2 is None:
        mirror2 = mirror
    dic = dict()
    for k, i in zip(CSS_CLOCK, range(len(liz))):
        dic[k] = liz[i]
    if not 'right' in dic:
        dic['right'] = mirror2(dic['top'])
    if not 'bottom' in dic:
        dic['bottom'] = mirror(dic['top'])
    if not 'left' in dic:
        dic['left'] = mirror(dic['right'])
    setattr(parser.values, option.dest, dic)

def cb_clockwise_single(option, opt_str, value, parser,
                        factory, key):
    """
    optparse callback function for single-value-spin-offs of clockwise options
    """
    try:
        val = factory(value)
    except ValueError: #, e:
        raise OptionValueError
    # getattr returns the dict itself:
    dic = getattr(parser.values, option.dest)
    writeback = dic is None
    if writeback:
        dic = dict(zip(CSS_CLOCK,
                       (0, 0, 0, 0)))
    dic[key] = val
    if writeback:
        setattr(parser.values, option.dest, dic)

def add_clockwise_option(parser,
                         *args,
                         **kwargs):
    """
    create an option which takes 1 to 4 comma-separated values
    which populate a dict with top, right, bottom, left keys
    in CSS fashion; e.g., if only a single value is given, it is
    used for all sides.

    help -- the help text
    dest -- the dest value (should look like a valid Python identifier)
    factory -- a callable which takes one of the separated values
    mirror -- a callable to 'mirror' the top to bottom, right to left value
    mirror2 -- a callable to 'mirror' the top to right value; default: mirror
    detail_options -- create ...-top, ...-right etc. options?
                      Default: yes, if long option string given
    group2 -- a separate group for the detail_options
    sep -- the separator, default: the comma (',')
    *args -- the option strings (at least one required)
    """
    # Notloesung...
    defaults = {'dest':           None,
                'factory':        int,
                'mirror':         None,
                'mirror2':        None,
                'detail_options': None,
                'sep':            ',',
                'help':           None,
                'single_metavar': None,
                'metavar':        None,
                'group2':         None,
                }
    defaults.update(kwargs)
    firstlong = None
    dest = defaults['dest']
    for a in args:
        if a.startswith('--'):
            firstlong = a
            if not dest:
                dest = a[2:]
            break
        elif not a.startswith('-'):
            raise OptParseError('not a valid option string: %r'
                                % a)
    if not args:
        raise OptParseError('no long nor short option strings')
    help = defaults['help']
    if help.find('%(') != -1:
        help = help % defaults
    detail_options = defaults['detail_options']
    sep = defaults['sep']
    factory = defaults['factory']
    metavar = defaults['metavar'] or sep.join(['top[', 'right[',
                                               'bottom[', 'left]]]'])
    kwargs1 = dict(help=help,
                   dest=dest,
                   type='string',    # ?!
                   metavar=metavar,
                   action='callback',
                   callback=cb_clockwise,
                   callback_kwargs=dict(sep=sep,
                                        factory=factory,
                                        mirror=defaults['mirror'],
                                        mirror2=defaults['mirror2']))
    parser.add_option(*args, **kwargs1)
    if detail_options is None:
        detail_options = bool(firstlong)
    elif detail_options and not firstlong:
        raise OptParseError('detail_options requested, but no long '
                            'option given')
    if detail_options:
        try:
            group_ = defaults['group2']
        except KeyError:
            group_ = parser
        for key in CSS_CLOCK:
            group_.add_option('-'.join((firstlong, key)),
                              dest=dest,
                              type='string',    # ?!
                              action='callback',
                              metavar=defaults['single_metavar'],
                              callback=cb_clockwise_single,
                              callback_kwargs=dict(factory=factory,
                                                   key=key))

def add_resampling_option(parser,
                          help=None,
                          default='ANTIALIAS',
                          dest='filter',
                          *args):
    if help is None:
        help = _('the resampling filter to use; one of: '
                 'antialias (default; best known as of PIL 1.1.5), '
                 'nearest, bilinear, bicubic (not case sensitive)')
    if not args:
        args = ('--resampling-filter', '--rf')
    kwargs = dict(action='callback',
                  callback=cb_int_from_pil,
                  callback_kwargs=dict(known=set((
                      'NEAREST', 'NONE',    # the same; PIL default
                      'ANTIALIAS',          # best as of PIL 1.1.5
                      'BILINEAR', 'BICUBIC',
                      'LINEAR',   'CUBIC',
                      ))),
                  type='string',
                  default=default,
                  metavar=default,
                  dest=dest,
                  help=help)
    parser.add_option(*args, **kwargs)

scales = ScaleRegistry()

def cb_resolve_scale(option, opt_str, value, parser):
    try:
        val = scales.getRatio(value)
    except KeyError:
        val = value.split('x')
        if len(val) != 2:
            raise OptionValueError('x between two integer values, or known'
                    ' format spec. expected (%r)' % str(value))
        try:
            # TODO: dict(width, height, scalespec) anstelle des Tupels
            val = tuple(map(int, val))
        except ValueError:
            raise OptionValueError('%r: not a known/valid format spec' % value)
    val = dict(width=val[0],
               height=val[1],
               given=value)
    val['name'] = scales.bestFormatName(**val) \
                  or ('%(width)dx%(height)d' % val)
    setattr(parser.values, option.dest, val)

def add_scale_option(parser, help=None, dest='scale', *args):
    if help is None:
        help = _('width [px] of the resulting image, which is completed'
                 ' with the common companion height, '
                 'e.g. 1280 (x1024), 1024 (x768) or 640 (x480). '
                 'Some scales are known by name, e.g. VGA (640x480); '
                 'you may specify any other scale explicitly, '
                 'e.g. 1280x960.')
    elif not help:
        help = None
    parser.add_option('-s', '--scale',
                      action='callback',
                      type='string',    # callback yields tuple
                      metavar=_('WIDTH[xHEIGHT]|Name'),
                      dest=dest,
                      callback=cb_resolve_scale,
                      help=help)

def cb_resolve_cut(option, opt_str, value, parser):
    cut_opt={'vertical': 'middle',
             'horizontal': 'center',
             }
    for o in value.split(','):
        if o in ('top', 'middle', 'bottom'):
            cut_opt['vertical']=o
        elif o in ('left', 'center', 'right'):
            cut_opt['horizontal']=o
        else:
            fatal('%s: illegal option for --cut' % o, 5)
    setattr(parser.values, option.dest, cut_opt)

def add_cut_option(parser, help=None, dest='cut', *args):
    if help is None:
        help = _("specify up to one of 'middle' (default), 'top' and 'bottom', "
                 "and up to one of 'center' (default), 'left' and 'right', "
                 'divided by comma. If this option is omitted, the resulting '
                 'image will reach the maximum possible size only '
                 'if it features exactly the same side length ratio.')
    elif not help:
        help = None
    parser.add_option('--cut',
                      action='callback',
                      type='string',    # callback yields tuple
                      metavar=_('HORI,VERT'),
                      dest=dest,
                      callback=cb_resolve_cut,
                      help=help)

def cb_showKeys(option, opt_str, value, parser):
    scales.showKeys()

def cb_showKeysByRatio(option, opt_str, value, parser):
    scales.showKeysByRatio()

def cb_showKeysRaw(option, opt_str, value, parser):
    scales.showKeysRaw()

def add_scale_helpers(parser):
    parser.add_option('--help-scales',
                      action='callback',
                      callback=cb_showKeys,
                      help=_('show known scales'))
    parser.add_option('--help-scales-grouped',
                      action='callback',
                      callback=cb_showKeysByRatio,
                      help=_('show known scales, grouped by side ratio'))
    parser.add_option('--help-scales-raw',
                      action='callback',
                      callback=cb_showKeysRaw,
                      help=_('show known scales in "raw" format'))


for tup in (
        ( 640,  480, ('VGA',
                      '480p',   # <http://en.wikipedia.org/wiki/480p>
                      ), 1),
        ( 800,  600, 'SVGA', 1),
        ( 800,  480, 'WVGA', 0),
        (1024,  600, 'WSVGA', 0),
        (1024,  768, 'XGA', 1),
        (1280,  720, '720p', 0), # smaller HDTV format, non-interlaced
        (1280,  800, 'WXGA', 0), # a.k.a. "Vesa 1280"
        (1280,  960, 'QVGA', 0), # original meaning "quadruple"
        (1280, 1024, 'SXGA', 1), # a.k.a. "Vesa 1280"
        (1400, 1050, 'SXGA+', 1),
        (1600, 1200, 'UXGA', 1),
        (1600, 1024, 'WSXGA', 0),
        (1680, 1050, 'WSXGA+', 1),
        (1920, 1200, 'WUXGA', 1), # maximum for Single-Link DVI
        (1920, 1080, ('FullHD',
                      'FHD',    # http://en.wikipedia.org/wiki/Graphic_display_resolutions
                      '1080i',  # well, "interlaced" doesn't apply to images ...
                      '1080p',  # ... neither does 'p'
                      ), 0),
        (2048, 1536, ('QXGA',
                      'SUXGA',
                      ), 1),
        (2048, 1152, 'QWXGA', 0),
        (2560, 2048, 'QSXGA', 1),
        (2560, 1536, 'WQXGA', 0),   # c't 1/2011, S. 96: 2560x1600
        (2560, 1440, 'WQHD', 0),    # c't 1/2011, S. 96: 'Pixel-Autobahn'
        (3200, 2048, 'WQSXGA', 0),
        # (854,  480,  '480p', 0),  # non-standard according to wp
        # <http://en.wikipedia.org/wiki/Low-definition_television>:
        (640,  360,  '360p', 0),    
        (320,  240,  '240p', 1),    
        # (400,  226,  '240p', 0),  # ?!
        (480,  360,  'HQ6', 0),
        (176,  144,  'HQ13', 0),
        (3200, 2400, 'QUXGA', 1),
        (3840, 2400, ('QWUXGA',
                      'WQUXGA',
                      ), 1),
        # ( 320,  240),
        ( 240,  180),
        ( 180,  135),
        ( 160,  120, 'QQVGA', 1),
        (  88,   31), # small banner buttons, e.g. for W3C validation links
        ):
    scales.register(*tup)   # width, height[, names[, wkey]]
del tup

def clip_arg(val):
    """
    take a string, and
    return an integer number, a percent value (as a string), or 'auto'
    (a possible 'factory' function, e.g. for add_clockwise_option)

    Will raise ValueErrors if something else is given.

    >>> clip_arg('50')
    50
    >>> clip_arg('50%')
    '50%'
    >>> clip_arg('0%')
    0
    """
    val = val.strip().lower()
    if val == 'auto':
        return val
    if val.endswith('%'):
        i = int(val[:-1])
        if not i:
            return i
        return '%d%%' % i
    return int(val or 0)

def mirror_auto(val):
    """
    mirror 0 to 0, and any other value to 'auto'

    >>> mirror_auto(0)
    0
    >>> mirror_auto(1)
    'auto'
    """
    if val == 0:
        return 0
    return 'auto'

def mirror_zero(val):
    """
    return 0 for any given value

    >>> mirror_zero(0)
    0
    >>> mirror_zero(1)
    0
    """
    return 0

def clockwise_info(val):
    """
    take None or a dictionary with top, right, bottom, left keys,
    and return a string
    """
    if val is None:
        return _('not specified')
    return ('{%s}' % ', '.join(['%s: %%(%s)r' % (k, k)
                                for k in CSS_CLOCK])
            ) % val

def main():
    from thebops.optparse import OptionParser, OptionGroup
    from thebops.modinfo import main as modinfo
    from thebops.opo import add_trace_option, DEBUG
    from thebops.errors import progname

    parser = OptionParser(usage='import %(prog)s | %%prog f1 f2 | %%prog --help'
                                % dict(prog=progname()),
                          prog=progname())
    group_ = OptionGroup(parser, _('Usage'))
    def cb_usage(*args):
        print (__doc__ + __usage__) % dict(prog=progname())
        exit(HELP_RC)

    group_.add_option('--usage',
                      action='callback',
                      callback=cb_usage,
                      help=_('show a usage example'))
    parser.add_option_group(group_)

    group_ = OptionGroup(parser, _('Known scales'))
    add_scale_helpers(group_)
    parser.add_option_group(group_)

    h = OptionGroup(parser, 'hidden options')
    add_trace_option(h)

    o, a = modinfo(version='.'.join(map(str, __version__)),
                   parser=parser)
    DEBUG()
    if a:
        for x in a:
            try:
                print x, '->', scales.getRatio(x)
            except KeyError:
                print '%s: unknown' % x
    elif o:
        print __doc__
        print '(usually imported by other other Python scripts)'
        print 'Enter --help to get some help, or try some format specs.'
        exit(HELP_RC)

if __name__ == '__main__':
    main()
