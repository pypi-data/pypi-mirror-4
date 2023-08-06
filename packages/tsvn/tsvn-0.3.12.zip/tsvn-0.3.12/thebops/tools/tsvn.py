#!/usr/bin/env python
# -*- coding: utf-8 -*- vim: ts=8 sts=4 sw=4 si et tw=79
''"""\
Commandline interface to TortoiseSVN

As similar as possible to svn; the given arguments are transformed accordingly
(and relative file specs converted to absolute ones, for example).
'tsvn help' gives a list of available commands.\
"""

__author__ = "Tobias Herp <tobias.herp@gmx.net>"
VERSION = (0,
           3, # sys.argv-Filterung
           12, # i18n preparations
           'rev-%s' % '$Rev: 946 $'[6:-2],
           )
__version__ = '.'.join(map(str, VERSION))
from sys import argv
from os import getcwd
from os.path import isdir, isfile, exists, abspath, normpath
from subprocess import Popen

# --- eigene Module:
from thebops.errors import check_errors, err, warn, info, RC_HELP
from thebops.shtools import CommandError, NoCommandError, \
        CommandNotImplementedError, CommandUnknownError, \
        ExplainedValueError, \
        mapfunc, replaced_switches
from thebops.likeix import find_tsvn, get_1st
from thebops.rexxbi import overlay
from thebops.opo import add_version_option
from thebops.anyos import quoted_seq


try:
    from thebops.enhopa import OptionParser, OptionGroup, \
            OptionError, OptionValueError, OptionConflictError
except ImportError:
    from optparse import OptionParser, OptionGroup, \
            OptionError, OptionValueError, OptionConflictError

## ---------------------------------------------------------- Daten [[
SVN_COMMANDS = {
   'add': None,
   'blame': ('praise', 'annotate', 'ann'),
   'cat': None,
   'changelist': ('cl',),
   'checkout': ('co',),
   'cleanup': None,
   'commit': ('ci',),
   'copy': ('cp',),
   'delete': ('del', 'remove', 'rm'),
   'diff': ('di',),
   'export': None,
   'help': ('?', 'h'),
   'import': None,
   'info': None,
   'list': ('ls',),
   'lock': None,
   'log': None,
   'merge': None,
   'mergeinfo': None,
   'mkdir': None,
   'move': ('mv', 'rename', 'ren'),
   'propdel': ('pdel', 'pd'),
   'propedit': ('pedit', 'pe'),
   'propget': ('pget', 'pg'),
   'proplist': ('plist', 'pl'),
   'propset': ('pset', 'ps'),
   'resolve': None,
   'resolved': None,
   'revert': None,
   'status': ('stat', 'st'),
   'switch': ('sw',),
   'unlock': None,
   'update': ('up',),
    }
# zusätzliche Kommandos:
TSVN_ONLY = {
    'about': None,
    'ignore': None,
    'conflictedit': ('ce', 'conflicteditor'),
    'browse': ('explore', 'e'),
    'pea': ('propeditall',),
    }
SVN_COMMANDS.update(TSVN_ONLY)
SVN_ALIASES = {}
for k, v in SVN_COMMANDS.items():
    if v is not None:
        for alias in v:
            SVN_ALIASES[alias] = k
    SVN_ALIASES[k] = k
SVN_ONLY = {
    'propdel': 'pea',
    'propget': 'pea',
    'proplist': 'pea',
    'propset': 'pea',
    'pd': 'pea',
    'pg': 'pea',
    'pl': 'pea',
    'ps': 'pea',
    'pdel': 'pea',
    'pget': 'pea',
    'plist': 'pea',
    'pset': 'pea',
    'changelist': None,
    'list': 'browse',
    'propedit': 'pea',
    }
## ---------------------------------------------------------- Daten ]]

try:
    _
except NameError:
    def dummy(s): return s
    _ = dummy

class SvnCommandOnly(CommandUnknownError):
    def __str__(self):
        cmd = self.cmd
        instead = SVN_ONLY[cmd]
        if instead is None:
            return _('There is no TortoiseSVN equivalent to the svn %s command'
                     ) % (cmd,
                          )
        else:
            return _('The best equivalent to the svn command %(cmd)s'
                     ' is perhaps %(instead)s'
                     ) % locals()


