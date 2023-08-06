# Core of LP
#
# Author: Balkansoft.BlogSpot.com
# GNU GPL licensed

__VERSION__ = '1.0i'
__ABOUT__ = 'Nano LP, v. %s'%__VERSION__

import re
import os
import sys
import copy
import pprint
import string
import random
import inspect
import fnmatch
import itertools
import functools
import xml.sax as sax
import xml.sax.saxutils as saxutils
from collections import OrderedDict, Callable, Iterable

ANONDICTNAME = '_anon'
UNDEFINED = ['undefined']
CMDQUOTE = string.punctuation # symbols can be escaped with \ in Cmd

FSURLRE = re.compile(r'^file://') # URL form for FS
URLRE = re.compile(r'^.+?://') # common URL form

################################################################################
# Python 2 -> 3 compatibility

_PY23 = 3 if sys.version_info.major > 2 else 2

# to avoid syntax errors (reraise23() for ex.) implements in different modules
if _PY23 == 2:
    from nanolp.lpcompat2 import *
elif _PY23 == 3:
    from nanolp.lpcompat3 import *

#################################################################################

def fix_crlf(buf):
    """Translate \r\n -> \n (actual for binary file)
    """
    return buf.replace('\r\n', '\n')

def absurl(urlstr, path):
    """Like abspath but for URL:
    >>> absurl('http://web.site.com/a/b?x=1&y=2', 'xxx.md')
    'http://web.site.com/a/xxx.md?x=1&y=2'
    >>> absurl('http://web.site.com/a/b?x=1&y=2', '/xxx.md')
    'http://web.site.com/xxx.md?x=1&y=2'
    >>> absurl('http://web.site.com/a/b/c?x=1&y=2', '../xxx.md')
    'http://web.site.com/a/xxx.md?x=1&y=2'
    >>> absurl('http://web.site.com/a/b/', 'xxx.md')
    'http://web.site.com/a/b/xxx.md'
    >>> absurl('http://web.site.com/a/b', 'xxx.md')
    'http://web.site.com/a/xxx.md'
    >>> absurl('http://web.site.com/a', '/xxx.md')
    'http://web.site.com/xxx.md'
    >>> absurl('http://localhost:8000/example.md', 'xxx.md')
    'http://localhost:8000/xxx.md'
    """
    spl = urlsplit(urlstr)
    if path.startswith('/'):
        spl = spl._replace(path=path)
    else:
        curpath = os.path.dirname(spl.path)
        if curpath and curpath != '/':
            path = os.path.normpath('/'.join((curpath, path)))
            path = path.replace(os.sep, '/')
        spl = spl._replace(path=path)
    return urlunsplit(spl)

def updatedict(dst, src, *onlykeys, **additional):
    """Update dst dictionary from src with only keys,
    and add additional values:
    >>> r = updatedict({}, {'a':1, 'b':2, 'c':3}, 'c', 'a', x=10)
    >>> sorted(r.keys())
    ['a', 'c', 'x']
    >>> r['a'], r['c'], r['x']
    (1, 3, 10)
    """
    if not onlykeys: dst.update(src)
    else: dst.update((k,v) for k,v in src.items() if k in onlykeys)
    dst.update(additional)
    return dst

def islices(seq, num):
    """Cuts sequence seq on slices with length num.
    Each slice is iterator on its elements. Yielding
    will be to the end of sequence. To finish early,
    use close() of Generator:
    >>> res = []
    >>> for sl in islices((1,2,3,4,5,6,7,8,9,0), 4):
    ...     for x in sl: res.append(x)
    ...     res.append('--')
    >>> res
    [1, 2, 3, 4, '--', 5, 6, 7, 8, '--', 9, 0, '--']
    """
    if num <= 0:
        raise ValueError("num must be > 0")

    # find 'empty' - criteria of iteration end
    try:
        # if 'seq' has len, limit yielding of slices with it
        length = len(seq)
        empty = lambda abeg: abeg >= length
    except:
        empty = lambda _:False

    # else for list/tuple will yield 0,1,2; 0,1,2; 0,1,2.. instead of 0,1,2; 3,4,5..
    seq = iter(seq)
    beg = 0
    while not empty(beg):
        yield itertools.islice(seq, 0, num)
        beg += num 

def indentstr(text, from_):
    """Looks for indent in text from 'from_' position in reverse order.
    But if from_ is 0 - in direct order:
    >>> indentstr('012345 aaa', 7)
    ''
    >>> indentstr('   aaa', 3)
    '   '
    >>> indentstr('\\n    aaa', 5)
    '    '
    >>> indentstr('aaa', 0)
    ''
    >>> indentstr('  aaa', 0)
    '  '
    """
    if from_ == 0:
        # direct order indent lookup
        i = 0
        while i < len(text):
            if text[i] not in (' ', '\t'):
                break
            i += 1
        # cut indent part
        return text[:i]

    else:
        # reverse order indent lookup
        i = from_-1
        while i >= 0:
            if text[i] not in (' ', '\t'):
                break
            i -= 1
        # cut indent part
        if i == -1:
            return text[:from_]
        elif text[i] in ('\n', '\r'):
            return text[i+1:from_]
        else:
            return ''

def indenttext(text, indent, first=False, cr='\n'):
    """Indent text block with indent string (split to lines, then
    join to lines with 'cr' symbol. If first is True, then indent
    also first line too:
    >>> indenttext('aaa\\nbbb', '  ')
    'aaa\\n  bbb'
    >>> indenttext('aaa\\nbbb', '  ', first=1)
    '  aaa\\n  bbb'
    """
    lines = text.splitlines()
    for i in range(0 if first else 1, len(lines)):
        lines[i] = indent + lines[i]
    return cr.join(lines)

def deltextindent(text, cr='\n'):
    """Remove indentation of text:
    >>> deltextindent('  a\\n   b\\n    c')
    'a\\n b\\n  c'
    >>> deltextindent('a\\n  b\\n   c')
    'a\\n  b\\n   c'
    >>> deltextindent(' a\\n\\n\\n  b\\n   c')
    'a\\n\\n\\n b\\n  c'
    >>> deltextindent('\\n  a\\n\\n  b')
    '\\na\\n\\nb'
    >>> text = '\\n  aaa\\n    bbb\\n\\n\\n  cc\\n'
    >>> deltextindent(text)
    '\\naaa\\n  bbb\\n\\n\\ncc'
    """
    lines = text.splitlines()
    minindent = min(len(indentstr(s, 0)) for s in lines if s)
    return cr.join(s[minindent:] for s in lines)

def prn(*args, **opts):
    """Write args serially (without spacing, or with delimiter
    opts['delim']), with newline (or without if opts['nonl']),
    to stdout (or any other opts['file']).
    Nothing does if opts['engine'].quiet or opts['quiet']
    """
    quiet = opts.get('quiet', False)
    if not quiet:
        engine = opts.get('engine', None)
        if engine:
            quiet = engine.quiet
    # now test if needed output
    if quiet: return

    delim = opts.get('delim', '')
    s = delim.join(args)
    if not opts.get('nonl', False): s+= '\n'
    out = opts.get('file', '')
    if out == 'null' or out == '/dev/null':
        return
    elif out == 'stdout':
        sys.stdout.write(s)
    elif out == 'stderr':
        sys.stderr.write(s)
    else:
        fwrite23(out, s, mode='a+t')

################################################################################

class CmdRe:
    """Hides different surround symbol usage in regular expressions
    """
    _surr = () # pair of left, right plain (not quoted) surr. symbols
    _re = None

    def __init__(self):
        """Init with default surround symbols:
        >>> r = CmdRe()
        >>> r._surr == ('<<', '>>')
        True
        """
        self._re = {
                # template, re, compiled-re
                'cmd': ['$L2(?!=)(.+?)$R2', None, None],
                'pasted': ['$L2=.+?$R2', None, None],
                'arg': ['\$[^ $]+', None, None],
                'pasted_cmd': ['$L2=%s(,.+?)?$R2', None, None],
        }
        self.change_surr(('<<', '>>'))

    def _suballre(self):
        L2, R2 = (re.escape(s) for s in self._surr)
        for k, v in self._re.items():
            v[1] = v[0]
            v[1] = v[1].replace('$L2', L2)
            v[1] = v[1].replace('$R2', R2)
            if k != 'pasted_cmd':
                v[2] = re.compile(v[1])

    def change_surr(self, surr):
        """Change surround symbol
        >>> r = CmdRe()
        >>> r.cre('xxx')
        Traceback (most recent call last):
            ...
        KeyError: 'xxx'
        >>> r.change_surr(('[[', ']]'))
        >>> r._surr == ('[[', ']]')
        True
        >>> bool(r.cre('cmd').findall('aaa [[a.b.c]] bbb'))
        True
        """
        self._surr = surr
        self._suballre()

    def surround(self, s):
        """Surround string s with surround symbol (doubled as usual):
        >>> r = CmdRe()
        >>> r.surround('x')
        '<<x>>'
        """
        return '%s%s%s' % (self._surr[0], s, self._surr[1])

    def check_cmd_form(self, s):
        """Check that s looks like cmd
        """
        return s.startswith(self._surr[0]) and s.endswith(self._surr[1])

    def re(self, name, *args):
        return self._re[name][1] % args

    def cre(self, name, *args):
        """Get compiled reg. expr by name:
        """
        cre = self._re[name][2]
        if cre is None:
            return re.compile(self._re[name][1] % args)
        else:
            return cre
CMDRE = CmdRe()

################################################################################

class CmdError(Exception): pass

