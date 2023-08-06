# Engine module
# Author: Balkansoft.BlogSpot.com
# GNU GPL licensed
#
# TODO Improve OOParser and make general XML/HTML parser and inherits it
# in OOParser

__VERSION__ = '1.0g'
__ABOUT__ = 'Nano LP, v. %s'%__VERSION__

import re
import os
import sys
import copy
import getopt
import string
import pprint
import random
import fnmatch
import zipfile
import itertools
import xml.sax as sax
import xml.sax.saxutils as saxutils
from collections import OrderedDict

CSSFILENAME = 'nanolp.css'
ANONDICTNAME = '_anon'
UNDEFINED = ['undefined']

################################################################################
# Python 2 -> 3 compatibility

_PY23 = 3 if sys.version_info.major > 2 else 2

# to avoid syntax errors (reraise23() for ex.) implements in different modules
if _PY23 == 2:
    from nanolp.lpcompat2 import *
elif _PY23 == 3:
    from nanolp.lpcompat3 import *

#################################################################################

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
    gpath = None # global path matcher for class factory (Cmd-for not matched)
    commands = [] # registered Cmd successors (or used base Cmd)

    text = None # original text
    ispaste = None # pasting or definition
    isset = None # set of commands or one ('*' is used in path)
    path = None # list of path components (with possible '*')
    args = None # list of pairs: (key, value)
    body = None # list of unnamed args
    indent = None # indent string

    def _reset(self):
        """Reset internal fields"""
        self.text = ""
        self.ispaste = False
        self.isset = False
        self.path = []
        self.args = []
        self.body = []
        self.indent = ''

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
    def textcmd(text=None, indent=''):
        """Cmd factory, returns INSTANCE:
        >>> c = Cmd.textcmd('<<use, file.h>>')
        >>> isinstance(c, UseCmd)
        True
        >>> c = Cmd.textcmd('<<file.x, file.h>>')
        >>> isinstance(c, UseCmd)
        False
        """
        cmd = Cmd(text=text, indent=indent)
        for cls in Cmd.commands:
            if cmd.matchpath(cls.gpath):
                return cls(cmd=cmd)
        else:
            return cmd

    def matchpath(self, patt):
        """Match me with glob-style path pattern:
        >>> p = Cmd.textcmd('<<c.f>>')
        >>> p.matchpath('c*')
        True
        >>> p.matchpath('*x')
        False
        """
        re_ = fnmatch.translate(patt)
        cre = re.compile(re_)
        return bool(cre.match(self.jpath()))

    def setpath(self, path=None, prefix=None, suffix=None):
        """Change path with optional prefix (str|list|tuple),
        suffix (str|list|tuple). IF no path, current is used:
        >>> p = Cmd.textcmd('<<c.f>>')
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
        >>> d[Cmd.textcmd('<<c.f>>')] = 123
        >>> d[Cmd.textcmd('<<c.f>>')]
        123
        >>> d[Cmd.textcmd('<<c.f, x>>')] = 321
        >>> d[Cmd.textcmd('<<c.f,  x>>')]
        321
        >>> d[Cmd.textcmd('<<c.f>>')]
        123
        >>> Cmd.textcmd('<<c.f1>>') in d
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

    def getarg(self, args, default=None):
        """Returns value of named arg (or arg aliases, args may be list or str):
        >>> c = Cmd.textcmd()
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
        >>> Cmd.textcmd('')
        Traceback (most recent call last):
            ...
        CmdError: mismatch form
        >>> c = Cmd.textcmd()
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
        >>> c.parse('<<c.sum, x.y:10>>')
        Traceback (most recent call last):
            ...
        CmdError: arg 'x.y' contains unallowed symbols
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
        >>> c.parse('<<c.sum, a:b, *:*>>') and c.body==[] \
                and c.args==[('a', 'b'), ('novars', True)]
        True
        """
        # These symbols may be quoted with '\'
        QUOTE = (',',)
        def _quote_text(txt):
            for i,q in enumerate(QUOTE):
                txt = txt.replace(r'\%s'%q, '@Q%d@'%i)
            return txt
        def _unquote_text(txt):
            for i,q in enumerate(QUOTE):
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
            arg = _unquote_text(arg)
            tmp = [t.strip() for t in arg.split(':', 1)]
            tmplen = len(tmp)
            if tmplen == 1:
                self.body.append(tmp[0])
            elif tmplen == 2:
                # process argument
                if tmp[0] == '*':
                    if tmp[1] == '*':
                        self.args.append(('novars', True))
                    elif tmp[1].startswith('$'):
                        self.args.append(('varsdict', tmp[1][1:]))
                else:
                    if any(tmp0ch in string.punctuation for tmp0ch in tmp[0]):
                        raise CmdError("arg '%s' contains unallowed symbols"%tmp[0])
                    self.args.append((tmp[0], tmp[1]))
        return True

    # events

    def ondefine(self, parser, chunktext):
        """Calling on define new chunk with this cmd.
        Should returns modified or original chunk text.
        If returns None, adding is disable (skipped).
        """
        return chunktext

    def onpost(self, parser, flush):
        """Called on post-processing of input.
        parser is concrete Parser object, flush is flag - flushing to
        file is enabled
        """
        pass

################################################################################

class UseCmd(Cmd):
    """Processor of <<use...>> command"""
    gpath = "use"

    inclfilename = '' # path to included file

    def onpost(self, parser, flush):
        chunk = parser.chunkdict.getbykey(self)
        self.inclfilename = ''.join(self.body)
        self.inclfilename = os.path.join(parser.indir, self.inclfilename)
        mnt = self.getarg('mnt', '')
        sys.stderr.write("using '%s' mounted to '%s'...\n"%(self.inclfilename, mnt))
        inclparser = Parser.fileparser(self.inclfilename)
        inclparser.parsefile(self.inclfilename, flush=False)
        parser.importparser(inclparser, mnt)
Cmd.commands.append(UseCmd)

################################################################################

class FileCmd(Cmd):
    """Processor of <<file...>> command"""
    gpath = "file.*"

    outfilename = '' # path to output file

    def onpost(self, parser, flush):
        if flush:
            jpath = self.jpath()
            chunk = parser.chunkdict.getbykey(self)
            if not parser.expand(jpath):
                raise ParserError("'%s' can not be expanded"%jpath)
            # body of out is output file name
            self.outfilename = ''.join(self.body)
            self.outfilename = os.path.join(parser.indir, self.outfilename)
            sys.stderr.write("writing to '%s'...\n"%self.outfilename)
            fwrite23(self.outfilename, chunk.tangle)
Cmd.commands.append(FileCmd)

################################################################################

class VarsCmd(Cmd):
    """Processor of <<vars...>> command"""
    gpath = "vars"

    def ondefine(self, parser, chunktext):
        """Add dictionary of vars, body[0] of Cmd will be name of dict
        otherwise anonym. dict is used
        """
        parser.updatevars(self.body[0] if self.body else '', dict(self.args))
Cmd.commands.append(VarsCmd)

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
            result.append(Cmd.textcmd(txtdep.group(0), indent=indent))
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
        >>> cd1.define_chunk(Cmd.textcmd('<<c.sum>>'), Chunk('x + y'))
        True
        >>> cd2 = ChunkDict()
        >>> cd2.define_chunk(Cmd.textcmd('<<c.abs>>'), Chunk('x + y'))
        True
        >>> cd1.merge(cd2, 'a.b')
        >>> Cmd.textcmd('<<c.abs>>') in cd1.chunks
        False
        >>> Cmd.textcmd('<<a.b.c.abs>>') in cd1.chunks
        True
        >>> cd3 = ChunkDict()
        >>> cd3.define_chunk(Cmd.textcmd('<<c.sum>>'), Chunk('x + y'))
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
        >>> cd.define_chunk(Cmd.textcmd('<<c.sum>>'), Chunk('x + y'))
        True
        >>> Cmd.textcmd('<<c.sum>>') in cd.chunks
        True
        """
        self.chunks[cmd] = chunk
        return True

    @staticmethod
    def __askey(something):
        if isinstance(something, Cmd):
            return something
        elif isinstance(something, StringTypes23):
            return Cmd.textcmd(CMDRE.surround(something))
        else:
            return None

    def globpath(self, patt, _onlypath=False):
        """Return keys for pattern 'patt' - components
        may be '*' - match like glob. If '_onlypath', returns list of paths, not
        Cmd's (for tests purpose):
        >>> cd = ChunkDict()
        >>> cd.define_chunk(Cmd.textcmd('<<c>>'), Chunk('a'))
        True
        >>> cd.define_chunk(Cmd.textcmd('<<c.sum>>'), Chunk('a'))
        True
        >>> cd.define_chunk(Cmd.textcmd('<<c.abs>>'), Chunk('a'))
        True
        >>> cd.define_chunk(Cmd.textcmd('<<d.defs>>'), Chunk('a'))
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
            if cmd.matchpath(patt):
                found.append(cmd)
        if _onlypath:
            return [f.jpath() for f in found]
        else:
            return found

    def getbypath(self, key):
        """key is dotted path or Cmd:
        >>> cd = ChunkDict()
        >>> cd.define_chunk(Cmd.textcmd('<<c.sum, a:1, b:2>>'), Chunk('x + y'))
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
        >>> cd.define_chunk(Cmd.textcmd('<<c.sum>>'), Chunk('x + y'))
        True
        >>> cd.define_chunk(Cmd.textcmd('<<c.abs>>'), Chunk('x + y'))
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
        >>> cd.define_chunk(Cmd.textcmd('<<c.sum>>'), Chunk('x + y'))
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
        >>> cd.define_chunk(Cmd.textcmd('<<c.a>>'), Chunk('aaa <<=c.b>> bbb'))
        True
        >>> cd.check_cycles()
        >>> cd.define_chunk(Cmd.textcmd('<<c.b>>'), Chunk('<<=c.a>>'))
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
        >>> cd.define_chunk(Cmd.textcmd('<<c.a>>'), Chunk('aaa <<=c.b, d:end, x:10>> bbb'))
        True
        >>> cd.define_chunk(Cmd.textcmd('<<c.b>>'), Chunk('<<=c.d, y:2>> $d'))
        True
        >>> cd.define_chunk(Cmd.textcmd('<<c.d>>'), Chunk('xxx $x $y'))
        True
        >>> cd.expand('c.a')
        True
        >>> cd.getbypath('c.a')[1].tangle
        'aaa xxx 10 2 end bbb'

        >>> cd = ChunkDict()
        >>> cd.define_chunk(Cmd.textcmd('<<c.a>>'), Chunk('aaa'))
        True
        >>> cd.define_chunk(Cmd.textcmd('<<c.b>>'), Chunk('bbb'))
        True
        >>> cd.define_chunk(Cmd.textcmd('<<c>>'), Chunk('ccc <<=c.*, join:\\,>> ddd'))
        True
        >>> cd.expand('c')
        True
        >>> cd.getbypath('c')[1].tangle
        'ccc aaa,bbb ddd'

        >>> cd = ChunkDict()
        >>> cd.define_chunk(Cmd.textcmd('<<c.a>>'), Chunk('aaa <<=c.b>>'))
        True
        >>> cd.define_chunk(Cmd.textcmd('<<c.b>>'), Chunk('bbb <<=c.a>>'))
        True
        >>> cd.define_chunk(Cmd.textcmd('<<c>>'), Chunk('ccc <<=c.*, join:\\,>> ddd'))
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
        return depsaredone and chunk.isdone

