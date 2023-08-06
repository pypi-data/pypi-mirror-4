#!/usr/bin/python
# -*- coding: latin-1 -*- vim: ts=8 sts=4 et si sw=4 tw=79 
u"""\
%(prog)s.py: Python-Modul für Fehlerausgaben (für Konsolenprogramme)
"""

__author__ = "Tobias Herp <tobias.herp@gmx.net>"

# TODO:
# * introspection:
#   - skip foreign functions and objects (from imported modules)
#   - for pairs of identical functions (e.g. err and error),
#     print once and refer to it
#   - filtering by name
#   - put the whole introspection functionality in a special module

from sys import stdout, stderr, exit, argv, exc_info
from os.path import basename

_beispiele = u"""\
Einfaches Anwendungsbeispiel (Python-Skript):

Das folgende Python-Skript erwartet ganze Zahlen als Argumente.
Es überprüft zunächst alle übergebenen Argumente und gibt für *jedes* falsche
Argument eine Fehlermeldung aus; wenn Fehler aufgetreten sind, beendet es das
Programm, und gibt ansonsten das Produkt aller übergebenen Zahlen aus:

<snip>
from %(prog)s import err, check_errors
from sys import argv
numbers = []
for a in argv[1:]:
    try:
        numbers.append(int(a))
    except ValueError:
        err(u'%%r ist keine ganze Zahl' %% a)

check_errors()
print reduce(lambda a, b: a*b, numbers)
</snip>

(In einer interaktiven Python-Sitzung können Sie Zeile 2 durch so etwas wie
"argv = 'ignored 1 a 2 b 3 4'.split()" ersetzen.  Wenn argv[1:] Nicht-Zahlen
enthält, wird check_errors() die Python-Shell beenden.)

Hilfe, auch zu Funktionen und Daten: %(prog)s.py -h
"""
VERSION = '.'.join(map(str,
                   (0,
                    3, # modinfo
                    'rev-%s' % '$Rev: 845 $'[6:-2],
                    )))

RC_ERROR = 1   # bei Fehler ans System zurückzugeben, wenn nicht ein Zähler o.ä.
RC_OK = 0      # trivial, aber hiermit dokumentiert
RC_HELP = 3    # nach Hilfeausgabe zurückzugeben
RC_CANCEL = 98 # bei Abbruch durch Benutzer, z. B. nach Prompt
RC_ABORT = 99  # bei Abbruch durch Benutzer durch Interrupt

def set_progname(name=None):
    u"""
    setze den von warning, err, fatal und info auszugebenden Namen;
    in der Regel nicht nötiger Aufruf:
    set_progname(progname())
    """
    global _PROGNAME, _LOGNAME
    if name:
        _PROGNAME = name+':'
        _LOGNAME = '['+name+']'
    else:
        _PROGNAME = ''
        _LOGNAME = ''

set_progname('errors')

def info(text, to=None):
    u"""
    gib die übergebene Info aus, per Default zur Standardausgabe
    """
    if to is None:
        to = stdout
    print >> to, _PROGNAME+'i', text

WARNINGS = 0
def warn(text):
    u"""
    gib die übergebene Warnung aus und erhöhe den Warnungszähler
    """
    global WARNINGS
    WARNINGS += 1
    print >> stderr, _PROGNAME+'W', text
warning = warn

ERRORS = 0
def err(text, code=None):
    u"""
    gib die übergebene Fehlermeldung aus und beende das Programm,
    sofern ein Code ungleich None übergeben wird; andernfalls
    wird der Fehlerzähler erhöht
    """
    global ERRORS
    print >> stderr, _PROGNAME+'E', text
    if code is not None:
        exit(code or 1)
    ERRORS += 1
error = err

def fatal(text=None,
          code=None,
          tell=True,
          count=None,
          help=None):
    u"""
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

    help -- wenn übergeben, ein Hinweis auf die Hilfe
    """
    global ERRORS
    if count is None:
        count = False # bool(text)
    if count:
        ERRORS += 1
    if tell is None: # Automatik
        tell = not text or not count

    if text is not None:
        print >> stderr, _PROGNAME+'!', text
    RC = code or ERRORS or RC_ERROR or 1
    if tell:
        if ERRORS:
            info('%d Fehler' % ERRORS, stderr)
        if WARNINGS and tell > 1:
            info('%d Warnung[en]' % WARNINGS, stderr)
    if help:
        info(help)
    if tell:
        info('Beende mit RC %d' % RC, stderr)
    exit(RC)

def errline(text=''):
    """
    gib eine (per Default leere) Zeile zur Standardfehlerausgabe aus

    text -- der auszugebende Text
    """
    print >> stderr, text

def progname(stripchar=None, stripext=True):
    u"""
    gib den Namen des Programms zurück, ohne Verzeichnisangaben und
    Extension
    """
    tmp = basename(argv[0])
    if stripext and tmp.endswith('.py'):
        tmp = tmp[:-3]
    if stripchar:
        tmp = tmp.rstrip(stripchar)
    return tmp

def check_errors(text=None,
                 code=None):
    u"""
    ggf. zu fatal() durchgereichte Argumente:

    text -- als help-Argument durchgereicht, ein Hinweis
            auf die Hilfe (unterdrücken durch '')
    """
    if text is None:
        text = u"Aufruf mit -h oder --help für Hilfe"
    if ERRORS:
        fatal(code=code, tell=True, count=False, help=text)

def prompt(txt):
    u"""
    vorläufige Version; noch hartcodierte Antwortmöglichkeiten
    (yes/ja vs. no/nein), und noch kein yes/no/all/none/abort
    """
    idx = 0
    txt += ' (y/n) '
    txt2 = 'Bitte mit yes/ja oder no/nein antworten! '
    try:
        while True:
            try:
                answer = raw_input(idx and txt2 or txt)
            except AssertionError, e: # der isses nicht...
                print >> stderr, idx and txt2 or txt,
                answer = raw_input(': ')
            except EOFError:
                warn('stdin is redirected')
                return 0
            answer = answer.strip().lower()
            if not answer:
                idx = 1
                continue
            if 'yes'.startswith(answer):
                return 1
            elif 'ja'.startswith(answer):
                return 1
            elif 'no'.startswith(answer):
                return 0
            elif 'nein'.startswith(answer):
                return 0
            idx = (idx + 1) % 5
    finally:
        print

set_progname(progname())

try:
    from gettext import gettext as _
except ImportError:
    def _(message):
        return message

# direkter Aufruf auf Kommandozeile (nicht ausgeführt bei Import):
if __name__ == '__main__':
    import thebops.modinfo
    thebops.modinfo.main(version=VERSION)