class Cmd:
    """Parse text into internal fields
    """
    descr = '' # description of command
    gpath = None # global path matcher for class factory (Cmd-for not matched)
    commands = [] # registered Cmd successors (or used base Cmd)

    text = None # original text
    ispaste = None # pasting or definition
    isset = None # set of commands or one ('*' is used in path)
    path = None # list of path components (with possible '*')
    args = None # list of pairs: (key, value)
    body = None # list of unnamed args
    indent = None # indent string
    srcinfo = None # source info dict (set by ondefine())

    def _reset(self):
        """Reset internal fields"""
        self.text = ""
        self.ispaste = False
        self.isset = False
        self.path = []
        self.args = []
        self.body = []
        self.indent = ''
        self.srcinfo = {}

    def __init__(self, text=None, indent='', cmd=None):
        """Init from another cmd, or from text...
        """
        if cmd:
            self._reset()
            SKIP = ('gpath', 'commands')
            self.__dict__.update((k,v) for k,v in cmd.__dict__.items() if k not in SKIP)
        else:
            self._reset()
            if text is not None:
                self.parse(text)
            self.indent = indent

    @staticmethod
    def register(cmd):
        """Register new special command"""
        Cmd.commands.append(cmd)

    @staticmethod
    def get_uniform_commands(name):
        """Returns command and all it's successors. 'name' is string.
        """
        for basecmd in Cmd.commands:
            if basecmd.__name__ == name:
                break
        else:
            # base Cmd class was not found
            return []
        ret = []
        for cmd in Cmd.commands:
            if issubclass(cmd, basecmd):
                ret.append(cmd)
        return ret

    @staticmethod
    def create_cmd(text=None, indent=''):
        """Cmd factory, returns INSTANCE:
        >>> c = Cmd.create_cmd('<<use, file.h>>')
        >>> isinstance(c, UseCmd)
        True
        >>> c = Cmd.create_cmd('<<file.x, file.h>>')
        >>> isinstance(c, UseCmd)
        False
        """
        cmd = Cmd(text=text, indent=indent)
        for cls in Cmd.commands:
            if cmd.matchpath(cls.gpath):
                return cls(cmd=cmd)
        else:
            return cmd

    def get_srcinfo(self, attr, default=None):
        """Return some item from srcinfo"""
        return self.srcinfo.get(attr, default)

    def matchpath(self, gpath):
        """Match me with glob-style path pattern:
        >>> p = Cmd.create_cmd('<<c.f>>')
        >>> p.matchpath('c*')
        True
        >>> p.matchpath('*x')
        False
        """
        re_ = fnmatch.translate(gpath)
        cre = re.compile(re_)
        return bool(cre.match(self.jpath()))

    def setpath(self, path=None, prefix=None, suffix=None):
        """Change path with optional prefix (str|list|tuple),
        suffix (str|list|tuple). IF no path, current is used:
        >>> p = Cmd.create_cmd('<<c.f>>')
        >>> p.path
        ['c', 'f']
        >>> p.setpath('', ('a','b'), 'x.y')
        ['a', 'b', 'c', 'f', 'x', 'y']
        >>> p.setpath(('a', 'b'))
        ['a', 'b']
        >>> p.setpath(prefix='x')
        ['x', 'a', 'b']
        >>> p.setpath('x.y.z', '', ['t'])
        ['x', 'y', 'z', 't']
        """
        if not path: path = self.path
        if not prefix: prefix = []
        if not suffix: suffix = []

        if isinstance(path, StringTypes23):
            path = path.split('.')
        if isinstance(suffix, StringTypes23):
            suffix = suffix.split('.')
        if isinstance(prefix, StringTypes23):
            prefix = prefix.split('.')
        self.path = list(prefix) + list(path) + list(suffix)
        return self.path

    def __hash__(self):
        """Generate key when object is used as key:
        >>> d = dict()
        >>> d[Cmd.create_cmd('<<c.f>>')] = 123
        >>> d[Cmd.create_cmd('<<c.f>>')]
        123
        >>> d[Cmd.create_cmd('<<c.f, x>>')] = 321
        >>> d[Cmd.create_cmd('<<c.f,  x>>')]
        321
        >>> d[Cmd.create_cmd('<<c.f>>')]
        123
        >>> Cmd.create_cmd('<<c.f1>>') in d
        False
        """
        factors = []
        factors.append(self.jpath())
        factors.append(','.join('%s:%s'%(n,v) for n,v in self.args))
        factors.append(','.join(self.body))
        return hash(''.join(factors))

    def __eq__(self, oth):
        if isinstance(oth, Cmd):
            return self.path == oth.path
        elif isinstance(oth, StringTypes23):
            return self.jpath() == oth
        else:
            return False

    def hasarg(self, args):
        """Test existent of arg name:
        >>> c = Cmd.create_cmd()
        >>> c.parse('<<c.sum, a: 1, b: 2>>')
        True
        >>> c.hasarg('a')
        True
        >>> c.hasarg('b')
        True
        >>> c.hasarg(('a', 'b'))
        True
        >>> c.hasarg(('a', 'b', 'x'))
        False
        >>> c.hasarg(('x', 'b'))
        False
        >>> c.hasarg('x')
        False
        """
        if isinstance(args, StringTypes23):
            args = [args]
        for arg in args:
            if not any(myarg[0]==arg for myarg in self.args):
                return False
        return True

    def getarg(self, args, default=None):
        """Returns value of named arg (or arg aliases, args may be list or str):
        >>> c = Cmd.create_cmd()
        >>> c.parse('<<c.sum, a: 1, b: 2>>')
        True
        >>> c.getarg('a')
        '1'
        >>> c.getarg(('aa', 'a'))
        '1'
        >>> c.getarg('x', default=10)
        10
        """
        if isinstance(args, StringTypes23):
            args = [args]
        for k,v in self.args:
            if k in args:
                return v
        return default

    def jpath(self, delim='.'):
        return delim.join(self.path)

    def parse(self, text):
        """Reset fields then parse text:
        >>> Cmd.create_cmd('')
        Traceback (most recent call last):
            ...
        CmdError: mismatch form
        >>> c = Cmd.create_cmd()
        >>> c.parse('<c.sum>')
        Traceback (most recent call last):
            ...
        CmdError: mismatch form
        >>> c.parse('<<>>')
        Traceback (most recent call last):
            ...
        CmdError: empty path
        >>> c.parse('<<c.sum,,>>')
        Traceback (most recent call last):
            ...
        CmdError: missed arg
        >>> c.parse('<<c.sum, x!y:10>>')
        Traceback (most recent call last):
            ...
        CmdError: arg 'x!y' contains unallowed symbols
        >>> c.parse('<<c.sum, x.y:10>>') and c.body==[] \
                and c.args==[('x.y', '10')]
        True
        >>> c.parse('<<c.sum>>') and not c.ispaste and not c.isset
        True
        >>> c.parse('<<=c.sum.*>>') and c.text=='<<=c.sum.*>>' and c.ispaste \
                and c.isset and c.path==['c', 'sum', '*']
        True
        >>> c.parse('<<c.sum>>') and c.text=='<<c.sum>>' and not c.ispaste \
                and c.path==['c', 'sum'] and c.args==[] and c.body==[]
        True
        >>> c.parse('<<c.a sum, bbb, ddd>>') and c.text=='<<c.a sum, bbb, ddd>>' \
                and not c.ispaste and c.path==['c', 'a sum'] and c.args==[] \
                and c.body==['bbb', 'ddd']
        True
        >>> c.parse('<<c.sum, a:>>') and c.body==[] \
                and c.args==[('a', '')]
        True
        >>> c.parse('<<c.sum, a: 1, b: 2>>') and c.body==[] \
                and c.args==[('a', '1'), ('b', '2')]
        True
        >>> c.parse('<<c.sum, a:b:c>>') and c.body==[] \
                and c.args==[('a', 'b:c')]
        True
        >>> c.parse('<<c.sum, a::c>>') and c.body==[] \
                and c.args==[('a', ':c')]
        True
        >>> c.parse('<<c.sum, :a:b:c>>') and c.body==[] \
                and c.args==[('', 'a:b:c')]
        True
        >>> c.parse('<<c.sum, a::>>') and c.body==[] \
                and c.args==[('a', ':')]
        True
        >>> c.parse('<<c.sum, a:1, ccc, b:2, ddd>>') and c.body==['ccc', 'ddd'] \
                and c.args==[('a', '1'), ('b', '2')]
        True
        >>> c.parse('<<c.sum, a:\\,>>') and c.body==[] \
                and c.args==[('a', ',')]
        True
        >>> c.parse('<<c.sum, a:b c d>>') and c.body==[] \
                and c.args==[('a', 'b c d')]
        True
        >>> c.parse('<<c.sum, a\\:8000/>>') and c.body==['a:8000/'] \
                and c.args==[]
        True
        >>> c.parse('<<use, mnt:c, fmt:md, http\\://localhost\\:8000/cstd.md>>') \
                and c.args==[('mnt', 'c'), ('fmt', 'md')] \
                and c.body==['http://localhost:8000/cstd.md']
        True
        >>> c.parse('<<c.sum, a:\\:, xxx\\:yyy\\,>>') and c.body==['xxx:yyy,'] \
                and c.args==[('a', ':')]
        True
        >>> c.parse('<<c.sum, a:b, *:*>>') and c.body==[] \
                and c.args==[('a', 'b'), ('novars', True)]
        True
        """
        # denied in kw arg name
        _ArgNameDeniedSymbols = string.punctuation.replace('.', '')

        def _quote_text(txt):
            for i,q in enumerate(CMDQUOTE):
                txt = txt.replace(r'\%s'%q, '@Q%d@'%i)
            return txt
        def _unquote_text(txt):
            for i,q in enumerate(CMDQUOTE):
                txt = txt.replace('@Q%d@'%i, q)
            return txt

        self._reset()
        if not CMDRE.check_cmd_form(text):
            raise CmdError('mismatch form')

        self.text = text
        text = text[2:-2]

        text = _quote_text(text)
        tmp = [t.strip() for t in text.split(',')]
        pathpart, args = tmp[0], tmp[1:]
        if not pathpart:
            raise CmdError('empty path')

        if pathpart[0] == '=':
            self.path = pathpart[1:].split('.')
            self.ispaste = True
        else:
            self.path = pathpart.split('.')
            self.ispaste = False
        self.isset = '*' in self.path

        for arg in args:
            if not arg:
                raise CmdError('missed arg')
            tmp = [t.strip() for t in arg.split(':', 1)]
            tmplen = len(tmp)
            if tmplen == 1:
                tmp[0] = _unquote_text(tmp[0])
                self.body.append(tmp[0])
            elif tmplen == 2:
                # process argument
                if tmp[0] == '*':
                    if tmp[1] == '*':
                        self.args.append(('novars', True))
                    elif tmp[1].startswith('$'):
                        self.args.append(('varsdict', tmp[1][1:]))
                else:
                    if any(tmp0ch in _ArgNameDeniedSymbols for tmp0ch in tmp[0]):
                        raise CmdError("arg '%s' contains unallowed symbols"%tmp[0])
                    tmp[0] = _unquote_text(tmp[0])
                    tmp[1] = _unquote_text(tmp[1])
                    self.args.append((tmp[0], tmp[1]))
        return True

    # events
    # ======

    # Are calling now:
    #
    # If recepient of event has method __onEVENT__() - it call, nothing else.
    # Else parser.emitevent() create FuncChain with onEVENT() and instance-based
    # handlers, class-based handlers (which canhandle() this event for this recepient)
    # and call this chain.
    # Class-based handlers are created by <<on.*>> cmd: <<on.CLASS.EVENT, do:...>> or
    # <<on.CLASS, do.EVENT1:..., do.EVENT2:...>>. Instance-based handlers are created
    # in any user-command (macros!) by <<some, do.EVENT1:..., do.EVENT2:...>>.
    # Class-basd needs 'gpath' arg. necessary!
    #
    # So, scheme is:
    #
    #  recep., event - matching -> onEVENT() + handlers
    #                                        |
    #                                       do!
    #
    # onEVENT() is callback of successor, it should call BaseClass.onEVENT()

    def ondefine(self, parser=None, chunktext=None):
        """Calling on define new chunk with this cmd.
        Should returns modified or original chunk text.
        If returns None in chunktext, adding is disable (skipped).
        """
        if parser:
            self.srcinfo['infile'] = parser.infile
        return dict(parser=parser, chunktext=chunktext)

    def onpost(self, parser=None, flush=None):
        """Called on post-processing of input.
        parser is concrete Parser object, flush is flag - flushing to
        file is enabled
        """
        return dict(parser=parser, flush=flush)

    def onpaste(self, parser=None, chunktext=None):
        """Called after extending text of command
        """
        return dict(parser=parser, chunktext=chunktext)

