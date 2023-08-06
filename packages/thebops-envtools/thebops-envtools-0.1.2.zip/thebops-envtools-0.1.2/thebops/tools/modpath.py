#!/usr/bin/env python
# -*- coding: latin1 -*- vim: ts=8 sts=4 et si sw=4 
u"""
_modpath.py (aufzurufen durch modpath.cmd): Pfadvariablen ändern
"""
__version__ = (1,
               2, # --update-vars (noch ohne -v)
               2, # normpath-Verwendung beim Einfügen
               'rev-%s' % '$Rev: 915 $'[6:-2],
               )
u"""
TODO:
 - --update-vars sollte mehrere Pfadvariablen verwursten können,
   die von der-/denselben Variablen abhängen; dann aber ohne -i/-a/-r;
   auch --pypath usw. müssen dann auf append_const umgestellt werden
 - ebd.: Modularisierung
 - ebd.: Info darüber, was passiert
 - ebd.: -c (bisher nur ungeprüfte Übernahme der Variablenwerte)
 - Option --refresh o.ä., um unaufgelöste Variablenreferenzen auszuwerten,
   auch wenn sonst nichts zu tun ist
 - Verwendung von Sets
"""

from sys import argv, exit, stderr, exc_info
from os.path import sep, pathsep, curdir, pardir
from os.path import isdir, split, normpath, normcase, abspath
from thebops.errors import err, check_errors, progname
import os

try:
    from thebops.enhopa import OptionParser, OptionGroup
except:
    from optparse import OptionParser, OptionGroup

WARNINGS = 0
def warn(txt):
    global WARNINGS
    from sys import stderr
    print >> stderr, 'W modpath:', txt
    WARNINGS += 1

def detect_family():
    from sys import platform
    if platform in ('win32',  # realer Wert; angenommene:
                    'os2', 'dos', 'win', 'win16', 'win64'):
        return 'dos'
    elif platform in ('linux', 'linux2', 'cygwin'):
        return 'linux'
    else:
        warn('Unbekannte Plattform: '+platform)

family = detect_family()# or 'linux'
prog = split(argv[0])[1]
VERSION = '%s %s' % (prog, '.'.join(map(str, __version__)))
descr = (u'%(prog)s nimmt Änderungen in der übergebenen Umgebungsvariablen vor '
         u'und schreibt einen entsprechenden Befehl zur Standardausgabe'
         ) % locals()
if family == 'linux':
    usage = "`%prog [options]` | --help"
    descr += (u'; um diesen auszuführen, das Kommando in '
              u'Backticks einschließen.'
              u' Für die Bash sollte z. B. folgendes funktionieren: '
              'alias modpath `\'modpath$.py\' "$*"`')
else:
    from os.path import splitext
    prog = splitext(prog.replace('$', ''))[0]
    usage = "%(prog)s [options] | --help" % locals()
    descr += (u'. Da Python-Programme die Umgebung der aufrufenden Shell '
              u'nicht direkt ändern können, '
              u'erfolgt der Aufruf über die Batch-Datei %(prog)s.bat.'
              ) % locals()

parser=OptionParser(usage=usage,
                    version=VERSION)
parser.set_description(descr)
parser.add_option('--verbose', '-v',
                  action='count',
                  default=1,
                  help=_('be verbose (-vv: even more verbose)'))
parser.add_option('--quiet', '-q',
                  action='store_const',
                  const=0,
                  dest='verbose',
                  help=u'alle nicht unbedingt nötigen Ausgaben ausschalten')
parser.add_option('--debug', '-D',
                  action='store_true',
                  help=u'Debugging-Modus, pdb.set_trace() (für Entwickler)'
                  )

metaverz = pathsep.join(('BIN1[',
                         'V2]'
                         ))
group_ = OptionGroup(parser, 'Operationen')
group_.add_option('--insert', '-i',
                  action='store',
                  metavar=metaverz,
                  help=u'vorn einzufügende Einträge. Zur Sicherstellung, '
                  u'daß ein schon weiter hinten vorhandener Eintrag vorge'
                  u'zogen wird, zusätzlich --move und ggf. --unique angeben')
group_.add_option('--append', '-a',
                  action='store',
                  metavar=metaverz,
                  help=u'hinten (jedenfalls aber nicht ganz vorn) anzufü'
                  u'gende Einträge; um einen vorhandenen Eintrag nach hinten'
                  u' zu kopieren, --move angeben sowie, um ihn zu '
                  u'verschieben, zusätzlich --unique')
