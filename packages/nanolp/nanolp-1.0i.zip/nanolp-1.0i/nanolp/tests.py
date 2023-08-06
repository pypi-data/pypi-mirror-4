# Itself testing facilities
#
# Author: Balkansoft.BlogSpot.com
# GNU GPL licensed

from nanolp import core
from nanolp import commands
from nanolp import parsers
from nanolp import utils
from nanolp import lp
import unittest as ut
import doctest as dt
import os
import sys
import glob
import shutil
import subprocess
import re

# modules to be tested with docstrings
DOCTESTMODULES = (core, parsers, utils)
# port number for URL fetching tests
HTTP_PORT = 8000
# path to 'Scripts/' dir in installed Python
SCRIPTS_DIR = os.path.join(sys.exec_prefix, 'Scripts')

if core._PY23 == 2:
    SIMPLEHTTPSERVER = 'SimpleHTTPServer'
elif core._PY23 == 3:
    SIMPLEHTTPSERVER = 'http.server'

################################################################################

def msgfmt(msg, *args, **opts):
    caption = opts.get('caption', 'REASON')
    msg = msg % args
    return '\n>>> %s: %s\n'%(caption, msg)

def rmoutfiles(indir):
    """Remove all out files ('xxx.ext' from 'xxx.ext.master') in directory indir"""
    def _rmreflectionof(ext):
        """Remove reflection of some extension; reflection
        is the same file but without extension"""
        for master in globfiles(indir, '*.%s'%ext, True):
            out = master.replace('__', os.sep)
            out = change_ext(out, '')
            if os.path.exists(out):
                os.remove(out)
    _rmreflectionof('master')
    _rmreflectionof('in')

def readfile(filename):
    """Return buffer from *.master file"""
    return lp.fread23(filename).rstrip('\r\n')

def globfiles(indir, patt, rec=False):
    """Return list of globbing files from directory indir with pattern.
    """
    files = []
    for root, dirnames, filenames in os.walk(indir):
        files.extend(glob.glob(os.path.join(root, patt)))
    return files

def change_ext(filename, newext):
    """Change file extension"""
    oldext = os.path.splitext(filename)[1]
    return re.sub(oldext+'$', newext, filename)

def default_testdir():
    """Default test directory is current directory of running script"""
    return os.path.dirname(os.path.realpath(__file__))

def script_path(filename):
    """Returns full-path to script (Python/Scripts)"""
    return os.path.join(SCRIPTS_DIR, filename)

################################################################################

class NanoLPTestCase(ut.TestCase):
    def __init__(self):
        ut.TestCase.__init__(self) #, 'run')
        self.longMessage = True
        #self.maxDiff = None

    #def assertBufsEqual(self, buf1, buf2, msg):
        #pass

################################################################################

class TestExampleFile(NanoLPTestCase):
    """Test parsing of example.* file:
    1. Run nlp.py -i example.* if no example.sh otherwise use it as cmdline args
    2. If exists example.stderr, check stderr of run with example.stderr (as regexp)
    """
    def __init__(self, filename):
        NanoLPTestCase.__init__(self)
        self.indir = os.path.dirname(filename)
        self.filename = filename

    def runTest(self, *args):
        shfile = change_ext(self.filename, '.sh')
        args = [sys.executable, script_path("nlp.py")]
        if os.path.exists(shfile):
            # XXX no spaces in path!!!!
            args = args + lp.fread23(shfile).split()
        else:
            args = args + ["-i", self.filename]
        proc = subprocess.Popen(args, stderr=subprocess.PIPE)
        exitcode = proc.wait()
        stderrbuf = lp.bytestostr23(proc.stderr.read()).strip('\n')

        if exitcode != 0 or len(stderrbuf) != 0:
            err = os.path.splitext(self.filename)[0] + '.stderr'
            if os.path.exists(err):
                errbuf = readfile(err)
                self.assertRegexpMatches(stderrbuf, errbuf, msgfmt('unexpected exception'))
            else:
                self.fail('Exit with 1, stderr="%s"'%stderrbuf)

################################################################################

class TestExampleDirOuts(NanoLPTestCase):
    """Test matching contents of *.master files and it's original in
    example directory
    """
    def __init__(self, indir=''):
        NanoLPTestCase.__init__(self)
        self.indir = indir if indir else os.getcwd()

    def runTest(self, *args):
        for master in globfiles(self.indir, '*.master'):
            sys.stderr.write(msgfmt('%s', master, caption='MASTERFILE'))
            mbuf = readfile(master)
            out = os.path.splitext(master)[0].replace('__', os.sep)
            obuf = readfile(out)
            self.assertMultiLineEqual(mbuf, obuf,
                    msgfmt("out does not match '%s'", master))

################################################################################

class TestExamplesDir(ut.TestSuite):
    """TestSuite for example directory"""
    indir = ''
    def __init__(self, indir='', modpath=''):
        """Modpath is __file__ of caller module"""
        ut.TestSuite.__init__(self)
        if not indir:
            if modpath:
                indir = os.path.dirname(os.path.realpath(modpath))
            else:
                raise ValueError('indir or modpath should be setted')

        self.indir = indir
        rmoutfiles(self.indir)
        # create files from *.in files
        for in_ in globfiles(self.indir, '*.in'):
            f = change_ext(in_, '')
            shutil.copyfile(in_, f)
        # obtain extensions of testes examples from cfg file
        os.chdir(self.indir)
        lp.Lp()
        # now parsers are configured via cfg file (see os.chdir())
        example_exts = []
        for p in lp.Parser.parsers:
            example_exts.extend(p.ext)

        tests = []
        sys.stderr.write(msgfmt("'%s'"%self.indir, caption='TESTDIR'))
        for example in globfiles(self.indir, 'example.*'):
            name = os.path.split(example)[1]
            if name.count('.') > 1:
                # has more then one extension - possible master or out file
                continue
            ext = os.path.splitext(example)[1]
            if ext not in example_exts:
                continue
            tests.append(TestExampleFile(example))
            #sys.stderr.write("\nAdded example test '%s'"%example)
        tests.append(TestExampleDirOuts(self.indir))
        self.addTests(tests)

################################################################################

class TestDocStrings(ut.TestSuite):
    """TestSuite for docstrings in lp module"""
    def __init__(self):
        ut.TestSuite.__init__(self)
        # to use in doctests class names without package prefix:
        globals = {}
        globals.update(lp.__dict__)
        globals.update(core.__dict__)
        globals.update(parsers.__dict__)
        globals.update(commands.__dict__)
        # modules to test with docstrings
        for mod in DOCTESTMODULES:
            sys.stderr.write(msgfmt("'%s' module"%mod.__name__, caption='DOCTESTS'))
            self.addTests(dt.DocTestSuite(mod, globs=globals, optionflags=dt.IGNORE_EXCEPTION_DETAIL))

################################################################################

class TestExamplesDirViaUrl(TestExamplesDir):
    """Like TestExamplesDir but first run HTTP server on HTTP_PORT to serve
    all files in example dir."""
    def __init__(self, indir='', modpath=''):
        TestExamplesDir.__init__(self, indir, modpath)
    def run(self, results):
        args = [sys.executable, "-m", SIMPLEHTTPSERVER, str(HTTP_PORT)]
        proc = subprocess.Popen(args, cwd=self.indir)
        ret = TestExamplesDir.run(self, results)
        proc.kill()
        #print 80*'!'
        return ret

################################################################################

def run(tests):
    runner = ut.TextTestRunner()
    runner.run(tests)

