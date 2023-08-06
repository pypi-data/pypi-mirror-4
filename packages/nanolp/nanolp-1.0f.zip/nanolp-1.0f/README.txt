====================================
Nano LP -- Literate Programming tool
====================================

`WiKi pages <http://code.google.com/p/nano-lp/w/list>`_

`Project HOME <http://code.google.com/p/nano-lp/>`_

It's very simple, art-of-concept literate programming (LP) tool. Main idea
is too avoid processing document (LP source) format, so input document
format is supported (WYSIWYG editing/text processing/converting) by some
traditional external tool, like markdown processor or LibreOffice suite.

General scheme is::

        some format with  --> extracted sources...
          LP commands
               |
               +--> ( external processor )

So, this kind of LP tool known about LP input format only how to extract
LP commands and code chunks, nothing else. At the moment, supported
formats are:

- Markdown/MultiMarkdown
- OpenOffice/LibreOffice
- Creole
- reStructuredText
- TeX/LaTeX

Installation
============

Install Python (2.7 or 3+) first, then run::

    $ python setup.py install

Then run::

    $ nlp.py -h

or::

    $ python path-to-scripts/nlp.py -h

Commands
========

Command is the **macros** in D. Knuth terminology.

There are 2 kinds of commands:

#. definition of code-chunk
#. usage of code-chunk

They have a form:

#. <<...>>
#. <<=...>>

Instead of '<' symbol using, it's possible to configure another text
fragment, see 'lprc' setup file.

So, programmer defines chunks, then uses them in another chunks. Syntax is
simple::

    ... command ... chunk ... command ... chunk ...

If chunk is missed, empty chunk will be used.

Chunk is defined in different ways for different formats. For Markdown usual
code formatting is used: ``...`` for inline chunks and code block for chunks
as paragraphs.

In OpenOffice inline chunk must have symbol style 'lpcode'. Block chunks must
have paragraph style 'lpcode' (or another as user configures in 'lprc'
config file).

Each command has form::

    path, args

path is one word or words joined with dot (.), args are positional arguments
(for command running) or keyword arguments (for substitution)::

    <<a.b.c>>
    <<a.b, some positional arg>>
    <<a.b.c, x:1, y:2>>
    <<a, x:1, y:2, zzz>>

NOTE: special characters ('.', etc.) are unallowed in arg. names!

Positional arguments interpreating depends on command implementation, keyword
arguments are used to substitute special place-holders in code chunk, linked to
this command definition. For example, code chunk may be::

    if ($x > 5)

Pasting of this chunk to another::

    <<=its_name, x:myVariable>>

Result is::

    if (myVariable > 5)

Or another example::

    #ifndef _${file}_H_
    #define _${file}_H_

and such chunk is usuable::

    <<=its_name, file: GUI>>

There is a special keyword argument '*'. When it has value '*', it
means 'replace all keyword arguments with their names', so::

    <<=its_name, *:*>>

becames now::

    if (x > 5)

Also is possible to create variables dictionary; anonymous dictionary ex.::

    <<vars, v1:1, v2:2>>

OR::

    <<vars, dict1, v1:1, v2:2>>

Now anywhere in chunks will be allowed variables::

    $v1, $v2, ${dict1.v1}, ${dict1.v2}

Also it's possible to set what dictionary to use when substitute chunk::

    <<=some, *:$dict1>>

or even what variable value from another dictionary::

    <<=some, v:$dict1.v1>>

If there is command with serial chunks after it, they will be available with
names::

    path.0, path.1, path.2...

So::

    command ... chunk ... chunk ...

will creates chunks available with names command_path.0, command_path.1.
It may be used in creation complex chunks with start and end parts::

    <<=H_file_guarg.0, file:GUI>>
    ...
    <<=H_file_guarg.1>>

It's possible to paste commands with glob-pattern::

    <<=path.*>>
    <<=path.*, join:;\n>>
    <<=path.*, end:;>>

First pastes all commands linewise, second and third pastes with ;\n between
them. join argument is used for joining several chunks. Special globbing
symbol '*' is used to match ANY path component.

Also argument 'end' (as 'start' too) is supported - symbols trailed to the end
of each fragment::

    <<=path.*, join:\n, end:;>>

to generates lines like::

    aaaa;
    bbbb;
    ....

Special commands
================

file
----

There is special command name file.*. It's used to flush code to source files.
Example (for Markdown)::

    <<file.a, gui.java>> .... `<<=code.*>>`...

This snippet flush all code fragments (see globbing) into file with name
gui.java.

use
---

Also there is special command use with body as file name and 'mnt' keyword
argument (optional) pointed out the mount path. Example of usage::

    <<use, mnt:c.std, this_file.md>>

And now you can use it's command 'somecmd' as::

    <<=c.std.somecmd>>

Variable dictionary of included (imported) file will be imported too, and with
new names of dictionaries::

    ${new_path.v} - anonymous dictionary of imported file, mounted in 'new_path'
    ${new_path.some_dict.v} - 'some_dict' dictionary, mounted in 'new_path'

vars
----

Command vars is used to create variable dictionary and has 2 forms::

    <<vars, v1:..., v2:...>>

for anonymous dictionary. It's variables are accessible in any chunk as $v1, $v2... and second with named dictionary::

    <<vars, d, v1:..., v2:...>>

so it's variables are: ${d.v1}, ${d.v2}.

Examples
========

See tests/ directory.

Configuration
=============

Very simple, 'lprc' text file is used. General options are:

- PARSER_SURR - surround symbol for this parser (<, [, (, {)
- PARSER_EXT - extensions binding for this parser

Lookup order of config. file is:

#. First, try folder of input file
#. Then try current working directory
#. And the script directory 

Running with -h options shows real directory of 'lprc' file.

Usage
=====

Run with -h option for command line options.

Features
========

Works with Python 2.7 - Python 3.x.

OpenOffice parser supports style inheritance (OpenOffice creates such style
all the time behind the scene), special symbols, direct formatting in
code-chunks (see test6/ example for all of these).

Used charset is UTF8.

Testing
=======

Run test.py::

    test.py -f [-q] -- do only doctests [-quiet]
    test.py -d -- do only file tests (see tests/ dir)

Extending
=========

- To add new format support, extend base class Parser (see OOParser...)
- To add new command processor, extend Cmd (see FileCmd...)

BUGS
====

OpenOffice
----------

Don't break line in inline code-chunks, because parts will joined without spaces!