group_.add_option('--remove', '-r',
                  action='store',
                  metavar=metaverz,
                  help=u'zu löschende Einträge; wird zuerst ausgeführt. '
                  'Siehe auch --unique')
group_.add_option('--update-vars',
                  dest='update_vars',
                  action="append",
                  metavar='ENVVAR=NeuerWert[%s...]' % ',',
                  default=[],
                  help='Variable(n) aktualisieren, deren Wert im fraglichen '
                  u'PATH vorkommt, und die entsprechenden Einträge an Ort '
                  u'und Stelle ändern.'
                  ' TODO: Verarbeitung mehrerer Pfad-'
                  'Variablen (dann aber ohne -i/-a/-r!)')
parser.add_option_group(group_)

group_ = OptionGroup(parser, 'Auswahl der Variablen')
group_.add_option('--varname',
                  action='store',
                  metavar='PATH',
                  help=u'Name der zu ändernden Variablen,'
                  ' z. B. PATH (Standardwert) oder PATHEXT')
group_.add_option('--path',
                  action='store_const',
                  dest='varname',
                  const='PATH',
                  help=u'Abk. für --varname=PATH')
group_.add_option('--pypath',
                  action='store_const',
                  dest='varname',
                  const='PYTHONPATH',
                  help=u'Abk. für --varname=PYTHONPATH')
group_.add_option('--pathext',
                  action='store_const',
                  dest='varname',
                  const='PATHEXT',
                  help=u'Abk. für --varname=PATHEXT')
group_.add_option('--classpath',
                  action='store_const',
                  dest='varname',
                  const='CLASSPATH',
                  help=u'Abk. für --varname=CLASSPATH')
group_.add_option('--ldlib',
                  action='store_const',
                  dest='varname',
                  const='LD_LIBRARY_PATH',
                  help=u'Abk. für --varname=LD_LIBRARY_PATH')
parser.add_option_group(group_)

group_ = OptionGroup(parser, u'Ausführungsoptionen')
group_.add_option('--unique', '-1',
                  '-u',
                  action='count',
                  help=u'Doppelte Einträge eliminieren. Mit --append: '
                  u'wenn nicht auch --move angegeben wird, bleibt stets '
                  'der erste vorgefundene Eintrag erhalten'
                  '; -uu'
                  ' (NOCH NICHT IMPLEMENTIERT)'
                  u': auch vorhandene Mehrfacheinträge entfernen')
group_.add_option('--move', '-m',
                  action='store_true',
                  help=u'Schon vorhandene Einträge entsprechend kopieren '
                  'bzw. (mit --unique) verschieben '
                  '(--insert: nach vorn, --append: nach hinten). Zu beachten'
                  ' bei Kombination von --append und --unique, aber ohne --move:')
group_.add_option('--force', '-f',
                  action='count',
                  default=1,
                  help=u'Kein Fehler, wenn Umgebungsvariable nicht vorhanden'
                  '; default')
group_.add_option('--fail',
                  action='store_const',
                  const=0,
                  dest='force',
                  help=u'Abbruch, wenn Umgebungsvariable nicht vorhanden; '
                  'negiert --force')
group_.add_option('--check-dirs', '-c', # -> check_dirs
                  action='count',
                  help=u'Verzeichnisse auf Existenz prüfen: '
                  u'-c: Warnung, wenn nicht vorhandene hinzugefügt werden; '
                  u'-cc: nur hinzufügen wenn vorhanden, sowie vorhandene Einträge prüfen; '
                  '-ccc: nicht vorhandene automatisch entfernen')
group_.add_option('--expand-dirs', '-e', # -> check_dirs
                  action='count',
                  help=u'Verzeichnisnamen expandieren'
                  ' (NOCH NICHT IMPLEMENTIERT)'
                  u': -c: hinzugefügte expandieren; '
                  u'-cc: auch vorhandene expandieren; '
                  u'-ccc: auch Argumente für --remove expandieren'
                  )
parser.add_option_group(group_)

group_ = OptionGroup(parser, u'Konfiguration')
group_.add_option('--command',
                  action='store',
                  choices=('none', 'set', 'export'),
                  help=u'zu verwendendes Kommando; Vorgabewert abhängig vom '
                  'Betriebssystem (DOS/Windows usw.: set; '
                  'Linux: Zuweisung ohne "export")')
group_.add_option('--comment',
                  action='store',
                  choices=('rem', 'hash'),
                  help=u'zu verwendendes Kommentarpräfix; '
                  u'Vorgabewert abhängig vom '
                  'Betriebssystem (DOS/Windows usw.: @rem; Linux: hash (#)')
