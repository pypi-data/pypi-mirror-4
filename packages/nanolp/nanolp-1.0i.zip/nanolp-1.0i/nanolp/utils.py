# Utils for NanoLP
#
# Author: Balkansoft.BlogSpot.com
# GNU GPL licensed

import os
import re
import json
import itertools
import collections
import xml.sax.saxutils as saxutils
from xml.dom import minidom
import nanolp.core as core

__HOMEURL__ = 'http://code.google.com/p/nano-lp'
__BLOGURL__ = 'http://balkansoft.blogspot.com'
__BLOGNAME__ = 'BalkanSoft.BlogSpot.Com'

def snumerate(obj, collection, fmt=None):
    """numerate object with numeric suffix like 'obj(2)'
    >>> c = []
    >>> snumerate(1, c)
    '1'
    >>> snumerate(1, c)
    '1(2)'
    >>> snumerate(1, c)
    '1(3)'
    >>> snumerate(1, c, '%s -- %d')
    '1 -- 4'
    >>> snumerate(1, c, lambda o,n:'%s..%d'%(o,n))
    '1..5'
    """
    if not fmt:
        _fmt = lambda o,n: '%s(%d)'%(o,n)
    elif isinstance(fmt, core.StringTypes23):
        _fmt = lambda o,n: fmt%(o,n)
    else:
        _fmt = fmt
    obj = str(obj)
    nrepeats = collection.count(obj)
    collection.append(obj)
    if nrepeats:
        return _fmt(obj, nrepeats+1)
    else:
        return '%s'%obj

class RefsFile:
    """Generates references HTML file"""

    REFS_CSS_FILE = 'nanolp.css'

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
    background-color: #F0EBFE;
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
    padding: 10px 0 20px 5px;
    font-size: 24px;
}

#about {
    text-align: center;
    font-size: 8pt;
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
    padding: 10px 0 5px 10px;
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

.dlarrow {
    margin: 7px;
    padding: 0;
    display: inline;
    font-size: 17pt;
    font-weight: bold;
    background-color: #77AA11;
    border: 1px solid #777700;
    text-color: white;
    border-radius: .4em;
}