## ------------------------------------------------------ Baukasten [[
def common_options(p):
    r"""
    Allgemeine Subversion-Optionen, z. B. zum Zugriff auf das Repo,
    aber ohne die leicht varierenden und nicht generell unterstützten
    Revisionsangaben --revision (-r) und --change (-c)

    TortoiseSVN-spezifische Kandidaten:
    /closeonend:0-4
    /closeforlocal
    /configdir:"path\to\config\directory"
    """
    return

def extract_cmd(tup, parser):
    """
    Extrahiere das Kommando:

    >>> extract_cmd(('log', '--opt'), None)
    tsvn_log
    >>> extract_cmd(('help', 'log', '--opt'), None)
    tsvn_log
    """
    if not tup:
        raise NoCommandError()
    args = list(tup)
    cmd = None
    try:
        try:
            helpcmd = 0
            for raw in args[:2]:
                cmd = SVN_ALIASES[raw]
                if cmd != 'help' or helpcmd:
                    try:
                        return globals()['tsvn_%s' % cmd]
                    except KeyError:
                        raise CommandNotImplementedError(cmd,
                                SVN_COMMANDS[cmd])
                elif helpcmd:
                    return tsvn_help
                else:
                    helpcmd = 1
            if helpcmd:
                return tsvn_help
        except CommandNotImplementedError, e:
            if cmd in SVN_ONLY:
                err(str(e))
                raise SvnCommandOnly(cmd)
            else:
                raise
        except KeyError, e:
            raise CommandUnknownError(e.args[0])
    except SvnCommandOnly, e:
        info(str(e))
        return
    return parser.print_help

def parser_and_group(cmd, helptail=None):
    groupname = groupname4cmd(cmd)
    if helptail is None:
        helptail = _('[--options]')
    elif not helptail:
        helptail = None
    liz = ['%prog', cmd]
    if helptail is not None:
        liz.append(helptail)
    parser = OptionParser(usage=' '.join(liz),
                          add_help_option=0)
    group = OptionGroup(parser, groupname4cmd(cmd))
    return parser, group

def groupname4cmd(cmd):
    aliases = SVN_COMMANDS[cmd]
    if aliases is None:
        return _("Options for the %s command"
                 ) % cmd
    else:
        return _("Options for the %s command (%s)"
                 ) % (cmd, ', '.join(aliases))

def groupname4nonsvnoptions(cmd, a=0):
    aliases = SVN_COMMANDS[cmd]
    if (aliases is None) or a:
        return _("Functionality not in svn's %s command"
                 ) % cmd
    else:
        return _("Functionality not in svn's %s command (%s)"
                 ) % (cmd, ', '.join(aliases))

def groupname4missingsvnoptions(cmd, a=0):
    return _('svn %s options not supported by TortoiseSVN'
             ) % cmd

def _parse_opts(parser):
    o, a = parser.parse_args()
    if a and 'help'.startswith(a[0]):
        parser.print_help()
        raise SystemExit(RC_HELP)
    else:
        return o, list(a[1:])

def add_revision_options(parser,
                         including=0,
                         c_option=0,
                         single_r_like_c=0):
    """
    erstelle Optionen für --revision und --change

    including -- wenn 1, ist bei -rNN:MM die Revision MM mit eingeschlossen
    c_option  -- --change-Option erzeugen?
    single_r_like_c -- wenn 1, hat -rNN dieselbe Bedeutung wie -cNN
    """
    pass
    # return True
    #     (wenn implementiert, True zurückgeben)

def add_message_options(g, g2=None):
    """
    g -- parser or group
    g2 -- OptionGroup object; used to hide the --file option
    """
    g.add_option('--message', '-m',
                 metavar=_('TEXT'),
                 help=_('specify log message TEXT'))
    if g2 is not None:
        G = g2
    else:
        G = g
    G.add_option('--file', '-F',
                 metavar=_('FILE'),
                 help='read log message from FILE')