################################################################################

class Chunk:
    """Base class for all chunk handlers, like 'c'
    """
    orig = None # original text
    tangle = None # code text
    isdone = None # all expanded
    deps = None # dependencies for this chunk (list of Cmd)
    # for cycle detection:
    _walkid = None # ID of traversing session
    _nvisits = None # count of visiting

    _varplaceholders_re_ = r'\$({.+?}|.+?\b)' # '$...\b' or '${...}'
    _varplaceholders_re = re.compile(_varplaceholders_re_)

    def __init__(self, text=None):
        """Construct and if there is text, do some preparing:
        >>> c = Chunk('')
        >>> c.isdone
        True
        >>> bool(c)
        False
        >>> c = Chunk('aaa')
        >>> c.isdone
        True
        >>> c.tangle
        'aaa'

        # TODO tangle will be '<<c.fun>>' but looks strange. May be warning?
        >>> c = Chunk('<<c.fun>>')
        >>> c.isdone
        True
        >>> c = Chunk('<<=c.fun>>')
        >>> c.isdone
        False
        """
        self.orig = text
        self._reset()

    def _reset(self):
        self.tangle = ''
        self.isdone = False
        self.deps = []
        self._walkid = 0
        self._nvisits = 0
        # update deps, isdone, tangle (if no deps, tangle is text) from self.orig
        if self.orig is not None:
            self.deps = self._finddeps(self.orig)
            if Chunk._isdone(self.orig):
                self.tangle = self.orig # i.e. = text
                self.isdone = True

    def __len__(self):
        return len(self.orig)

    @staticmethod
    def _subargs(text, parser=None, novars=False, varsdict=None, **args):
        """Substitute args with their values. Arg in text should be
        prefixed with $. If there is arg novars=True, replaces
        args with it's names:
        >>> Chunk._subargs('A text $a $b b c $a $c', a='AAA', b=9, x=10)
        'A text AAA 9 b c AAA $c'
        >>> Chunk._subargs('A text $a $b b c $a $c', a='AAA', b=9, x=10, novars=True)
        'A text a b b c a c'
        >>> Chunk._subargs('aaa $a')
        'aaa $a'
        """
        def _varname(s):
            """Name of variable from it's placeholder in text -
            'xxx' -> 'xxx' and '{xxx}' -> 'xxx':
            >>> _varname('')
            ''
            >>> _varname('aa')
            'aa'
            >>> _varname('{aaa}')
            'aaa'
            """
            if s.startswith('{'):
                return s[1:-1]
            else:
                return s
        def _varvalue(varname, args, novars, varsdict):
            """Value-replacer for var. name (placeholder)"""
            if novars: return varname
            elif varsdict:
                assert parser, "parser can't be None when varsdict is used"
                # order of var getting ("frame inheritance")
                return args.get(varname, None) or \
                        parser.getvar(varname, varsdict, default=None)
            else:
                return args.get(varname, None) or \
                        (parser.getvar(varname, default=None) if parser else None)

        # resolve '$...' values of args
        for argname, argvalue in args.items():
            argvalue = str(argvalue)
            if argvalue.startswith('$'):
                assert parser, "parser can't be None with arg reference"
                argvalue = parser.getvar(argvalue)
                args[argname] = argvalue

        # substitute
        textvars = Chunk._varplaceholders_re.findall(text)
        for textvar in set(textvars):
            varname = _varname(textvar)
            #print 'Found textvar %s with name %s'%(textvar, varname)
            varvalue = _varvalue(varname, args, novars, varsdict)
            #print 't: %s, n:%s, v:%s, novars=%s'%(textvar, varname, varvalue, novars)
            if varvalue is not None:
                text = text.replace('$%s'%textvar, str(varvalue))
            #print "So text is '%s'"%text
        return text

    def subargs(self, parser=None, **args):
        """Substitute arguments and set 'tangle' and 'isdone':
        >>> c = Chunk('aaa $a $b')
        >>> c.isdone
        False
        >>> c.subargs(a=1)
        False
        >>> c.subargs(b=2)
        True
        >>> c.tangle
        'aaa 1 2'
        >>> c = Chunk('aaa $a')
        >>> c.subargs()
        False
        >>> c.tangle
        'aaa $a'
        """
        self.tangle = Chunk._subargs(self.tangle or self.orig, parser=parser, **args)
        return self.update_isdone()

    @staticmethod
    def _subcmd(text, path, content):
        """Substitute FIRST pasted cmd (has 'path') with 'content':
        >>> Chunk._subcmd('aaa <<=x.y, a:1, b:2>>', 'x.y', 'zzz')
        'aaa zzz'
        >>> Chunk._subcmd('aaa <<=x.yz>>', 'x.y', 'zzz')
        'aaa <<=x.yz>>'
        """
        return CMDRE.cre('pasted_cmd', path).sub(content, text, 1)

    def subcmd(self, path, content):
        """Substitute pasted cmd and set 'tangle' and 'isdone':
        >>> c = Chunk('aaa $a $b <<=x.y, z>>')
        >>> c.isdone
        False
        >>> c.subargs(a=1)
        False
        >>> c.subcmd('x.y', 'zzz')
        False
        >>> c.subargs(b=2)
        True
        >>> c.tangle
        'aaa 1 2 zzz'
        """
        self.tangle = Chunk._subcmd(self.tangle or self.orig, path, content)
        return self.update_isdone()

    @staticmethod
    def _isdone(text):
        """Check is text does not need more substitution:
        >>> Chunk._isdone('')
        True
        >>> Chunk._isdone('A $a $b $c')
        False
        >>> Chunk._isdone('A $$ $')
        True
        >>> Chunk._isdone('<<aa>>')
        True
        >>> Chunk._isdone('<<=aa>>')
        False
        """
        if CMDRE.cre('arg').search(text) is None and \
                CMDRE.cre('pasted').search(text) is None:
            return True
        else:
            return False

    def update_isdone(self):
        self.isdone = Chunk._isdone(self.tangle)
        return self.isdone

    @staticmethod
    def _finddeps(text):
        """Find dependencies in text:
        >>> Chunk._finddeps('')
        []
        >>> Chunk._finddeps('aaa')
        []
        >>> Chunk._finddeps('<<c.fun>>')
        []
        >>> ['.'.join(d.path) for d in \
                Chunk._finddeps('aaa <<=c.fun1>> and <<=c.fun2, a:1,b:2,ccc>>')]
        ['c.fun1', 'c.fun2']
        >>> deps = Chunk._finddeps('   <<=c.fun1>> and <<=c.fun2, a:1,b:2,ccc>>')
        >>> deps[0].indent == '   '
        True
        >>> deps[1].indent == ''
        True
        """
        txtdeps = CMDRE.cre('pasted').finditer(text)
        result = []
        for txtdep in txtdeps:
            # each pasted cmd should have indent string, to indent tangled text later
            indent = indentstr(text, txtdep.start(0))
            result.append(Cmd.create_cmd(txtdep.group(0), indent=indent))
        return result

    def visit(self, walkid):
        if self._walkid != walkid:
            # new walk session
            self._walkid = walkid
            self._nvisits = 1
        else:
            # old walk session
            self._nvisits += 1
        return self._nvisits

################################################################################

class ChunkDictError(Exception): pass