.dlarrow a {
    text-decoration: none;
    color: white;
}
'''

    parser = None
    inputattrs = ''

    def __init__(self, parser, title=''):
        self.parser = parser
        self.inputattrs = self.__uriattrs(core.Uri(self.parser.infile))
        self.title = title

    def __url(self, obj):
        """Return URL to obj; obj is Uri/Cmd. If Uri is FS-path, try to return
        relative URL instead of full 'file://...'
        """
        if isinstance(obj, core.Cmd):
            return obj.jpath()
            #return base64.b64encode(obj.jpath())
            #return str(hash(obj.jpath())).replace('-', '_')
        elif isinstance(obj, core.Uri):
            if obj.fspath:
                objdir = os.path.dirname(obj.fspath)
                relpath = os.path.relpath(objdir, self.parser.outdir)
                if '.' == relpath:
                    # if in the same output directory, URL is file name
                    return obj.name
                elif '..' not in relpath:
                    # if is internal in parser.outdir, URL is relative
                    return os.path.join(relpath, obj.name)
                else:
                    # else is out of parser.outdir, so URL will be full qualified
                    return obj.url # it's "file://fspath"
            else:
                return obj.url
        else:
            raise RuntimeError("Can not generate URL for '%s'"%str(obj))

    def __uriattrs(self, uri):
        """Uri as attributes for <a> tag: url, title, orig name, short-name (moniker)"""
        return dict(url=self.__url(uri),
                name=uri.name,
                title=uri.fspath or uri.url,
                moniker=uri.getmoniker())

    def _header(self):
        return ('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">',
        '<html xmlns="http://www.w3.org/1999/xhtml">',
        '<head>',
        '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>',
        '<link rel="stylesheet" href="%s" type="text/css"/>' % self.REFS_CSS_FILE,
        '<title>%s: references</title>' % self.inputattrs['name'],
        '</head>',
        '<body>')

    def _footer(self):
        yield '<div id="about">'
        yield '<a href="%s">%s</a> - ' % (__HOMEURL__, core.__ABOUT__)
        yield '<a href="%s">%s</a>'%(__BLOGURL__, __BLOGNAME__)
        yield '</div></body></html>'

    def _output_info(self):
        """HTML tags for info about parser and it's results"""
        yield '<table class="outputinfo">'
        # Outputs - all FileCmd's
        cmds = self.parser.chunkdict.get_uniform_commands('FileCmd')
        yield '<tr>'
        yield '<td class="param">Outputs:</td>'
        yield '<td>'
        for cmd in cmds:
            if not cmd.outfile:
                # if flushing of files is disable, FileCmd.onpost() will not be call, so
                # cmd.outfile will be unset
                yield '<i title="Flush of files is disabled">%s</i>'%(cmd.body[0] or 'no output')
            else:
                uriattrs = self.__uriattrs(core.Uri(cmd.outfile))
                yield '<a title="%s" href="%s">%s</a>&nbsp;&nbsp;' % \
                        (uriattrs['title'], uriattrs['url'], uriattrs['name'])
        yield '</td>'
        yield '</tr>'
        # Includes - all UseCmd's
        cmds = self.parser.chunkdict.get_uniform_commands('UseCmd')
        yield '<tr>'
        yield '<td class="param">Includes:</td>'
        yield '<td>'
        for cmd in cmds:
            uriattrs = self.__uriattrs(core.Uri(cmd.infile))
            yield '<a title="%s" href="%s">%s</a>&nbsp;&nbsp;' % \
                    (uriattrs['title'], uriattrs['url'], uriattrs['name'])
        yield '</td>'
        yield '</tr>'
        # Config file
        if self.parser.engine:
            yield '<tr>'
            yield '<td class="param">Cfg. file:</td>'
            yield '<td>'
            cfgfile = self.parser.engine.cfgfile.filename
            uriattrs = self.__uriattrs(core.Uri(cfgfile))
            yield '<a href="%s" title="%s">%s</a>' % \
                    (uriattrs['url'], uriattrs['title'], uriattrs['name'])
            yield '</td>'
            yield '</tr>'
        # Index of commands
        cmds = self.parser.chunkdict.keys()
        yield '<tr>'
        yield '<td class="param">Index:</td>'
        yield '<td>'
        url_collection = []; jpath_collection = []
        for cmd in sorted(cmds, key=lambda c:c.jpath()):
            url = snumerate(self.__url(cmd), url_collection)
            jpath = snumerate(cmd.jpath(), jpath_collection)
            yield '<a href="#%s">%s</a>&nbsp;&nbsp;' % (url, jpath)
        yield '</td>'
        yield '</tr>'
        # Variables
        # XXX sort only for tests
        pre = collections.OrderedDict()
        for k in sorted(self.parser.vars.keys()):
            d = self.parser.vars[k]
            pre[k] = collections.OrderedDict(d)
        pre = json.dumps(pre)
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
            return '<a href="#%s">%s</a>' % (self.__url(cmd), cmd.text)
        # glob path
        popup = ['<span class="popup">%s'%cmd.text, '<div><span id="caption">Matched:</span>']
        cmds = self.parser.chunkdict.globpath(jpath)
        for cmd in cmds:
            popup.append(self.__cmdref(cmd))
        popup.append('</div></span>')
        return ''.join(popup)

    def _body(self):
        yield '<div id="ctrlbar">'
        yield '<h1><span class="dlarrow"><a href="%s" title="%s">&dArr;</a></span>%s: references</h1>' % \
                (self.inputattrs['url'], self.inputattrs['title'], self.inputattrs['moniker'])
        for y in self._output_info(): yield y
        yield '</div>'

        url_collection = []; jpath_collection = []
        for cmd, chunk in self.parser.chunkdict.chunks.items():
            url = snumerate(self.__url(cmd), url_collection)
            jpath = snumerate(cmd.jpath(), jpath_collection)
            yield '<h2><a name="%s">%s</a></h2>'%(url, jpath)

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
        cssfname = os.path.join(self.parser.outdir, self.REFS_CSS_FILE)
        if not os.path.exists(cssfname):
            # if CSS file doesnt exists, create
            core.prn("writing CSS-styles file '%s'..."%cssfname, engine=self.parser.engine, file='stdout')
            core.fwrite23(cssfname, self._css)

        #if not self.parser.infile:
            # define output file name
            #fname = 'nanolp-refs.html'
        #else:
            #fname = os.path.split(self.parser.infile)[1] + '-refs.html'
        fname = self.inputattrs['name'] + '-refs.html'
        fname = os.path.join(self.parser.outdir, fname)

        lines = itertools.chain(self._header(), self._body(), self._footer())
        text = '\n'.join(lines)
        core.prn("writing references file '%s'..."%fname, engine=self.parser.engine, file='stdout')
        core.fwrite23(fname, text)

################################################################################

class Publisher:
    """Prepare HTML file for publishing
    """
    CSSFILENAME = 'nanolp-pub.css'
    JSFILENAME = 'nanolp-pub.js'

    _css = '''
