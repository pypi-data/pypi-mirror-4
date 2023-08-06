#!/usr/bin/env python

# Main module (to run from command line)
# Author: Balkansoft.BlogSpot.com
# GNU GPL licensed

import getopt
import sys
import os
from nanolp import lp

################################################################################

class AppError(Exception): pass

class App:
    input_file = None # input file name
    cfgfile = '' # path to config. file
    tb = False # show traceback on exceptions
    refs = False # flush references file

    def print_usage(self):
        def parser_info(cls):
            ext = '%s' % ', '.join(cls.ext)
            return '   %s - %s: %s'%(cls.__name__, cls.descr or 'Unknown', ext)

        formats = [parser_info(p) for p in lp.Parser.parsers]
        formats = '\n'.join(formats)

        if self.cfgfile:
            cfginfo = "Setup from: '%s'" % self.cfgfile
        else:
            cfginfo = ''

        USAGE = '''\
Syntax: -i FILE [-x] [-r] [-h]
   -i FILE      Input file
   -x           Detailed stack-trace on errors
   -r           Flush references file
   -h           This help
Supported formats:
%s
%s
'''%(formats, cfginfo)
        sys.stdout.write(USAGE)

    def parse_cmdline(self):
        """Returns True, if app may continue execution, False otherwise
        (help printing is only need)
        """
        try:
            opts, args = getopt.getopt(sys.argv[1:], 'rxhi:', [])
        except getopt.GetoptError as x:
            sys.stderr.write('Syntax error! See help (-h)\n')
            sys.exit(1)

        self.input_file = None
        for o, v in opts:
            if o == '-h':
                return False
            elif o == '-i':
                self.input_file = v
            elif o == '-x':
                self.tb = True
            elif o == '-r':
                self.refs = True
        if not self.input_file:
            sys.stderr.write('Input file is mandatory. See help (-h)\n')
            sys.exit(1)
        return True

    # XXX first call parse_cmdline() to determine input dir (as possible place
    # of cfg. file)
    def findcfgfile(self):
        """Return path to cfg file or raise exception, if not found. Priority
        of search:
            - folder of input file
            - current working directory
            - script directory
        """
        dirs = [os.getcwd(), os.path.dirname(os.path.realpath(__file__))]
        if self.input_file:
            # input dir has higher priority for search of cfgfile
            absp = os.path.abspath(self.input_file)
            dirs.insert(0, os.path.dirname(absp))
        for indir in dirs:
            cfgfile = os.path.join(indir, 'lprc')
            if os.path.exists(cfgfile):
                return cfgfile
        raise AppError('Can not found configuration file')

    def main(self):
        sys.stderr.write(lp.__ABOUT__+'\n')
        onlyhelp = not self.parse_cmdline()

        def _do():
            """real action"""
            self.cfgfile = self.findcfgfile()
            if onlyhelp:
                self.print_usage()
                sys.exit(0)
            lp.Lp(cfgfile=self.cfgfile)
            parserclass = lp.Parser.fileparser(self.input_file)
            parser = parserclass.parsefile(self.input_file)
            if self.refs:
                # if need to flush references, do it
                fn = os.path.split(self.input_file)[1]
                fn = fn.upper()
                refsfile = lp.RefsFile(parser, "%s: references"%fn)
                refsfile.save()

        if self.tb:
            _do()
        else:
            try:
                _do()
            except Exception as x:
                sys.stderr.write("ERROR '%s': %s\n"%(x.__class__.__name__,str(x)))

################################################################################

if __name__ == "__main__":
    app = App()
    app.main()