group_.add_option('--dos',
                  action='store_const',
                  const='dos',
                  dest='sys_family',
                  help=u'verwende Konventionen der DOS-Familie incl. Windows '
                  'und OS/2 (Kommando, Kommentar)')
group_.add_option('--linux',
                  action='store_const',
                  const='linux',
                  dest='sys_family',
                  help=u'verwende Konventionen der *x-Familie (Linux, Unixe)')

parser.add_option_group(group_)

try:
    parser.set_collecting_group('Allerweltsoptionen')
except AttributeError:
    pass

(option, args) = parser.parse_args()

if option.varname is None:
    option.varname = 'PATH'

if option.verbose > 1:
    INFO_PREFIX = 'i modpath('+option.varname+')'
else:
    INFO_PREFIX = 'i modpath'

def info(txt):
    from sys import stderr
    print >> stderr, INFO_PREFIX, txt

def getOriginalVarname(k, v):
    """
    Ermittelt den Variablennamen so, wie er in der Umgebung steht
    """
    from os import environ
    keys = environ.keys()
    if k in keys:
        return k
    uk=k.upper()
    for ek in keys:
        if ek.upper() == uk and environ[ek] == v:
            return ek
    raise RuntimeError('getOriginalVarname(%r, %r)' % (k, v))

if option.debug:
    import pdb
    pdb.set_trace()

USEDVARS={} # Namen verwendeter Variablen, normcase
if option.update_vars:
    OLDVALS_LIST=[] # Liste alter Werte, normcase
    OLD2VARNAME={}  # alter Wert (normcase) -> Variable (normcase)
    OLD2NEW={}      # alter Wert (normcase) -> neuer Wert
    VAR2NEW={}      # Variable (normcase) -> neuer Wert
    VARSNOTFOUND={} # Variable (normcase) -> Variable
    for raw1 in option.update_vars:
        for raw2 in raw1.split(','):
            if not '=' in raw2:
                err('%s: VAR=Wert erwartet' % raw2)
            else:
                head, tail=raw2.split('=', 1)
                nhead=normcase(head)
                if not tail:
                    err('%s: Leerer Wert ([noch?] nicht erlaubt)')
                elif pathsep in tail:
                    err('%s: Pfadseparator %s in Wert nicht erlaubt' %
                        (tail, pathsep))
                    tail=None
                if not head:
                    err('%s: Leerer Variablenname' % raw2)
                elif nhead in USEDVARS:
                    err('%s: Variable %s ist doppelt' % (raw2, head))
                    continue
                else:
                    if '%' in head:
                        warn('Prozentzeichen (%%) in Variablennamen (%s)'
                             ' ist kritisch' % head)
                    try:
                        oldval=os.environ[head]
                        oriname=getOriginalVarname(head, oldval)
                        if pathsep in oldval:
                            err('Alter Wert von %s (%s) enthaelt Pfadtrenner'
                                ' (%s)' % (oriname, oldval, pathsep))
                            tail=None
                    except KeyError:
                        err('Umgebungsvariable %r nicht gefunden' % head)
                        tail=None
                if head and tail: #xxx
                    oval=normcase(oldval)
                    OLDVALS_LIST.append(oval)
                    noriname=normcase(oriname)
                    OLD2VARNAME[oval]=noriname
                    VAR2NEW[noriname]=tail
                    OLD2NEW[oval]=tail
                    USEDVARS[noriname]=oriname
                    VARSNOTFOUND[noriname]=oriname

# zur Auswahl der Filterfunktionen:
def opt_warn():
    return option.check_dirs == 1

def opt_remove():
    return option.check_dirs > 2

def opt_skip():
    return option.check_dirs > 1

_tmp_mask = []
if USEDVARS:
    _tmp_mask.append('%(replaced)d ersetzt')
if option.remove:
    _tmp_mask.append('%(removed)d entfernt')
if option.insert:
    _tmp_mask.append('%(inserted)d eingefuegt')
if option.append:
    _tmp_mask.append('%(appended)d angehaengt')
if option.unique:
    _tmp_mask.append('%(duplicates)s Duplikate entfernt')

if not (_tmp_mask or opt_remove() or USEDVARS):
    if option.update_vars and not USEDVARS:
        info('Nichts zu tun!')
    else:
        err('Nichts zu tun!')

summary_mask = '%(prog)s(%(varname)s): ' + ', '.join(_tmp_mask)
del _tmp_mask

if option.sys_family is None:
    option.sys_family = family