################################################################################

# TODO add info about all 'use' files, index of cmd, all saved 'file's, all 'var's,
# configuration of used parser
class RefsFile:
    """Generates references HTML file"""
    _css = '''
body {
	background-color: white;
    font-size: 12px;
	margin: 0;
	padding: 0;
}

.outputinfo {
    width: 100%;
    border-style: none;
}

.outputinfo td {
    vertical-align: middle;
}

.outputinfo .code {
    background-color: white;
}

.outputinfo .param {
	color: #111166;
}

.chunkinfo {
    width: 100%;
    border-style: none;
}

.param {
	width: 13ex;
	font-weight: bold;
	padding: 2px 10px 2px 0px;
	vertical-align: middle;
	text-align: right;
}

.code {
	background-color: #E0E0FF;
	display: inline-block;
	margin: 0;
	padding: 5px;
	display: inline-block;
	border: thin solid #AAF;
	border-radius: .5em;
}

h1 {
	color: #111166;
	margin: 0;
	padding: 10px 0 15px 10px;
	font-size: 24px;
}

#about {
	text-align: center;
	font-size: 10pt;
	font-family: Verdana;
	margin: 5px 0 10px 0;
}

h2 {
	color: #111166;
	padding-left: 10px;
	font-size: 22px;
}

#ctrlbar {
	background-color: #F0EBFE;
	border-color: #707070;
	border-style: none none solid none;
	border-width: 1px;
	margin: 0;
	padding: 5px 0 5px 5px;
}

.popup {
}

/*.popup * {
    position: relative;
}*/

.popup div {
    display: none;
}

.popup div #caption {
    display: block;
    text-align: center;
    font-weight: bold;
    margin: 2px 2px 5px 2px;
}

.popup div a {
    line-height: 2;
    display: block;
}

.popup:hover div {
    position: absolute;
    display: block;
    margin: 0;
    padding: 5px;
	background-color: #E6E6FF;
    color: black;
    /*max-width: 200px;*/
    border: 1px solid #C0C0C0;
    font: normal 10px/12px verdana;
    text-align:left;
    border-radius: .5em;
}
'''

    parser = None
    title = ''

    def __init__(self, parser, title=''):
        self.parser = parser
        self.title = title

    def __cmdurl(self, cmd):
        """Returns URL (name/href) from Cmd instance"""
        return str(hash(cmd.jpath())).replace('-', '_')

    def _header(self):
        return ('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">',
        '<html xmlns="http://www.w3.org/1999/xhtml">',
        '<head>',
        '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">',
        '<link rel="stylesheet" href="%s" type="text/css">' % CSSFILENAME,
        '<title>%s</title>' % self.title,
        '</head>',
        '<body>')

    def _footer(self):
        about = '<div id="about"><i>' \
                'Generated by <a href="http://code.google.com/p/nano-lp">%s</a>' \
                '</i></div>' % __ABOUT__
        return (about, '</body>', '</html>')

    def _output_info(self):
        """HTML tags for info about parser and it's results"""
        yield '<table class="outputinfo">'
        # Outputs - all FileCmd's
        cmds = self.parser.chunkdict.globpath(FileCmd.gpath)
        yield '<tr>'
        yield '<td class="param">Outputs:</td>'
        yield '<td>'
        for cmd in cmds:
            p = cmd.outfilename
            n = os.path.split(p)[1]
            yield '<a title="%s" href="file://%s">%s</a>&nbsp;&nbsp;' % (p, p, n)
        yield '</td>'
        yield '</tr>'
        # Includes - all UseCmd's
        cmds = self.parser.chunkdict.globpath(UseCmd.gpath)
        yield '<tr>'
        yield '<td class="param">Includes:</td>'
        yield '<td>'
        for cmd in cmds:
            p = cmd.inclfilename
            n = os.path.split(p)[1]
            yield '<a title="%s" href="file://%s">%s</a>&nbsp;&nbsp;' % (p, p, n)
        yield '</td>'
        yield '</tr>'
        # Index of commands
        cmds = self.parser.chunkdict.keys()
        yield '<tr>'
        yield '<td class="param">Index:</td>'
        yield '<td>'
        for cmd in sorted(cmds, key=lambda c:c.jpath()):
            yield '<a href="#%s">%s</a>&nbsp;&nbsp;' % (self.__cmdurl(cmd), cmd.jpath())
        yield '</td>'
        yield '</tr>'
        # Variables
        pre = pprint.pformat(self.parser.vars)
        yield '<tr>'
        yield '<td class="param">Variables:</td>'
        yield '<td>'
        if pre:
            yield '<pre class="code">'
            yield pre
            yield '</pre>'
        yield '</td>'
        yield '</tr>'
        yield '</table>'

    def __cmdref(self, cmd):
        """Returns <a> HTML tag (for cmd or list of commands-dependencies) OR
        tags for popup box"""
        jpath = cmd.jpath()
        for ch in jpath:
            if ch in ('?', '*', '['):
                break # glob path
        else:
            # not glob path
            return '<a href="#%s">%s</a>' % (self.__cmdurl(cmd), cmd.text)
        # glob path
        popup = ['<span class="popup">%s'%cmd.text, '<div><span id="caption">Matched:</span>']
        cmds = self.parser.chunkdict.globpath(jpath)
        for cmd in cmds:
            popup.append(self.__cmdref(cmd))
        popup.append('</div></span>')
        return ''.join(popup)

    def _body(self):
        yield '<div id="ctrlbar">'
        yield '<h1>%s</h1>' % self.title
        for y in self._output_info(): yield y
        yield '</div>'

        for cmd, chunk in self.parser.chunkdict.chunks.items():
            yield '<h2><a name="%s">%s</a></h2>'%(self.__cmdurl(cmd), cmd.jpath())

            yield '<table class="chunkinfo">'

            yield '<tr>'
            yield '<td class="param">pos-args:</td>'
            yield '<td>'
            last = len(cmd.body)-1; i = 0
            for posarg in cmd.body:
                yield saxutils.escape(posarg)
                if i != last: yield ', '
                i += 1
            yield '</td>'
            yield '</tr>'

            yield '<tr>'
            yield '<td class="param">kw-args:</td>'
            yield '<td>'
            last = len(cmd.args)-1; i = 0
            for n, v in cmd.args:
                yield '%s : %s' % (saxutils.escape(n), saxutils.escape(v))
                if i != last: yield ', '
                i += 1
            yield '</td>'
            yield '</tr>'

            yield '<tr>'
            yield '<td class="param">chunk:</td>'
            if chunk.orig:
                chunkorig = chunk.orig
                # next trick is replacing dep text with <A HREF> (or popup)
                # and escaping it's text without to escape <A HREF>/popup
                deprefs = []
                for dep in chunk.deps:
                    chunkorig = chunkorig.replace(dep.text, '__DEP:%d:'%len(deprefs))
                    # add one dep, but its jpath may be glob (matched several cmd's),
                    # so __cmdref() detects real number of dep's
                    deprefs.append(dep)
                chunkorig = saxutils.escape(chunkorig)
                chunkorig = re.sub(r'__DEP:(.+?):',
                        lambda m: self.__cmdref(deprefs[int(m.group(1))]),
                        chunkorig)
                yield '<td><pre class="code">%s</pre></td>' % chunkorig
            else:
                yield '<td>&nbsp;</td>'
            yield '</tr>'

            yield '</table>'
            yield '<hr width="100%" />'

    def save(self):
        cssfname = os.path.join(self.parser.indir, CSSFILENAME)
        if not os.path.exists(cssfname):
            # if CSS file doesnt exists, create
            sys.stderr.write("creating CSS-styles file '%s'...\n"%cssfname)
            fwrite23(cssfname, self._css)

        if not self.parser.infilename:
            # define output file name
            fname = os.path.join(self.parser.indir, 'nanolp-refs.html')
        else:
            fname = os.path.splitext(self.parser.infilename)[0] + '-refs.html'
        lines = itertools.chain(self._header(), self._body(), self._footer())
        text = '\n'.join(lines)
        sys.stderr.write("flushing references file '%s'...\n"%fname)
        fwrite23(fname, text)

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