def add_diff_options(p, rev_args=True):
    """
    -x --ignore-space-change, -x -b: --> /ignorespaces
    -x --ignore-all-space, -x -w: --> /ignoreallspaces
    -x --ignore-eol-style: --> /ignoreeol

    Mö. eigene Abkürzung:
    --ignore=space-changes,[all-]spaces,eol[s,-style]

    --> cb_diff_extensions

    -rN:M: excludierendes oberes Ende (diff; auch blame?)
    /line: für :diff und :blame,
    nicht dokumentiert für :conflicteditor und :showcompare
    """
    if rev_args:
        p.add_option('--revision', '-r',
                     type='string',
                     action='callback',
                     callback=cb_rev_or_revs,
                     metavar=_('first[:last]'),
                     help=_('Revision(s) to compare'
                     '; symbolic names (BASE, HEAD ...) allowed'
                     ))
        p.add_option('--change', '-c',
                     action='callback',
                     metavar='REV',
                     callback=cb_change_as_revs,
                     type='int',
                     help=_('Revision of interest, numerical only'
                     '; -cREV equals -rREV-1:REV'))
    p.add_option('-x', '--extensions',
                 action='callback',
                 metavar='--option',
                 callback=cb_diff_extensions,
                 type='string',
                 help=_("For svn, an option passed on to the used diff "
                 "program; for compatibility implemented here as well, "
                 "featuring the values --ignore-space-change "
                 "(-b), --ignore-all-space (-w) and --ignore-eol-style"
                 ))

    extensions_mapper = mapfunc((
             # '--ignore-space-change', '-b':
             ('/ignorespaces', 'space', 'space-change'),
             # '--ignore-all-space', '-w':
             ('/ignoreallspaces', 'all-spaces'),
             # --ignore-eol-style:
             ('/ignoreeol', 'eol', 'eol-style', 'eols'),
            ),
            cls=str)
    if 1:\
    p.add_option('--ignore',
                 action='callback',
                 metavar=extensions_mapper.metavar(),
                 callback=cb_list,
                 type='string',
                 callback_kwargs={'f': extensions_mapper},
                 help=('alternative way to specify the'
                 ' known --extensions values'
                 ))

def find_tproc():
    """
    http://tortoisesvn.net/docs/nightly/TortoiseSVN_en/tsvn-automation.html
    http://tortoisesvn.net/docs/release/TortoiseSVN_en/tsvn-cli-main.html
    """
    return get_1st(find_tsvn)

def url_and_local(cmdlist, args,
              takes_files=None,
              takes_dirs=None,
              takes_special=None,
              takes_urls=None,
              default2cwd=1,
              skip_invalid=0):
    """
    Erst eine URL, dann etwas lokales

    cmdlist - die mit TortoiseSVN-Argumenten zu füllende Liste

    default2cwd - wenn True (default) und kein lokales (zweites) Argument
                  angegeben, verwende das aktuelle Arbeitsverzeichnis

    skip_invalid - wenn True, gib für fehlerhafte Argumente lediglich eine
                   Warnung aus; wenn False (default), wirf eine Exception

    takes_... - von local_args_only(); hier (noch?) nicht implementiert
    """
    handleinv = (skip_invalid
                 and handleinv_warn
                 or  handleinv_exception)
    first = 1
    url_found = 0
    local_found = 0
    theurl = None
    for a in args:
        if not url_found:
            if not '/' in a:
                handleinv(a, _("%s doesn't look like a URL"))
            cmdlist.append('/url:%s' % a)
            theurl = a
            url_found = 1
        elif not local_found:
            cmdlist.append('/path:%s' % abspath(a))
            local_found = 1
        else:
            handleinv(a, _('Surplus argument: %s'))
    if not url_found:
        # NOTE: the %s must not be omitted!
        handleinv('', _('No URL given!%s'))
        cmdlist.append('/path:%s' % getcwd())
    elif not local_found:
        liz = [s for s in theurl.split('/')
               if s]
        if liz:
            cmdlist.append('/path:%s' % abspath(liz[-1]))
        else:
            handleinv(theurl,
                      _("Can't extract a local resource from %s!"))


def handleinv_warn(a, msg):
    warn(msg % a)

def handleinv_exception(a, msg):
    raise ExplainedValueError(a, msg)