if option.command is None:
    if option.sys_family == 'dos':
        option.command = 'set'
    elif option.sys_family == 'linux':
        option.command = ''
    else:
        err('Kommando nicht bekannt (set, export, ...?)')
elif option.command == 'none':
    option.command = ''
if option.command:
    option.command += ' '

if option.comment is None:
    if option.sys_family == 'dos':
        option.comment = '@rem '
    elif option.sys_family == 'linux':
        option.comment = '# '
    else:
        err('Kommentar-Präfix nicht bekannt (@rem, hash (#)...?)')
elif option.comment == 'hash':
    option.comment = '# '

# bei fehlerhaften Argumenten:
if args:
    err('Argumente sind nur als Optionen erlaubt')

check_errors(usage)

def npath(p):
    from os.path import normpath, normcase
    return p and normpath(normcase(p)) or ''

def appsep(v):
    u"""
    Verzeichnistrenner anfügen, wenn nicht vorhanden
    """
    from os.path import sep
    if not v:
        return v
    elif v.endswith(sep):
        return v
    else:
        return v+sep

# Filter-Funktionen:

def non_existent_skip(v):
    u"""
    wenn Verzeichnis nicht vorhanden, False zurückgeben
    """
    if not v:
        if option.verbose > 1:
            warn('leerer Eintrag: %r' %v)
        return False
    if isdir(v):
        return True
    if option.verbose:
        warn('nicht gefunden: '+appsep(v))
    return False

def non_existent_info(v):
    u"""
    wenn Verzeichnis nicht vorhanden, False zurückgeben
    """
    if not v:
        if option.verbose > 1:
            info('leerer Eintrag: %r' %v)
        return False
    if isdir(v):
        return True
    if option.verbose:
        info('nicht gefunden: '+appsep(v))
    return False

def non_existent_warn(v):
    u"""
    wenn Verzeichnis nicht vorhanden, warnen;
    (fast) immer True zurückgeben
    """
    if not v:
        if option.verbose > 1:
            warn('leerer Eintrag: %r' %v)
        return False
    if not isdir(v):
        warn('nicht gefunden: '+appsep(v))
    return True

def empty_skip_silently(v):
    return v and True or False

def empty_skip_verbosely(v):
    if not v:
        warn('leerer Eintrag: %r' %v)
        return False
    else:
        return True

def duplicate_skip_silently(v):
    global filtered
    np = npath(v)
    if npath(v) in filtered:
        return False
    else:
        filtered.append(np)
        return True

def duplicate_skip_verbosely(v):
    global filtered, duplicates
    np = npath(v)
    if np in filtered:
        info('Duplikat: '+v)
        duplicates += 1
        return False
    else:
        filtered.append(np)
        duplicates += 1
        return True

if option.check_dirs:
    if opt_remove():
        f_new = non_existent_skip
        f_old = non_existent_info
    elif opt_skip():
        f_new = non_existent_skip
        f_old = non_existent_warn
    elif opt_warn():
        f_new = non_existent_warn
        f_old = lambda v: True
    else:
        raise AssertionError('option.check_dirs ist %r, aber opt_warn()...'
                             ' schlagen nicht an!' % option.check_dirs)
elif option.verbose > 1:
    f_new = empty_skip_verbosely
    f_old = f_new
else:
    f_new = empty_skip_silently
    f_old = f_new

if option.insert:
    INSERT = filter(f_new, option.insert.split(pathsep))
else:
    INSERT = ()
INSERT_N = map(npath, INSERT)

if option.append:
    APPEND = filter(f_new, option.append.split(pathsep))
else:
    APPEND = ()
APPEND_N = map(npath, APPEND)

if option.remove:
    REMOVE = option.remove.split(pathsep)
else:
    REMOVE = ()
REMOVE_N = map(npath, REMOVE)

try:
    OLDVAL = os.environ[option.varname]
    OLDVAL = filter(f_old, OLDVAL.split(pathsep))
except KeyError, e:
    if option.force:
        OLDVAL = []
        if option.verbose:
            warn('Variable %s war noch nicht vorhanden!' % option.varname)
    else:
        err('Variable %s ist noch nicht vorhanden!' % option.varname)

# zuerst entfernen:
removed =  0
if REMOVE:
    indexes = []
    idx = 0
    for dir in OLDVAL:
        if npath(dir) in REMOVE_N:
            indexes.append(idx)
        idx += 1
    removed = len(indexes)
    if indexes:
        indexes.reverse()
        for idx in indexes:
            if option.verbose > 1:
                info('entferne: '+ OLDVAL[idx])
            del OLDVAL[idx]
OLDVAL_N = map(npath, OLDVAL)