class ChunkDict:
    """Dictionary of chunks, where key is Cmd
    """
    def __init__(self):
        self.chunks = OrderedDict()

    def __len__(self):
        return len(self.chunks)

    # XXX does not check cycles, do it explicitly
    def merge(self, othchunkdict, path=''):
        """Like dict update(), but merge under prefixed path. Cycles are not
        checked after merging, do it explicitly.
        >>> cd1 = ChunkDict()
        >>> cd1.define_chunk(Cmd.create_cmd('<<c.sum>>'), Chunk('x + y'))
        True
        >>> cd2 = ChunkDict()
        >>> cd2.define_chunk(Cmd.create_cmd('<<c.abs>>'), Chunk('x + y'))
        True
        >>> cd1.merge(cd2, 'a.b')
        >>> Cmd.create_cmd('<<c.abs>>') in cd1.chunks
        False
        >>> Cmd.create_cmd('<<a.b.c.abs>>') in cd1.chunks
        True
        >>> cd3 = ChunkDict()
        >>> cd3.define_chunk(Cmd.create_cmd('<<c.sum>>'), Chunk('x + y'))
        True
        >>> cd1.merge(cd3)
        Traceback (most recent call last):
            ...
        ChunkDictError: 'c.sum' path already exists when merging
        >>> cd1.merge(cd3, 'x')
        """
        #print 'Try to merge %s'%', '.join(p.jpath() for p in othchunkdict.chunks.keys())
        for cmd, chunk in othchunkdict.chunks.items():
            cmd.setpath(prefix=path)
            if cmd in self.chunks:
                raise ChunkDictError("'%s' path already exists when merging" % \
                        cmd.jpath())
            self.chunks[cmd] = chunk

    def define_chunk(self, cmd, chunk):
        """Register chunk with name/header as cmd:
        >>> cd = ChunkDict()
        >>> cd.define_chunk(Cmd.create_cmd('<<c.sum>>'), Chunk('x + y'))
        True
        >>> Cmd.create_cmd('<<c.sum>>') in cd.chunks
        True
        """
        self.chunks[cmd] = chunk
        return True

    @staticmethod
    def __askey(something):
        if isinstance(something, Cmd):
            return something
        elif isinstance(something, StringTypes23):
            return Cmd.create_cmd(CMDRE.surround(something))
        else:
            return None

    def get_uniform_commands(self, name):
        """Returns registered commands instances which has class name 'name' or
        are it's successors - like Cmd.get_uniform_commands()
        """
        cmdcls = Cmd.get_uniform_commands(name)
        gpaths = [c.gpath for c in cmdcls]
        ret = []
        for gpath in gpaths:
            ret.extend(self.globpath(gpath))
        return ret

    def globpath(self, gpath, _onlypath=False):
        """Return keys for pattern 'gpath' - components
        may be '*' - match like glob. If '_onlypath', returns list of paths, not
        Cmd's (for tests purpose):
        >>> cd = ChunkDict()
        >>> cd.define_chunk(Cmd.create_cmd('<<c>>'), Chunk('a'))
        True
        >>> cd.define_chunk(Cmd.create_cmd('<<c.sum>>'), Chunk('a'))
        True
        >>> cd.define_chunk(Cmd.create_cmd('<<c.abs>>'), Chunk('a'))
        True
        >>> cd.define_chunk(Cmd.create_cmd('<<d.defs>>'), Chunk('a'))
        True
        >>> cd.globpath('c.sum', _onlypath=True)
        ['c.sum']
        >>> cd.globpath('*.sum', _onlypath=True)
        ['c.sum']
        >>> cd.globpath('c.*', _onlypath=True)
        ['c.sum', 'c.abs']
        >>> cd.globpath('*.*', _onlypath=True)
        ['c.sum', 'c.abs', 'd.defs']
        >>> cd.globpath('*.x', _onlypath=True)
        []
        >>> cd.globpath('*', _onlypath=True)
        ['c', 'c.sum', 'c.abs', 'd.defs']
        >>> cd.globpath('*.', _onlypath=True)
        []
        """
        found = []
        for cmd in self.chunks.keys():
            if cmd.matchpath(gpath):
                found.append(cmd)
        if _onlypath:
            return [f.jpath() for f in found]
        else:
            return found

    def getbypath(self, key):
        """key is dotted path or Cmd:
        >>> cd = ChunkDict()
        >>> cd.define_chunk(Cmd.create_cmd('<<c.sum, a:1, b:2>>'), Chunk('x + y'))
        True
        >>> k,v = cd.getbypath('c.sum')
        >>> k == 'c.sum'
        True
        >>> v.orig == 'x + y'
        True
        >>> cd.getbypath('aaa')
        Traceback (most recent call last):
            ...
        KeyError: 'aaa'
        """
        _key = ChunkDict.__askey(key)
        if _key is None:
            raise KeyError(key)
        else:
            for k,v in self.chunks.items():
                if k == _key:
                    return (k, v)
        raise KeyError(key)

    def getbykey(self, cmd):
        """Returns chunk by Cmd key"""
        return self.chunks[cmd]

    def keys(self, **attrs):
        """Returns Cmd (keys) matched by it's attrs (or all if no attrs):
        >>> cd = ChunkDict()
        >>> cd.define_chunk(Cmd.create_cmd('<<c.sum>>'), Chunk('x + y'))
        True
        >>> cd.define_chunk(Cmd.create_cmd('<<c.abs>>'), Chunk('x + y'))
        True
        >>> l = list(cd.keys(path=['c', 'sum']))
        >>> [c.jpath() for c in l]
        ['c.sum']
        """
        if attrs:
            for cmd in self.chunks.keys():
                if all(getattr(cmd, attr)==attrs[attr] for attr in attrs):
                    yield cmd
        else:
            for cmd in self.chunks.keys():
                yield cmd

    def __contains__(self, key):
        """Test of existent:
        >>> cd = ChunkDict()
        >>> cd.define_chunk(Cmd.create_cmd('<<c.sum>>'), Chunk('x + y'))
        True
        >>> 'c.sum' in cd
        True
        """
        key = ChunkDict.__askey(key)
        if key is None:
            return False
        else:
            return key in self.chunks

    # Seems that not work
    def check_cycle(self, cmd, walkid):
        """Check are any cycles, returns True if there are, False else
        """
        chunk = self.chunks[cmd]
        if chunk.visit(walkid) > 1:
            return True
        for dep in chunk.deps:
            if dep in self.chunks:
                if self.check_cycle(dep, walkid):
                    return True
        return False

    def check_cycles(self):
        """Check cycles in all registered chunks. If there are some cycles, raise
        ChunkDictError:
        >>> cd = ChunkDict()
        >>> cd.define_chunk(Cmd.create_cmd('<<c.a>>'), Chunk('aaa <<=c.b>> bbb'))
        True
        >>> cd.check_cycles()
        >>> cd.define_chunk(Cmd.create_cmd('<<c.b>>'), Chunk('<<=c.a>>'))
        True
        >>> cd.check_cycles()
        Traceback (most recent call last):
            ...
        ChunkDictError: cyclic 'c.a'
        """
        for cmd in self.chunks.keys():
            walkid = random.randint(0,32768) #os.urandom(8)
            if self.check_cycle(cmd, walkid):
                raise ChunkDictError("cyclic '%s'"%cmd.jpath())

    def expand(self, path, visited=None, parser=None, **args):
        """Try to expand all '<<=...>>' holders:
        >>> cd = ChunkDict()
        >>> cd.define_chunk(Cmd.create_cmd('<<c.a>>'), Chunk('aaa <<=c.b, d:end, x:10>> bbb'))
        True
        >>> cd.define_chunk(Cmd.create_cmd('<<c.b>>'), Chunk('<<=c.d, y:2>> $d'))
        True
        >>> cd.define_chunk(Cmd.create_cmd('<<c.d>>'), Chunk('xxx $x $y'))
        True
        >>> cd.expand('c.a')
        True
        >>> cd.getbypath('c.a')[1].tangle
        'aaa xxx 10 2 end bbb'

        >>> cd = ChunkDict()
        >>> cd.define_chunk(Cmd.create_cmd('<<c.a>>'), Chunk('aaa'))
        True
        >>> cd.define_chunk(Cmd.create_cmd('<<c.b>>'), Chunk('bbb'))
        True
        >>> cd.define_chunk(Cmd.create_cmd('<<c>>'), Chunk('ccc <<=c.*, join:\\,>> ddd'))
        True
        >>> cd.expand('c')
        True
        >>> cd.getbypath('c')[1].tangle
        'ccc aaa,bbb ddd'

        >>> cd = ChunkDict()
        >>> cd.define_chunk(Cmd.create_cmd('<<c.a>>'), Chunk('aaa <<=c.b>>'))
        True
        >>> cd.define_chunk(Cmd.create_cmd('<<c.b>>'), Chunk('bbb <<=c.a>>'))
        True
        >>> cd.define_chunk(Cmd.create_cmd('<<c>>'), Chunk('ccc <<=c.*, join:\\,>> ddd'))
        True
        >>> cd.expand('c') # doctest:+ELLIPSIS
        Traceback (most recent call last):
            ...
        ChunkDictError: cyclic ...
        """

        if visited is None:
            visited = []

        cmd, chunk = self.getbypath(path)

        jpath = cmd.jpath()
        if jpath in visited:
            raise ChunkDictError("cyclic '%s'"%jpath)

        visited.append(jpath)
        depsaredone = True
        for dep in chunk.deps:
            # over dependencies as Cmd (<<=dep>> - dep may be glob path)
            globpath = dep.jpath() # glob path or usual path
            joinkw = dep.getarg('join', '') # dep can have 'join' arg
            startkw = dep.getarg('start', '') # also 'start' arg
            endkw = dep.getarg('end', '') # also 'end' arg
            deps = self.globpath(globpath) # one or several Cmd's
            if not deps:
                raise KeyError(globpath)
            repls = [] # replace with joined items of this list (tangles of glob paths)
            for depcmd in deps:
                # how depend is registered in dict:
                deppath = depcmd.jpath()
                depchunk = self.getbykey(depcmd)
                depchunk._reset()
                _args = args.copy()
                _args.update(dep.args)
                if not self.expand(deppath, visited=visited, parser=parser, **_args):
                    # impossible to extend now, so skip this depend
                    depsaredone = False
                    continue

                # if dep is done or was sucessfully expanded, keep it in repls
                repls.append(startkw + depchunk.tangle + endkw)
                #print '>>', depchunk.tangle, repls, '<<'
            # join repls and substitute with it WITH INDENT
            repltext = indenttext(joinkw.join(repls), dep.indent)
            chunk.subcmd(globpath, repltext)
        # extend args (total result is chunk.isdone)
        chunk.subargs(parser=parser, **args)
        visited.pop()
        isdone = depsaredone and chunk.isdone
        if isdone and parser:
            chunk.tangle = parser.emitevent(cmd, 'paste', parser=parser,
                    chunktext=chunk.tangle)['chunktext']
        return isdone

################################################################################