# XXX not good that tokens() use text as input, better is to have
# feed(text='' OR filename='') and tokens() w/o args

class ParserError(Exception): pass

class Parser:
    """Parse doc file"""
    descr = None
    parsers = []
    chunkdict = None # ChunkDict object
    errloc = None # error locator object
    vars = None # {dict-name: vars-dict} of this parser
    indir = '' # input file directory (save output here too)
    infilename = '' # input file name

    ext = () # supported file extensions by concrete parser class
    surr = ('<<', '>>') # used when parse by concrete parser class
    config_params = ['ext:strlist', 'surr:strlist'] # params from config file (mandatory)


    def __init__(self):
        self._reset()

    def _reset(self):
        self.chunkdict = ChunkDict()
        self.errloc = ErrorLocator()
        self.vars = {ANONDICTNAME:{}}
        CMDRE.change_surr(self.surr)
        self.indir = os.getcwd()
        self.infilename = ''

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

    def readfile(self, filename):
        """Returns content of file"""
        return fread23(filename)

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
            return [('%s.%s'%(cmdtext, ci), b) \
                    for ci,b in enumerate(bodytexts)]

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
            cmd = Cmd.textcmd(CMDRE.surround(cmdtext))
            bodytext = cmd.ondefine(self, bodytext)
            if bodytext is not None:
                self.chunkdict.define_chunk(cmd, Chunk(bodytext))

    @staticmethod
    def fileparser(filename):
        """Parsers factory: find Parser class to parse file with such name
        (depends on ext) and returns it's INSTANCE"""
        ext = os.path.splitext(filename)[1]
        for cls in Parser.parsers:
            if ext in cls.ext:
                break
        else:
            raise ParserError('Unsupported file type')
        # return its instance
        return cls()

    def parsefile(self, filename, flush=True):
        """General usage method for processing input file.
        Flag flush enable writing files with <<file.*, FSPATH>> command.
        Returns used parser object
        """
        self._reset()
        self.infilename = os.path.abspath(filename)
        self.indir = os.path.dirname(self.infilename)
        filetext = self.readfile(filename)
        self.errloc.config(filename=filename, lncoords=self.findlines(filetext))
        self.parse(filetext)
        self.chunkdict.check_cycles()
        # post-process of commands
        for cmd in self.chunkdict.keys():
            cmd.onpost(self, flush)
        return self

    # XXX does not reset parser state like parsefile()
    def parse(self, text):
        """Parse with error info providing"""
        try:
            return self.__parse(text)
        except Exception as x:
            cls = sys.exc_info()[0]
            tb = sys.exc_info()[2]
            errlocation = self.errloc.locate()
            if not errlocation:
                raise
            else:
                file,line = errlocation
                reraise23(cls, "[%s, %d] %s"%(file, line+1, str(x)), tb)

    # XXX does not check cycles, do it explicitly
    def __parse(self, text):
        """Parse text. Don't forget to check cycles after!
        """
        self.errloc.reset()
        tokens = self.tokens(text)
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