def local_args_only(cmdlist, args,
                    takes_files=None,
                    takes_dirs=None,
                    takes_special=None,
                    takes_urls=None,
                    default2cwd=1,
                    skip_invalid=0):
    """
    Verarbeite und überprüfe lokale Argumente

    Es wird nur ein TortoiseSVN-Argument (/path:)
    mit ggf. mehreren Pfaden erzeugt
    """
    handleinv = (skip_invalid
                 and handleinv_warn
                 or  handleinv_exception)
    plist = []
    MSGS = (_('"%s" is a directory'),
            _('"%s" is a file'),
            _('"%s" is neither a directory nor a file'),
            _('"%s" is not a local resource'),
            )
    for a in args:
        if isdir(a):
            a = normpath(a)
            if takes_dirs is None:
                warn(MSGS[0] % a)
            elif not takes_dirs:
                handleinv(a, MSGS[0])
            plist.append(abspath(a))
        elif isfile(a):
            if takes_files is None:
                warn(MSGS[1] % a)
            elif not takes_files:
                handleinv(a, MSGS[1])
            plist.append(abspath(a))
        elif exists(a):
            if takes_special is None:
                warn(MSGS[2] % a)
            elif not takes_special:
                handleinv(a, MSGS[2])
            plist.append(abspath(a))
        else:
            if takes_urls is None:
                warn(MSGS[3] % a)
            elif not takes_urls:
                handleinv(a, MSGS[3])
            plist.append(abspath(a))
    if not plist and default2cwd:
        plist.append(getcwd())
    if plist:
        cmdlist.append('/path:%s' % '*'.join(plist))

def TSVN(args):
    cmd = ['start', '/b',
           'cmd', '/c',
           find_tproc()]
    cmd.extend(args)
    if 1:
        print ' '.join(list(quoted_seq(cmd))[4:])
    Popen(cmd, shell=1).wait()

def check_single_rev(val):
    if not val:
        raise OptionValueError(val, _('empty revision values not allowed'))
    try:
        return int(val)
    except ValueError, e:
        if val.startswith('{') and val.endswith('}'):
            return val
        val = val.upper()
        if val in ('HEAD', 'BASE', 'COMMITTED', 'PREV'):
            return val
        raise OptionValueError(_('%s: not an allowed revision spec.'
                                 ) % val)

def cb_flags(option, opt_str, value, parser, f):
    """
    option -- ein Optionsobjekt
    opt_str -- z. B. '--search'
    value -- ein String, z. B. 'revs,msg'
    parser -- der Parser
    f -- eine Funktion, die Zeichenketten auf Zahlen (2**n) mappt
    """
    val = value.strip().lower()
    val = getattr(parser.values, option.dest, 0)
    if val is None:
        val = 0
    try:
        for s in value.split(','):
            if s:
                val |= f(s)
    except KeyError, e:
        raise OptionValueError(e.args[0])
    setattr(parser.values, option.dest, val)

def cb_list(option, opt_str, value, parser, f):
    """
    option -- ein Optionsobjekt
    opt_str -- z. B. '--search'
    value -- ein String, z. B. 'revs,msg'
    parser -- der Parser
    f -- eine Funktion, die Zeichenketten auf einen Normalwert mappt
    """
    val = value.strip().lower()
    liz = getattr(parser.values, option.dest, None)
    new = liz is None
    if new:
        liz = []
    try:
        for s in value.split(','):
            if s:
                liz.append(f(s))
    except KeyError, e:
        raise OptionValueError(e.args[0])
    if new:
        setattr(parser.values, option.dest, liz)

def cb_rev_or_revs(option, opt_str, value, parser,
                   otherdest='change',
                   ifother='conflict',
                   revspecs=2,
                   diffmode=0,
                   otheropt=('-c', '--change')):
    """
    option -- ein Optionsobjekt
    opt_str -- z. B. '--search'
    value -- ein String, z. B. 'revs,msg'
    parser -- der Parser
    """
    otherval = getattr(parser.values, otherdest, None)
    if otherval is not None:    # klappt
        raise OptionConflictError(option,
                                  'Konflikt mit %s' % otheropt[0])
    liz = map(check_single_rev, value.split(':'))
    if not liz:
        raise OptionValueError(value, 'Leere Revisionsangabe')
    elif len(liz) > revspecs:
        raise OptionValueError(value, 'zu viele Revisionsangaben')
    elif len(liz) == 1:
        rev = liz[0]
        if diffmode:
            if isinstance(rev, int):
                liz.insert(rev-1, 0)
            else:
                import pdb; pdb.set_trace()
        else:
            liz.append(rev)
    setattr(parser.values, option.dest, liz)

def cb_change_as_revs(option, opt_str, value, parser,
                      otherdest='revision',
                      ifother='conflict',
                      otheropt=('-r', '--revision')):
    """
    option -- ein Optionsobjekt
    opt_str -- z. B. '--search'
    value -- ein String, z. B. 'revs,msg'
    parser -- der Parser
    """
    otherval = getattr(parser.values, otherdest, None)
    if otherval is not None:    # klappt
        raise OptionConflictError(option,
                                  'Konflikt mit %s' % otheropt[0])
    value = int(value)
    setattr(parser.values, option.dest, value)