class EventHandler:
    """Events handler - wrap event matching
    """
    params = None # dict of object attrs for matching
    helper_funcs = {} # {func-name: func}
    handler_func = None # on*() - gets dict, returns possible changed dict

    # kind of signatures of supported functions
    ONEARGFUNC = 1
    KWARGFUNC = 2

    def __init__(self, handler_func, **params):
        self.params = params.copy()
        self.handler_func = handler_func

    def __repr__(self):
        return "<EventHandler instance at 0x%X>"%id(self)

    def __getattr__(self, name):
        """Access params values as instance attribute
        >>> e = EventHandler(None, a=1, b=2)
        >>> e.a + e.b
        3
        """
        try: return self.params.get(name)
        except: raise AttributeError(name)

    def change_gpath(self, gpath='', prefix='', suffix=''):
        """If there is gpath in params, change it value, otherwise nothing to do
        >>> e = EventHandler(None, a=1, b=2)
        >>> e.change_gpath('xxx')
        >>> 'gpath' in e.params
        False
        >>> e = EventHandler(None, a=1, b=2, gpath='a.b')
        >>> e.change_gpath(prefix='0')
        >>> e.gpath
        '0.a.b'
        >>> e.change_gpath(gpath='x.y')
        >>> e.gpath
        'x.y'
        >>> e.change_gpath(gpath='', prefix='.a', suffix='.b.c.')
        >>> e.gpath
        'a.x.y.b.c'
        """
        if 'gpath' in self.params:
            if not gpath: gpath = self.params['gpath']
            p = (p for p in (prefix.strip('.'), gpath.strip('.'), suffix.strip('.')) if p)
            self.params['gpath'] = '.'.join(p)

    def canhandle(self, obj, event):
        """Test can this event handler handle this event for this object:
        >>> c = Cmd.create_cmd()
        >>> c.parse('<<c.sum, x.y:10>>')
        True
        >>> e = EventHandler(None, gpath='c.*', event='no-such-event')
        >>> e.canhandle(c, 'define')
        False
        >>> e = EventHandler(None, gpath='c.*', event='define')
        >>> e.canhandle(c, 'define')
        True
        >>> e = EventHandler(None, id=id(c), event='define')
        >>> e.canhandle(c, 'define')
        True
        >>> e = EventHandler(None, id=id(c), event='define')
        >>> e.canhandle(None, 'define')
        False
        >>> e = EventHandler(None, id=id(c), xxx=0, event='define')
        >>> e.canhandle(c, 'define')
        False
        """
        for parname, parval in self.params.items():
            if parname == 'classname':
                m = parval == obj.__class__.__name__
            elif parname == 'id':
                m = parval == id(obj)
            elif parname == 'hash':
                m = parval == hash(obj)
            elif parname == 'gpath':
                assert isinstance(obj, Cmd) # only Cmd has .gpath
                m = obj.matchpath(parval)
            elif parname == 'event':
                m = parval == event
            else:
                m = parval == getattr(obj, parname, UNDEFINED)
            if not m:
                return False
        return True

    @staticmethod
    def _isoneargfunc(func):
        """Check that func has right signature to get calls:
        f(*o|o, [x=.., *a, **kw])
        >>> def f():pass
        >>> EventHandler._isoneargfunc(f)
        False
        >>> def f(a):pass
        >>> EventHandler._isoneargfunc(f)
        True
        >>> def f(a=1):pass
        >>> EventHandler._isoneargfunc(f)
        True
        >>> def f(a, b):pass
        >>> EventHandler._isoneargfunc(f)
        False
        >>> def f(a, b, c=1, d=2):pass
        >>> EventHandler._isoneargfunc(f)
        False
        >>> def f(a=0, b=0, c=1, d=2):pass
        >>> EventHandler._isoneargfunc(f)
        True
        >>> def f(a, b=0, *args, **kw):pass
        >>> EventHandler._isoneargfunc(f)
        True
        >>> def f(a, b, *args):pass
        >>> EventHandler._isoneargfunc(f)
        False
        """
        argspec = inspect.getargspec(func)
        ndefaults = len(argspec.defaults) if argspec.defaults else 0
        nargs = len(argspec.args) if argspec.args else 0
        if not argspec.args:
            if argspec.varargs: return True
        else:
            if nargs - ndefaults <= 1: return True

        return False

    @staticmethod
    def _iskwargfunc(func):
        """Check that func has right signature for keyword-argument-function,
        func is one-arg-func (for _self) and (has keyword arguments or
        all other pos. args has default values):
        >>> def f():pass
        >>> EventHandler._iskwargfunc(f)
        False
        >>> def f(s):pass
        >>> EventHandler._iskwargfunc(f)
        False
        >>> def f(s, *args):pass
        >>> EventHandler._iskwargfunc(f)
        False
        >>> def f(s, **kw):pass
        >>> EventHandler._iskwargfunc(f)
        True
        >>> def f(s, a=1, b=2):pass
        >>> EventHandler._iskwargfunc(f)
        True
        >>> def f(s, a=1, *args):pass
        >>> EventHandler._iskwargfunc(f)
        True
        >>> def f(s, a=1, **kw):pass
        >>> EventHandler._iskwargfunc(f)
        True
        """
        argspec = inspect.getargspec(func)
        ndefaults = len(argspec.defaults) if argspec.defaults else 0
        nargs = len(argspec.args) if argspec.args else 0
        if EventHandler._isoneargfunc(func):
            if argspec.keywords: return True
            if nargs > 1 and nargs-1 == ndefaults: return True
        return False

    @staticmethod
    def register_func(name, func):
        """Register function (not class/instance) to process some event.
        Supported only KWARGFUNC and ONEARGFUNC functions:
        >>> EventHandler.register_func('f', lambda a:0)
        >>> EventHandler.register_func('f', lambda _self, a=1,b=2:0)
        >>> EventHandler.register_func('f', lambda _self, **kw:0)
        >>> EventHandler.register_func('f', lambda a,b:0)
        Traceback (most recent call last):
            ...
        TypeError: function...
        """
        # order has matter!
        if EventHandler._iskwargfunc(func):
            funcinfo = {'signature': EventHandler.KWARGFUNC}
        elif EventHandler._isoneargfunc(func):
            funcinfo = {'signature': EventHandler.ONEARGFUNC}
        else:
            raise TypeError("function '%s' has illegal signature"%str(func))
        EventHandler.helper_funcs[name] = func
        EventHandler.helper_funcs[name].info = funcinfo

    @staticmethod
    def getfunc(funcname):
        """Return helper func"""
        try: return EventHandler.helper_funcs[funcname]
        except KeyError: raise ValueError("no such helper function '%s'"%funcname)

################################################################################

class Uri:
    """URI for some filename or file-object
    """
    fspath = '' # path in FS (if exists in FS)
    url = '' # URL to object (in Web or FS)
    name = '' # short name

    def __init__(self, file):
        """file may be string filename or file-object
        >>> import tempfile, os
        >>> tmpdir = os.path.normpath(tempfile.gettempdir())
        >>> str(Uri('http://sub.aaa.com/my'))
        "Uri(fspath='', url='http://sub.aaa.com/my', name='my')"
        >>> str(Uri('http://sub.aaa.com/my/path.htm?q1=1&q2=2'))
        "Uri(fspath='', url='http://sub.aaa.com/my/path.htm?q1=1&q2=2', name='path.htm')"

        # Try 'file://<TMPDIR>'; may faults in splitdrive()
        >>> u = Uri('file://'+tmpdir)
        >>> u.fspath == tmpdir
        True
        >>> u.name == os.path.split(tmpdir)[1]
        True
        >>> u.url.startswith('file:///')
        True
        >>> os.path.splitdrive(tmpdir)[1] == os.path.normpath(os.path.splitdrive(u.url[8:])[1])
        True

        # The same but without 'file://'
        >>> u = Uri(tmpdir)
        >>> u.fspath == tmpdir
        True
        >>> u.name == os.path.split(tmpdir)[1]
        True
        >>> u.url == 'file:' + pathname2url(tmpdir)
        True
        """
        try:
            if isinstance(file, StringTypes23):
                if FSURLRE.match(file):
                    # 'file://'
                    file = FSURLRE.sub('', file, 1)
                elif URLRE.match(file):
                    # 'oth-proto://'
                    self.fspath = ''
                    self.url = file
                    self.name = os.path.split(urlparse(self.url).path)[1]
                    return

                #if os.path.exists(file):
                self.fspath = os.path.abspath(file)
                self.url = 'file:'+pathname2url(self.fspath)
                self.name = os.path.split(self.fspath)[1]
                return
            else:
                url = getattr(file, 'url', '')
                if url:
                    self.fspath = ''
                    self.url = url
                    self.name = os.path.split(urlparse(self.url).path)[1]
                    return
                else:
                    name = getattr(file, 'name', '')
                    # check open(file.name).fileno() == file.fileno() - i.e. in
                    # current dir.
                    if name:
                        absname = os.path.abspath(name)
                        if os.path.exists(absname):
                            with open(absname, 'r') as checkfp:
                                # XXX in Python docs it's Unix func. but exists in Win too
                                if os.path.sameopenfile(file.fileno(), checkfp.fileno()):
                                    self.fspath = absname
                                    self.url = 'file:'+pathname2url(self.fspath)
                                    self.name = os.path.split(self.fspath)[1]
                                    return
        except: pass
        raise ValueError("Can not convert '%s' to Uri object"%file)

    def withbase(self, base):
        """Returns new URL string from self but with new base address:
        >>> u = Uri('http://sub.aaa.com/my')
        >>> u.withbase('')
        'http://sub.aaa.com/my'
        >>> u.withbase('ftp://a.b.c/')
        'ftp://a.b.c/my'
        >>> u = Uri('http://sub.aaa.com/x/y/z.htm')
        >>> u.withbase('ftp://a.b.c/')
        'ftp://a.b.c/x/y/z.htm'
        """
        if not base: return self.url
        else:
            assert bool(self.url)
            up = urlsplit(base)
            path = urlsplit(self.url).path
            up = up._replace(path=path)
            return urlunsplit(up)

    def getmoniker(self):
        """Return some unique name for system"""
        def _url2str(url):
            if not url: return ''
            if len(url) < 64: return url
            else: return url[:32] + ' ... ' + url[-32:]
        # return FS-path or URL-as-str or name or empty-name
        return self.fspath or _url2str(self.url) or self.name or 'unknown'

    def __repr__(self):
        return "%s(fspath='%s', url='%s', name='%s')"%\
                (self.__class__.__name__, self.fspath, self.url, self.name)

################################################################################

class Token:
    text = ''
    start = -1
    end = -1

    def __init__(self, text, start=-1, end=-1):
        self.text = text
        self.start = start
        self.end = end
    def __repr__(self):
        return '<%s at %d...%d: %s>' % (self.__class__.__name__, self.start, self.end, self.text)

class EndToken(Token): pass

class CmdToken(Token): pass

class InlCodeToken(Token):
    @staticmethod
    def linearize(text, nl=('\n',), space=' '):
        """Convert new-lines symbols|text-fragments (nl) to space:
        >>> InlCodeToken.linearize('aaa#bbb!ccc', nl=('#', '!'))
        'aaa bbb ccc'
        >>> InlCodeToken.linearize('##aaa##bbb###ccc#', nl='#', space='-')
        'aaa-bbb-ccc'
        >>> InlCodeToken.linearize('@LFaaa@CRbbb@LFccc@LF@LF', nl=('@CR', '@LF'), space='-')
        'aaa-bbb-ccc'
        >>> InlCodeToken.linearize('aaa\\n\\nbbb')
        'aaa bbb'
        """
        if isinstance(nl, (list, tuple)):
            nl = '|'.join('(%s)'%n for n in nl)
        re_ = '(%s)+'%nl
        cre_ = re.compile(re_)
        return cre_.sub(space, text).strip(space)

class BlkCodeToken(Token):
    def jointoken(self, token):
        """Join token to existent text"""
        self.text = self.text.rstrip('\n') + '\n' + token.text.lstrip('\n')
        self.end = token.end
        return self

################################################################################

class StopChain(Exception):
    """Stop chaining with result"""
    def __init__(self, result, *args):
        self._result = result
        Exception.__init__(self, *args)