################################################################################

# XXX Text parser aren't good, better is full lexical analizer instead of regexp

class MDParser(Parser):
    """Markdown parser:
    >>> text = \
    'Some text <<c.fun1>> `fun1-body1` and `fun2-body2` then\\n' \
    '<<c.fun2>> `fun2-body`'
    >>> p = MDParser()
    >>> p.parse(text)
    3
    >>> p.chunkdict.globpath('c.fun1.*', _onlypath=True)
    ['c.fun1.0', 'c.fun1.1']
    >>> p.chunkdict.globpath('c.fun2', _onlypath=True)
    ['c.fun2']
    >>> p.chunkdict.getbypath('c.fun1.0')[1].orig
    'fun1-body1'
    >>> p.chunkdict.getbypath('c.fun1.0')[1].tangle
    'fun1-body1'
    >>> p.chunkdict.getbypath('c.fun2')[1].tangle
    'fun2-body'
    >>> text = '<<c.f>> and <<c.f1>>'
    >>> p = MDParser()
    >>> p.parse(text)
    2
    >>> p.chunkdict.getbypath('c.f')[1].orig
    ''
    >>> p.chunkdict.getbypath('c.f1')[1].orig
    ''

    Another text, only command name and end of text then:
    >>> p._reset()
    >>> p.parse('Some text <<c.fun>>')
    1
    >>> p.chunkdict.getbypath('c.fun')[0].jpath()
    'c.fun'
    >>> p.chunkdict.getbypath('c.fun')[1].orig
    ''
    """

    descr = 'Markdown/MultiMarkdown'
    ext = ('.md',)

    def tokens(self, text):
        """
        >>> text = \
        'Example of Literate Programming in Markdown\\n' \
        '===========================================\\n\\n' \
        \
        'Code 1\\n' \
        '------\\n\\n' \
        \
        'Test if variable is negative looks like <<c.isneg>>: `if a < 0`.\\n' \
        'So, we can write absolute function <<c.fun>>:\\n\\n' \
        \
        '    def fun(x):\\n' \
        '        <<=c.isneg,a:v>>:\\n' \
        '            a += 100\\n' \
        '            return -a\\n\\n' \
        \
        'And <<c.sum>>:\\n\\n' \
        \
        '    def sum(x, y):\\n' \
        '        return x+y\\n\\n' \
        \
        'not code\\n' \
        'not code\\n\\n' \
         \
        'Lalalalalalal\\n' \
        'Lalalalalalal\\n'
        >>> p = MDParser()
        >>> toks = p.tokens(text)
        >>> [tok.__class__.__name__ for tok in toks]
        ['CmdToken', 'InlCodeToken', 'CmdToken', 'BlkCodeToken', 'CmdToken', 'BlkCodeToken', 'EndToken']
        >>> toks[0].text
        'c.isneg'
        >>> toks[1].text
        'if a < 0'
        >>> toks[2].text
        'c.fun'
        >>> toks[3].text.startswith('def fun')
        True
        >>> toks[3].text.endswith('return -a')
        True
        """
        # left padding fragment of code-block
        indents = (4*' ', '\t') # possible padding
        indents = '|'.join(re.escape(s) for s in indents)

        _inlcode_re = r'`([^`]+)`'
        _blkcode_re = r'^\n(?P<code>((%s)(.*?)\n|\n)+)$' % indents
        _blkcode_lstrip_re = '^(%s)' % indents

        inlcode_re = re.compile(_inlcode_re)
        blkcode_re = re.compile(_blkcode_re, re.MULTILINE)
        blkcode_lstrip_re = re.compile(_blkcode_lstrip_re, re.MULTILINE)

        cmds = CMDRE.cre('cmd').finditer(text)
        inlcodes = inlcode_re.finditer(text)
        blkcodes = blkcode_re.finditer(text)

        tokens = []

        for m in cmds:
            token = CmdToken(m.group(1), m.start(0), m.end(0))
            tokens.append(token)
        for m in inlcodes:
            tokentext = InlCodeToken.linearize(m.group(1))
            token = InlCodeToken(tokentext, m.start(0), m.end(0))
            tokens.append(token)
        for m in blkcodes:
            # find each block and replace first left indent with ''
            tokentext = m.group('code').strip('\n')
            tokentext = blkcode_lstrip_re.sub('', tokentext)
            token = BlkCodeToken(tokentext, m.start(0), m.end(0))
            tokens.append(token)

        tokens.sort(key=lambda tok: tok.start)
        tokens.append(EndToken(None))
        return tokens