def cb_diff_extensions(option, opt_str, value, parser):
    """
    Noch nicht implementiert;
    siehe -> add_diff_options
    """
    pass

def _tsvn_x():
    """
    implementiert das Kommando x
    (Kopiervorlage)
    """
    p, g = parser_and_group('x', _('[--options]'))
    p.add_option_group(g)
    common_options(p)
    o, a = _parse_opts(p)
    cmd = ['/command:x']
    TSVN(cmd)

## ------------------------------------------------------ Baukasten ]]

## --------------------------------------- Implementierte Kommandos [[

def tsvn_about():
    ''"""\
    show the about dialog
    """
    p, g = parser_and_group('about', '')
    p.set_description(_(
            "Opens the About dialog (version information) of TortoiseSVN "
            "which allows to check for updates."
            ))
    o, a = _parse_opts(p)
    cmd = ['/command:about']
    TSVN(cmd)

def tsvn_blame():
    ''"""\
    Show the content of specified files or URLs
    with revision and author information in-line.
    """
    p, g = parser_and_group('blame', _('[directory|URL]'))
    add_diff_options(g)
    p.add_option_group(g)
    common_options(p)
    o, a = _parse_opts(p)
    cmd = ['/command:blame']
    if o.ignore is not None:
        cmd.extend(o.ignore)
    local_args_only(cmd, a,
                    takes_dirs=1,
                    takes_urls=1,
                    default2cwd=1)
    if o.revision:
        revs = tuple(o.revision)
    elif o.change:
        revs = (o.change-1, o.change)
    if revs:
        cmd.extend(('/startrev:%s' % revs[0],
                    '/endrev:%s'   % revs[1]))
    TSVN(cmd)

def tsvn_browse():
    ''"""\
    browse the repository
    """
    p, g = parser_and_group('browse', _('[directory|URL]'))
    g.add_option('--revision', '-r',
                 type='string',
                 action='callback',
                 callback=cb_rev_or_revs,
                 callback_kwargs={'revspecs': 1},
                 metavar='REV',
                 help=_('Revision, default: HEAD'
                 ))
    p.add_option_group(g)
    common_options(p)
    o, a = _parse_opts(p)
    cmd = ['/command:repobrowser']
    local_args_only(cmd, a,
                    takes_dirs=1,
                    # takes_files=1,
                    default2cwd=1)
    if o.revision:
        revs = tuple(o.revision)
        cmd.append('/rev:%s' % revs[0])
    TSVN(cmd)

def tsvn_checkout():
    ''"""\
    Check out a working copy from a repository.
    """
    p, g = parser_and_group('checkout', _('<URL> [directory]'))
    g.add_option('--revision', '-r',
                 type='string',
                 action='callback',
                 callback=cb_rev_or_revs,
                 callback_kwargs={'revspecs': 1},
                 metavar='REV',
                 help=_('Revision, default: HEAD'
                 ))
    p.add_option_group(g)
    common_options(p)
    o, a = _parse_opts(p)
    cmd = ['/command:checkout']
    url_and_local(cmd, a,
                  default2cwd=1)
    if o.revision:
        cmd.append('/revision:%s' % o.revision)
    TSVN(cmd)