class OneArgFunc:
    """Wrap one function with .procarg attribute - name of keyword argument of
    later call:
    >>> o = OneArgFunc(len, 'xxx')
    >>> repr(o)
    "OneArgFunc('len', 'xxx')"
    """
    def __init__(self, func, procarg):
        self.procarg = procarg
        self._func = func
    def __call__(self, value):
        return self._func(value)
    def __eq__(self, oth):
        return oth == self or getattr(oth, '_func', None) == self._func
    def __repr__(self):
        return 'OneArgFunc(%s, %s)'%(pprint.pformat(self._func.__name__), pprint.pformat(self.procarg))

class FuncChain:
    """Chain sequence of funcs. Func is something callable.
    To add funcs to sequence (before,after,instead - flex. piping),
    use put()
    """
    BEFORE = 0
    AFTER = 1
    INSTEAD = 2

    position = None # where to insert in chaining/piping
    items = None # callable list of items - chain

    def __init__(self, items=[], typesafe=True):
        """Init from iterable or items. typesafe - check that all
        items are callable:
        >>> f = FuncChain([1,2,3], typesafe=False)
        >>> f.items
        [1, 2, 3]
        """
        if not isinstance(items, Iterable): items = [items]

        if typesafe and any(not isinstance(el, Callable) for el in items):
            raise ValueError('some of items are not callable')
        self.items = []
        self.items.extend(list(items))

    def __getitem__(self, i): return self.items[i]

    def __len__(self): return len(self.items)

    def chain(self, othfuncchain):
        """Chain one FuncChain with another. Position is obtaned from
        othfuncchain:
        >>> def fall(_self, **args): args['x'] *= 100; return args
        >>> def fone(arg): arg += 1; return arg
        >>> EventHandler.register_func('fall', fall)
        >>> EventHandler.register_func('fone', fone)

        Try to do chaning and calling:
        >>> fc = FuncChain()
        >>> fc.put(FuncChain.AFTER, [OneArgFunc(fone, 'x')]) and None
        >>> fc.chain(FuncChain().parse('fall|'))
        >>> res = fc(None, x=23, z=9)
        >>> res['x'], res['z']
        (2301, 9)
        >>> fc = FuncChain()
        >>> fc.put(FuncChain.AFTER, [OneArgFunc(fone, 'x')]) and None
        >>> fc.chain(FuncChain().parse('|fall'))
        >>> res = fc(None, x=23, z=9)
        >>> res['x'], res['z']
        (2400, 9)
        >>> fc = FuncChain()
        >>> fc.put(FuncChain.AFTER, [OneArgFunc(fone, 'x')]) and None
        >>> fc.chain(FuncChain().parse('|fone z'))
        >>> res = fc(None, x=23, z=9)
        >>> res['x'], res['z']
        (24, 10)
        >>> fc = FuncChain()
        >>> fc.put(FuncChain.AFTER, [OneArgFunc(fone, 'x')]) and None
        >>> fc.chain(FuncChain().parse('|fone x fone z'))
        >>> res = fc(None, x=23, z=9)
        >>> res['x'], res['z']
        (25, 10)
        >>> fc = FuncChain()
        >>> fc.put(FuncChain.AFTER, [fall]) and None
        >>> fc.chain(FuncChain().parse('|fone x fone z'))
        >>> res = fc(None, x=23, z=9)
        >>> res['x'], res['z']
        (2301, 10)
        >>> fc = FuncChain()
        >>> fc.put(FuncChain.AFTER, [fall]) and None
        >>> fc.chain(FuncChain().parse('fone x fone z|'))
        >>> res = fc(None, x=23, z=9)
        >>> res['x'], res['z']
        (2400, 10)
        >>> fc = FuncChain()
        >>> fc.put(FuncChain.AFTER, [OneArgFunc(fone, 'x')]) and None
        >>> fc.chain(FuncChain().parse('|fone y fone z'))
        >>> res = fc(None, x=23, z=9)
        Traceback (most recent call last):
            ...
        TypeError: handler has not such argument 'y'
        """
        self.put(othfuncchain.position, othfuncchain)

    def put(self, position, items, typesafe=True):
        """Put items before, after or instead of already existen.
        typesafe - check that all items are callable:
        >>> f = FuncChain([1,2,3], typesafe=False)
        >>> f.items
        [1, 2, 3]
        >>> f.put(FuncChain.BEFORE, [0, 0], typesafe=False).items
        [0, 0, 1, 2, 3]
        >>> f.put(FuncChain.AFTER, [4, 5], typesafe=False).items
        [0, 0, 1, 2, 3, 4, 5]
        >>> f.put(FuncChain.INSTEAD, [10, 20], typesafe=False).items
        [10, 20]
        >>> FuncChain().put(FuncChain.BEFORE, [1,2], typesafe=False).items
        [1, 2]
        >>> FuncChain().put(FuncChain.AFTER, [1,2], typesafe=False).items
        [1, 2]
        >>> FuncChain().put(FuncChain.INSTEAD, [1,2], typesafe=False).items
        [1, 2]
        """

        if not isinstance(items, Iterable): items = [items]

        if typesafe and any(not isinstance(el, Callable) for el in items):
            raise ValueError('some of items are not callable')

        if position == FuncChain.BEFORE:
            self.items[0:0] = items
        elif position == FuncChain.AFTER:
            self.items[len(self.items):len(self.items)] = items
        elif position == FuncChain.INSTEAD:
            self.items[0:len(self.items)] = items
        else:
            raise ValueError('incorrect value for position')
        return self

    def callall(self, _self, **args):
        """Call all chaining funcs. _self is self of
        object ref. which call (sender):
        >>> def fall(_self, **args): args['x'] *= 100; return args
        >>> def fone(arg): arg += 1; return arg
        >>> EventHandler.register_func('fall', fall)
        >>> EventHandler.register_func('fone', fone)

        Try to do several chaining calls:
        >>> fc = FuncChain().parse('|fall')
        >>> fc.put(FuncChain.BEFORE, [OneArgFunc(fone, 'x')]) and None
        >>> res = fc(None, x=23, z=9)
        >>> res['x'], res['z']
        (2400, 9)
        >>> fc = FuncChain().parse('|fall')
        >>> fc.put(FuncChain.AFTER, [OneArgFunc(fone, 'x')]) and None
        >>> res = fc(None, x=23, z=9)
        >>> res['x'], res['z']
        (2301, 9)
        """
        _args = args.copy()
        try:
            for c in self.items:
                # c is some callable with .procarg attribute (to 
                # process only one argument of input-args-dictionary)
                procarg = getattr(c, 'procarg', '*')
                if procarg == '*':
                    #print 'CALL', c, 'g=',getattr(_self,'gpath',''), '_self=', _self, '_args=', _args
                    _args = c(_self, **_args)
                else:
                    if procarg not in _args:
                        raise TypeError("handler has not such argument '%s'"%procarg)
                    _args[procarg] = c(_args[procarg])
            #print 'RESULT=', _args
            return _args
        except StopChain as x:
            return x._result
    __call__ = callall

    def parse(self, text):
        """text is func calling expression:
            'fun' -> fun(**args)

            'fun1 a fun2 b' -> args['a'] = fun1(args['a'])
                            -> args['b'] = fun2(args['b'])

            '|fun1 a fun2 b' -> args = orig(args)
                             -> args['b'] = fun2(args['b'])
                             -> args['a'] = fun1(args['a'])

            '|fun' -> fun(orig(args))

            'fun|' -> orig(fun(args))
        etc.
        >>> def fall(_self, **args): pass
        >>> def fone(arg): pass
        >>> EventHandler.register_func('fall', fall)
        >>> EventHandler.register_func('fone', fone)
        >>> fc = FuncChain().parse('fall')
        >>> len(fc) == 1 and fc[0] == fall and fc.position == FuncChain.INSTEAD
        True
        >>> fc = FuncChain().parse('|fall')
        >>> len(fc) == 1 and fc[0] == fall and fc.position == FuncChain.AFTER
        True
        >>> fc = FuncChain().parse('fall|')
        >>> len(fc) == 1 and fc[0] == fall and fc.position == FuncChain.BEFORE
        True
        >>> fc = FuncChain().parse('|fall|')
        Traceback (most recent call last):
            ...
        ValueError: only one pipe symbol is allowed
        >>> fc = FuncChain().parse('fone xxx fone')
        Traceback (most recent call last):
            ...
        ValueError: 'func arg' pairs should be even
        >>> fc = FuncChain().parse('fone aaa fone bbb|')
        >>> len(fc) == 2 and fc.position == FuncChain.BEFORE
        True
        >>> fc[0].procarg == 'aaa' and fc[1].procarg == 'bbb'
        True
        >>> repr(fc[0]) == "OneArgFunc('fone', 'aaa')"
        True
        >>> repr(fc[1]) == "OneArgFunc('fone', 'bbb')"
        True
        >>> fc[0]._func == fone and fc[1]._func == fone
        True
        """
        self.items[:] = []
        position = None
        if text.startswith('|'):
            position = FuncChain.AFTER
            text = text.split('|', 1)[1].strip()
        elif text.endswith('|'):
            if position is not None: raise ValueError('only one pipe symbol is allowed')
            position = FuncChain.BEFORE
            text = text.rsplit('|', 1)[0].strip()
        else:
            position = FuncChain.INSTEAD
        arr = text.split()
        if len(arr) == 1:
            # one function
            func = EventHandler.getfunc(arr[0])
            if func.info['signature'] != EventHandler.KWARGFUNC:
                raise TypeError("function '%s' has illegal signature %s"%(arr[0], func.info['signature']))
            self.items.append(func)
        elif len(arr)%2:
            # odd number
            raise ValueError("'func arg' pairs should be even")
        else:
            # several functions
            for funcname,procarg in islices(arr, 2):
                func = EventHandler.getfunc(funcname)
                if func.info['signature'] != EventHandler.ONEARGFUNC:
                    raise TypeError("function '%s' has illegal signature"%funcname)
                func = OneArgFunc(func, procarg)
                self.items.append(func)
        self.position = position
        return self

################################################################################

class ParserError(Exception): pass