Parser.parsers.append(MDParser)

################################################################################

class CreoleParser(Parser):
    descr = 'Creole'
    ext = ('.creole', '.cre', '.crl')

    def tokens(self, text):
        """
        >>> text = \
        '= Example of Literate Programming in Creole =\\n' \
        \
        '== Code 1 ==\\n' \
        \
        'Test if variable is negative looks like <<c.isneg>>: {{{if a < 0}}}.\\n' \
        'So, we can write absolute function <<c.fun>>:\\n\\n' \
        '{{{\\n' \
        '    def fun(x):\\n' \
        '        <<=c.isneg,a:v>>:\\n' \
        '            a += 100\\n' \
        '            return -a }}}\\n\\n' \
        \
        'And <<c.sum>>:\\n\\n' \
        \
        '{{{    def sum(x, y):\\n' \
        '        return x+y }}}\\n\\n' \
        \
        'not code\\n' \
        'not code\\n\\n' \
         \
        'Lalalalalalal\\n' \
        'Lalalalalalal\\n'
        >>> p = CreoleParser()
        >>> toks = p.tokens(text)
        >>> [tok.__class__.__name__ for tok in toks]
        ['CmdToken', 'BlkCodeToken', 'CmdToken', 'BlkCodeToken', 'CmdToken', 'BlkCodeToken', 'EndToken']
        >>> toks[0].text
        'c.isneg'
        >>> toks[1].text
        'if a < 0'
        >>> toks[2].text
        'c.fun'
        >>> toks[3].text.startswith('    def fun')
        True
        >>> toks[3].text.endswith('return -a')
        True
        """

        # XXX Only block chunks, inline and block Creole chunks are the same.
        # In real Creole distinguish block|inline chunks, but it's not
        # valuable for LP
        _blkcode_re = r'{{{\n*(?P<code>.*?)[\ \n]*}}}'

        blkcode_re = re.compile(_blkcode_re, re.DOTALL|re.MULTILINE)

        cmds = CMDRE.cre('cmd').finditer(text)
        blkcodes = blkcode_re.finditer(text)

        tokens = []

        for m in cmds:
            token = CmdToken(m.group(1), m.start(0), m.end(0))
            tokens.append(token)
        for m in blkcodes:
            # find each block and replace first left indent with ''
            tokentext = m.group('code')
            token = BlkCodeToken(tokentext, m.start(0), m.end(0))
            tokens.append(token)

        tokens.sort(key=lambda tok: tok.start)
        tokens.append(EndToken(None))
        return tokens