def tsvn_diff():
    ''"""\
    Display the differences between two revisions or paths.
    """
    # Soll einmal (je nach (Konflikt-) Status) den Differenz-
    # oder Konflikteditor aufrufen (:conflicteditor).
    '''
    Bisher nur implementiert: lokale Differenz ohne Angabe von Revisionen

    Die Frage ist, ob alle Varianten des diff-Befehls vom selben
    TortoiseSVN-Kommando abgebildet werden können (den Konflikteditor
    gibt es im Standard-svn nicht zu expliziten Aufruf oder im Rahmen des
    diff-Befehls).

    Varianten von svn diff:
    1a [-cM | -rN[:M]] {lokale Pfade}
        Vorgabe: -rBASE, aktuelles Verzeichnis
        :diff /path (nur ein Argument? Auch URL möglich?)
              /startrev:, /endrev:, /pegrevision:,
              /blame, /line:
    1b {-cM | -rN[:M]} {URLs}
        wenn -r ohne M, ist die Vorgabe für M "HEAD"
    2a [-rN[:M]] --old=OLD-TARGET[@OLD-REV] --new=NEW-TARGET[@NEW-REV]
    2b [-rN[:M]]       OLD-TARGET[@OLD-REV]       NEW-TARGET[@NEW-REV]
        Wenn -rN[:M] angegeben wird, gibt N den Vorgabewert für OLD-REV an
        und M den Vorgabewert für NEW-REV
        Vermutung: :showcompare, Pflichtoptionen: /url1+2, /revision1+2

    Frage: Wie wird zwischen 1b mit -rN[:M] und 2 URLs einerseits und 2b
    unterschieden?!
    '''
    p, g = parser_and_group('diff', _('[--options]'))
    add_diff_options(g)
    p.add_option_group(g)
    common_options(p)
    o, a = _parse_opts(p)
    cmd = ['/command:diff']
    if o.ignore is not None:
        cmd.extend(o.ignore)
    local_args_only(cmd, a,
                    default2cwd=1,
                    takes_files=1)
    TSVN(cmd)

def tsvn_conflictedit():
    ''"""\
    call the conflicts editor
    """
    """
    siehe tsvn_diff; dieses soll mittelfristig
    im Konfliktfall automatisch den Konflikt-
    anstelle des Differenzeneditors starten.
    """
    p, g = parser_and_group('conflictedit', _('[--options]'))
    add_diff_options(g, rev_args=False)
    p.add_option_group(g)
    common_options(p)
    o, a = _parse_opts(p)
    cmd = ['/command:conflicteditor']
    if o.ignore is not None:
        cmd.extend(o.ignore)
    local_args_only(cmd, a,
                    default2cwd=1,
                    takes_files=1)
    TSVN(cmd)

def tsvn_commit():
    ''"""\
    Send changes from your working copy to the repository.
    """
    p, g = parser_and_group('commit', _('[--options]'))
    add_revision_options(g, including=0,
                         c_option=1)
    add_message_options(g, OptionGroup(p, 'hide --file option'))
    p.add_option_group(g)
    common_options(p)
    o, a = _parse_opts(p)
    cmd = ['/command:commit']
    if o.message:
        if o.file:
            err('Nur *entweder* --message *oder* --file ist erlaubt!')
        else:
            cmd.append('/logmsg:'+o.message)
    elif o.file:
        cmd.append('/logmsgfile:'+abspath(o.file))
    local_args_only(cmd, a,
                    default2cwd=1,
                    takes_files=1,
                    takes_dirs=1,
                    takes_urls=0)
    TSVN(cmd)

def tsvn_ignore():
    ''"""\
    Add the given resources to the ignore list
    """
    p, g = parser_and_group('ignore', _('{file|directory} [...]'))
    if add_revision_options(g, including=0,
                            c_option=0) or 0:
        p.add_option_group(g)
    common_options(p)
    o, a = _parse_opts(p)
    cmd = ['/command:ignore']
    local_args_only(cmd, a,
                    takes_dirs=1,
                    takes_files=1,
                    takes_urls=0,
                    default2cwd=0)
    TSVN(cmd)

def tsvn_pea():
    ''"""\
    Edit all properties ("propedit all").
    """
    p, g = parser_and_group('pea', _('{file|directory} [...]'))
    common_options(p)
    o, a = _parse_opts(p)
    cmd = ['/command:properties']
    local_args_only(cmd, a,
                    default2cwd=1,
                    takes_files=1,
                    takes_dirs=1)
    TSVN(cmd)

