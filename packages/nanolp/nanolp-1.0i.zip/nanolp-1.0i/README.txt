====================================
Nano LP -- Literate Programming tool
====================================

`Project HOME <http://code.google.com/p/nano-lp/>`_

`Documentation <http://code.google.com/p/nano-lp/w/list>`_

`Discussion <http://groups.google.com/group/nano-lp-discuss>`_

`ChangeLog <http://code.google.com/p/nano-lp/wiki/Changes>`_

Introduction
============

It's very simple, art-of-concept literate programming (LP) tool. Main idea
is too avoid processing document (LP source) format, so input document
format is supported by it's traditional external tool. So it's possible
to have favourite workflow: WYSIWYG editing/text processing/converting
with you favourite tool/suite (OpenOffice/Markdown tool/TeX/etc.).

General workflow schemes are::

                             local/WEB:
                             ____________
                           +------------+|
                           |            ||
                           | LP Library ||
                           |            |'
         local/WEB:        +------------+
     ------->>---------         /
    |                  |      use
    |                  v      /
    |          some format with  --> 1. extract sources...
    ^             LP commands    --> 2. cross-references
    ^                  |         --> 3. use as library  
    |                  v
    |     EXTERNAL TOOL/OFFICE SUITE
    |                  |
     -------<<--------- 

and::

       local/WEB:
       ____________
     +------------+|
     |            ||
     | LP Library ||
     |            |'
     +------------+
           /
         use
         /            READY TO PUBLISH  --> 1. online documentation
   'some-lp.html' -->      ON WEB       --> 2. extract sources...
         \                              --> 3. cross-references
          \                             --> 4. use as library
           -- PARSE AND MODIFYING:
                + embeeded Javascript configuration
                + linked 'nanolp-pub.js'
                + linked 'nanolp-pub.css'

So, this kind of LP tool knows about LP input format only how to extract
LP commands and code chunks - **tangle**, weaving is not needed, input format is
ready for **printing**, **publishing**, **reading**, etc.

At the moment, supported input formats are:

* Markdown/MultiMarkdown
* OpenOffice/LibreOffice
* Creole
* reStructuredText
* TeX/LaTeX
* Txt2Tags
* Asciidoc
* HTML/XML
* ... and any compatible

Main features
=============

* definition of command (macros) with placeholders in the body (code chunk)
* variables dictionaries (for substitution of placeholders)
* pasting command code chunk with substitution of placeholders
* definition of multiple parts code-chunks (for wrapping, etc.)
* joining, 'ending', etc. several code chunks
* 'globbing' commands when paste
* including one file to another (library)
* custom event handlers (filters in chain/pipe manner)
* supporting URLs in file names (read via HTTP)
* prepare of HTML files (with LP commands) for Web publishing
* generating cross-references file
* auto-detecting of cycles
* configurable via simple .INI like file
* works with Python 2.7 - Python 3+
* works with Unicode (UTF8) 
* extendible

Installation
============

Install Python (2.7 or 3+) first, then run::

    $ python setup.py install

Then run::

    $ nlp.py -h

or::

    $ python path-to-scripts/nlp.py -h