Parser.parsers.append(CreoleParser)

################################################################################

class RSTParser(Parser):
    """ReStructuredText parser"""
    descr = 'ReStructuredText'
    ext = ('.rst', '.rest', '.restr')

    def tokens(self, text):
        """
        >>> text = \
        'Example of Literate Programming in ReSt\\n' \
        '===========================================\\n\\n' \
        \
        'Code 1\\n' \
        '------\\n\\n' \
        \
        'Test if variable is negative looks like <<c.isneg>>: ``if a < 0``.\\n' \
        'So, we can write absolute function <<c.fun>>::\\n\\n' \
        \
        '    def fun(x):\\n' \
        '        <<=c.isneg,a:v>>:\\n' \
        '            a += 100\\n' \
        '            return -a\\n\\n' \
        \
        'And <<c.sum>>n\\n' \
        '::\\n\\n' \
        \
        '    def sum(x, y):\\n\\n' \
        \
        '        return x+y\\n\\n' \
        '    x += 1'
        >>> p = RSTParser()
        >>> toks = p.tokens(text)
        >>> [tok.__class__.__name__ for tok in toks]
        ['CmdToken', 'InlCodeToken', 'CmdToken', 'BlkCodeToken', 'CmdToken', 'BlkCodeToken', 'EndToken']
        >>> toks[0].text
        'c.isneg'
        >>> toks[1].text
        'if a < 0'
        >>> toks[2].text
        'c.fun'
        >>> toks[3].text.startswith('def fun')
        True
        >>> toks[3].text.endswith('        return -a')
        True
        >>> toks[5].text.startswith('def sum')
        True
        >>> toks[5].text.endswith('x += 1')
        True
        """

        _inlcode_re = r'``([^`]+)``'
        _blkcode_re = r'::\n\n(?P<code>.*?)(?:$|(?:\n\n[^ \t]+))'

        inlcode_re = re.compile(_inlcode_re)
        blkcode_re = re.compile(_blkcode_re, re.DOTALL)

        cmds = CMDRE.cre('cmd').finditer(text)
        inlcodes = inlcode_re.finditer(text)
        blkcodes = blkcode_re.finditer(text)

        tokens = []

        for m in cmds:
            token = CmdToken(m.group(1), m.start(0), m.end(0))
            tokens.append(token)
        for m in inlcodes:
            tokentext = InlCodeToken.linearize(m.group(1))
            token = InlCodeToken(tokentext, m.start(0), m.end(0))
            tokens.append(token)
        for m in blkcodes:
            # find each block and replace first left indent with ''
            tokentext = m.group('code').strip('\n')
            tokentext = deltextindent(tokentext)
            token = BlkCodeToken(tokentext, m.start(0), m.end(0))
            tokens.append(token)

        tokens.sort(key=lambda tok: tok.start)
        tokens.append(EndToken(None))
        return tokens
Parser.parsers.append(RSTParser)

################################################################################