def x_tsvn_propedit():
    ''"""\
    Edit a property with an external editor.
    """
    p, g = parser_and_group('propedit', _('{file|directory} [...]'))
    p = OptionParser(usage='%prog propedit {--all'
                           # '|Prop.name'
                           '|<ignoriert!>'
                           '} {Datei|Verzeichnis|?}',
                     add_help_option=0)
    p.set_description(u'Der Attribut-Editor von TortoiseSVN ignoriert derzeit '
            '(Stand: TortoiseSVN v1.7.9) jegliche Angabe eines Attributnamens'
            ' (es kann also auch einfach ein Punkt angegeben werden, '
           u'gleichbedeutend mit --all, das allerdings unmißverständlich und '
           u'vor geänderter Interpretation sicher ist). '
            ' Das ist nicht schlimm, weil alle Attribute bequem interaktiv '
           u'bearbeitet werden können.  Diese Funktionalität '
            'hat keine Entsprechung in der svn-Kommandozeile: '
            'svn bearbeitet (liest, schreibt) '
           u'stets nur ein Attribut auf einmal. '
           u' Daher muß dieses angegeben werden (außer bei »svn proplist«), '
           'und tsvn folgt dieser Konvention. '
           u' Möglicherweise wird der Schalter /property ja eines schönen '
            'Tages repariert!')
    g = OptionGroup(p, groupname4cmd('propedit'))
    g.add_option('--all',
                 action='store_true',
                 help=u'Öffne Dialog für *alle* Attribute;'
                u' andernfalls würde das erste Argument wie beim svn-Kommando'
                ' als Attributname interpretiert'
                u' (und von der Schildkröte derzeit ignoriert)'
                )
    p.add_option_group(g)
    common_options(p)
    o, a = _parse_opts(p)
    cmd = ['/command:properties']
    if o.all:
        pass
    elif a:
        cmd.append('/property:'+a.pop(0))
    local_args_only(cmd, a,
                    default2cwd=1,
                    takes_files=1,
                    takes_dirs=1)
    TSVN(cmd)

def tsvn_log():
    ''"""\
    Show the log messages for a set of revision(s) and/or path(s).
    """
    p, g = parser_and_group('log', _('[--options]'))
    g.add_option('--revision', '-r',
                 type='string',
                 action='callback',
                 callback=cb_rev_or_revs,
                 metavar='erste[:letzte]',
                 help=_('Revision(s) of interest'
                 '; symbolic names (BASE, HEAD...) allowed'
                 ))
    g.add_option('--change', '-c',
                 action='callback',
                 metavar='REV',
                 callback=cb_change_as_revs,
                 type='int',
                 help=_('Revision of interest, numerical only'
                 '; -cREV equals -rREV:REV'))
    g.add_option('--stop-on-copy',
                 dest='stop_on_copy',
                 action='store_true',
                 help=('Stop on copy and rename'
                 ))
    p.add_option_group(g)
    g = OptionGroup(p, groupname4missingsvnoptions('log'))
    g.add_option('--limit', '-l',
                 type='int',
                 default=100,
                 metavar='100',
                 help=_('limit the output to NUM changes'
                 '. TortoiseSVN ignores the value; '
                 'it is fixed to %default'))
    p.add_option_group(g)
    common_options(p)
    add_revision_options(p,
                         including=1, # /startrev, /endrev 
                         c_option=1,
                         single_r_like_c=1)
    g = OptionGroup(p, groupname4nonsvnoptions('log'))
    g.add_option('--filter',
                 dest='findstring',
                 metavar='EXPR',
                 action='store',
                 help=_("Search expression to search the protocol for"))
    bitfunc = mapfunc((
            [0,   ''],
            [1,   'msg', 'msgs', 'messages'],
            [2,   'path'],
            [4,   'author', 'authors'],
            [8,   'rev', 'revs', 'revisions'],
            [32,  'bugs'],
            [128, 'date'],
            [256, 'range', 'date-range'],
            [511, 'all'],
            ))
    g.add_option('--search',
                 action='callback',
                 dest='findtype',
                 metavar=bitfunc.metavar(),
                 type='string',    # ?!
                 callback=cb_flags,
                 callback_kwargs={'f': bitfunc},
                 help=_("What kind of information is searched?"
                 ))
    g.add_option('--regex',
                 action='store_true',
                 help=_('use regular expressions'))
    p.add_option_group(g)
    o, a = _parse_opts(p)
    cmd = ['/command:log']
    if o.stop_on_copy:
        cmd.append('/strict')
    revs = None
    if o.revision:
        revs = tuple(o.revision)
    elif o.change:
        revs = (o.change, o.change)
    if revs:
        cmd.extend(('/startrev:%s' % revs[0],
                    '/endrev:%s'   % revs[1]))
    if o.findstring:
        cmd.append('/findstring:%s' % o.findstring)
        if o.regex:
            cmd.append('/findregex')
        else:
            cmd.append('/findtext')
    if o.findtype is not None:
        cmd.append('/findtype:%d' % o.findtype)
    # mehrere mit '*' verknüpfen (auch log?):
    local_args_only(cmd, a,
                    default2cwd=1,
                    takes_files=1,
                    takes_dirs=1)
    TSVN(cmd)