class Parser:
    """Parse doc file"""
    descr = ''
    parsers = []
    chunkdict = None # ChunkDict object
    errloc = None # error locator object
    vars = None # {dict-name: vars-dict} of this parser
    handlers = None # list of EventHandler's
    outdir = '' # output directory (for saved files, used by FileCmd, RefsFile)
    infile = '' # input file name or file-object
    engine = None # LP instance (XXX may be None)

    ext = () # supported file extensions by concrete parser class
    surr = ('<<', '>>') # used when parse by concrete parser class
    config_params = ['ext:strlist', 'surr:strlist'] # params from config file (mandatory)

    def __init__(self, engine=None):
        """For doctests engine can be None"""
        self._reset()
        self.engine = engine

    def _reset(self):
        self.chunkdict = ChunkDict()
        self.errloc = ErrorLocator()
        self.vars = {ANONDICTNAME:{}}
        self.handlers = []
        CMDRE.change_surr(self.surr)
        self.outdir = os.getcwd()
        self.infile = ''

    @staticmethod
    def register(p):
        """Register new parser"""
        Parser.parsers.append(p)

    @classmethod
    def getcfgparams(class_):
        """Return names of config params"""
        return (s.split(':')[0] for s in class_.config_params)

    @classmethod
    def config(class_, name, value):
        """Configure concrete parser class"""
        def compilparam(s):
            arr = s.split(':')
            name, type = arr if len(arr)==2 else (arr[0], 'str')
            typefun = getattr(Cfgfile, type, None)
            assert typefun is not None
            return (name, typefun)
        paramsdict = dict(compilparam(p) for p in class_.config_params)
        if name not in paramsdict.keys():
            raise KeyError("Parameter '%s' is out of expected" % name)
        value = paramsdict[name](value)
        setattr(class_, name, value)

    def getindir(self):
        """Return input directory"""
        if self.infile:
            uri = Uri(self.infile)
            if uri.fspath:
                return os.path.dirname(uri.fspath)
        return os.getcwd()

    def ensureinput(self, path):
        """Return full path/URL from path/URL. If path is relative path (FS),
        try to treat it as in the same dir. as input directory of parser (with
        already parsed input file!). If path is relative but URL, return abs.
        URL (see absurl()).
        If it's FS path (not URL) and not exists, returns None
        """
        uri = Uri(self.infile)

        if URLRE.match(path):
            # if path is URL return it
            return path
        if not uri.fspath:
            # else path is local BUT input file is not (is URL), so return absurl. of path
            return absurl(uri.url, path)
        if not os.path.isabs(path):
            path = os.path.join(self.getindir(), path)
            if os.path.exists(path): return path
        return None

    def tokens(self, text):
        """Abstract: Iterator over tokens"""
        raise NotImplementedError

    @classmethod
    def findlines(class_, text, delim='\n'):
        """Split text to lines coordinates (coords of line-breaking symbols).
        delim is one symbol or list/tuple of symbols as line delimiters.
        If text of file is not usual text, this method should be reloaded!"
        >>> text = '@aaa bbb!ccc!ddd@'
        >>> Parser.findlines(text, delim=('!', '@'))
        [0, 8, 12, 16]
        >>> text = '\\naaa bbb\\nccc\\nddd\\n'
        >>> Parser.findlines(text)
        [0, 8, 12, 16]
        """
        lncoords = []
        if isinstance(delim, StringTypes23):
            splitter_re_ = re.escape(delim)
        else:
            splitter_re_ = '(%s)' % '|'.join(re.escape(s) for s in delim)
        splitter_re = re.compile(splitter_re_)
        for m in splitter_re.finditer(text):
            lncoords.append(m.start(0))
        return lncoords

    def readfile(self, file):
        """Returns content of file"""
        if isinstance(file, StringTypes23):
            return fread23(file)
        else:
            # XXX replace() is hack!
            return fix_crlf(bytestostr23(file.read()))

    @staticmethod
    def _prepare_cmd(cmdtext, bodytexts):
        """Prepare list of pairs (cmdtext, cmdbody) from cmdtext (path) and
        body texts:
        >>> Parser._prepare_cmd('c.a', [])
        [('c.a', '')]
        >>> Parser._prepare_cmd('c.a', ['b'])
        [('c.a', 'b')]
        >>> Parser._prepare_cmd('c.a', ['b1', 'b2'])
        [('c.a.0', 'b1'), ('c.a.1', 'b2')]
        """
        bodytextlen = len(bodytexts)
        if bodytextlen == 0:
            return [(cmdtext, '')]
        elif bodytextlen == 1:
            return [(cmdtext, bodytexts[0])]
        elif bodytextlen > 1:
            return [('%s.%s'%(cmdtext, ci), b) for ci,b in enumerate(bodytexts)]

    def _instance_handlers(self, obj):
        """There are 2 kind of handlers: class-based, created with <<on.CLASS...>>
        and instance-based, created with <<cmd, do.EVENT:...>>. Class-based are
        created by OnCmd.__ondefine__(). Before emit event, instance handlers should
        be created and added first
        """
        handlers = []
        if isinstance(obj, Cmd):
            cmd = obj
            if not hasattr(cmd, '__ondefine__'):
                # add handler from do.EVENTx attributes, but only if
                # no __ondefine__ method, which means 'No any handling!'
                classname = cmd.__class__.__name__
                for argname, argvalue in cmd.args:
                    if argname.startswith('do.'):
                        # some handler
                        event = argname[3:] # 3==len('do.')
                        params = dict(classname=classname, event=event)
                        if event == 'paste':
                            params['gpath'] = cmd.jpath()
                        else:
                            params['id'] = id(cmd)
                        functext = argvalue
                        func = FuncChain().parse(functext)
                        handlers.append(EventHandler(func, **params))
        return handlers

    def emitevent(self, obj, event, **args):
        """Call all handlers and object onXXX() if no __onXXX__().
        Otherwise call only __onXXX__()
        """
        methname = 'on%s'%event; __methname__ = '__%s__'%methname
        meth = getattr(obj.__class__, methname, None)
        __meth__ = getattr(obj, __methname__, None)
        if __meth__:
            # if there is hidden for handlers callback - call it only
            return __meth__(**args)
        elif not meth:
            # XXX is really need to have onXXX() ?
            # else if no usual callback - raise error
            raise AttributeError("'%s' should have '%s' method" % \
                    (obj.__class__.__name__, methname))
        else:
            # routing all handlers and usual callback
            _weights = dict(func=2, BEFORE=1, INSTEAD=3, AFTER=5)
            def _weight(c):
                """for reducing/sorting piped callables:
                'weight' of some callable 'c'
                """
                if isinstance(c, FuncChain):
                    if c.position == FuncChain.BEFORE:
                        return _weights['BEFORE']
                    elif c.position == FuncChain.INSTEAD:
                        return _weights['INSTEAD']
                    elif c.position == FuncChain.AFTER:
                        return _weights['AFTER']
                else:
                    return _weights['func']

            def _order(acc, c):
                """reducer function: accumulate or drop out callable 'c'
                """
                if not acc: acc = [c]
                else:
                    w1 = _weight(acc[-1])
                    w2 = _weight(c)
                    if w2 == _weights['INSTEAD']:
                        acc[-1] = c
                    elif w2 >= w1:
                        acc.append(c)
                    elif w2 < w1:
                        acc.insert(len(acc)-1, c)
                return acc

            # add add instance handlers
            self.updatehandlers(self._instance_handlers(obj))

            # get responsible handlers for this obj and event
            handlers = [meth]
            handlers.extend(h.handler_func for h in self.handlers if h.canhandle(obj, event))
            # reduce/sort - apply piping order
            handlers = functools.reduce(_order, handlers, [])
            #print 'H', handlers
            todo = FuncChain(handlers)
            return todo(obj, **args)

    def define_chunk(self, cmdtext, bodytexts):
        """Define new chunk with cmdtext (path) and list of body texts:
        >>> p = Parser()
        >>> p.define_chunk('c.a', ['b1', 'b2', 'b3'])
        >>> p.chunkdict.globpath('c.a.*', _onlypath=True)
        ['c.a.0', 'c.a.1', 'c.a.2']
        >>> p.chunkdict.getbypath('c.a.0')[1].orig
        'b1'
        >>> p.chunkdict.getbypath('c.a.2')[1].orig
        'b3'
        """
        p = Parser._prepare_cmd(cmdtext, bodytexts)
        for cmdtext, bodytext in p:
            cmd = Cmd.create_cmd(CMDRE.surround(cmdtext))
            #bodytext = cmd.ondefine(parser=self, chunktext=bodytext)['chunktext']
            bodytext = self.emitevent(cmd, 'define', parser=self, chunktext=bodytext)['chunktext']
            if bodytext is not None:
                self.chunkdict.define_chunk(cmd, Chunk(bodytext))

    @staticmethod
    def create_parser(engine, path='', fmt=''):
        """General parser factory. path is FS-path or URL (but fmt is mandatory
        is this case!)
        """
        if fmt:
            ext = '.' + fmt.strip('.').lower()
        elif path:
            ext = os.path.splitext(path)[1].lower()
        # find concrete parser class
        for cls in Parser.parsers:
            if ext in cls.ext:
                break
        else:
            raise ParserError('Unsupported file type')
        # return its instance
        return cls(engine=engine)

    def parsefile(self, file, flush=True, outdir=''):
        """General usage method for processing input file.
        Flag flush enable writing files with <<file.*, FSPATH>> command.
        outdir - where to save files.
        Returns self
        """
        if not outdir:
            outdir = '' # None/False -> ''
        elif not os.path.exists(outdir):
            raise ParserError("Output directory '%s' does not exists"%outdir)

        self._reset()
        if isinstance(file, StringTypes23):
            if URLRE.match(file):
                # its URL, not file name
                file = urlopen(file)
                return self.parsefile(file, flush=flush, outdir=outdir)
            else:
                self.infile = os.path.abspath(file)
                if not os.path.exists(self.infile):
                    raise ValueError("No such file '%s'"%self.infile)
        else:
            # treats as file-object
            self.infile = file

        # determine self.outdir
        if outdir: self.outdir = outdir
        else:
            uri = Uri(self.infile)
            if uri.fspath:
                self.outdir = os.path.dirname(uri.fspath)
            else:
                self.outdir = os.getcwd()

        filetext = self.readfile(file)
        self.errloc.config(filename=Uri(self.infile).getmoniker(), lncoords=self.findlines(filetext))
        # parse file content
        self._parse(filetext)
        self.chunkdict.check_cycles()
        # post-process of commands
        for cmd in self.chunkdict.keys():
            #cmd.onpost(parser=self, flush=flush)
            self.emitevent(cmd, 'post', parser=self, flush=flush)
        return self

    # XXX does not reset parser state like parsefile()
    def _parse(self, text):
        """Parse with error info providing"""
        try:
            return self.__parse(text)
        except Exception as x:
            tb = sys.exc_info()[2]
            errlocation = self.errloc.locate()
            if not errlocation:
                raise
            else:
                file,line = errlocation
                reraise23(x, "[%s, %d] %s"%(file, line+1, str(x)), tb)

    # XXX does not check cycles, do it explicitly
    def __parse(self, text):
        """Parse text. Don't forget to check cycles after!
        """
        self.errloc.reset()
        tokens = self.tokens(text)
        #print '\n\n|', getattr(self.infile, 'url', ''), '|', tokens, '\n\n'
        state = 'start' # start|cmd|body
        # EndToken will terminate tokens ALWAYS
        notokens = all(isinstance(t, EndToken) for t in tokens)
        if notokens:
            return 0

        self.errloc.config(pos=tokens[0].start)
        itok = 0
        cmdtext = ''; bodytexts = []
        while True:
            token = tokens[itok]
            self.errloc.config(pos=token.start)
            if state == 'start':
                if isinstance(token, CmdToken):
                    cmdtext = token.text
                    state = 'cmd'
                else:
                    raise ParserError('syntax error: expected CmdToken')
            elif state == 'cmd':
                if isinstance(token, (InlCodeToken, BlkCodeToken)):
                    bodytexts.append(token.text)
                    state = 'body'
                elif isinstance(token, CmdToken):
                    self.define_chunk(cmdtext, bodytexts) # bodytexts is []
                    state = 'start'
                    cmdtext = ''; bodytexts = []
                    continue
                elif isinstance(token, EndToken):
                    self.define_chunk(cmdtext, bodytexts) # bodytexts is []
                    break
                else:
                    raise ParserError('syntax error: expected InlCodeToken or BlkCodeToken')
            elif state == 'body':
                if isinstance(token, (InlCodeToken, BlkCodeToken)):
                    bodytexts.append(token.text)
                elif isinstance(token, CmdToken):
                    self.define_chunk(cmdtext, bodytexts)
                    state = 'start'
                    cmdtext = ''; bodytexts = []
                    continue
                elif isinstance(token, EndToken):
                    self.define_chunk(cmdtext, bodytexts)
                    break
            itok += 1
        return len(self.chunkdict)

    def expand(self, path, **args):
        return self.chunkdict.expand(path, parser=self, **args)

    def updatevars(self, dictname, varsdict):
        """Add new vars dict under dictname:
        """
        if not dictname: dictname = ANONDICTNAME
        if dictname in self.vars:
            # this dict already exists
            self.vars[dictname].update(varsdict)
        else:
            # no such dict yet
            self.vars[dictname] = varsdict.copy()

    def updatehandlers(self, handlers):
        """Add new event handlers"""
        self.handlers.extend(handlers)

    def getvar(self, varname, dictname=UNDEFINED, default=UNDEFINED):
        """Get var value from dict (if dictname is used), args no mean,
        instead of containing of 'default'
        """
        #print '+++++++ Try to resolve var %s of dict %s'%(varname, dictname)
        if dictname is UNDEFINED:
            # dictname is not used, so get it from varname
            lastdot = varname.rfind('.')
            if lastdot != -1:
                # there are dots in varname
                dictname = varname[:lastdot]
                varname = varname[lastdot+1:]
            else:
                # no dots in varname - it's from anon dict
                varname = varname
                dictname = ANONDICTNAME
        # get value from dict (or default)
        if default is not UNDEFINED:
            return self.vars.get(dictname, {}).get(varname, default)
        else:
            return self.vars[dictname][varname]

    def _mergehandlers(self, othparser, path=''):
        """Merge handlers from another parser
        """
        handlers = othparser.handlers[:]
        for h in handlers:
            h.change_gpath(prefix=path)
        self.handlers.extend(handlers)

    def _mergevars(self, othparser, path=''):
        """Merge vars dictionaries with vars of othparser. They names
        will be prefixed with path. Inheritance is supported: othparser
        vars will be reloaded by itself vars:
        >>> p0 = Parser()
        >>> p0.updatevars('', {'v1':1, 'v2':2})
        >>> p0.updatevars('d1', {'v1':10, 'v2':20})
        >>> p0.getvar('v1'), p0.getvar('v2')
        (1, 2)
        >>> p0.getvar('d1.v1'), p0.getvar('d1.v2')
        (10, 20)

        >>> p1 = Parser()
        >>> p1.updatevars('', {'v1':1, 'v2':2})
        >>> p1.updatevars('d1', {'v1':10, 'v2':20})
        >>> p1.getvar('v1'), p1.getvar('v2')
        (1, 2)

        >>> p2 = Parser()
        >>> p2.updatevars('', {'v1':100, 'v2':200, 'v3':300})
        >>> p2.updatevars('d1', {'v1':1000, 'v2':2000, 'v3':3000})
        >>> p2.getvar('v1'), p2.getvar('v2'), p2.getvar('v3')
        (100, 200, 300)
        >>> p2.getvar('d1.v1'), p2.getvar('d1.v2'), p2.getvar('d1.v3')
        (1000, 2000, 3000)

        >>> p0._mergevars(p2)
        >>> p0.getvar('v1'), p0.getvar('v2'), p0.getvar('v3'), p0.getvar('d1.v1'), p0.getvar('d1.v3')
        (1, 2, 300, 10, 3000)

        p1 is unmodified:
        >>> p1.getvar('v1'), p1.getvar('v2'), p0.getvar('d1.v1'), p1.getvar('d1.v2')
        (1, 2, 10, 20)

        But no such var in p1:
        >>> p1.getvar('d1.v3')
        Traceback (most recent call last):
            ...
        KeyError: 'v3'

        >>> p1._mergevars(p2, 'x')
        >>> p1.getvar('v1'), p1.getvar('v2'), p1.getvar('d1.v1'), p1.getvar('d1.v2')
        (1, 2, 10, 20)
        >>> p1.getvar('v3')
        Traceback (most recent call last):
            ...
        KeyError: 'v3'
        >>> p1.getvar('d1.v3')
        Traceback (most recent call last):
            ...
        KeyError: 'v3'
        >>> p1.getvar('x.v3'), p1.getvar('x.d1.v3')
        (300, 3000)
        """
        for dictname, vars in othparser.vars.items():
            if path:
                # if there is path, imported dicts will have new names
                newdictname = '.'.join((path, dictname))
                if dictname == ANONDICTNAME:
                    # if import anon. dict with new path, it's be==path, i.e.
                    # $v == $anon.v, but the same with new path: $path.v
                    newdictname = path
            else:
                # if no path, amm other var. dicts will be with the same names
                newdictname = dictname
            if newdictname in self.vars:
                # there is such dict (under newdictname sure)
                myvars = self.vars[newdictname]
                for varname, varvalue in vars.items():
                    if varname not in myvars:
                        # import only unique names (inverse inheritance)
                        myvars[varname] = varvalue
            else:
                self.vars[newdictname] = vars.copy()

    def importparser(self, othparser, path=''):
        """Does importing of one parsed file (result of parsing is in othparser)
        with self
        """
        self.chunkdict.merge(othparser.chunkdict, path)
        self.chunkdict.check_cycles()
        self._mergevars(othparser, path)
        self._mergehandlers(othparser, path)