class TeXParser(Parser):
    """TeX parser:
    >>> p = TeXParser()
    >>> p.parse('<<cmd>> \\\\verb#text#')
    1
    >>> p.chunkdict.getbypath('cmd')[1].tangle
    'text'

    More complex:
    >>> text = \
    'Some text <<c.fun1>> \\\\verb#fun1-body1# and \\\\verb!fun2-body2! then\\n' \
    '<<c.fun2>> \\\\verb{fun2-body}'
    >>> p = TeXParser()
    >>> p.parse(text)
    3
    >>> p.chunkdict.globpath('c.fun1.*', _onlypath=True)
    ['c.fun1.0', 'c.fun1.1']
    >>> p.chunkdict.globpath('c.fun2', _onlypath=True)
    ['c.fun2']
    >>> p.chunkdict.getbypath('c.fun1.0')[1].orig
    'fun1-body1'
    >>> p.chunkdict.getbypath('c.fun1.0')[1].tangle
    'fun1-body1'
    >>> p.chunkdict.getbypath('c.fun2')[1].tangle
    'fun2-body'
    """

    descr = 'TeX/LaTeX'
    ext = ('.tex', '.latex')
    inlcmds = ('verb', 'verb*')
    blkcmds = ('verbatim', 'verbatim*')

    config_params = Parser.config_params + ['inlcmds:strlist', 'blkcmds:strlist']

    def tokens(self, text):
        """
        >>> text = \
        '\\\\documentclass[12pt]{article}\\n' \
        '\\\\usepackage{amsmath}\\n' \
        '\\\\title{\\\\LaTeX}\\n' \
        '\\\\date{}\\n' \
        '\\\\begin{document}\\n' \
        '  \\\\maketitle\\n' \
        '  \\\\LaTeX{} is a document preparation system for the \\\\TeX{}\\n' \
        '\\n' \
        '  Testing of negative value <<isneg>>: \\\\verb#if a < 0#. Signature will\\n' \
        '  be <<fn.abs.decl>>: \\\\verb!int abs(int a)!. And now:\\n' \
        '  function absolute <<fn.abs>>:\\n' \
        '\\n' \
        '  \\\\begin{verbatim}\\n' \
        '    <<=fn.abs.decl>>\\n' \
        '        if (<<=isneg, x:a>>) return -a;\\n' \
        '        else return a;\\n' \
        '    }\\n' \
        '  \\\\end{verbatim}\\n' \
        '\\n' \
        '  % This is a comment; it will not be shown in the final output.\\n' \
        '  % The following shows a little of the typesetting power of LaTeX:\\n' \
        '  \\\\begin{align}\\n' \
        '    m &= \\\\frac{m_0}{\\\\sqrt{1-\\\\frac{v^2}{c^2}}}\\n' \
        '  \\\\end{align}\\n' \
        '\\\\end{document}'
        >>> p = TeXParser()
        >>> toks = p.tokens(text)
        >>> [tok.__class__.__name__ for tok in toks]
        ['CmdToken', 'InlCodeToken', 'CmdToken', 'InlCodeToken', 'CmdToken', 'BlkCodeToken', 'EndToken']
        >>> toks[0].text
        'isneg'
        >>> toks[1].text
        'if a < 0'
        >>> toks[2].text
        'fn.abs.decl'
        >>> toks[3].text == 'int abs(int a)'
        True
        >>> toks[5].text.startswith('<<=fn.abs.decl>>')
        True
        >>> toks[5].text.endswith('}')
        True
        """
        _inlcmds = '|'.join(re.escape(s) for s in TeXParser.inlcmds)
        # text inside inline chunk
        _inltext = r'{(?P<code1>.+?)}|(?P<s>[+#!])(?P<code2>.+?)(?P=s)'
        _blkcmds = '|'.join(re.escape(s) for s in TeXParser.blkcmds)

        _inlcode_re = r'\\(%s)%s'%(_inlcmds, _inltext)
        _blkcode_re = r'\\begin(\[.+?\])?{(%s)}(?P<code>.*?)\\end{(%s)}'%(_blkcmds, _blkcmds)

        inlcode_re = re.compile(_inlcode_re)
        blkcode_re = re.compile(_blkcode_re, re.DOTALL)

        cmds = CMDRE.cre('cmd').finditer(text)
        inlcodes = inlcode_re.finditer(text)
        blkcodes = blkcode_re.finditer(text)

        tokens = []

        for m in cmds:
            token = CmdToken(m.group(1), m.start(0), m.end(0))
            tokens.append(token)
        for m in inlcodes:
            groups = m.groupdict()
            g = 'code1' if groups['code1'] else 'code2'
            tokentext = InlCodeToken.linearize(m.group(g))
            token = InlCodeToken(tokentext, m.start(0), m.end(0))
            tokens.append(token)
        for m in blkcodes:
            # find each block and replace first left indent with ''
            tokentext = m.group('code').lstrip('\n').rstrip('\n ')
            tokentext = deltextindent(tokentext)
            token = BlkCodeToken(tokentext, m.start(0), m.end(0))
            tokens.append(token)

        tokens.sort(key=lambda tok: tok.start)
        tokens.append(EndToken(None))
        return tokens
Parser.parsers.append(TeXParser)

################################################################################

