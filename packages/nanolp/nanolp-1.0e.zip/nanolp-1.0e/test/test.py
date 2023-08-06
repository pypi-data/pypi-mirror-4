from nanolp import lp
import os
import sys
import glob
import difflib
import string
#import unittest
import doctest

def intsuffix(s):
    i = len(s)-1
    while s[i] in string.digits:
        i -= 1
    return int(s[i+1:])

def cmpfiles(example, out, errors, master='', text=''):
    if text:
        master_buf = text
    else:
        with open(master, "rt") as masterfile:
            master_buf = masterfile.read().rstrip('\n')

    with open(out, "rt") as outfile:
        out_buf = outfile.read().rstrip('\n')
        out_buf = out_buf.replace('$example', example)

    res = (out_buf == master_buf)
    sys.stderr.write('\nExample %s %s\n'%(out, 'OK.' if res else 'FAILED:'))
    if not res:
        errors.append((example, out))
        master_lines = ['%s\n'%l for l in master_buf.splitlines()]
        out_lines = ['%s\n'%l for l in out_buf.splitlines()]
        for diffln in difflib.context_diff(master_lines, out_lines):
            if not diffln.endswith('\n'):
                diffln += '\n'
            sys.stderr.write(diffln)

def argv1():
    if len(sys.argv) > 1:
        return sys.argv[1]
    else:
        return ''

if argv1() != '-d':
    sys.stderr.write('==================== DO DOCTESTS ====================\n')
    testres = doctest.testmod(lp, verbose='-q' not in sys.argv, optionflags=doctest.IGNORE_EXCEPTION_DETAIL)

if argv1() != '-f':
    sys.stderr.write('==================== DO FILE TESTS ====================\n')

    failed = []
    PWD = os.getcwd()
    testdirs = glob.glob(os.path.join(PWD, 'tests', 'test*'))
    testdirs.sort(key=intsuffix)
    for d in testdirs:
        path = os.path.join(PWD, 'tests', d)

        outs = glob.glob(os.path.join(path, '*.out'))
        for out in outs:
            os.remove(out)

        os.chdir(path)
        examples = glob.glob(os.path.join(path, 'example*'))
        for example in examples:
            if example.endswith('.out'): continue
            if example.endswith('.err'): continue
            sys.stderr.write('\nProcess %s...\n'%example)
            try:
                lp.Lp()
                parser = lp.Parser.fileparser(example)
                parser.parsefile(example)
            except Exception as x:
                msg = str(x)
                err = os.path.splitext(example)[0] + '.err'
                if os.path.exists(err):
                    cmpfiles(example=example, text=msg, out=err, errors=failed)
                    continue
                else:
                    raise

        masters = glob.glob(os.path.join(path, '*.master'))
        for master in masters:
            out = master.replace('.master', '.out')
            cmpfiles(example=example, master=master, out=out, errors=failed)
    if failed:
        sys.stderr.write('\n====================\n')
        sys.stderr.write('%d FAILED:\n'%len(failed))
        for example,out in failed:
            out = out.split(os.sep)[-1]
            example = os.sep.join(example.split(os.sep)[-2:])
            sys.stderr.write("  '%s' in '%s'\n" % (out, example))