################################################################################

class Cfgfile(dict):
    """Config. file (rc-format) loader and parser
    """
    filename = None # loaded file path

    # config file param convert-functions:
    @staticmethod
    def strlist(value):
        """Convert string value as 'a,b,c...' to list of strings"""
        res = [s.strip() for s in value.split(',')]
        if all(not s for s in res): return []
        else: return res

    str = str
    int = int
    float = float

    def load(self, filename):
        self.filename = filename
        with open(self.filename, "rt") as ifile:
            for line in ifile:
                line = line.strip()
                if not line or line.startswith('#'): continue
                k, v = [s.strip() for s in line.split('=')]
                self[k] = v

################################################################################

class ErrorLocator:
    """Used to locate parsing error: what file and where in the file
    error occurs
    """
    filename = None # parsed file name
    lncoords = None # positions of lines: coords of its line-breaking symbol
    pos = None # position in text; must be set before locate() call

    def __init__(self):
        self.filename = ''
        self.lncoords = []

    def config(self, filename=None, lncoords=None, pos=None):
        """Set current context, lncoords is the list of line coordinates:
        >>> l = ErrorLocator()
        >>> l.config('file', [50, 20, 10, 0, 4])
        >>> l.lncoords
        [0, 4, 10, 20, 50]
        >>> l.config(pos=10)
        >>> l.pos
        10
        """
        if filename is not None:
            self.filename = filename
        if lncoords is not None:
            lncoords.sort()
            self.lncoords = lncoords
        if pos is not None:
            self.pos = pos

    def reset(self):
        """Opposite to config(), after call, locate() w/o pos arg returns None"""
        self.pos = None

    def locate(self, pos=None, default=True):
        """Get current context for pos symbol position in
        file text, if pos is None, self.pos is used:
        >>> l = ErrorLocator()
        >>> l.locate(12, default=False) is None
        True
        >>> l.locate(12, default=True)
        ('<str>', 0)
        >>> l.config('file', [0, 30, 20, 10, 55])
        >>> l.locate(12)
        ('file', 2)
        >>> l.config(pos=1)
        >>> l.locate()
        ('file', 1)
        """
        if pos is None: pos = self.pos

        if self.filename and self.lncoords and pos is not None:
            return (self.filename, self._findline(pos))
        else:
            return ('<str>', 0) if default else None 

    def _findline(self, pos):
        """Find line number for this text position:
        >>> l = ErrorLocator()
        >>> l.config('file', [0, 30, 20, 10, 55])
        >>> l._findline(0)
        0
        >>> l._findline(1)
        1
        >>> l._findline(10)
        1
        >>> l._findline(19)
        2
        >>> l._findline(30)
        3
        >>> l._findline(31)
        4
        >>> l._findline(55)
        4
        >>> l._findline(56)
        5
        >>> l._findline(100)
        5
        """
        for ln, lncoord in enumerate(self.lncoords):
            if pos <= lncoord:
                return ln
        return ln+1

################################################################################

class Lp:
    """Engine"""
    cfgfile = None # config file loader (dict)
    quiet = False

    def __init__(self, cfgfile='lprc', quiet=False):
        self.cfgfile = Cfgfile()
        self.quiet = quiet
        # load configuration from cfgfile (abs. path or in current dir)
        cfgfile = os.path.abspath(cfgfile)
        self.cfgfile.load(cfgfile) # config file name
        for parser_class in Parser.parsers:
            cfgparser_class = parser_class.__name__.upper() # name of class in cfg file
            # obtain config values
            for param in parser_class.getcfgparams():
                cfgparam = '%s_%s' % (cfgparser_class, param.upper())
                parser_class.config(param, self.cfgfile[cfgparam])