class OOSaxHandler(sax.ContentHandler):
    level = None # current level
    codelevel = None # level where code-chunk was found
    codetype = None # 'inline'|'block'
    text = None # list of text collected fragments
    style = None # name of code-chunk style
    styleinh = None # inheritance of style {name:parent-name}

    def __init__(self, style):
        self.style = style
        self.level = 0
        self.codelevel = None
        self.codetype = None
        self.text = []
        self.styleinh = {}
        sax.ContentHandler.__init__(self)

    def _style_extends(self, style, parent):
        """Check does style extend parent style
        >>> o = OOSaxHandler('lpcode')
        >>> o.styleinh = {'P1':'P2', 'P2':'P3', 'P3':'lpcode'}
        >>> o._style_extends('P3', 'lpcode')
        True
        >>> o._style_extends('P2', 'lpcode')
        True
        >>> o._style_extends('P1', 'lpcode')
        True
        >>> o._style_extends('P1', 'P2')
        True
        >>> o._style_extends('P2', 'P3')
        True
        >>> o._style_extends('P3', 'P2')
        False
        >>> o._style_extends('P5', 'P2')
        False
        >>> o._style_extends('P5', 'P6')
        False
        >>> o._style_extends('', 'P6')
        False
        >>> o._style_extends(' ', '')
        False
        """
        if not style or not parent:
            return False
        elif style == parent:
            return True
        else:
            return self._style_extends(self.styleinh.get(style, None), parent)

    def _code_element(self, name, attrs):
        stylename = attrs.get('text:style-name', '')
        if stylename and self._style_extends(stylename, self.style):
            if name == 'text:span':
                return 'inline'
            elif name == 'text:p':
                return 'block'
        return None

    @staticmethod
    def _decode_spec_chars(text):
        """replace special chars with it's real symbols"""
        # see _encode_spec_tag() and startElement()
        text = text.replace(u'\u201D', '"') # "
        text = text.replace(u'\u301D', '"') # "
        text = text.replace(u'\u275D', '"') # "
        text = text.replace(u'\u0022', '"') # "
        text = text.replace(u'\u201F', '"') # "
        text = text.replace(u'\u201C', '"') # "
        text = text.replace(u'\u00AB', '"') # "
        text = text.replace(u'\u00BB', '"') # "
        text = text.replace(u'\u2011', '-') # soft hyphen
        text = text.replace(u'\u00AD', '-') # non-breaking hyphen
        text = text.replace(u'\u00A0', ' ') # non-breaking space
        text = text.replace('@tab@', '\t')
        text = text.replace('@space@', ' ')
        text = text.replace('@line_break@', '\n')
        return text

    @staticmethod
    def _encode_spec_tag(tag, attrs):
        """Encode (replace) special chars with it's internal form.
        If not special char, returns None. Diff. from _decode_spec_chars()
        bcz encode tag, not text"""
        if tag == 'text:tab':
            return '@tab@'
        elif tag == 'text:s':
            n = int(attrs.get('text:c', 1))
            return n*'@space@'
        elif tag == 'text:line-break':
            return '@line_break@'
        else:
            return None

    #def endDocument(self):
        #print ''.join(self.text).encode('cp866', errors='ignore')

    def characters(self, content):
        self.text.append(content)

    #<style:style style:name="P1" style:family="paragraph" style:parent-style-name="lpcode">
    def startElement(self, name, attrs):
        elem = self._code_element(name, attrs)
        if name == 'style:style':
            parentstyle = attrs.get('style:parent-style-name', '')
            stylename = attrs.get('style:name')
            if parentstyle and stylename:
                self.styleinh[stylename] = parentstyle
            # styles inheritance
        elif name in ('text:span', 'text:p'):
            if elem and self.codelevel is None:
                self.codelevel = self.level
                self.codetype = elem
                if self.text[-1] == '@end_inline@' and elem == 'inline':
                    # remove empty @start_inline@@end_inline@
                    self.text.pop()
                elif self.text[-1] == '@end_block@' and elem == 'block':
                    # remove empty @start_block@@end_block@
                    self.text.pop()
                else:
                    self.text.append('@start_%s@'%elem)
            self.level += 1
        else:
            spectag = OOSaxHandler._encode_spec_tag(name, attrs)
            if spectag:
                self.text.append(spectag)

    def endElement(self, name):
        if name in ('text:span', 'text:p'):
            self.level -= 1
            if self.codelevel == self.level:
                self.codelevel = None
                if self.codetype == 'block' and self.text and self.text[-1] != '@line_break@':
                    # make to each block ends with \n
                    self.text.append('@line_break@')
                self.text.append('@end_%s@'%self.codetype)
                self.codetype = None

class OOParser(Parser):
    """OpenOffice/LibreOffice parser:
    """

    descr = 'OpenOffice/LibreOffice'
    ext = ('.odt',)
    style = 'lpcode'

    config_params = Parser.config_params + ['style']

    # FIXME not sure that works right
    @classmethod
    def findlines(class_, text):
        """Split text to lines coordinates
        """
        #return Parser.findlines(text, delim=('@line_break@', '\n'))
        return None # disable error location

    def readfile(self, filename):
        """Return text of document"""
        with zipfile.ZipFile(filename) as zip:
            return bytestostr23(zip.read('content.xml'))

    def tokens(self, text):
        oosaxhandler = OOSaxHandler(style=self.style)
        # next conversion seems bug in python (why need bytes, not str?!)
        if type(text) is str:
            parsetext = strtobytes23(text)
        else:
            parsetext = text
        sax.parseString(parsetext, oosaxhandler)
        text = ''.join(oosaxhandler.text)

        _inlcode_re = r'@start_inline@(.*?)@end_inline@'
        _blkcode_re = r'@start_block@(.*?)@end_block@'

        inlcode_re = re.compile(_inlcode_re, re.MULTILINE)
        blkcode_re = re.compile(_blkcode_re, re.MULTILINE)

        cmds = CMDRE.cre('cmd').finditer(text)
        inlcodes = inlcode_re.finditer(text)
        blkcodes = blkcode_re.finditer(text)

        tokens = []

        for m in cmds:
            token = CmdToken(OOSaxHandler._decode_spec_chars(m.group(1)), m.start(0), m.end(0))
            tokens.append(token)
        for m in inlcodes:
            # XXX break line in OO is coded with paragraph styling and this linearizing
            # does not help
            tokentext = OOSaxHandler._decode_spec_chars(m.group(1))
            tokentext = InlCodeToken.linearize(tokentext)
            token = InlCodeToken(tokentext, m.start(0), m.end(0))
            tokens.append(token)
        for m in blkcodes:
            token = BlkCodeToken(OOSaxHandler._decode_spec_chars(m.group(1)), m.start(0), m.end(0))
            tokens.append(token)

        tokens.sort(key=lambda tok: tok.start)
        tokens.append(EndToken(None))
        #print [t.text for t in tokens]
        return tokens
Parser.parsers.append(OOParser)

################################################################################

class Cfgfile(dict):
    """Config. file (rc-format) loader and parser
    """

    # config file param convert-functions:
    @staticmethod
    def strlist(value):
        """Convert string value as 'a,b,c...' to list of strings"""
        return [s.strip() for s in value.split(',')]
    str = str
    int = int
    float = float

    def load(self, filename):
        with open(filename, "rt") as ifile:
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
    cfg = None # config file loader (dict)

    def __init__(self, cfgfile='lprc'):
        self.cfg = Cfgfile()
        # load configuration from cfgfile (abs. path or in current dir)
        self.cfg.load(cfgfile) # config file name
        for parser_class in Parser.parsers:
            cfgparser_class = parser_class.__name__.upper() # name of class in cfg file
            # obtain config values
            for param in parser_class.getcfgparams():
                cfgparam = '%s_%s' % (cfgparser_class, param.upper())
                parser_class.config(param, self.cfg[cfgparam])