.lpdefine {
    font-weight: bold;
    font-style: italic;
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

    _script0 = '''
var LP_CFG = {{'SURR':{SURR}, 'CMDS':{CMDS}}};
'''

    _script1 = r'''
/// traverse DOM
function walk(func, node, acc) {
    if (typeof acc == 'undefined')
        acc = new Array();
    acc = func(acc, node);
    node = node.firstChild;
    while(node) {
        walk(func, node, acc);
        node = node.nextSibling;
    }
    return acc;
}

/// escaping function
RegExp.quote = function(str) {
    return (str+'').replace(/([.?*+^$[\]\\(){}|-])/g, "\\$1");
};

/// creates regexp for <<cmd>>
function defineRegExp() {
    var lSur = RegExp.quote(LP_CFG['SURR'][0]);
    var rSur = RegExp.quote(LP_CFG['SURR'][1]);
    return new RegExp(lSur + '([^=]+?)(,.*?)?' + rSur, 'g');
}

/// creates regexp for <<=cmd>>
function pasteRegExp() {
    var lSur = RegExp.quote(LP_CFG['SURR'][0]);
    var rSur = RegExp.quote(LP_CFG['SURR'][1]);
    return new RegExp(lSur + '=(.+?)(,.*?)?' + rSur, 'g');
}

var defineRe = defineRegExp();
var pasteRe = pasteRegExp();

function _replDefine(g0, g1, g2) {
    if (g2 == undefined) g2 = '';
    var s = '<a name="@1"><span class="lpdefine">(@1@2)</span></a>';
    return s.replace(/@1/g, g1).replace(/@2/, g2);
}

function _replPaste(g0, g1, g2) {
    _cmdUrl = function(cmdPath) {
        var srcFile = LP_CFG['CMDS'][cmdPath];
        if (srcFile == '') {
            return '#' + cmdPath;
        } else if (/.htm$|.html$|.shtml$/.test(srcFile)) {
            // HTML source file of defined chunk
            return srcFile + '#' + cmdPath;
        } else {
            return srcFile;
        }
    }

    if (g2 == undefined) g2 = '';
    if (-1 != g1.indexOf('*')) {
        // some glob
        var s = '<span class="popup">='+g1+g2+'<div><span id="caption">Matched:</span>';
        var re = new RegExp(glob2re(g1));
        for (var cmdPath in LP_CFG['CMDS']) {
            if (re.test(cmdPath)) {
                var dsuff = /\.\d+$/.exec(cmdPath);
                if (dsuff) {
                    // finished with '.DIGITS', found ref will ends with the same
                    // numeric suffix, so cut it, bcz in HTML is only parent chunk,
                    // i.e. 'xxx' instead of 'xxx.0', 'xxx.1'...
                    var ref = _cmdUrl(cmdPath).slice(0, dsuff['index']+1);
                } else {
                    var ref = _cmdUrl(cmdPath);
                }
                s += '<a href="@1">@2</a>'.replace(/@1/, ref).replace(/@2/, cmdPath);
            }
        }
        s += '</div></span>';
        return s;
    }
    else {
        var s = '<a href="@1">=@2@3</a>';
        return s.replace(/@1/, _cmdUrl(g1)).replace(/@2/, g1).replace(/@3/, g2);
    }
}

/// on visit DOM node
function visitDefine(acc, node) {
    var txt = node.innerHTML;
    if (txt) {
        txt = txt.replace(defineRe, _replDefine);
        node.innerHTML = txt;
    }
    return acc;
}

function visitPaste(acc, node) {
    var txt = node.innerHTML;
    if (txt) {
        txt = txt.replace(pasteRe, _replPaste);
        node.innerHTML = txt;
    }
    return acc;
}

/** Translate a shell PATTERN to a regular expression.
  * Adapted from Python
  * There is no way to quote meta-characters */
function glob2re(pat) {
    var i = 0;
    var n = pat.length;
    var res = '';
    while (i < n) {
        var c = pat[i];
        i = i+1;
        if (c == '*')
            res = res + '.*';
        else if (c == '?')
            res = res + '.';
        else if (c == '[') {
            var j = i;
            if (j < n && pat[j] == '!')
                j = j+1;
            if (j < n && pat[j] == ']')
                j = j+1;
            while (j < n && pat[j] != ']')
                j = j+1;
            if (j >= n)
                res = res + '\\[';
            else {
                //stuff = pat[i:j].replace('\\','\\\\');
                var stuff = pat.slice(i, j).replace('\\','\\\\');
                i = j+1;
                if (stuff[0] == '!')
                    stuff = '^' + stuff.slice(1);
                else if (stuff[0] == '^')
                    stuff = '\\' + stuff;
                res = res + '[' + stuff + ']';
                //res = '%s[%s]' % (res, stuff);
            }
        }
        else
            res = res + RegExp.quote(c);
    }
    return res; // + '\Z(?ms)';
}

window.onload = function() {
    var body = document.body;
    /// XXX really replace once - all occurs in body.innerHTML
    var res;
    res = walk(visitDefine, body);
    res = walk(visitPaste, body);
}
'''

    parser = None
    baseurl = ''

    def __init__(self, parser, baseurl=''):
        self.parser = parser
        if baseurl and not re.match(r'\w+://', baseurl, re.I):
            baseurl = 'http://' + baseurl
        self.baseurl = baseurl

    def __url(self, path):
        """Returns URL for files (css, js) and infile's of defined chunks
        """
        uri = core.Uri(path)
        if uri.fspath:
            dir = os.path.dirname(uri.fspath)
            relpath = os.path.relpath(dir, self.parser.outdir)
            if '.' == relpath:
                # if in the same output directory, URL is file name
                relpath = uri.name
            elif '..' not in relpath:
                # if is internal in parser.outdir, URL is relative
                relpath = os.path.join(relpath, uri.name)
            else:
                # else is out of parser.outdir, so URL will be full qualified
                raise RuntimeError("Can not generate URL for '%s'"%str(path))
            # TODO may be need some escaping/quoting?
            return relpath if not self.baseurl else '/'.join((self.baseurl, relpath))
        else:
            return uri.url

    def publish(self, filename):
        # TODO ignore errors (<br/>)

        # to fix (i.e. remove <?xml version="1.0" ?>)
        fixed_head_len = len(minidom.Document().toxml())

        # modify input HTML...

        dom = minidom.parse(filename)
        root = dom.documentElement
        head = root.getElementsByTagName('head').item(0)
        scripts = head.getElementsByTagName('script')
        if any(self.JSFILENAME in s.getAttribute('src') for s in scripts):
            raise RuntimeError('This document is already modified')

        # Script 0
        script0 = dom.createElement('script')
        script0.setAttribute('type', 'text/javascript')
        cmds = collections.OrderedDict()
        for cmd in self.parser.chunkdict.keys():
            infile = cmd.get_srcinfo('infile', '')
            if infile:
                infile = "" if infile == self.parser.infile else self.__url(infile)
            cmds[cmd.jpath()] = infile
        fmtargs = {
                'SURR': self.parser.surr,
                'CMDS': cmds,
        }
        for k,v in fmtargs.items():
            fmtargs[k] = json.dumps(v).replace('"', "'") # ' instead of "
        text = self._script0.format(**fmtargs)
        script0_text = dom.createTextNode(text) # "->&quot; so use ' instead of "
        script0.appendChild(script0_text)

        # Script 1
        script1 = dom.createElement('script')
        script1.setAttribute('type', 'text/javascript')
        script1.setAttribute('src', self.__url(self.JSFILENAME))
        script1_text = dom.createTextNode('')
        script1.appendChild(script1_text)

        # Stylesheet
        css = dom.createElement('link')
        css.setAttribute('rel', 'stylesheet')
        css.setAttribute('href', self.__url(self.CSSFILENAME))
        css.setAttribute('type', 'text/css')

        # Head inserts
        head.appendChild(css)
        head.appendChild(script0)
        head.appendChild(script1)

        # Save to file
        xml = dom.toxml()
        core.prn("modifying '%s' for publish..."%filename, engine=self.parser.engine, file='stdout')
        core.fwrite23(filename, xml[fixed_head_len:])

        # Flush additional files
        indir = os.path.dirname(filename)
        cssfname = os.path.join(indir, self.CSSFILENAME)
        jsfname = os.path.join(indir, self.JSFILENAME)
        if not os.path.exists(cssfname):
            core.prn("writing CSS-styles file '%s'..."%cssfname, engine=self.parser.engine, file='stdout')
            core.fwrite23(cssfname, self._css)
        if not os.path.exists(jsfname):
            core.prn("writing JS file '%s'..."%jsfname, engine=self.parser.engine, file='stdout')
            core.fwrite23(jsfname, self._script1)

################################################################################