def tsvn_resolved():
    ''"""\
    Remove 'conflicted' state on working copy files or directories.
    """
    p, g = parser_and_group('resolved', _('[--options] args'))
    common_options(p)
    o, a = _parse_opts(p)
    cmd = ['/command:resolve']
    local_args_only(cmd, a,
                    takes_files=1,
                    takes_dirs=1)
    TSVN(cmd)

def tsvn_status():
    ''"""\
    Print the status of working copy files and directories.
    """
    p, g = parser_and_group('status', _('[--options]'))
    g.add_option('-u', '--show-updates',
                 dest='remote',
                 action='store_true',
                 help=_('display update information (connect to server)'
                 ))
    p.add_option_group(g)
    common_options(p)
    o, a = _parse_opts(p)
    cmd = ['/command:repostatus']
    if o.remote:
        cmd.append('/remote')
    local_args_only(cmd, a,
                    default2cwd=1)
    TSVN(cmd)

## --------------------------------------- Implementierte Kommandos ]]

def tsvn_help():
    ''"""\
    tell about the implemented commands
    """
    # (Hilfe auf Basis der Docstrings)
    print globals()['__doc__']
    print
    funcs = []
    shiftright = 15
    prefix = ' '*shiftright
    def thishelp(cmd, explanation):
        if len(cmd) < shiftright:
            print overlay(cmd, explanation)
        else:
            print cmd
            print explanation
    def cmdheader(cmd):
        try:
            aliases = SVN_COMMANDS[cmd]
            if aliases is not None:
                return '   %s (%s)' % (cmd, ', '.join(aliases))
            return '   ' + cmd
        except KeyError:
            return '   ' + cmd
    for k, v in globals().items():
        if k.startswith('tsvn_'):
            cn = k[5:]
            funcs.append((cn in TSVN_ONLY,
                          cn,
                          doc(v, prefix)))
    funcs.sort()
    tail = []
    prevflag = None
    for flag, cname, doclines in funcs:
        if flag != prevflag:
            if prevflag is None:
                print _('Implemented svn commands:')
            elif flag:
                print
                print _('Additional commands:')
            prevflag = flag
        if cname in ('help',):
            tail.append((cmdheader(cname), doclines))
        else:
            thishelp(cmdheader(cname), doclines)
    if tail:
        print
        print _('Help interface:')
        for tup in tail:
            thishelp(*tup)
    thishelp(_('   help {command}'),
             prefix+_('display help about the subcommand {command}'))
    raise SystemExit(RC_HELP)

def doc(f, prefix='\t'):
    liz = [s.rstrip()
           for s in f.__doc__.split('\n')]
    lf = '\n'+prefix
    paragraphs = []
    ind = None
    for z in liz:
        if paragraphs:
            paragraphs.append(z[ind:])
        elif z:
            tmp = z.lstrip()
            ind = len(z) - len(tmp)
            paragraphs.append(tmp)
    while paragraphs and not paragraphs[-1]:
        del paragraphs[-1]
    return prefix + lf.join(paragraphs)

## ---------------------------------------- Verwendung als Programm [[

def main():
    usage = _('tsvn [help] command [--options] [args]')
    descr_list = [usage,
                  '',
                  _(globals()['__doc__']),
                  ]
    p = OptionParser(usage='\n'.join(descr_list))
    add_version_option(p, version=VERSION)
    shadow = list(argv)
    for idx in range(len(argv)-1, -1, -1):
        a = argv[idx]
        if a.startswith('-') \
           and a not in ('-h', '-?', '--help',
                         '--version', '-V'):
            del argv[idx]

    o, a = p.parse_args()

    try:
        try:
            cmd = extract_cmd(a, p)
            if cmd == 'help':
                p.print_help()
                raise SystemExit(RC_HELP)
            del argv[:]
            argv.extend(shadow)
            if cmd is not None:
                cmd()
        except OptionError, e:
            err(str(e))
        except SvnCommandOnly, e:
            info(str(e))
        except CommandError, e:
            err(str(e))
    finally:
        check_errors()

if __name__ == '__main__':
    main()

## ---------------------------------------- Verwendung als Programm ]]
else:
    __all__ = [k for k in globals().keys()
               if k.startswith('tsvn_')
                  or k.startswith('cb_')
               ]