# jetzt ersetzen; beim Hinzufügen könnten sich Duplikate ergeben,
# die ggf. (--unique) entfernt werden sollen:
replaced=0
if USEDVARS:
    for di in range(len(OLDVAL)):
        dir = abspath(OLDVAL[di])
        ndir = normcase(dir) # abspath impliziert normpath
        # print '--------------------------'
        # print 'ndir:', ndir
        di_done=0
        for oval in OLDVALS_LIST: # enthält normcase-Werte   xxx
            # print 'oval:', oval
            if oval == ndir:
                # print ' oval=ndir'
                OLDVAL[di] = OLD2NEW[oval]
                replaced += 1
                di_done=1
                uvar=OLD2VARNAME[oval]
                break
            elif ndir.startswith(oval):
                # print ' ndir beginnt mit oval'
                leno=len(oval)
                if ndir[leno] == sep:
                    OLDVAL[di] = OLD2NEW[oval]+ndir[leno:]
                    replaced += 1
                    di_done=1
                    uvar=OLD2VARNAME[oval]
                    break
                else:
                    warn('%r ist kein Verzeichnistrenner' % oval[leno])
        if not di_done:
            for uvar in USEDVARS:
                if ndir.startswith('%'+uvar+'%'):
                    OLDVAL[di] = VAR2VAL[uvar]+dir.split('%', 2)[-1]
                    di_done=1
                    break
        if di_done:
            try:
                del VARSNOTFOUND[uvar]
            except KeyError:
                pass
    if VARSNOTFOUND: # in den Werten des PATH
        liz=VARSNOTFOUND.keys()
        lv=len(liz)
        liz.sort()
        warn('%d Variable%s nicht gefunden (%s)'
             % (lv,
                (lv > 1) and 'n' or '',
                ', '.join(liz)))

if replaced:
    OLDVAL_N = map(npath, OLDVAL)



ADDED_N = []

inserted = 0
if INSERT:
    for dir in INSERT:
        dn = npath(dir)
        if dn in ADDED_N:
            pass
        elif option.move:
            if dn in OLDVAL_N[:inserted+1]:
                if option.verbose > 1:
                    info(u'schon da: '+dir)
            elif dn in OLDVAL_N: # ja, aber zu weit hinten...
                OLDVAL.insert(inserted, normpath(dir))
                if option.verbose > 1:
                    info(u'füge ein: '+dir)
                inserted += 1
                ADDED_N.append(dn)

        elif dn in OLDVAL_N:
            if option.verbose > 1:
                info(u'schon da: '+dir)
        else:
            OLDVAL.insert(inserted, normpath(dir))
            if option.verbose > 1:
                info(u'füge ein: '+dir)
            inserted += 1
            ADDED_N.append(dn)


if option.unique:
    duplicates = 0
    dupfunc = option.verbose \
                and duplicate_skip_verbosely \
                or  duplicate_skip_silently

appended = 0
if APPEND:
    if option.move:
        filtered=[]
    for dir in APPEND:
        dn = npath(dir)
        if dn in ADDED_N:
            pass
        elif option.move:
            if dn in OLDVAL_N[-len(APPEND):]:
                if option.verbose > 1:
                    info(u'schon da: '+dir)
            elif dn in OLDVAL_N: # ja, aber zu weit vorn...
                if option.unique:
                    filtered.append(dn)
                    OLDVAL = filter(dupfunc, OLDVAL)
                OLDVAL.append(normpath(dir))
                if option.verbose > 1:
                    info(u'hänge an: '+normpath(dir))
                appended += 1
                ADDED_N.append(dn)
        elif dn in OLDVAL_N:
            if option.verbose > 1:
                info(u'schon da: '+dir)
        else:
            OLDVAL.append(normpath(dir))
            if option.verbose > 1:
                info(u'hänge an: '+normpath(dir))
            appended += 1
            ADDED_N.append(dn)

if option.unique:
    filtered=[]
    idx = 0
    while OLDVAL[idx:]:
        dir = OLDVAL[idx]
        dn = npath(dir)
        if dn in filtered:
            if option.verbose > 1:
                info(u'Duplikat: '+dir)
            del OLDVAL[idx]
            duplicates += 1
        else:
            filtered.append(dn)
            idx += 1

varname = option.varname
print option.comment+(summary_mask % locals())
for uvar in USEDVARS:
    print option.command+USEDVARS[uvar]+'='+VAR2NEW[uvar]
print option.command+option.varname+'='+pathsep.join(map(normpath,
                                                 filter(None, OLDVAL)))

