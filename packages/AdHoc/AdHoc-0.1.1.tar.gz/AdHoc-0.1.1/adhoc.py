#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011, 2012, Wolfgang Scherer, <Wolfgang.Scherer at gmx.de>
# Sponsored by WIEDENMANN SEILE GMBH, http://www.wiedenmannseile.de
#
# This file is part of Wiedenmann Utilities.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>,
# or write to Wolfgang Scherer, <Wolfgang.Scherer at gmx.de>

# @:adhoc_uncomment:@
# @:adhoc_template:@ doc/index.rst
# AdHoc Standalone Package Generator
# ##################################

# AdHoc consists of a single python source file `adhoc.py`, which can be
# used as a program (see `Script Usage`_) as well as a module.
#
# After installation of the binary package, run ``adhoc.py --explode``
# to obtain the full source in directory ``__adhoc__``.
#
# @:adhoc_template:@ doc/index.rst # off
# @:adhoc_uncomment:@

"""\
.. _Script Usage:

adhoc.py - Python ad hoc compiler.

======  ====================
usage:  adhoc.py [OPTIONS] [file ...]
or      import adhoc
======  ====================

Options
=======

  -c, --compile         compile arguments. (default)

  -q, --quiet           suppress warnings
  -v, --verbose         verbose test output
  -d, --debug=NUM       show debug information

  -h, --help            display this help message
  --documentation       display module documentation.

  --template list       show available templates.
  --template=NAME       extract named template to standard
                        output. Default NAME is `-`.
  --extract=DIR         extract adhoc files to directory DIR (default: `.`)
  --explode=DIR         explode script with adhoc in directory DIR
                        (default `__adhoc__`)
  --implode             implode script with adhoc
  --install             install adhoc.py script

  -t, --test            run doc tests

`adhoc.py` is compatible with Python 2.5+ and Python 3. (For Python
2.5 the packages `stringformat` and `argparse` are needed and
included.)

.. _END_OF_HELP:

Script Examples
===============

Templates
---------

``python adhoc.py --template list`` provides a list of templates:

>>> ign = main('adhoc.py --template list'.split())
====================================== ===================== ==============
               Command                       Template             Type
====================================== ===================== ==============
adhoc.py --template adhoc_test         # !adhoc_test         adhoc_import
adhoc.py --template adhoc_test.sub     # !adhoc_test.sub     adhoc_import
adhoc.py --template argparse_local     # !argparse_local     adhoc_import
adhoc.py --template namespace_dict     # !namespace_dict     adhoc_import
adhoc.py --template stringformat_local # !stringformat_local adhoc_import
adhoc.py --template                    # -                   adhoc_template
adhoc.py --template col-param-closure  # -col-param-closure  adhoc_template
adhoc.py --template doc/index.rst      # doc/index.rst       adhoc_template
adhoc.py --template max-width-class    # -max-width-class    adhoc_template
adhoc.py --template rst-to-ascii       # -rst-to-ascii       adhoc_template
adhoc.py --template test               # -test               adhoc_template
adhoc.py --template MANIFEST.in        # !MANIFEST.in        adhoc_unpack
adhoc.py --template Makefile           # !Makefile           adhoc_unpack
adhoc.py --template README.css         # !README.css         adhoc_unpack
adhoc.py --template doc/Makefile       # !doc/Makefile       adhoc_unpack
adhoc.py --template doc/conf.py        # !doc/conf.py        adhoc_unpack
adhoc.py --template doc/make.bat       # !doc/make.bat       adhoc_unpack
adhoc.py --template docutils.conf      # !docutils.conf      adhoc_unpack
adhoc.py --template setup.py           # !setup.py           adhoc_unpack
====================================== ===================== ==============

``python adhoc.py --template`` prints the standard template ``-``:

>>> ign = main('./adhoc.py --template'.split())
Standard template.

``python adhoc.py --template test`` prints the template named ``-test``.
the leading ``-`` signifies disposition to standard output:

>>> ign = main('./adhoc.py --template test'.split())
Test template.

Export
------

``python adhoc.py --explode`` unpacks the following files into
directory ``__adhoc__``:

.. >>> ign = main('./adhoc.py --explode'.split())

.. _END_OF_SCRIPT_USAGE:

Module Members
==============
"""

# @:adhoc_uncomment:@
# @:adhoc_template:@ doc/index.rst
#
# Description
# ===========
#
# `AdHoc` parses text for tagged lines and processes them as instructions.
#
# The minimal parsed entity is a marker line, which is any line
# containing a recognized `AdHoc` tag.
#
# Marker lines come in two flavors, namely flags and section delimiters.
#
# All `AdHoc` tags are enclosed in |@:| and |:@|. E.g:
#
#   |@:|\ adhoc\ |:@|
#
# Flags are marker lines, which denote a single option or command (see
# `Flags`_). E.g.:
#
#   | import module     # |@:|\ adhoc\ |:@|
#   | # |@:|\ adhoc_self\ |:@| my_module_name
#
# Sections are marker line pairs, which delimit a block of text. The
# first marker line opens the section, the second marker line closes the
# section (see `Sections`_). E.g.:
#
#   | # |@:|\ adhoc_enable\ |:@|
#   | # disabled_command()
#   | # |@:|\ adhoc_enable\ |:@|
#
# The implementation is realized as class :class:`AdHoc` which is mainly
# used as a namespace. The runtime part of :class:`AdHoc` which handles
# module import and file export is included verbatim as class
# :class:`RtAdHoc` in the generated output.
#
# Flags
# -----
#
# :|adhoc_runtime|:
#   The place where the AdHoc runtime code is added.  This flag must be
#   present in files, which use the |adhoc| import feature.  It is not
#   needed for the enable/disable features.
#
# :|adhoc|:
#   Mark import line for run-time compilation.  If the line is commented
#   out, the respective module is not compiled.
#
# :|adhoc_self| name ...:
#     Mark name(s) as currently compiling.  This is useful, if
#     `__init__.py` imports other module parts. E.g:
#
#       | from pyjsmo.base import * # |@:|\ adhoc\ |:@|
#
# :|adhoc_include| file [from default-file], ...:
#     Include files for unpacking. `file` is the name for extraction. If
#     `file` is not found, `default-file` is used for inclusion.
#
# :|adhoc_verbatim| [flags] file [from default-file], ...:
#     Include files for verbatim extraction. `file` is the name for
#     extraction. If `file` is not found, `default-file` is used for
#     inclusion.
#
#     The files are included as |adhoc_template_v| sections. `file` is used
#     as `export_file` mark. If `file` is ``--``, the template disposition
#     becomes standard output.
#
#     Optional flags can be any combination of ``[+|-]NUM`` for
#     indentation and ``#`` for commenting. E.g::
#
#       # |adhoc_verbatim| +4# my_file from /dev/null
#
#     `my_file` (or `/dev/null`) is read, commented and indented 4
#     spaces. If the |adhoc_verbatim| tag is already indented, the
#     specified indentation is subtracted.
#
# :|adhoc_compiled|:
#     If present, no compilation is done on this file. This flag is
#     added by the compiler to the run-time version.
#
# Sections
# --------
#
# :|adhoc_enable|:
#     Leading comment char and exactly one space are removed from lines
#     in these sections.
#
# :|adhoc_disable|:
#     A comment char and exactly one space are added to lines in these
#     sections.
#
# :|adhoc_template| -mark | export_file:
#     If mark starts with ``-``, the output disposition is standard output
#     and the template is ignored, when exporting.
#
#     Otherwise, the template is written to output_file during export.
#
#     All template parts with the same mark/export_file are concatenated
#     to a single string.
#
# :|adhoc_uncomment|:
#     Treated like |adhoc_enable| before template output.
#
# :|adhoc_indent| [+|-]NUM:
#     Add or remove indentation before template output.
#
# :|adhoc_import|:
#     Imported files are marked as such by the compiler. There is no
#     effect during compilation.
#
# :|adhoc_unpack|:
#     Included files are marked as such by the compiler. There is no
#     effect during compilation.
#
# :|adhoc_remove|:
#     Added sections are marked as such by the compiler.  The flag is
#     renamed to |adhoc_remove_| during compilation.  Which in turn is
#     renamed to |adhoc_remove| during export.
#
# Internal
# --------
#
# :|adhoc_run_time_class|:
#     Marks the beginning of the run-time class.  This is only
#     recognized in the AdHoc programm/module.
#
# :|adhoc_run_time_section|:
#     All sections are concatenated and used as run-time code.  This is
#     only recognized in the AdHoc programm/module.
#
# \|:todo:| make enable/disable RX configurable
#
# @:adhoc_template:@ doc/index.rst # off
# @:adhoc_uncomment:@

# @:adhoc_uncomment:@
# @:adhoc_template:@ doc/index.rst
#
# .. |@:| replace:: `@:`
# .. |:@| replace:: `:@`
# .. |adhoc_runtime| replace:: |@:|\ `adhoc_runtime`\ |:@|
# .. |adhoc| replace:: |@:|\ `adhoc`\ |:@|
# .. |adhoc_self| replace:: |@:|\ `adhoc_self`\ |:@|
# .. |adhoc_include| replace:: |@:|\ `adhoc_include`\ |:@|
# .. |adhoc_verbatim| replace:: |@:|\ `adhoc_verbatim`\ |:@|
# .. |adhoc_compiled| replace:: |@:|\ `adhoc_compiled`\ |:@|
# .. |adhoc_enable| replace:: |@:|\ `adhoc_enable`\ |:@|
# .. |adhoc_disable| replace:: |@:|\ `adhoc_disable`\ |:@|
# .. |adhoc_template| replace:: |@:|\ `adhoc_template`\ |:@|
# .. |adhoc_template_v| replace:: |@:|\ `adhoc_template_v`\ |:@|
# .. |adhoc_uncomment| replace:: |@:|\ `adhoc_uncomment`\ |:@|
# .. |adhoc_indent| replace:: |@:|\ `adhoc_indent`\ |:@|
# .. |adhoc_import| replace:: |@:|\ `adhoc_import`\ |:@|
# .. |adhoc_unpack| replace:: |@:|\ `adhoc_unpack`\ |:@|
# .. |adhoc_remove| replace:: |@:|\ `adhoc_remove`\ |:@|
# .. |adhoc_remove_| replace:: |@:|\ `adhoc_remove_`\ |:@|
# .. |adhoc_run_time_class| replace:: |@:|\ `adhoc_run_time_class`\ |:@|
# .. |adhoc_run_time_section| replace:: |@:|\ `adhoc_run_time_section`\ |:@|
#
# @:adhoc_template:@ doc/index.rst # off
# @:adhoc_uncomment:@

# @:adhoc_uncomment:@
# @:adhoc_template:@ doc/index.rst
# @:adhoc_template:@ doc/index.rst # off
# @:adhoc_uncomment:@

# --------------------------------------------------
# |||:sec:||| COMPATIBILITY
# --------------------------------------------------

import sys
# (progn (forward-line 1) (snip-insert-mode "py.b.printf" t) (insert "\n"))
# adapted from http://www.daniweb.com/software-development/python/code/217214
try:
    printf = eval("print") # python 3.0 case
except SyntaxError:
    printf_dict = dict()
    try:
        exec("from __future__ import print_function\nprintf=print", printf_dict)
        printf = printf_dict["printf"] # 2.6 case
    except SyntaxError:
        def printf(*args, **kwd): # 2.4, 2.5, define our own Print function
            fout = kwd.get("file", sys.stdout)
            w = fout.write
            if args:
                w(str(args[0]))
            sep = kwd.get("sep", " ")
            for a in args[1:]:
                w(sep)
                w(str(a))
            w(kwd.get("end", "\n"))
    del printf_dict

# (progn (forward-line 1) (snip-insert-mode "py.f.isstring" t) (insert "\n"))
# hide from 2to3
exec('''
def isstring(obj):
    return isinstance(obj, basestring)
''')
try:
    isstring("")
except NameError:
    def isstring(obj):
        return isinstance(obj, str) or isinstance(obj, bytes)

# (progn (forward-line 1) (snip-insert-mode "py.b.dict_items" t) (insert "\n"))
try:
    getattr(dict(), 'iteritems')
    ditems  = lambda d: getattr(d, 'iteritems')()
    dkeys   = lambda d: getattr(d, 'iterkeys')()
    dvalues = lambda d: getattr(d, 'itervalues')()
except AttributeError:
    ditems  = lambda d: getattr(d, 'items')()
    dkeys   = lambda d: getattr(d, 'keys')()
    dvalues = lambda d: getattr(d, 'values')()

import os
import re

# --------------------------------------------------
# |||:sec:||| CONFIGURATION
# --------------------------------------------------

dbg_comm = globals()['dbg_comm'] if 'dbg_comm' in globals() else '# '
dbg_twid = globals()['dbg_twid'] if 'dbg_twid' in globals() else 9
dbg_fwid = globals()['dbg_fwid'] if 'dbg_fwid' in globals() else 23

# (progn (forward-line 1) (snip-insert-mode "py.b.dbg.setup" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.b.strings" t) (insert "\n"))
def _uc(string):                                           # ||:fnc:||
    return unicode(string, 'utf-8')
try:
    _uc("")
except NameError:
    _uc = lambda x: x

uc_type = type(_uc(""))

def uc(value):                                             # ||:fnc:||
    if isstring(value) and not isinstance(value, uc_type):
        return _uc(value)
    return value

def _utf8str(string):                                      # ||:fnc:||
    if isinstance(string, uc_type):
        return string.encode('utf-8')
    return string

def utf8str(value):                                        # ||:fnc:||
    if isstring(value):
        return _utf8str(value)
    return value

def _nativestr(string):                                    # ||:fnc:||
    # for python3, unicode strings have type str
    if isinstance(string, str):
        return string
    # for python2, encode unicode strings to utf-8 strings
    if isinstance(string, uc_type):
        return string.encode('utf-8')
    try:
        return str(string.decode('utf-8'))
    except UnicodeDecodeError:
        return string

def nativestr(value):                                      # ||:fnc:||
    if isstring(value):
        return _nativestr(value)
    return value

# (progn (forward-line 1) (snip-insert-mode "py.f.strclean" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.f.issequence" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.b.logging" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.b.ordereddict" t) (insert "\n"))

# (progn (forward-line 1) (snip-insert-mode "py.main.pyramid.activate" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.main.project.libdir" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.main.sql.alchemy" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.main.sql.ws" t) (insert "\n"))

# @:adhoc_disable:@ allow modification of exploded sources in original place
sys.path.insert(0, '__adhoc__')
# @:adhoc_disable:@ allow modification of exploded sources in original place

# @:adhoc_run_time:@
#import adhoc                                               # @:adhoc:@

# (progn (forward-line 1) (snip-insert-mode "py.b.sformat" t) (insert "\n"))
try:
    ('{0}').format(0)
    def sformat (fmtspec, *args, **kwargs):
        return fmtspec.format(*args, **kwargs)
except AttributeError:
    try:
        import stringformat
    except ImportError:
        try:
            import stringformat_local as stringformat      # @:adhoc:@
        except ImportError:
            printf('error: stringformat missing.'
                   ' Try `easy_install stringformat`.', file=sys.stderr)
            exit(1)
    def sformat (fmtspec, *args, **kwargs):
        return stringformat.FormattableString(fmtspec).format(
            *args, **kwargs)

import base64
import urllib

#import something.non.existent                              # @:adhoc:@
try:
    import namespace_dict
except ImportError:
    import namespace_dict                                  # @:adhoc:@

# copy of ws_prop_dict.dict_dump
def dict_dump(dict_, wid=0, trunc=0, commstr=None, tag=None, out=None): # ||:fnc:||
    '''Dump a dictionary.'''

    if out is None:
        out = sys.stderr
    if commstr is None:
        commstr = globals()['dbg_comm'] if 'dbg_comm' in globals() else '# '

    dbg_twid = globals()['dbg_twid'] if 'dbg_twid' in globals() else 9
    if tag is None:
        tag = ':DBG:'

    max_wid = 0
    for key in dict_.keys():
        _wid = len(key)
        if max_wid < _wid:
            max_wid = _wid

    dbg_fwid = globals()['dbg_fwid'] if 'dbg_fwid' in globals() else max_wid
    if dbg_fwid < max_wid:
        dbg_fwid = max_wid

    printf(sformat('{0}{1}', commstr, '-' * 30), file=out)
    indent = (sformat("{0}{3:^{1}} {4:<{2}s}:  ",
            commstr, dbg_twid, dbg_fwid,
            '', ''))

    for key, value in sorted(dict_.items()):
        value = str(value)
        value = value.replace('\n', '\\n')
        value = value.replace('\r', '\\r')
        value = value.replace('\t', '\\t')
        value = value.replace('\f', '\\f')
        if wid == 0:
            wid = 78 - len(indent) - 1
            if wid < 50:
                wid = 50
        start = 0
        limit = len(value)
        value_lines = []
        while start < limit:
            line = value[start:start+wid]
            space_pos = wid - 1
            if len(line) == wid:
                space_pos = line.rfind(' ')
                if space_pos > 0:
                    line = line[:space_pos + 1]
                else:
                    space_pos = wid - 1
            value_lines.append(line)
            start += space_pos + 1
        if trunc > 0:
            value_lines = value_lines[:trunc]
        value_lines[-1] = sformat('{0}[', value_lines[-1])
        printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5!s}",
                commstr, dbg_twid, dbg_fwid,
                tag, key, value_lines[0]), file=out)
        for line in value_lines[1:]:
            printf(sformat('{0}{1}',indent, line), file=out)

def dump_attr(obj, wid=0, trunc=0, commstr=None,           # ||:fnc:||
              tag=None, out=None):
    if out is None:
        out = sys.stdout
    dict_dump(
        vars(obj), wid=wid, trunc=trunc, commstr=commstr, tag=tag, out=out)

printe = printf

# (progn (forward-line 1) (snip-insert-mode "py.b.posix" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.b.os.system.sh" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.b.prog.path" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.b.line.loop" t) (insert "\n"))

# --------------------------------------------------
# |||:sec:||| CLASSES
# --------------------------------------------------

# (progn (forward-line 1) (snip-insert-mode "py.c.placeholder.template" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.c.key.hash.ordered.dict" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.c.progress" t) (insert "\n"))

# --------------------------------------------------
# |||:sec:||| EXCEPTION
# --------------------------------------------------

class AdHocError(Exception):                               # ||:cls:||
    pass

# --------------------------------------------------
# |||:sec:||| ADHOC
# --------------------------------------------------

# @:adhoc_run_time_section:@ on
import sys
import os
import re

try:
    from cStringIO import StringIO as _AdHocBytesIO, StringIO as _AdHocStringIO
except ImportError:
    from io import BytesIO as _AdHocBytesIO, StringIO as _AdHocStringIO

# @:adhoc_run_time_section:@
if not hasattr(os.path, 'relpath'):
    def relpath(path, start=os.curdir):
        """Return a relative version of a path"""

        if not path:
            raise ValueError("no path specified")

        start_list = os.path.abspath(start).split(os.sep)
        path_list = os.path.abspath(path).split(os.sep)

        # Work out how much of the filepath is shared by start and path.
        i = len(os.path.commonprefix([start_list, path_list]))

        rel_list = [os.pardir] * (len(start_list)-i) + path_list[i:]
        if not rel_list:
            return os.curdir
        return os.path.join(*rel_list)
    os.path.relpath = relpath
    del relpath

# @:adhoc_run_time_section:@ on
# @:adhoc_run_time_class:@
class AdHoc(object):                                     # |||:cls:|||
    '''
    :class:`AdHoc` is mainly used as a namespace, which is partially
    included verbatim as :class:`RtAdHoc` in the generated output.

    '''
    section_delimiters = ('@:', ':@')
    line_delimiters = ('@:', ':@')
    frozen = False

    include_path = []
    export_dir = '__adhoc__'
    export_need_init = {}
    export_have_init = {}
    extract_dir = '.'
    extract_warn = False

    quiet = False
    verbose = False
    debug = False

    @staticmethod
    def decode_source(source):                               # |:mth:|
        if not source:
            return ''
        eol_seen = 0
        for eol, c in enumerate(source):
            if c == '\n':
                eol_seen += 1
                if eol_seen == 2:
                    break
        check = source[:eol].decode('utf-8')
        mo = re.search('-[*]-.*coding:\\s*([^\\s]+).*-[*]-', check)
        if mo:
            coding = mo.group(1)
        else:
            coding = 'utf-8'
        source = source.decode(coding)
        return source

    @staticmethod
    def encode_source(source):                               # |:mth:|
        if not source:
            return ''.encode('utf-8')
        eol_seen = 0
        for eol, c in enumerate(source):
            if c == '\n':
                eol_seen += 1
                if eol_seen == 2:
                    break
        mo = re.search('-[*]-.*coding:\\s*([^\\s]+).*-[*]-', source[:eol])
        if mo:
            coding = mo.group(1)
        else:
            coding = 'utf-8'
        source = source.encode(coding)
        return source

    @classmethod
    def read_source(cls, file_):                             # |:clm:|
        if file_ == '-':
            source = sys.stdin.read()
        else:
            sf = open(file_, 'rb')
            source = cls.decode_source(sf.read())
            sf.close()
        return source

    @classmethod
    def write_source(cls, file_, source):                    # |:clm:|
        if file_ == '-':
            sys.stdout.write(source)
        else:
            sf = open(file_, 'wb')
            sf.write(cls.encode_source(source))
            sf.close()

    @classmethod
    def check_xfile(cls, file_, xdir=None, mtime=None):      # |:mth:|
        if xdir is None:
            xdir = cls.extract_dir
        if file_ == '-':
            return file_
        xfile = os.path.join(xdir, file_)
        if os.path.exists(xfile):
            # do not overwrite files
            if (cls.extract_warn or (cls.verbose)) and not cls.quiet:
                map(sys.stderr.write, (
                    "# xf: ", cls.__name__, ": warning file `", file_,
                    "` exists. skipping ...\n"))
            return None
        xdir = os.path.dirname(xfile)
        if not os.path.exists(xdir):
            os.mkdir(xdir)
        return xfile

    @classmethod
    def pack_file(cls, source, zipped=True):                 # |:clm:|
        import base64, gzip
        if zipped:
            sio = _AdHocBytesIO()
            gzf = gzip.GzipFile('', 'wb', 9, sio)
            gzf.write(cls.encode_source(source))
            gzf.close()
            source = sio.getvalue()
            sio.close()
        else:
            source = cls.encode_source(source)
        source = base64.b64encode(source)
        source = source.decode('ascii')
        return source

    @staticmethod
    def strquote(source, indent=(' ' * 4)):                  # |:fnc:|
        source = source.replace("'", "\\'")
        length = 78 - 2 - 4 - len(indent)
        if length < 50:
            length = 50
        output_parts = []
        indx = 0
        limit = len(source)
        while indx < limit:
            output_parts.extend((
                indent, "    '", source[indx:indx+length], "'\n"))
            indx += length
        return ''.join(output_parts)

    @classmethod
    def unpack_file(cls, source64, zipped=True):             # |:clm:|
        import base64, gzip
# @:adhoc_run_time_section:@
        if cls.debug:
            printf(sformat(
                "{0}{3:^{1}} {4:<{2}s}: ]{5:>7d}[ ]{6!s}[ {7}",
                dbg_comm, dbg_twid, dbg_fwid,
                ':DBG:', 'source64', len(source64), source64[:80],
                'b64decode ...'))
# @:adhoc_run_time_section:@ on
        source = source64.encode('ascii')
        source = base64.b64decode(source)
        if zipped:
# @:adhoc_run_time_section:@
            if cls.debug:
                printf(sformat(
                    "{0}{3:^{1}} {4:<{2}s}: ]{5:>7d}[ ]{6!s}[ {7}",
                    dbg_comm, dbg_twid, dbg_fwid,
                    ':DBG:', 'source (zip)', len(source), repr(source)[:80],
                    'unzipping ...'))
# @:adhoc_run_time_section:@ on
            sio = _AdHocBytesIO(source)
            gzf = gzip.GzipFile('', 'rb', 9, sio)
            source = gzf.read()
            gzf.close()
            sio.close()
        source = cls.decode_source(source)
# @:adhoc_run_time_section:@
        if cls.debug:
            printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5:>7d}[ ]{6!s}[",
                    dbg_comm, dbg_twid, dbg_fwid,
                    ':DBG:', 'source', len(source), repr(source)[:80]))

# @:adhoc_run_time_section:@ on
        return source

    @staticmethod
    def adhoc_tag(symbol, delimiters, is_re=False):          # |:fnc:|
        ldlm = delimiters[0]
        rdlm = delimiters[1]
        if is_re:
            ldlm = re.escape(ldlm)
            rdlm = re.escape(rdlm)
        #symbol = re.sub('[^-0-9A-Za-z_]', '_', symbol) # |:check:| why?
        return ''.join((ldlm, symbol, rdlm))

    @classmethod
    def line_tag(cls, symbol, is_re=False):                  # |:clm:|
        return cls.adhoc_tag(symbol, cls.line_delimiters, is_re)

    @classmethod
    def section_tag(cls, symbol, is_re=False):               # |:clm:|
        return cls.adhoc_tag(symbol, cls.section_delimiters, is_re)

    @classmethod
    def line_tag_parse(cls, tag_line, tag=None):             # |:mth:|
        if tag is None:
            tag = '[^:]+'
        else:
            tag = re.escape(tag)
        tag_rx = cls.line_tag(''.join(('(', tag, ')')), is_re=True)
        mo = re.search(tag_rx, tag_line)
        if mo:
            ptag = mo.group(1)

        else:
            ptag = ''
        strip_rx = ''.join(('^.*', cls.line_tag(tag, is_re=True), '\\s*'))
        tag_arg = re.sub(strip_rx, '', tag_line).strip()
        return (ptag, tag_arg)

    @classmethod
    def line_tag_strip(cls, tag_line, tag=None):             # |:mth:|
        return cls.line_tag_parse(tag_line, tag)[1]

    @staticmethod
    def adhoc_split(string, marker, is_re=False):            # |:fnc:|
        '''Split string with marker line.

        :returns:
          a list of tuples with a flag and a section::

            [(is_marker, section), ... ]
        '''
        if not is_re:
            marker = re.escape(marker)
        ro = re.compile(''.join(('^[^\n]*(', marker, ')[^\n]*$')), re.M)
        result = []
        last_end = 0
        for mo in re.finditer(ro, string):
            start = mo.start(0)
            end = mo.end(0)
            result.append((False, string[last_end:start]))
            result.append((True, string[start:end+1]))
            last_end = end+1
        result.append((False, string[last_end:]))
        return result

    @classmethod
    def get_lines(cls, string, marker, is_re=False):         # |:clm:|
        result = []
        for section in cls.adhoc_split(string, marker, is_re):
            if section[0]:
                result.append(section[1])
        return result

    @classmethod
    def partition(cls, string, marker, is_re=False, headline=False): # |:clm:|
        '''Split the string into body parts and sections.

        If `headline` is True, the starting tag line is included for
        sections.'''
        in_section = False
        body_parts = []
        sections = []
        tag_line = ''
        for section in cls.adhoc_split(string, marker, is_re):
            if section[0]:
                in_section = not in_section
                tag_line = section[1]
                continue
            if in_section:
                if headline:
                    sections.append((tag_line, section[1]))
                else:
                    sections.append(section[1])
            else:
                body_parts.append(section[1])
        return body_parts, sections

    @classmethod
    def get_sections(cls, string, marker, is_re=False):      # |:clm:|
        body_parts, sections = cls.partition(string, marker, is_re)
        return sections

    @classmethod
    def transform_sections(cls, transform, string,           # |:clm:|
                           symbol, is_re=False):
        result = []
        in_section = False
        for section in cls.adhoc_split(
            string, cls.section_tag(symbol, is_re), is_re):
            blob = section[1]
            if section[0]:
                in_section = not in_section
            elif in_section:
                blob = transform(blob)
            result.append(blob)
        string = ''.join(result)
        return string

    @classmethod
    def transform_markers(cls, transform, string,            # |:clm:|
                          symbol, is_re=False):
        result = []
        in_section = False
        for section in cls.adhoc_split(
            string, cls.line_tag(symbol, is_re), is_re):
            blob = section[1]
            if section[0]:
                in_section = not in_section
                blob = transform(blob)
            result.append(blob)
        string = ''.join(result)
        return string

    @classmethod
    def rename_marker(cls, string, symbol, renamed, is_re=False): # |:clm:|
        if is_re:
            transform = lambda blob: re.sub(symbol, renamed, blob)
        else:
            transform = lambda blob: blob.replace(symbol, renamed)
        return cls.transform_markers(transform, string, symbol, is_re)

    @classmethod
    def remove_marker(cls, string, symbol, is_re=False): # |:clm:|
        '''
        >>> tpl = AdHoc.get_named_template("col-param-closure")

        .. >>> printf(str(AdHoc.remove_marker(tpl, "adhoc_run_time_section")))
        '''
        transform = lambda blob: ''
        return cls.transform_markers(transform, string, symbol, is_re)

    @classmethod
    def indent_sections(cls, string, symbol, is_re=False):   # |:clm:|
        # @:adhoc_run_time_section:@
        '''
        >>> section = """\\
        ... # prefix
        ...   # @:adhoc_indent_check:@ +4
        ...   #line 1
        ...   #  line 2
        ...   #
        ...   # line 3
        ...   # @:adhoc_indent_check:@
        ...   # suffix\\
        ... """
        >>> printf(AdHoc.indent_sections(section, "adhoc_indent_check"))
        # prefix
          # @:adhoc_indent_check:@ +4
              #line 1
              #  line 2
              #
              # line 3
              # @:adhoc_indent_check:@
          # suffix

        >>> printf(AdHoc.indent_sections(section.replace("+4", "-1"),
        ...        "adhoc_indent_check"))
        # prefix
          # @:adhoc_indent_check:@ -1
         #line 1
         #  line 2
         #
         # line 3
          # @:adhoc_indent_check:@
          # suffix

        '''
        # @:adhoc_run_time_section:@ on
        result = []
        in_section = False
        indent = 0
        for section in cls.adhoc_split(
            string, cls.section_tag(symbol, is_re), is_re):
            blob = section[1]
            if section[0]:
                in_section = not in_section
                if in_section:
                    tag_arg = cls.line_tag_strip(blob)
                    if tag_arg:
                        indent = int(tag_arg)
                    else:
                        indent = -4
            else:
                if in_section and indent:
                    if indent < 0:
                        rx = re.compile(''.join(('^', ' ' * (-indent))), re.M)
                        blob = rx.sub('', blob)
                    elif indent > 0:
                        rx = re.compile('^', re.M)
                        blob = rx.sub(' ' * indent, blob)
                    indent = 0
            result.append(blob)
        string = ''.join(result)
        return string

    @classmethod
    def enable_sections(cls, string, symbol, is_re=False):   # |:clm:|
        # @:adhoc_run_time_section:@
        '''
        >>> section = """\\
        ... # prefix
        ...   # @:adhoc_enable_check:@
        ...   #line 1
        ...   #  line 2
        ...   #
        ...   # line 3
        ...   # @:adhoc_enable_check:@
        ...   # suffix\\
        ... """
        >>> printf(AdHoc.enable_sections(section, "adhoc_enable_check"))
        # prefix
          # @:adhoc_enable_check:@
          line 1
           line 2
        <BLANKLINE>
          line 3
          # @:adhoc_enable_check:@
          # suffix
        '''
        # @:adhoc_run_time_section:@ on
        enable_ro = re.compile('^([ \t\r]*)(# ?)', re.M)
        enable_sub = '\\1'
        transform = lambda blob: enable_ro.sub(enable_sub, blob)
        return cls.transform_sections(transform, string, symbol, is_re)

    adhoc_rx_tab_check = re.compile('^([ ]*\t)', re.M)
    adhoc_rx_disable_simple = re.compile('^', re.M)
    adhoc_rx_min_indent_check = re.compile('^([ ]*)([^ \t\r\n]|$)', re.M)

    @classmethod
    def disable_transform(cls, section):                     # |:clm:|
        if not section:
            return section

        if cls.adhoc_rx_tab_check.search(section):
            # tabs are evil
            if cls.verbose:
                map(sys.stderr.write,
                    ('# dt: evil tabs: ', repr(section), '\n'))
            return cls.adhoc_rx_disable_simple.sub(
                '# ', section.rstrip()) + '\n'

        min_indent = ''
        for mo in cls.adhoc_rx_min_indent_check.finditer(section):
            indent = mo.group(1)
            if indent:
                if (not min_indent or len(min_indent) > len(indent)):
                    min_indent = indent
            elif mo.group(2):
                min_indent = ''
                break
        adhoc_rx_min_indent = re.compile(
            ''.join(('^(', min_indent, '|)([^\n]*)$')), re.M)

        if section.endswith('\n'):
            section = section[:-1]
        dsection = []
        for mo in adhoc_rx_min_indent.finditer(section):
            indent = mo.group(1)
            rest = mo.group(2)
            if not indent and not rest:
                dsection.extend((min_indent, '#', '\n'))
            else:
                dsection.extend((indent, '# ', rest, '\n'))
        return ''.join(dsection)

    @classmethod
    def disable_sections(cls, string, symbol, is_re=False):  # |:clm:|
        # @:adhoc_run_time_section:@
        '''
        >>> section = """\\
        ... prefix
        ...   @:adhoc_disable_check:@
        ...   line 1
        ...     line 2
        ...
        ...   line 3
        ...   @:adhoc_disable_check:@
        ...   suffix\\
        ... """
        >>> printf(AdHoc.disable_sections(section, "adhoc_disable_check"))
        prefix
          @:adhoc_disable_check:@
          # line 1
          #   line 2
          #
          # line 3
          @:adhoc_disable_check:@
          suffix
        '''
        # @:adhoc_run_time_section:@ on
        return cls.transform_sections(
            cls.disable_transform, string, symbol, is_re)

    @classmethod
    def remove_sections(cls, string, symbol, is_re=False):   # |:clm:|
        ah_retained, ah_removed = cls.partition(
            string, cls.section_tag(symbol, is_re), is_re)
        return ''.join(ah_retained)

    @classmethod
    def export_source(cls, string):                          # |:clm:|
# @:adhoc_run_time_section:@
        '''
        ============================ =========================
        check for |adhoc_remove|     sections and remove them!
        check for |adhoc_import|     sections and remove them!
        check for |adhoc_unpack|     sections and remove them!
        check for |adhoc_template_v| sections and remove them!
        check for |adhoc_disable|    sections and enable them!
        check for |adhoc_enable|     sections and disable them!
        check for |adhoc_remove_|    markers and rename them!
        ============================ =========================
        '''
# @:adhoc_run_time_section:@ on
        string = cls.remove_sections(string, 'adhoc_remove')
        string = cls.remove_sections(string, 'adhoc_import')
        string = cls.remove_sections(string, 'adhoc_unpack')
        string = cls.remove_sections(string, 'adhoc_template_v')
        string = cls.enable_sections(string, 'adhoc_disable')
        string = cls.disable_sections(string, 'adhoc_enable')
        string = cls.rename_marker(string, 'adhoc_remove_', 'adhoc_remove')
        return string

    @classmethod
    def export__(cls, mod_name=None, file_=None, mtime=None, # |:mth:|
                zipped=True, source64=None):
        source = cls.unpack_file(source64, zipped)
# @:adhoc_run_time_section:@
        if cls.debug:
            sys.stderr.write(
                ''.join(("# xp: ", cls.__name__, ".export__ for `",
                         file_, "`\n")))
# @:adhoc_run_time_section:@ on
        file_base = os.path.basename(file_)
        if file_base.startswith('__init__.py'):
            is_init = True
        else:
            is_init = False

        parts = mod_name.split('.')
        base = parts.pop()
        if parts:
            module_dir = os.path.join(*parts)
            cls.export_need_init[module_dir] = True
        else:
            module_dir = ''
        if is_init:
            module_dir = os.path.join(module_dir, base)
            cls.export_have_init[module_dir] = True
        module_file = os.path.join(module_dir, file_base)

        cls.export_(source, module_file)

    @classmethod
    def export_(cls, source, file_):                         # |:mth:|
        source_sections, import_sections = cls.partition(
            source, cls.section_tag('adhoc_import'))
        source = cls.export_source(''.join(source_sections))
        export_call = ''.join((cls.__name__, '.export__'))

        xfile = cls.check_xfile(file_, cls.export_dir)
        if xfile is not None:
            cls.write_source(xfile, source)
            if cls.verbose:
                map(sys.stderr.write,
                    ("# xp: ", cls.__name__, ".export_ for `", file_,
                     "` using `", export_call,"`\n"))

        for import_section in import_sections:
            # this calls RtAdHoc.export__
            import_section = re.sub('^\\s+', '', import_section)
            import_section = re.sub(
                '^[^(]*(?s)', export_call, import_section)
            try:
                #RtAdHoc = cls # export_call takes care of this
                exec(import_section, globals(), locals())
            except IndentationError:
                sys.stderr.write("!!! IndentationError !!!\n")
# @:adhoc_run_time_section:@
                sys.stderr.write(''.join((import_section, "\n")))
# @:adhoc_run_time_section:@ on

    @classmethod
    def std_source_param(cls, file_=None, source=None,       # |:mth:|
                         marker=None, is_re=False):
        # @:adhoc_run_time_section:@
        '''Setup standard source parameters.

        :param file_: If None, `__file__` is used.
        :param source: If None, `read_source(file_)` is used.
        '''
        # @:adhoc_run_time_section:@ on
        if file_ is None:
            file_ = __file__
        if file_.endswith('.pyc'):
            file_ = file_[:-1]
        if source is None:
            if len(file_) == 0 or file_ == '-':
                source = sys.stdin.read()
            else:
                source = cls.read_source(file_)
        return (file_, source)

    @classmethod
    def export(cls, file_=None, source=None):                # |:mth:|
        file_, source = cls.std_source_param(file_, source)
        # |:todo:| this chaos needs cleanup (cls.import_/cls.export__)
        sv_import = cls.import_
        cls.import_ = cls.export__

        file_ = os.path.basename(file_)
# @:adhoc_run_time_section:@
        if cls.verbose:
            map(sys.stderr.write,
                ("# xp: ", cls.__name__, ".export for `", file_, "`\n"))
# @:adhoc_run_time_section:@ on
        cls.export_(source, file_)
        for init_dir in cls.export_need_init:
            if not cls.export_have_init[init_dir]:
                if cls.verbose:
                    map(sys.stderr.write,
                        ("# xp: create __init__.py in `", init_dir, "`\n"))
                inf = open(os.path.join(
                    cls.export_dir, init_dir, '__init__.py'), 'w')
                inf.write('')
                inf.close()
        cls.import_ = sv_import

        # unpack to export directory
        sv_extract_dir = cls.extract_dir
        cls.extract_dir = cls.export_dir
        cls.extract(file_, source)
        cls.extract_dir = sv_extract_dir

    @classmethod
    def dump__(cls, module_name, file_=None, mtime=None, # |:mth:|
               zipped=True, source64=None):
        if cls.verbose:
            map(sys.stderr.write,
                ("# xf: ", cls.__name__, ": dumping `", file_, "`\n"))
        source = cls.unpack_file(source64, zipped)
        return source

    @classmethod
    def dump_(cls, dump_section, dump_type=None):            # |:mth:|
        if dump_type is None:
            dump_type = 'adhoc_import'
        dump_call = ''.join(('unpacked = ', cls.__name__, '.dump__'))
        dump_section = re.sub('^\\s+', '', dump_section)
        dump_section = re.sub(
            '^[^(]*(?s)', dump_call, dump_section)
        dump_dict = {'unpacked': ''}
        try:
            #RtAdHoc = cls # dump_call takes care of this
            exec(dump_section.lstrip(), globals(), dump_dict)
        except IndentationError:
            sys.stderr.write("!!! IndentationError !!!\n")
# @:adhoc_run_time_section:@
            sys.stderr.write(''.join((dump_section, "\n")))
# @:adhoc_run_time_section:@ on
        return dump_dict['unpacked']

    @classmethod
    def dump_file(cls, match, file_=None, source=None, marker=None, # |:mth:|
                  is_re=False):
        file_, source = cls.std_source_param(file_, source)
        if marker is None:
            marker = '(adhoc_import|adhoc_update)'
            is_re = True
        source_sections, dump_sections = cls.partition(
            source, marker, is_re, headline=True)
        dump_call = ''.join((cls.__name__, '.dump_'))
        for dump_section in dump_sections:
            tag_line = dump_section[0]
            dump_section = dump_section[1]
            tag_arg = cls.line_tag_strip(tag_line)
            check_match = match
            if tag_arg != match and not match.startswith('-'):
                check_match = ''.join(('-', match))
            if tag_arg != match and not match.startswith('!'):
                check_match = ''.join(('!', match))
            if tag_arg != match:
                continue
            dump_section = re.sub('^\\s+', '', dump_section)
            dump_section = re.sub(
                '^[^(]*(?s)', dump_call, dump_section)
            try:
                #RtAdHoc = cls # dump_call takes care of this
                exec(dump_section.lstrip(), globals(), locals())
            except IndentationError:
                sys.stderr.write("!!! IndentationError !!!\n")
# @:adhoc_run_time_section:@
                sys.stderr.write(''.join((dump_section, "\n")))
# @:adhoc_run_time_section:@ on

    @classmethod
    def unpack_(cls, ignored, file_=None, mtime=None,        # |:mth:|
                 zipped=True, source64=None):
        xfile = cls.check_xfile(file_, cls.extract_dir)
        if xfile is None:
            return
        if cls.verbose:
            map(sys.stderr.write,
                ("# xf: ", cls.__name__, ": unpacking `", file_, "`\n"))
        source = cls.unpack_file(source64, zipped)
        cls.write_source(xfile, source)

    @classmethod
    def unpack(cls, file_=None, source=None):                # |:mth:|
        file_, source = cls.std_source_param(file_, source)
        source_sections, unpack_sections = cls.partition(
            source, cls.section_tag('adhoc_unpack'))
        sv_extract_warn = cls.extract_warn
        cls.extract_warn = True
        unpack_call = ''.join((cls.__name__, '.unpack_'))
        for unpack_section in unpack_sections:
            unpack_section = re.sub('^\\s+', '', unpack_section)
            unpack_section = re.sub(
                '^[^(]*(?s)', unpack_call, unpack_section)
            try:
                #RtAdHoc = cls # unpack_call takes care of this
                exec(unpack_section.lstrip(), globals(), locals())
            except IndentationError:
                sys.stderr.write("!!! IndentationError !!!\n")
# @:adhoc_run_time_section:@
                sys.stderr.write(''.join((unpack_section, "\n")))
# @:adhoc_run_time_section:@ on
        cls.extract_warn = sv_extract_warn

    @classmethod
    def std_template_param(cls, file_=None, source=None,     # |:mth:|
                           marker=None, is_re=False, all_=False):
        # @:adhoc_run_time_section:@
        '''Setup standard template parameters.

        :param marker: If None, `adhoc_template(_v)?` is used.

        See :meth:`std_source_param` for `file_` and `source`.
        '''
        # @:adhoc_run_time_section:@ on
        file_, source = cls.std_source_param(file_, source)
        if marker is None:
            is_re=True
            if all_:
                marker = cls.section_tag('adhoc_(template(_v)?|import|unpack)')
            else:
                marker = cls.section_tag('adhoc_template(_v)?', is_re=is_re)
        return (file_, source, marker, is_re)

    @classmethod
    def get_templates(cls, file_=None, source=None,          # |:mth:|
                      marker=None, is_re=False,
                      ignore_mark=False, all_=False):
        # @:adhoc_run_time_section:@
        '''Extract templates matching section marker.

        :param ignore_mark: If True, all templates are mapped to
          standard output name ``-``.
        :param marker: If None, `adhoc_template` is used.
        '''
        # @:adhoc_run_time_section:@ on
        # |:here:|
        file_, source, marker, is_re = cls.std_template_param(
            file_, source, marker, is_re, all_)
        source = cls.enable_sections(source, 'adhoc_uncomment')
        source = cls.indent_sections(source, 'adhoc_indent')
        source_sections, template_sections = cls.partition(
            source, marker, is_re=is_re, headline=True)
        templates = {}
        for template_section in template_sections:
            tag_line = template_section[0]
            section = template_section[1]
            tag, tag_arg = cls.line_tag_parse(tag_line)
            if ignore_mark:
                tag_arg = '-'
            else:
                if not tag_arg:
                    tag_arg = '-'
            if tag_arg not in templates:
                templates[tag_arg] = [[section], tag]
            else:
                templates[tag_arg][0].append(section)
        if all_:
            result = dict([(m, (''.join(t[0]), t[1])) for m, t in templates.items()])
        else:
            result = dict([(m, ''.join(t[0])) for m, t in templates.items()])
        return result

    @classmethod
    def template_list(cls, file_=None, source=None,          # |:mth:|
                      marker=None, is_re=False, all_=False):
        # @:adhoc_run_time_section:@
        '''Sorted list of templates.

        See :meth:`std_template_param` for `file_`, `source`, `marker`, `is_re`.
        '''
        # @:adhoc_run_time_section:@ on
        file_, source, marker, is_re = cls.std_template_param(
            file_, source, marker, is_re, all_)
        templates = cls.get_templates(file_, source, marker, is_re, all_=all_)
        if all_:
            result = list(sorted(
                [(k, v[1]) for k, v in templates.items()],
                key=lambda kt: '||'.join((
                    kt[1], kt[0] if
                    not (kt[0].startswith('-') or kt[0].startswith('!')) else
                    kt[0][1:]))))
        else:
            result = list(sorted(
                templates.keys(),
                key=lambda kt: '||'.join((
                    kt[1], kt[0] if
                    not (kt[0].startswith('-') or kt[0].startswith('!')) else
                    kt[0][1:]))))
        return result

    # @:adhoc_run_time_section:@
    # @:adhoc_template:@ -col-param-closure
    # @:adhoc_run_time_section:@ on
    @classmethod
    def col_param_closure(cls):
        # @:adhoc_run_time_section:@
        '''Closure for setting up maximum width, padding and separator
        for table columns.

        :returns: a setter and a getter function for calculating the
          maximum width of a list of strings (e.g. a table column).

        >>> set_, get_ = AdHoc.col_param_closure()
        >>> i = set_("string")
        >>> get_()
        [6, '      ', '======']

        >>> i = set_("str")
        >>> get_()
        [6, '      ', '======']

        >>> i = set_("longer string")
        >>> get_()
        [13, '             ', '=============']

        >>> table_in = """\\
        ... Column1 Column2
        ... some text text
        ... some-more-text text text
        ... something text
        ... less"""

        A splitter and column parameters depending on column count:

        >>> col_count = 2
        >>> splitter = lambda line: line.split(' ', col_count-1)
        >>> col_params = [AdHoc.col_param_closure() for i in range(col_count)]

        Generic table processor:

        >>> process_cols = lambda cols: [
        ...     col_params[indx][0](col) for indx, col in enumerate(cols)]
        >>> table = [process_cols(cols) for cols in
        ...          [splitter(line) for line in table_in.splitlines()]]

        Generic table output parameters/functions:

        >>> mws = [cp[1]()[0] for cp in col_params]
        >>> sep = ' '.join([cp[1]()[2] for cp in col_params])
        >>> paddings = [cp[1]()[1] for cp in col_params]
        >>> pad_cols_c = lambda cols: [
        ...     col if paddings[indx] is None else
        ...     (paddings[indx][:int((mws[indx]-len(col))/2)]
        ...      + col + paddings[indx])[:mws[indx]]
        ...     for indx, col in enumerate(cols)]
        >>> pad_cols = lambda cols: [
        ...     col if paddings[indx] is None else
        ...     (col + paddings[indx])[:mws[indx]]
        ...     for indx, col in enumerate(cols)]

        Generic table output generator:

        >>> output = []
        >>> if table:
        ...     output.append(sep)
        ...     output.append(' '.join(pad_cols_c(table.pop(0))).rstrip())
        ...     if table: output.append(sep)
        ...     output.extend([' '.join(pad_cols(cols)).rstrip()
        ...                    for cols in table])
        ...     output.append(sep)

        >>> i = sys.stdout.write("\\n".join(output))
        ============== =========
           Column1      Column2
        ============== =========
        some           text text
        some-more-text text text
        something      text
        less
        ============== =========
        '''
        # @:adhoc_run_time_section:@ on
        mw = [0, "", ""]
        def set_(col):
            lc = len(col)
            if mw[0] < lc:
                mw[0] = lc
                mw[1] = " " * lc
                mw[2] = "=" * lc
            return col
        def get_():
            return mw
        return set_, get_
    # @:adhoc_run_time_section:@
    # @:adhoc_template:@ -col-param-closure
    # @:adhoc_run_time_section:@ on

    @classmethod
    def template_table(cls, file_=None, source=None,         # |:mth:|
                       marker=None, is_re=False):
        # @:adhoc_run_time_section:@
        '''Table of template commands.

        See :meth:`std_template_param` for `file_`, `source`, `marker`, `is_re`.
        '''
        # @:adhoc_run_time_section:@ on
        file_, source, marker, is_re = cls.std_template_param(
            file_, source, marker, is_re, all_=True)
        # Parse table
        table = []
        tpl_arg_name = (lambda t: t if not (t.startswith('-') or t.startswith('!')) else t[1:])
        col_param = [cls.col_param_closure() for i in range(3)]
        table.append((col_param[0][0]('Command'), col_param[1][0]('Template'), col_param[2][0]('Type')))
        table.extend([(col_param[0][0](''.join((
            os.path.basename(file_), ' --template ',
            tpl_arg_name(t[0]))).rstrip()),
                       col_param[1][0](''.join(('# ', t[0])).rstrip()),
                       col_param[2][0](''.join((t[1])).rstrip()),
                       )
                      for t in cls.template_list(file_, source, marker, is_re, all_=True)])
        # Setup table output
        mw, padding = (col_param[0][1]()[0], col_param[0][1]()[1])
        mw1, padding1 = (col_param[1][1]()[0], col_param[1][1]()[1])
        mw2, padding2 = (col_param[2][1]()[0], col_param[2][1]()[1])
        sep = ' '.join([cp[1]()[2] for cp in col_param])
        make_row_c = lambda row: ''.join((
            ''.join((padding[:int((mw-len(row[0]))/2)], row[0], padding))[:mw],
            ' ', ''.join((padding1[:int((mw1-len(row[1]))/2)],
                          row[1], padding1))[:mw1],
            ' ', ''.join((padding2[:int((mw2-len(row[2]))/2)],
                          row[2], padding2))[:mw2].rstrip()))
        make_row = lambda row: ''.join((''.join((row[0], padding))[:mw],
                                        ' ', ''.join((row[1], padding))[:mw1],
                                        ' ', row[2])).rstrip()
        # Generate table
        output = []
        output.append(sep)
        output.append(make_row_c(table.pop(0)))
        if table:
            output.append(sep)
            output.extend([make_row(row) for row in table])
        output.append(sep)
        return output

    @classmethod
    def get_named_template(cls, name=None, file_=None, source=None, # |:mth:|
                           marker=None, is_re=False, ignore_mark=False):
        # @:adhoc_run_time_section:@
        '''Extract templates matching section marker and name.

        :param name: Template name. If None, standard output name ``-`` is used.
        :param marker: If None, `adhoc_template(_v)?` is used.
        :param ignore_mark: If True, all templates are mapped to
          standard output name ``-``.

        If a named template cannot be found and `name` does not start
        with ``-``, the template name `-name` is tried.

        >>> ign = main("adhoc.py --template adhoc_test.sub".split())
        # -*- coding: utf-8 -*-
        <BLANKLINE>
        ADHOC_TEST_SUB_IMPORTED = True

        '''
        # @:adhoc_run_time_section:@ on
        if name is None:
            name = '-'
        file_, source, marker, is_re = cls.std_template_param(
            file_, source, marker, is_re, all_=True)
        templates = cls.get_templates(
            file_, source, marker, is_re=is_re, ignore_mark=ignore_mark, all_=True)
        check_name = name
        if check_name not in templates and not name.startswith('-'):
            check_name = ''.join(('-', name))
        if check_name not in templates and not name.startswith('!'):
            check_name = ''.join(('!', name))
        if check_name in templates:
            template_set = templates[check_name]
        else:
            template_set = ['', 'adhoc_template']
        template = template_set[0]
        template_type = template_set[1]
        if check_name.startswith('!'):
            template = cls.dump_(template, template_type)
        return template

    @classmethod
    def extract_templates(cls, file_=None, source=None,      # |:mth:|
                          marker=None, is_re=False, ignore_mark=False,
                          export=False):
        # @:adhoc_run_time_section:@
        '''Extract template.

        # @:adhoc_template_check:@ -mark
        A template ...
        # @:adhoc_template_check:@

        # @:adhoc_template_check:@ -other
        Another interleaved
        # @:adhoc_template_check:@

        # @:adhoc_template_check:@ -mark
        continued
        # @:adhoc_template_check:@

        >>> AdHoc.extract_templates(
        ...     marker=AdHoc.section_tag("adhoc_template_check"))
                A template ...
                continued
                Another interleaved

        >>> rt_section = AdHoc.get_templates(
        ...     __file__, None,
        ...     marker=AdHoc.section_tag("adhoc_run_time_section"),
        ...     ignore_mark=True)
        >>> rt_section = ''.join(rt_section.values())

        .. >>> printf(rt_section)
        '''
        # @:adhoc_run_time_section:@ on
        file_, source, marker, is_re = cls.std_template_param(
            file_, source, marker, is_re)
        templates = cls.get_templates(
            file_, source, marker, is_re=is_re, ignore_mark=ignore_mark)
        sv_extract_warn = cls.extract_warn
        cls.extract_warn = True
        for outf, template in sorted(templates.items()):
            if outf.startswith('-'):
                outf = '-'
            if outf == '-' and export:
                continue
            xfile = cls.check_xfile(outf, cls.extract_dir)
            if xfile is not None:
                cls.write_source(xfile, template)
        cls.extract_warn = sv_extract_warn

    @classmethod
    def extract(cls, file_=None, source=None):               # |:mth:|
        cls.unpack(file_, source)
        cls.extract_templates(file_, source, export=True)

    @classmethod
    def import_(cls, mod_name=None, file_=None, mtime=None,  # |:mth:|
                zipped=True, source64=None):
        import datetime

        module = cls.module_setup(mod_name)

        if mtime is None:
            mtime = datetime.datetime.fromtimestamp(0)
        else:
            # mtime=2011-11-23T18:04:26[.218506], zipped=True, source64=
            try:
                date, ms = mtime.split('.')
            except ValueError:
                date = mtime
                ms = 0
            mtime = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
            mtime += datetime.timedelta(microseconds=int(ms))

        source = cls.unpack_file(source64, zipped)

        # |:todo:| add to parent module
        mod_parts = mod_name.split('.')
        mod_child = mod_parts[-1]
        parent = '.'.join(mod_parts[:-1])
# @:adhoc_run_time_section:@
        printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'parent', parent))

# @:adhoc_run_time_section:@ on
        old_mtime = module.__adhoc__.mtime
        module = cls.module_setup(mod_name, file_, mtime, source)
        if len(parent) > 0:
            setattr(sys.modules[parent], mod_child, module)

        if module.__adhoc__.mtime != old_mtime:
# @:adhoc_run_time_section:@
            printf(sformat('{0}Executing source',dbg_comm))
# @:adhoc_run_time_section:@ on
            source = cls.encode_source(module.__adhoc__.source)
            exec(source, module.__dict__)
# @:adhoc_run_time_section:@

        msg = 'YES' if mod_name in sys.modules else 'NO'
        printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                       dbg_comm, dbg_twid, dbg_fwid, ':DBG:',
                       mod_name + ' imported', msg))

        module_name = module.__name__
        printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                       dbg_comm, dbg_twid, dbg_fwid, ':DBG:',
                       'module_name', module_name))
        dump_attr(module, wid=80, trunc=5)
# @:adhoc_run_time_section:@ on

    @classmethod
    def module_setup(cls, module=None, file_=None, mtime=None, # |:mth:|
                     source=None):
        m = 'ms: '
# @:adhoc_run_time_section:@
        '''Setup module for AdHoc.
        |:todo:| various modes are possible:
        - always use newest version (development) (currently implemented)
        - always use adhoc\'ed version (freeze) (not implemented)
        '''
# @:adhoc_run_time_section:@ on
        class Attr:                                          # |:cls:|
            pass

        import types, datetime, os
        if not isinstance(module, types.ModuleType):
            mod_name = module
            if mod_name is None:
                mod_name = __name__
            try:
                if mod_name not in sys.modules:
# @:adhoc_run_time_section:@
                    if cls.verbose:
                        printe(sformat('{0}{1}__import__({2})',
                                       dbg_comm, m, mod_name))
# @:adhoc_run_time_section:@ on
                    __import__(mod_name)
                module = sys.modules[mod_name]
            except (ImportError, KeyError):
# @:adhoc_run_time_section:@
                if cls.verbose:
                    printe(sformat('{0}{1}imp.new_module({2})',
                                   dbg_comm, m, mod_name))
# @:adhoc_run_time_section:@ on
                import imp
                module = imp.new_module(mod_name)
                sys.modules[mod_name] = module
        else:
            mod_name = module.__name__

        if mtime is None:
            if (file_ is not None
                or source is not None):
                # the info is marked as outdated
                mtime = datetime.datetime.fromtimestamp(1)
            else:
                # the info is marked as very outdated
                mtime = datetime.datetime.fromtimestamp(0)

        if not hasattr(module, '__adhoc__'):
            adhoc = Attr()
            setattr(module, '__adhoc__', adhoc)
            setattr(adhoc, '__module__', module)

            mtime_set = None
            if hasattr(module, '__file__'):
                module_file = module.__file__
                if module_file.endswith('.pyc'):
                    module_file = module_file[:-1]
                if os.access(module_file, os.R_OK):
                    stat = os.stat(module_file)
                    mtime_set = datetime.datetime.fromtimestamp(
                        stat.st_mtime)
            if mtime_set is None:
                # the info is marked as very outdated
                mtime_set = datetime.datetime.fromtimestamp(0)
            adhoc.mtime = mtime_set
        else:
            adhoc = module.__adhoc__

        if (mtime > adhoc.mtime
            or not hasattr(module, '__file__')):
            if file_ is not None:
                setattr(module, '__file__', file_)
                if os.access(file_, os.R_OK):
                    stat = os.stat(file_)
                    adhoc.mtime = datetime.datetime.fromtimestamp(
                        stat.st_mtime)
                    if adhoc.mtime > mtime:
                        # the file on disk is newer than the adhoc'ed source
                        try:
                            delattr(adhoc, 'source')
                        except AttributeError:
                            pass
                        source = None

        if (mtime > adhoc.mtime
            or not hasattr(adhoc, 'source')):
            if source is not None:
                adhoc.source = source
                adhoc.mtime = mtime

        if not hasattr(adhoc, 'source'):
            try:
                file_ = module.__file__
                if file_.endswith('.pyc'):
                    file_ = file_[:-1]
                source = cls.read_source(file_)
                adhoc.source = source
            except (AttributeError, IOError):
# @:adhoc_run_time_section:@
                # if hasattr(module, '__path__'): # |:debug:|
                #     map(sys.stderr.write,
                #         ('module path: ', module.__path__, '\n'))
                # else:
                #     sys.stderr.write('no module.__path__\n')
                #     map(sys.stderr.write,
                #         [''.join((attr, str(value), "\n")) for attr, value in
                #          filter(lambda i: i[0] != '__builtins__',
                #                 sorted(vars(module).items()))])
                if cls.verbose:
                    (t, e, tb) = sys.exc_info()
                    import traceback
                    printe(''.join(traceback.format_tb(tb)), end='')
                    printe(sformat('{0}: {1}', t.__name__, e))
                    del(tb)
# @:adhoc_run_time_section:@ on
                pass

        return module
# @:adhoc_run_time_section:@

    # --------------------------------------------------
    # ||:sec:|| COMPILER DATA
    # --------------------------------------------------

    # tags are generated from symbols on init
    run_time_flag = None                      # line
    import_flag = None                        # line
    compiled_flag = None                      # line
    run_time_class_flag = None                # line

    ensable_section_tag = None                # section
    disable_section_tag = None                # section
    remove_section_tag = None                 # section
    import_section_tag = None                 # section
    run_time_section_tag = None               # section

    run_time_section = None

    run_time_flag_symbol = 'adhoc_run_time'   # line
    import_flag_symbol = 'adhoc'              # line
    verbatim_flag_symbol = 'adhoc_verbatim'   # line
    include_flag_symbol = 'adhoc_include'     # line
    compiled_flag_symbol = 'adhoc_compiled'   # line
    run_time_class_symbol = 'adhoc_run_time_class' # line

    enable_section_symbol = 'adhoc_enable'    # section
    disable_section_symbol = 'adhoc_disable'  # section
    remove_section_symbol = 'adhoc_remove'    # section
    import_section_symbol = 'adhoc_import'    # section
    unpack_section_symbol = 'adhoc_unpack'    # section
    run_time_section_symbol = 'adhoc_run_time_section' # section

    run_time_class_prefix = 'Rt'
    import_function = 'AdHoc.import_'

    modules = {}
    compiling = []

    # --------------------------------------------------
    # ||:sec:|| Setup
    # --------------------------------------------------

    def __init__(self):                                      # |:mth:|
        self.modules = {}
        self.compiling = []
        self.setup_tags()
        self.run_time_section = self.prepare_run_time_section().rstrip() + '\n'

    def setup_tags(self):                                    # |:mth:|
        self.run_time_flag = self.line_tag(self.run_time_flag_symbol)
        self.import_flag = self.line_tag(self.import_flag_symbol)
        self.verbatim_flag = self.line_tag(self.verbatim_flag_symbol)
        self.include_flag = self.line_tag(self.include_flag_symbol)
        self.compiled_flag = self.line_tag(self.compiled_flag_symbol)
        self.run_time_class_flag = self.line_tag(self.run_time_class_symbol)

        self.enable_section_tag = self.section_tag(self.enable_section_symbol)
        self.disable_section_tag = self.section_tag(self.disable_section_symbol)
        self.remove_section_tag = self.section_tag(self.remove_section_symbol)
        self.import_section_tag = self.section_tag(self.import_section_symbol)
        self.unpack_section_tag = self.section_tag(self.unpack_section_symbol)
        self.run_time_section_tag = self.section_tag(
            self.run_time_section_symbol)

    def prepare_run_time_section(self):                      # |:mth:|
        rts = self.adhoc_get_run_time_section(
            self.run_time_section_symbol)
        rtc_sections = self.adhoc_split(
            rts, self.run_time_class_flag)
        transform = []
        done = False
        use_next = False
        for section in rtc_sections:
            blob = section[1]
            if section[0]:
                use_next = blob
                continue
            if use_next:
                if not done:
                    mo = re.search('class[ \t\r]+', blob)
                    if mo:
                        blob = (blob[:mo.end(0)]
                              + self.run_time_class_prefix
                              + blob[mo.end(0):])
                        done = True
                    else:
                        #transform.append(use_next)
                        pass
                use_next = False
            transform.append(blob)
        transform.append(sformat('# {0}\n',self.remove_section_tag))
        # |:todo:| make frozen configurable
        transform.append(sformat('{0}AdHoc.frozen = False\n',
                self.run_time_class_prefix))
        transform.append(sformat('# {0}\n',self.remove_section_tag))
        rts = ''.join(transform)
        if not done:
            raise AdHocError(
                sformat('run-time class(marker) `{0}` not found in:\n{1}',
                        self.run_time_class_flag, rts))
        return rts

    # --------------------------------------------------
    # ||:sec:|| Internal Includer
    # --------------------------------------------------

    def verbatim_(self, string, name=None):                  # |:mth:|
        '''Entry point for inclusion. \\|:here:|

        >>> section = """\\
        ... some
        ...     @:""" """adhoc_verbatim:@ -2# my_verbatim from /dev/null
        ... text\\
        ... """

        >>> adhoc = AdHoc()
        >>> sv_verbose = AdHoc.verbose
        >>> #AdHoc.verbose = True
        >>> source = adhoc.verbatim_(section)
        >>> AdHoc.verbose = sv_verbose
        >>> printf(source) #doctest: +ELLIPSIS
        some
            @:adhoc_verba...:@ -2# my_verbatim from /dev/null
          # @:adhoc_uncomment:@
          # @:adhoc_indent:@ -2
          # @:adhoc_templ..._v:@ my_verbatim
          # @:adhoc_templ..._v:@
          # @:adhoc_indent:@
          # @:adhoc_uncomment:@
        text
        '''
        m = 'is: '

        import datetime

        if name is None:
            name = repr(string[:50])
        # # check for @: adhoc_compiled :@
        # adhoc_compiled_lines = self.get_lines(
        #     string, self.line_tag('adhoc_compiled'))
        # if len(adhoc_compiled_lines) > 0:
        #     sys.stderr.write(sformat(
        #         '{0}{1}' 'warning: {2} already AdHoc\'ed `{3}`\n',
        #         dbg_comm, m, name, adhoc_compiled_lines[0].rstrip()))
        #     return string

        # handle @: adhoc_verbatim :@
        result = []
        verbatim_cmd_sections = self.adhoc_split(string, self.verbatim_flag)
        for section in verbatim_cmd_sections:
            verbatim_def = section[1]
            result.append(verbatim_def)
            if section[0]:
                # skip commented verbatims
                if re.match('\\s*#\\s*#', verbatim_def):
                    if self.verbose:
                        printe(sformat(
                            '{0}{1}Skipping disabled verbatim `{2}`',
                            dbg_comm, m, verbatim_def.rstrip()))
                    continue

                indent = ''
                mo = re.match('\\s*', verbatim_def)
                if mo:
                    indent = mo.group(0)

                verbatim_def = self.line_tag_strip(
                    verbatim_def, self.verbatim_flag_symbol)
                verbatim_specs = []
                for verbatim_spec in re.split('\\s*,\\s*', verbatim_def):
                    verbatim_spec1 = re.split('\\s+from\\s+', verbatim_spec)
                    verbatim_spec = re.split('\\s+', verbatim_spec1[0], 1)
                    if len(verbatim_spec) == 1:
                        verbatim_spec.insert(0, '')
                    verbatim_spec.extend(verbatim_spec1[1:])
                    if not verbatim_spec:
                        continue
                    # if len(verbatim_spec) == 1:
                    #     verbatim_spec.append(verbatim_spec[0])
                    verbatim_specs.append(verbatim_spec)

                for verbatim_spec in verbatim_specs:
                    vflags = verbatim_spec.pop(0)
                    ifile = verbatim_spec[0]
                    found = False
                    for lfile in verbatim_spec:
                        blfile = lfile
                        for include_dir in self.include_path:
                            if not os.path.exists(lfile):
                                if not (blfile.startswith('/')):
                                    lfile = os.path.join(include_dir, blfile)
                                    continue
                            break
                        if os.path.exists(lfile):
                            stat = os.stat(lfile)
                            mtime = datetime.datetime.fromtimestamp(
                                stat.st_mtime)

                            exp_source = self.read_source(lfile)
                            source_len = len(exp_source)

                            start_tags = []
                            end_tags = []
                            prefix = []
                            tag_prefix = ['# ']

                            mo = re.search('[-+]?[0-9]+', vflags)
                            if mo:
                                uindent = int(mo.group(0))
                            else:
                                uindent = 0

                            tindent = (len(indent) + uindent)
                            if tindent < 0:
                                tindent = 0
                            if tindent:
                                tag = self.section_tag('adhoc_indent')
                                start_tags.insert(
                                    0, ''.join((tag, ' ', str(-tindent))))
                                end_tags.append(tag)
                                prefix.insert(0, ' ' * tindent)
                                tag_prefix.insert(0, ' ' * tindent)

                            if '#' in vflags:
                                tag = self.section_tag('adhoc_uncomment')
                                start_tags.insert(0, tag)
                                end_tags.append(tag)
                                exp_source = self.disable_transform(exp_source)

                            tag = self.section_tag('adhoc_template_v')
                            start_tags.append(''.join((tag, ' ', ifile)))
                            end_tags.insert(0,tag)

                            prefix = ''.join(prefix)
                            tag_prefix = ''.join(tag_prefix)
                            if prefix and exp_source:
                                exp_source = re.sub('^(?m)', prefix, exp_source)
                                if not exp_source.endswith('\n'):
                                    exp_source = ''.join((exp_source, '\n'))

                            output = []
                            output.extend([''.join((
                                tag_prefix, tag, '\n')) for tag in start_tags])
                            output.append(exp_source)
                            output.extend([''.join((
                                tag_prefix, tag, '\n')) for tag in end_tags])
                            result.append(''.join(output))
                            found = True

                            # |:debug:|
                            if self.verbose:
                                printe(sformat(
                                    "{0}{3:^{1}} {4:<{2}s}: ]len: {5:>6d}"
                                    " exp: {6:>6d} ]{9}[",
                                    dbg_comm, dbg_twid, dbg_fwid, ':INF:',
                                    'source stats', source_len, len(exp_source),
                                    0, 0, ifile))
                            # |:debug:|
                            break
                    if not found and not self.quiet:
                        map(sys.stderr.write,
                            ("# if: ", self.__class__.__name__,
                             ": warning verbatim file `", ifile,
                             "` not found from `",
                             ', '.join(verbatim_spec), "`\n"))
        #adhoc_dump_list(result)
        return ''.join(result)

    # --------------------------------------------------
    # ||:sec:|| Internal Includer
    # --------------------------------------------------

    def include_(self, string, name=None, zipped=True):      # |:mth:|
        '''Entry point for inclusion. \\|:here:|

        >>> section = """\\
        ... some
        ... @:""" """adhoc_include:@ Makefile
        ... text\\
        ... """

        >>> adhoc = AdHoc()
        >>> source = adhoc.include_(section)
        >>> printf(source) #doctest: +ELLIPSIS
        some
        @:adhoc_include... Makefile
        # @:adhoc_unpack...
        RtAdHoc.unpack_(None, file_='Makefile',
            mtime='...', zipped=True, source64=
        ...
        # @:adhoc_unpack...
        text
        '''
        m = 'is: '

        import datetime

        if name is None:
            name = repr(string[:50])
        # # check for @: adhoc_compiled :@
        # adhoc_compiled_lines = self.get_lines(
        #     string, self.line_tag('adhoc_compiled'))
        # if len(adhoc_compiled_lines) > 0:
        #     sys.stderr.write(sformat(
        #         '{0}{1}' 'warning: {2} already AdHoc\'ed `{3}`\n',
        #         dbg_comm, m, name, adhoc_compiled_lines[0].rstrip()))
        #     return string

        # handle @: adhoc_include :@
        result = []
        include_cmd_sections = self.adhoc_split(string, self.include_flag)
        for section in include_cmd_sections:
            include_def = section[1]
            result.append(include_def)
            if section[0]:
                # skip commented includes
                if re.match('\\s*#\\s*#', include_def):
                    if self.verbose:
                        printe(sformat(
                            '{0}{1}Skipping disabled include `{2}`',
                            dbg_comm, m, include_def.rstrip()))
                    continue

                indent = ''
                mo = re.match('\\s*', include_def)
                if mo:
                    indent = mo.group(0)

                include_def = self.line_tag_strip(
                    include_def, self.include_flag_symbol)
                include_specs = []
                for include_spec in re.split('\\s*,\\s*', include_def):
                    include_spec = re.split('\\s+from\\s+', include_spec)
                    if not include_spec:
                        continue
                    # if len(include_spec) == 1:
                    #     include_spec.append(include_spec[0])
                    include_specs.append(include_spec)

                for include_spec in include_specs:
                    ifile = include_spec[0]
                    found = False
                    for lfile in include_spec:
                        blfile = lfile
                        for include_dir in self.include_path:
                            if not os.path.exists(lfile):
                                if not (blfile.startswith('/')):
                                    lfile = os.path.join(include_dir, blfile)
                                    continue
                            break
                        if os.path.exists(lfile):
                            stat = os.stat(lfile)
                            mtime = datetime.datetime.fromtimestamp(
                                stat.st_mtime)

                            exp_source = self.read_source(lfile)

                            source64 = self.pack_file(exp_source, zipped)
                            output = self.strquote(source64, indent)
                            output = sformat(
                                "{0}# {1}\n{0}{9}{2}(None, file_={4},\n"
                                "{0}    mtime={5}, zipped={6},"
                                " source64=\n{7})\n{0}# {8}\n",
                                indent,
                                ''.join((self.unpack_section_tag, ' !', ifile)),
                                'AdHoc.unpack_',
                                None,
                                repr(str(ifile)),
                                (repr(mtime.isoformat()) if
                                 mtime is not None else
                                 repr(mtime)),
                                zipped, output.rstrip(),
                                self.unpack_section_tag,
                                self.run_time_class_prefix
                                )
                            result.append(output)
                            found = True
                            # |:debug:|
                            if self.verbose:
                                source_len = len(exp_source)
                                exp_source_len = len(exp_source)
                                source64_len = len(source64)
                                printe(sformat(
                                    "{0}{3:^{1}} {4:<{2}s}: ]len: {5:>6d}"
                                    " exp: {6:>6d} b64: {8:>6d}[ ]{9}[",
                                    dbg_comm, dbg_twid, dbg_fwid, ':INF:',
                                    'source stats', source_len, exp_source_len,
                                    0, source64_len, ifile))
                            # |:debug:|
                            break
                    if not found and not self.quiet:
                        map(sys.stderr.write,
                            ("# if: ", self.__class__.__name__,
                             ": warning include file `",
                             ifile, "` not found from `",
                             ', '.join(include_spec), "`\n"))
        #adhoc_dump_list(result)
        return ''.join(result)

    # --------------------------------------------------
    # ||:sec:|| Internal Compiler
    # --------------------------------------------------

    def encode_module_(                                      # |:mth:|
        self, module, for_=None, indent='', zipped=True):
        m = 'gm: '

        if for_ is None:
            for_ = self.import_function

        module = self.module_setup(module)
        module_name = module.__name__

        # no multiple occurences
        if (module_name in self.modules
            or module_name in self.compiling):
            if self.verbose:
                 # |:check:| what, if the previous import was never
                 # executed?
                sys.stderr.write(sformat(
                        '{0}{1}`{2}` already seen. skipping ...\n',
                        dbg_comm, m, module_name))
            return ''

        self.compiling.append(module_name)

        result = []
        # |:todo:| parent modules
        parts = module_name.split('.')
        parent_modules = parts[:-1]
        if self.verbose and len(parent_modules) > 0:
            sys.stderr.write(sformat(
                    '{0}{1}Handle parent module(s) `{2}`\n',
                    dbg_comm, m, parent_modules))
        for parent_module in parent_modules:
            result.append(self.encode_module_(
                parent_module, for_, indent, zipped))

        if (module_name in self.modules):
            if self.verbose:
                sys.stderr.write(sformat(
                    '{0}{1}{1} already seen after parent import\n',
                    dbg_comm, m, module_name))
            return ''.join(result)

        if hasattr(module, '__file__'):
            module_file = module.__file__
            if module_file.endswith('.pyc'):
                module_file = module_file[:-1]
        else:
            module_file = None

        if hasattr(module.__adhoc__, 'source'):
            source = module.__adhoc__.source
        else:
            if not self.quiet:
                printf(sformat(
                    '{0}{1}|' 'warning: `{2}` does not have any source code.',
                    dbg_comm, m, module_name), file=sys.stderr)
            source = ''

        # recursive!
        exp_source = self.compile_(source, module_file, for_, zipped)
        source64 = self.pack_file(exp_source, zipped)
        output = self.strquote(source64, indent)

        mtime = module.__adhoc__.mtime
        # |:todo:| make Rt prefix configurable
        output = sformat(
            "{0}# {1}\n{0}{9}{2}({3}, file_={4},\n{0}    mtime={5}, zipped={6},"
            " source64=\n{7})\n{0}# {8}\n",
            indent,
            ''.join((self.import_section_tag, ' !', module_name)),
            for_,
            repr(module.__name__),
            (module_file if module_file is None else
             repr(str(os.path.relpath(module_file)))),
            #repr(mtime),
            repr(mtime.isoformat()) if mtime is not None else repr(mtime),
            zipped, output.rstrip(),
            self.import_section_tag,
            self.run_time_class_prefix
            )
        result.append(output)

        # |:debug:|
        if self.verbose:
            source_len = len(source)
            exp_source_len = len(exp_source)
            source64_len = len(source64)
            printe(sformat(
                "{0}{3:^{1}} {4:<{2}s}: ]len: {5:>6d} exp: {6:>6d}"
                " b64: {8:>6d}[ ]{9}[",
                dbg_comm, dbg_twid, dbg_fwid, ':INF:',
                'source stats', source_len, exp_source_len, 0,
                source64_len, module_file))
        # |:debug:|
        return ''.join(result)

    def compile_(self, string, name=None, for_=None,         # |:mth:|
                 zipped=True):
        '''Entry point for compilation. \\|:here:|

        '''
        m = 'cs: '
        if name is None:
            name = repr(string[:50])
        # check for @: adhoc_compiled :@
        adhoc_compiled_lines = self.get_lines(
            string, self.line_tag('adhoc_compiled'))
        if len(adhoc_compiled_lines) > 0:
            if not self.quiet:
                map(sys.stderr.write,
                    ('# ', m,  'warning: ', name, ' already AdHoc\'ed `',
                     adhoc_compiled_lines[0].rstrip(), '`\n',))
            return string

        # check for @: adhoc_self :@
        adhoc_self_tag = self.line_tag('adhoc_self')
        adhoc_self_lines = self.get_lines(
            string, adhoc_self_tag)
        if len(adhoc_self_lines) > 0:
            for line in adhoc_self_lines:
                line = re.sub(''.join(('^.*', adhoc_self_tag)), '', line)
                line = line.strip()
                selfs = line.split()
                if self.verbose:
                    printe(sformat(
                        '{0}{1}|' ':INF:| {2} found self: `{3}`',
                        dbg_comm, m, name, ', '.join(selfs)))
                self.compiling.extend(selfs)

        # check for @: adhoc_enable :@
        string = self.enable_sections(string, 'adhoc_enable')

        # check for @: adhoc_disable :@
        string = self.disable_sections(string, 'adhoc_disable')

        # check for @: adhoc_remove :@
        string = self.rename_marker(string, 'adhoc_remove', 'adhoc_remove_')

        # check for @: adhoc_include :@
        string = self.include_(string, name, zipped)

        # check for @: adhoc_include :@
        string = self.verbatim_(string, name)

        # search for @: adhoc_run_time :@ and put run-time section there!
        result = []
        ah_run_time_sections = self.adhoc_split(
            string, self.line_tag(self.run_time_flag_symbol))
        good = False
        for section in ah_run_time_sections:
            config_def = section[1]
            if not good and section[0]:
                config_def = sformat('{0}{1}',
                    config_def, self.run_time_section)
                good = True
            result.append(config_def)
        string = ''.join(result)

        # handle @: adhoc :@ imports
        result = []
        import_cmd_sections = self.adhoc_split(string, self.import_flag)
        if not good and len(import_cmd_sections) > 1:
            adhoc_dump_sections(import_cmd_sections)
            raise AdHocError(sformat('{0} not found',
                    self.line_tag(self.run_time_flag_symbol)))
        for section in import_cmd_sections:
            import_def = section[1]
            if section[0]:
                # skip commented imports
                if re.match('[ \t\r]*#', import_def):
                    if self.verbose:
                        printe(sformat(
                            '{0}{1}Skipping disabled `{2}`',
                            dbg_comm, m, import_def.rstrip()))
                    result.append(import_def)
                    continue
                module = ''
                mo = re.match(
                    '([ \t\r]*)from[ \t\r]+([a-zA-Z_][.0-9a-zA-Z_]*)[ \t\r]+'
                    'import', import_def)
                if mo:
                    indent = mo.group(1)
                    module = mo.group(2)
                else:
                    mo = re.match(
                        '([ \t\r]*)import[ \t\r]+([a-zA-Z_][.0-9a-zA-Z_]*)',
                        import_def)
                    if mo:
                        indent = mo.group(1)
                        module = mo.group(2)
                if len(module) > 0:
                    source = self.encode_module_(module, for_, indent, zipped)
                    import_def = sformat('{0}{1}',source, import_def)
                else:
                    if self.verbose:
                        map(sys.stderr.write,
                            ('# ', m, 'warning: no import found! `',
                             import_def.rstrip(), '`\n'))
            result.append(import_def)

        #adhoc_dump_list(result)
        return ''.join(result)

    # --------------------------------------------------
    # ||:sec:|| User API
    # --------------------------------------------------

    def encode_include(                                      # |:mth:|
        self, file_, as_=None, indent='', zipped=True):
        m = 'if: '

    def encode_module(                                       # |:mth:|
        self, module, for_=None, indent='', zipped=True):
        if hasattr(module, __name__):
            name = module.__name__
        else:
            name = module
        if self.verbose:
            sys.stderr.write(sformat(
                '{0}--------------------------------------------------\n',
                dbg_comm))
            sys.stderr.write(sformat(
                '{0}Get module `{1}`\n',
                dbg_comm, name))
            sys.stderr.write(sformat(
                '{0}--------------------------------------------------\n',
                dbg_comm))
        return self.encode_module_(module, for_, indent, zipped)

    def compile(self, string, name=None, for_=None,          # |:mth:|
                zipped=True):
        if self.verbose:
            if name is None:
                name = repr(string[:50])
            sys.stderr.write(sformat(
                    '{0}--------------------------------------------------\n',
                    dbg_comm))
            sys.stderr.write(sformat(
                    '{0}Compiling string `{1}`\n',
                    dbg_comm, name))
            sys.stderr.write(sformat(
                    '{0}--------------------------------------------------\n',
                    dbg_comm))
        return self.compile_(string, name, for_, zipped)
# @:adhoc_run_time_section:@ on

    def compileFile(self, file_name, for_=None, zipped=True): # |:mth:|
# @:adhoc_run_time_section:@
        if self.verbose:
            sys.stderr.write(sformat(
                '{0}--------------------------------------------------\n',
                dbg_comm))
            sys.stderr.write(
                sformat('{0}Compiling {1}\n',dbg_comm, file_name))
            sys.stderr.write(sformat(
                '{0}--------------------------------------------------\n',
                dbg_comm))
# @:adhoc_run_time_section:@ on
        file_name, source = self.std_source_param(file_name, None)
# @:adhoc_run_time_section:@
        source = self.compile_(source, file_name, for_, zipped)
# @:adhoc_run_time_section:@ on
        return source
# @:adhoc_run_time_section:@

    @classmethod
    def adhoc_run_time_sections_from_string(cls, string, symbol): # |:clm:|
        marker = sformat('(#[ \t\r]*)?{0}', cls.section_tag(symbol, is_re=True))
        def_sections = cls.get_sections(string, marker, is_re=True)
        return def_sections

    @classmethod
    def adhoc_run_time_section_from_file(cls, file_, symbol): # |:clm:|
        if file_.endswith('.pyc'):
            file_ = file_[:-1]
        string = cls.read_source(file_)
        def_sections = cls.adhoc_run_time_sections_from_string(
            string, symbol)
        return def_sections

    @classmethod
    def adhoc_get_run_time_section(                          # |:clm:|
        cls, symbol, prolog='', epilog=''):
        import datetime

        adhoc_module_places = []

        # try __file__
        adhoc_module_places.append(__file__)
        def_sections = cls.adhoc_run_time_section_from_file(
            __file__, symbol)
        if len(def_sections) == 0:
            # try adhoc.__file__
            try:
                import adhoc
                adhoc_module_places.append(adhoc.__file__)
                def_sections = cls.adhoc_run_time_section_from_file(
                    adhoc.__file__, symbol)
            except:
                pass
        if len(def_sections) == 0:
            # try adhoc.__adhoc__.source
            try:
                adhoc_module_places.append('adhoc.__adhoc__.source')
                def_sections = cls.adhoc_run_time_sections_from_string(
                    adhoc.__adhoc__.source, symbol)
            except:
                pass

        if len(def_sections) == 0:
            adhoc_dump_list(def_sections)
            raise AdHocError(sformat('{0} not found in {1}',
                    cls.section_tag(symbol),
                    ', '.join(adhoc_module_places)))

        def_ = ''.join((
                sformat('# {0}\n', cls.section_tag('adhoc_remove')),
                sformat('# {0} {1}\n', cls.line_tag('adhoc_compiled'),
                                     datetime.datetime.now(),
                                     # |:todo:| add input filename
                                     ),
                prolog,
                ''.join(def_sections),
                epilog,
                sformat('# {0}\n', cls.section_tag('adhoc_remove')),
                ))
        return def_

# (progn (forward-line -1) (insert "\n") (snip-insert-mode "py.s.class" t) (backward-symbol-tag 2 "fillme" "::"))

# --------------------------------------------------
# |||:sec:||| FUNCTIONS
# --------------------------------------------------

# (progn (forward-line 1) (snip-insert-mode "py.f.hl" t) (insert "\n"))
hlr = None
def hlcr(title=None, tag='|||' ':CHP:|||', rule_width=50, **kwargs): # ||:fnc:||
    comm = globals()['dbg_comm'] if 'dbg_comm' in globals() else '# '
    dstr = []
    dstr.append(''.join((comm, '-' * rule_width)))
    if title:
        dstr.append(sformat('{0}{2:^{1}} {3!s}',
                comm, globals()['dbg_twid'] if 'dbg_twid' in globals() else 9,
                tag, title))
        dstr.append(''.join((comm, '-' * rule_width)))
    return '\n'.join(dstr)

def hlsr(title=None, tag='||' ':SEC:||', rule_width=35, **kwargs): # |:fnc:|
    return hlcr(title, tag, rule_width)

def hlssr(title=None, tag='|' ':INF:|', rule_width=20, **kwargs): # |:fnc:|
    return hlcr(title, tag, rule_width)

def hlc(*args, **kwargs):                                    # |:fnc:|
    for line in hlcr(*args, **kwargs).splitlines():
        printf(line, **kwargs)

def hls(*args, **kwargs):                                    # |:fnc:|
    for line in hlsr(*args, **kwargs).splitlines():
        printf(line, **kwargs)

def hlss(*args, **kwargs):                                   # |:fnc:|
    for line in hlssr(*args, **kwargs).splitlines():
        printf(line, **kwargs)

def hl(*args, **kwargs):                                     # |:fnc:|
    for line in hlr(*args, **kwargs).splitlines():
        printf(line, **kwargs)

def hl_lvl(level=0):                                         # |:fnc:|
    global hlr
    if level == 0:
        hlr = hlssr
    elif level == 1:
        hlr = hlsr
    else:
        hlr = hlcr

hl_lvl(0)

# (progn (forward-line 1) (snip-insert-mode "py.f.single.quote" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.f.remove.match" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.f.printenv" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.f.uname-s" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.f.printe" t) (insert "\n"))
def printe(*args, **kwargs):                               # ||:fnc:||
    kwargs['file'] = kwargs.get('file', sys.stderr)
    printf(*args, **kwargs)

# (progn (forward-line 1) (snip-insert-mode "py.f.dbg.squeeze" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.f.dbg.indent" t) (insert "\n"))

# (progn (forward-line -1) (insert "\n") (snip-insert-mode "py.s.func" t) (backward-symbol-tag 2 "fillme" "::"))

# --------------------------------------------------
# |||:sec:||| UTILTIES
# --------------------------------------------------

def adhoc_dump_list(list_):                                # ||:fnc:||
    for elt in list_:
        elt = str(elt)
        if len(elt) > 78:
            elt = elt[:75] + ' ...'
        printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'elt', repr(elt)))

def adhoc_dump_sections(sections):                         # ||:fnc:||
    for section in sections:
        cut_section = list(section)
        if len(cut_section[1]) > 78:
            cut_section[1] = cut_section[1][:75] + ' ...'
        printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'section', cut_section))

# --------------------------------------------------
# |||:sec:||| SYMBOL-TAG TOOLS
# --------------------------------------------------

def adhoc_line_tagr(symbol):                               # ||:fnc:||
    return AdHoc.line_tag(symbol, True)
def adhoc_section_tagr(symbol):                            # ||:fnc:||
    return AdHoc.section_tag(symbol, True)
def adhoc_splitr(string, marker):                          # ||:fnc:||
    return AdHoc.adhoc_split(string, marker, True)
def adhoc_get_linesr(string, marker):                      # ||:fnc:||
    return AdHoc.get_lines(string, marker, True)
def adhoc_partitionr(string, marker):                      # ||:fnc:||
    return AdHoc.partition(string, marker, True)
def adhoc_get_sectionsr(string, marker):                   # ||:fnc:||
    return AdHoc.get_sections(string, marker, True)

def compile_(files=None):                                  # ||:fnc:||
    '''compile a file or standard input.'''
    if files is None:
        files = []

    # use current libdir
    # @:adhoc_disable:@
    # current_topdir = os.path.abspath(os.curdir)
    # if current_topdir not in sys.path:
    #     sys.path.insert(0,current_topdir)
    # current_libdir = current_topdir
    # _current_topdir = current_topdir
    # for indx in range(0,10):
    #     _current_libdir = os.path.join(_current_topdir, 'lib', 'python')
    #     if os.path.exists(_current_libdir):
    #         current_topdir = _current_topdir
    #         current_libdir = _current_libdir
    #         break
    #     _current_topdir = os.path.abspath(
    #         os.path.join(_current_topdir, os.pardir))
    # if current_libdir not in sys.path:
    #     sys.path.insert(0,current_libdir)
    # if _debug:
    #     printe(sformat(
    #             "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
    #             dbg_comm, dbg_twid, dbg_fwid, ':DBG:',
    #             'current_topdir', current_topdir))
    #     printe(sformat(
    #             "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
    #             dbg_comm, dbg_twid, dbg_fwid, ':DBG:',
    #             'current_libdir', current_libdir))
    # @:adhoc_disable:@

    std_sys_path = sys.path

    if len(files) == 0:
        files.append('-')
    compiled_files = []
    for file_ in files:
        sys.path = std_sys_path
        if file_ != '-':

            # use source libdir
            # @:adhoc_disable:@
            # source_topdir = os.path.abspath(os.curdir)
            # if source_topdir not in sys.path:
            #     sys.path.insert(0,source_topdir)
            # source_libdir = source_topdir
            # _source_topdir = source_topdir
            # for indx in range(0,10):
            #     _source_libdir = os.path.join(_source_topdir, 'lib', 'python')
            #     if os.path.exists(_source_libdir):
            #         source_topdir = _source_topdir
            #         source_libdir = _source_libdir
            #         break
            #     _source_topdir = os.path.abspath(os.path.join(
            #         _source_topdir, os.pardir))
            # if source_libdir not in sys.path:
            #     sys.path.insert(0,source_libdir)
            # if _debug:
            #     printe(sformat(
            #             "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
            #             dbg_comm, dbg_twid, dbg_fwid, ':DBG:',
            #             'source_topdir', source_topdir))
            #     printe(sformat(
            #             "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
            #             dbg_comm, dbg_twid, dbg_fwid, ':DBG:',
            #             'source_libdir', source_libdir))
            # @:adhoc_disable:@
            pass

        ah = AdHoc()
        compiled = ah.compileFile(file_)
        compiled_files.append(compiled)

    return ''.join(map(lambda c: c if c.endswith('\n') else ''.join((c, '\n')),
                       compiled_files))

# --------------------------------------------------
# |||:sec:||| TEST
# --------------------------------------------------

def adhoc_run_time_module():         # ||:fnc:|| |:todo:| experimental
    import imp
    if 'adhoc.rt' in sys.modules:
        return

    file_ = __file__
    source = None
    exec_ = False
    if file_.endswith('.pyc'):
        file_ = file_[:-1]
    if 'adhoc' in sys.modules:
        adhoc = sys.modules['adhoc']
    else:
        adhoc = imp.new_module('adhoc')
        setattr(adhoc, '__file__', file_)
        sys.modules['adhoc'] = adhoc
        exec_ = True

    if not hasattr(adhoc, '__adhoc__'):
        __adhoc__ = {}
        adhoc.__adhoc__ = __adhoc__

    if 'source' not in adhoc.__adhoc__:
        adhoc.__adhoc__['source'] = AdHoc.read_source(file_)
    if exec_:
        source = AdHoc.encode_source(adhoc.__adhoc__['source'])
        exec(source, adhoc)

    RT = imp.new_module('adhoc.rt')
    setattr(adhoc, 'rt', RT)

def adhoc_check_modules():                                 # ||:fnc:||

    hl_lvl(0)
    hlc('adhoc_check_modules')

    printf(sformat('{0}--------------------------------------------------',
                   dbg_comm))
    msg = 'SEEN' if 'adhoc_test' in sys.modules else 'NOT SEEN'
    printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                   dbg_comm, dbg_twid, dbg_fwid, ':DBG:',
                   'PRE  sub import', 'adhoc_test ' + msg))
    import adhoc_test.sub                                  # @:adhoc:@
    msg = 'SEEN' if 'adhoc_test' in sys.modules else 'NOT SEEN'
    printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                   dbg_comm, dbg_twid, dbg_fwid, ':DBG:',
                   'POST sub import', 'adhoc_test ' + msg))

    printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                   dbg_comm, dbg_twid, dbg_fwid, ':DBG:',
                   'dir(adhoc_test.sub)', dir(adhoc_test.sub)))
    printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                   dbg_comm, dbg_twid, dbg_fwid, ':DBG:',
                   'adhoc_test.sub.__file__', adhoc_test.sub.__file__))
    if 'adhoc_test' in sys.modules:
        printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                       dbg_comm, dbg_twid, dbg_fwid, ':DBG:',
                       'dir(adhoc_test)[auto]', dir(adhoc_test)))

    printf(sformat('{0}--------------------------------------------------',
                   dbg_comm))
    import adhoc_test                                      # @:adhoc:@
    printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                   dbg_comm, dbg_twid, dbg_fwid, ':DBG:',
                   'dir(adhoc_test)', dir(adhoc_test)))
    printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                   dbg_comm, dbg_twid, dbg_fwid, ':DBG:',
                   'adhoc_test.__file__', adhoc_test.__file__))
    if hasattr(adhoc_test, '__path__'):
        printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                       dbg_comm, dbg_twid, dbg_fwid, ':DBG:',
                       'adhoc_test.__path__', adhoc_test.__path__))

def adhoc_check_module_setup():                            # ||:fnc:||
    '''

    >>> sv_stdout = sys.stdout
    >>> output = _AdHocStringIO()
    >>> sys.stdout = output
    >>> adhoc_check_module_setup()
    >>> contents = output.getvalue()
    >>> output.close()
    >>> sys.stdout = sv_stdout
    >>> contents = re.sub('(mtime.*\\])[^[]*(\\[)', r'\\1\\2', contents)
    >>> contents = re.sub(' at 0x([0-9a-f]+)', '', contents)
    >>> contents = re.sub(r'adhoc\\.pyc', 'adhoc.py', contents)
    >>> contents = '\\n'.join([l.strip() for l in contents.splitlines()])
    >>> ign = open('yyy', 'w').write(re.sub('^(?m)', '    ', contents)
    ...     .replace('\\\\', '\\\\\\\\') + '\\n')
    >>> printf(contents, end='') #doctest: +ELLIPSIS
    # --------------------------------------------------
    # |||:CHP:||| adhoc_check_module_setup
    # --------------------------------------------------
    # -----------------------------------
    # ||:SEC:|| no:module:found
    # -----------------------------------
    #   :DBG:   module                 : ]['__adhoc__', '__doc__', '__name__', '__package__'][
    # ------------------------------
    #   :DBG:   __adhoc__              : ]...
    #   :DBG:   __doc__                : ]None[
    #   :DBG:   __name__               : ]no:module:found[
    #   :DBG:   __package__            : ]None[
    # --------------------
    #  |:INF:|  no:module:found.__adhoc__
    # --------------------
    #   :DBG:   __adhoc__              : ]...
    # ------------------------------
    #   :DBG:   __module__             : ]<module 'no:module:found' (built-in)>[
    #   :DBG:   mtime                  : ][
    # -----------------------------------
    # ||:SEC:|| adhoc_test.sub
    # -----------------------------------
    #   :DBG:   module                 : ]['ADHOC_TEST_SUB_IMPORTED',...
    # ------------------------------
    #   :DBG:   ADHOC_TEST_SUB_IMPORTED: ]True[
    #   :DBG:   __adhoc__              : ]...
    ...
    #   :DBG:   __doc__                : ]None[
    #   :DBG:   __file__               : ].../adhoc_test/sub/__init__.py...[
    #   :DBG:   __name__               : ]adhoc_test.sub[
    #   :DBG:   __package__            : ]None[
    #   :DBG:   __path__               : ]['.../adhoc_test/sub'][
    # --------------------
    #  |:INF:|  adhoc_test.sub.__adhoc__
    # --------------------
    #   :DBG:   __adhoc__              : ]...
    # ------------------------------
    #   :DBG:   __module__             : ]<module 'adhoc_test.sub' from '.../adhoc_test/sub/__init__.py...'>[
    #   :DBG:   mtime                  : ][
    #   :DBG:   source                 : ]# -*- coding: utf-8 -*-\\n\\nADHOC_TEST_SUB_IMPORTED = True\\n[
    # -----------------------------------
    # ||:SEC:|| adhoc
    # -----------------------------------
    #   :DBG:   adhoc                  : ]...
    # ------------------------------
    #   :DBG:   AdHoc                    : ]<class 'adhoc.AdHoc'>[
    #   :DBG:   AdHocError               : ]<class 'adhoc.AdHocError'>[
    ...
    #   :DBG:   RST_HEADER               : ]...
    ...
    #   :DBG:   __adhoc__                : ]...
    ...
    #   :DBG:   __file__                 : ].../adhoc.py...[
    #   :DBG:   __name__                 : ]adhoc[
    #   :DBG:   __package__              : ]None[
    #   :DBG:   _debug                   : ]False[
    #   :DBG:   _nativestr               : ]<function _nativestr>[
    #   :DBG:   _quiet                   : ]False[
    #   :DBG:   _uc                      : ]<function ...>[
    #   :DBG:   _utf8str                 : ]<function _utf8str>[
    #   :DBG:   _verbose                 : ]False[
    #   :DBG:   adhoc_check_encode_module: ]<function adhoc_check_encode_module>[
    #   :DBG:   adhoc_check_module_setup : ]<function adhoc_check_module_setup>[
    #   :DBG:   adhoc_check_modules      : ]<function adhoc_check_modules>[
    #   :DBG:   adhoc_check_packing      : ]<function adhoc_check_packing>[
    #   :DBG:   adhoc_dump_list          : ]<function adhoc_dump_list>[
    #   :DBG:   adhoc_dump_sections      : ]<function adhoc_dump_sections>[
    #   :DBG:   adhoc_get_linesr         : ]<function adhoc_get_linesr>[
    #   :DBG:   adhoc_get_sectionsr      : ]<function adhoc_get_sectionsr>[
    #   :DBG:   adhoc_line_tagr          : ]<function adhoc_line_tagr>[
    #   :DBG:   adhoc_partitionr         : ]<function adhoc_partitionr>[
    #   :DBG:   adhoc_rst_to_ascii       : ]<function adhoc_rst_to_ascii>[
    #   :DBG:   adhoc_run_time_module    : ]<function adhoc_run_time_module>[
    #   :DBG:   adhoc_section_tagr       : ]<function adhoc_section_tagr>[
    #   :DBG:   adhoc_splitr             : ]<function adhoc_splitr>[
    #   :DBG:   base64                   : ]<module 'base64' from '.../base64.py...'>[
    #   :DBG:   compile_                 : ]<function compile_>[
    #   :DBG:   dbg_comm                 : ]# [
    #   :DBG:   dbg_fwid                 : ]23[
    #   :DBG:   dbg_twid                 : ]9[
    #   :DBG:   dict_dump                : ]<function dict_dump>[
    #   :DBG:   ditems                   : ]<function <lambda>>[
    #   :DBG:   dkeys                    : ]<function <lambda>>[
    #   :DBG:   dump_attr                : ]<function dump_attr>[
    #   :DBG:   dvalues                  : ]<function <lambda>>[
    #   :DBG:   file_encoding_is_clean   : ]True[
    #   :DBG:   get_readme               : ]<function get_readme>[
    #   :DBG:   hl                       : ]<function hl>[
    #   :DBG:   hl_lvl                   : ]<function hl_lvl>[
    #   :DBG:   hlc                      : ]<function hlc>[
    #   :DBG:   hlcr                     : ]<function hlcr>[
    #   :DBG:   hlr                      : ]<function hlssr>[
    #   :DBG:   hls                      : ]<function hls>[
    #   :DBG:   hlsr                     : ]<function hlsr>[
    #   :DBG:   hlss                     : ]<function hlss>[
    #   :DBG:   hlssr                    : ]<function hlssr>[
    #   :DBG:   isstring                 : ]<function isstring>[
    #   :DBG:   main                     : ]<function main>[
    #   :DBG:   mw_                      : ]<class 'adhoc.mw_'>[
    #   :DBG:   mwg_                     : ]<class 'adhoc.mwg_'>[
    #   :DBG:   namespace_dict           : ]<module 'namespace_dict' from '.../namespace_dict.py...'>[
    #   :DBG:   nativestr                : ]<function nativestr>[
    #   :DBG:   os                       : ]<module 'os' from '.../os.py...'>[
    #   :DBG:   printe                   : ]<function printe>[
    #   :DBG:   printf                   : ]<built-in function print>[
    #   :DBG:   re                       : ]<module 're' from '.../re.py...'>[
    #   :DBG:   rst_to_ascii             : ]<function rst_to_ascii>[
    #   :DBG:   run                      : ]<function run>[
    #   :DBG:   setdefaultencoding       : ]<function setdefaultencoding>[
    #   :DBG:   sformat                  : ]<function sformat>[
    #   :DBG:   sys                      : ]<module 'sys' (built-in)>[
    #   :DBG:   uc                       : ]<function uc>[
    #   :DBG:   uc_type                  : ]<...>[
    #   :DBG:   urllib                   : ]<module 'urllib' from '.../urllib...'>[
    #   :DBG:   utf8str                  : ]<function utf8str>[
    # --------------------
    #  |:INF:|  adhoc.__adhoc__
    # --------------------
    #   :DBG:   __adhoc__              : ]...
    # ------------------------------
    #   :DBG:   __module__             : ]<module 'adhoc' from '.../adhoc.py...'>[
    #   :DBG:   mtime                  : ][
    #   :DBG:   source                 : ]#!/usr/bin/env python\\n# -*- coding: utf-8 -*-\\n# Copyright (C) 2011, 2012, Wolfgang Scherer,
    ...

    .. \\|:here:|
    '''
# :ide-menu: Emacs IDE Menu - Buffer @BUFFER@
# . M-x `eIDE-menu' ()(eIDE-menu "z")

# also remove __builtins__, _AdHocStringIO ...
# (progn
# (goto-char point-min) (replace-string "/home/ws/project/ws-util/adhoc" "..." nil (if (and transient-mark-mode mark-active) (region-beginning)) (if (and transient-mark-mode mark-active) (region-end)))
# (goto-char point-min) (replace-string "/home/ws/project/ws-util/lib/python" "..." nil (if (and transient-mark-mode mark-active) (region-beginning)) (if (and transient-mark-mode mark-active) (region-end)))
# (goto-char point-min) (replace-string "/home/ws/project/ws-util" "..." nil (if (and transient-mark-mode mark-active) (region-beginning)) (if (and transient-mark-mode mark-active) (region-end)))
# (goto-char point-min) (replace-string ".pyc" ".py" nil (if (and transient-mark-mode mark-active) (region-beginning)) (if (and transient-mark-mode mark-active) (region-end)))
# (goto-char point-min) (replace-string ".py" ".py..." nil (if (and transient-mark-mode mark-active) (region-beginning)) (if (and transient-mark-mode mark-active) (region-end)))
# (goto-char point-min) (replace-string ".../urllib.py..." ".../urllib..." nil (if (and transient-mark-mode mark-active) (region-beginning)) (if (and transient-mark-mode mark-active) (region-end)))
# (goto-char point-min) (replace-string "/usr/lib/python2.7" "..." nil (if (and transient-mark-mode mark-active) (region-beginning)) (if (and transient-mark-mode mark-active) (region-end)))
# (goto-char point-min) (replace-string-regexp "#   :DBG:   __adhoc__\\( *\\): \\].*" "#   :DBG:   __adhoc__\\1: ]..." nil (if (and transient-mark-mode mark-active) (region-beginning)) (if (and transient-mark-mode mark-active) (region-end)))
# (goto-char point-min) (replace-string-regexp "#   :DBG:   adhoc\\( *\\): \\].*" "#   :DBG:   adhoc\\1: ]..." nil (if (and transient-mark-mode mark-active) (region-beginning)) (if (and transient-mark-mode mark-active) (region-end)))
# (goto-char point-min) (replace-string-regexp "#   :DBG:   module                 : ..'ADHOC_TEST_SUB_IMPORTED',.*" "#   :DBG:   module                 : ]['ADHOC_TEST_SUB_IMPORTED',..." nil (if (and transient-mark-mode mark-active) (region-beginning)) (if (and transient-mark-mode mark-active) (region-end)))
# (goto-char point-min) (replace-string "<function _uc>" "<function ...>" nil (if (and transient-mark-mode mark-active) (region-beginning)) (if (and transient-mark-mode mark-active) (region-end)))
# (goto-char point-min) (replace-string "<type 'unicode'>" "<...>" nil (if (and transient-mark-mode mark-active) (region-beginning)) (if (and transient-mark-mode mark-active) (region-end)))
# (goto-char point-min)
# (goto-char point-min)
# (goto-char point-min)
# )
    wid = 100
    trunc = 10
    hl_lvl(0)
    hlc('adhoc_check_module_setup')

    mod_name = 'no:module:found'
    hls(mod_name)
    module = AdHoc.module_setup('no:module:found')
    printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                   dbg_comm, dbg_twid, dbg_fwid, ':DBG:',
                   'module', str(dir(module))[:wid]))
    dump_attr(module, wid=wid, trunc=trunc)

    hl(sformat('{0}.__adhoc__',mod_name))
    printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                   dbg_comm, dbg_twid, dbg_fwid, ':DBG:',
                   '__adhoc__', str(dir(module.__adhoc__))[:wid]))
    dump_attr(module.__adhoc__, wid=wid, trunc=trunc)

    hls('adhoc_test.sub')
    import adhoc_test.sub
    module = AdHoc.module_setup('adhoc_test.sub')
    printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                   dbg_comm, dbg_twid, dbg_fwid, ':DBG:',
                   'module', str(dir(module))[:wid]))
    dump_attr(module, wid=wid, trunc=trunc)

    hl('adhoc_test.sub.__adhoc__')
    printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                   dbg_comm, dbg_twid, dbg_fwid, ':DBG:',
                   '__adhoc__', str(dir(module.__adhoc__))[:wid]))
    dump_attr(module.__adhoc__, wid=wid, trunc=trunc)

    try:
        import adhoc
        hls('adhoc')
        module = AdHoc.module_setup('adhoc')
        printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                       dbg_comm, dbg_twid, dbg_fwid, ':DBG:',
                       'adhoc', str(dir(module))[:wid]))
        dump_attr(module, wid=wid, trunc=trunc)

        hl('adhoc.__adhoc__')
        printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                       dbg_comm, dbg_twid, dbg_fwid, ':DBG:',
                       '__adhoc__', str(dir(module.__adhoc__))[:wid]))
        dump_attr(module.__adhoc__, wid=wid, trunc=trunc)
    except ImportError:
        pass

def adhoc_check_encode_module():                           # ||:fnc:||

    wid = 100
    trunc = 10
    hl_lvl(0)
    hlc('adhoc_check_encode_module')

    module = AdHoc.module_setup('no:module:found')

    hl('IMPORT SPEC')
    ahc = AdHoc()
    import_spec = '\n'.join(ahc.run_time_section.splitlines()[:5])
    printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                   dbg_comm, dbg_twid, dbg_fwid, ':DBG:',
                   'ahc.run_time_section', import_spec))

    for_=None

    module_name = 'no:module:found'
    #hl(sformat('GET MODULE {0}',module_name))
    module_import = ahc.encode_module(module_name, for_)
    printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                   dbg_comm, dbg_twid, dbg_fwid, ':DBG:',
                   'module_import',
                   '\n'.join(module_import.splitlines()[:5])))

    module_name = 'ws_sql_tools'
    #hl(sformat('GET MODULE {0}',module_name))
    module_import = ahc.encode_module(module_name, for_)
    printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                   dbg_comm, dbg_twid, dbg_fwid, ':DBG:',
                   'module_import',
                   '\n'.join(module_import.splitlines()[:5])))

    hl('EXECUTE')
    exec(module_import)

def adhoc_check_packing():                                 # ||:fnc:||
    """
    >>> source = AdHoc.read_source(__file__)
    >>> AdHoc.write_source('write-check', source)
    >>> rsource = AdHoc.read_source('write-check')
    >>> os.unlink('write-check')
    >>> (source == rsource)
    True
    >>> psource = AdHoc.pack_file(source, zipped=False)
    >>> usource = AdHoc.unpack_file(psource, zipped=False)
    >>> (source == usource)
    True
    >>> psource = AdHoc.pack_file(source, zipped=True)
    >>> usource = AdHoc.unpack_file(psource, zipped=True)
    >>> (source == usource)
    True
    """

def run(parameters, pass_opts):                            # ||:fnc:||
    """Application runner, when called as __main__."""

    # (progn (forward-line 1) (snip-insert-mode "py.bf.sql.ws" t) (insert "\n"))
    # (progn (forward-line 1) (snip-insert-mode "py.bf.file.arg.loop" t) (insert "\n"))

    # @:adhoc_disable:@
    run_time = False
    # @:adhoc_disable:@
    run_time = parameters.compile
    # @:adhoc_enable:@
    # run_time = True
    # @:adhoc_enable:@

    # empty disabled section
    # @:adhoc_disable:@
    # @:adhoc_disable:@

    # empty enabled section
    # @:adhoc_enable:@
    # @:adhoc_enable:@

    # |:here:|
    if False:
        exit(0)

    if run_time:
        compiled = compile_(parameters.args)
        printf(compiled, end='')
        return

    # |:here:|
    # @:adhoc_disable:@ -development_tests
    myfile = __file__
    if myfile.endswith('.pyc'):
        myfile = myfile[:-1]
    myself = AdHoc.read_source(myfile)

    if False:
        adhoc_check_modules()       # |:debug:|
        adhoc_check_module_setup()  # |:debug:|

        # import ws_sql_tools
        # ws_sql_tools.dbg_fwid = dbg_fwid
        ws_sql_tools.check_file()

        import_cmd_sections = AdHoc.get_lines(
            myself, AdHoc.line_tag('adhoc'))
        printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                       dbg_comm, dbg_twid, dbg_fwid, ':DBG:',
                       'import_cmd_sections', import_cmd_sections))

        import_cmd_sections = AdHoc.adhoc_split(
            myself, AdHoc.line_tag('adhoc'))
        adhoc_dump_sections(import_cmd_sections)

        pass
    # |:here:|
    # @:adhoc_disable:@

    # @:adhoc_disable:@ -more_development_tests
    # @:adhoc_remove:@
    ah_retained, ah_removed = AdHoc.partition(
        myself, AdHoc.section_tag('adhoc_remove'))
    hl('REMOVED')
    adhoc_dump_list(ah_removed)
    hl('RETAINED')
    adhoc_dump_list(ah_retained)
    # @:adhoc_remove:@

    # |:debug:| def/class
    ah = AdHoc()
    ah_run_time_section = ah.prepare_run_time_section()
    printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                   dbg_comm, dbg_twid, dbg_fwid, ':DBG:',
                   'ah_run_time_section', ah_run_time_section))

    # adhoc_check_modules()       # |:debug:|
    # adhoc_check_module_setup()  # |:debug:|
    # adhoc_check_encode_module() # |:debug:|

    # |:debug:| compiler
    ah = AdHoc()
    compiled = ah.compile(myself, 'myself')
    printf(compiled, end='')
    # @:adhoc_disable:@

    # |:here:|
    return

# --------------------------------------------------
# |||:sec:||| MAIN
# --------------------------------------------------

_quiet = False
_verbose = False
_debug = False

# (progn (forward-line 1) (snip-insert-mode "py.f.setdefaultencoding" t) (insert "\n"))
file_encoding_is_clean = True
def setdefaultencoding(encoding=None, quiet=False):
    if file_encoding_is_clean:
        return
    if encoding is None:
        encoding='utf-8'
    try:
        isinstance('', basestring)
        if not hasattr(sys, '_setdefaultencoding'):
            if not quiet:
                printf('''\
Add this to /etc/python2.x/sitecustomize.py,
or put it in local sitecustomize.py and adjust PYTHONPATH=".:${PYTHONPATH}"::

    try:
        import sys
        setattr(sys, '_setdefaultencoding', getattr(sys, 'setdefaultencoding'))
    except AttributeError:
        pass

Running with reload(sys) hack ...
''', file=sys.stderr)
            reload(sys)
            setattr(sys, '_setdefaultencoding',
                    getattr(sys, 'setdefaultencoding'))
        sys._setdefaultencoding(encoding)
    except NameError:
        # python3 already has utf-8 default encoding ;-)
        pass

# @:adhoc_uncomment:@
# @:adhoc_template:@ -max-width-class
class mw_(object):
    mw = 0
    def __call__(self, col):
        if self.mw < len(col):
            self.mw = len(col)
        return col
class mwg_(object):
    def __init__(self, mwo):
        self.mwo = mwo
    def __call__(self):
        return self.mwo.mw
# mws = [mw_(), mw_()]
# mwg = [mwg_(mwo) for mwo in mws]
# @:adhoc_template:@ -max-width-class
# @:adhoc_uncomment:@

# @:adhoc_template:@ -rst-to-ascii
RST_HEADER = '''\
.. role:: mod(strong)
.. role:: class(strong)
.. role:: func(strong)
.. role:: meth(strong)

'''

RST_FOOTER = '''
.. :ide: COMPILE: render reST as HTML
.. . (let* ((fp (buffer-file-name)) (fn (file-name-nondirectory fp))) (save-match-data (if (string-match-t "[.][^.]*$" fn) (setq fn (replace-match "" nil t fn)))) (let ((args (concat " " fp " | ws_rst2html.py --traceback --cloak-email-addresses | tee " fn ".html "))) (save-buffer) (compile (concat "PATH=\\".:$PATH\\"; cat " args))))

.. 
.. Local Variables:
.. mode: rst
.. snip-mode: rst
.. truncate-lines: t
.. symbol-tag-symbol-regexp: "[-0-9A-Za-z_#]\\\\([-0-9A-Za-z_. ]*[-0-9A-Za-z_]\\\\|\\\\)"
.. symbol-tag-auto-comment-mode: nil
.. symbol-tag-srx-is-safe-with-nil-delimiters: nil
.. End:
'''

def rst_to_ascii(string):                                  # ||:fnc:||
    '''Transform ReST documentation to ASCII.'''
    string = re.sub(
        '^\\s*[.][.]\\s*(note|warning|attention)::(?im)', '\\1:', string)
    string = re.sub(
        '^\\s*[.][.]\\s*automodule::[^\\n]*\\n(\\s[^\\n]+\\n)*\\n(?m)',
        '', string + '\n\n')
    string = re.sub('^\\s*[.][.][^\\n]*\\n(?m)', '', string)
    string = re.sub('\\n\\n\\n+', '\\n\\n', string)
    return string

def adhoc_rst_to_ascii(string):                            # ||:fnc:||
    '''Transform ReST documentation to ASCII.'''
    string = rst_to_ascii(string)
    string = string.replace('|@:|\\\\? ', '@:')
    string = string.replace('\\\\? |:@|', ':@')
    string = string.replace('|@:|', '`@:`')
    string = string.replace('|:@|', '`:@`')
    string = re.sub('^:[|](adhoc[^|]*)[|]([^:]*):(?m)', '@:\\1:@\\2', string)
    string = re.sub('[|](adhoc[^|]*)[|]', '@:\\1:@', string)
    return string

def get_readme(file_=None, source=None, as_template=False, transform=True): # ||:fnc:||
    file_, source = AdHoc.std_source_param(file_, source)
    template_name = 'doc/index.rst'
    template = AdHoc.get_named_template(template_name, file_, source)
    template = template + '\n\n'
    template = re.sub(
        '^\\s*[.][.]\\s+_END_OF_ADHOC_DOC:\\s*\n.*(?ms)', '', template)
    template = template + '\n\n' + __doc__ + '\n\n'
    template = re.sub(
        '^\\s*[.][.]\\s+_END_OF_SCRIPT_USAGE:\\s*\n.*(?ms)',
        '', template)
    if transform:
        template = adhoc_rst_to_ascii(template).strip() + '\n'
    if as_template:
        output = []
        output.append('# ' + AdHoc.line_tag('adhoc_template_v') + ' README.txt\n')
        output.append(RST_HEADER)
        output.append(template)
        output.append(RST_FOOTER)
        output.append('# ' + AdHoc.line_tag('adhoc_template_v') + ' README.txt\n')
        template = ''.join(output)
    return template
# @:adhoc_template:@

def main(argv):                                            # ||:fnc:||
    global _quiet, _debug, _verbose
    global RtAdHoc, AdHoc
    global adhoc_rst_to_ascii

    _parameters = None
    _pass_opts = []
    try:
        # try system library first
        import argparse
    except ImportError:
        # use canned version
        try:
            import argparse_local as argparse              # @:adhoc:@
        except ImportError:
            printe('error: argparse missing. Try `easy_install argparse`.')
            sys.exit(1)

    parser = argparse.ArgumentParser(add_help=False)
    # parser.add_argument('--sum', dest='accumulate', action='store_const',
    #                    const=sum, default=max,
    #                    help='sum the integers (default: find the max)')
    # |:opt:| add options
    # |:special:|
    parser.add_argument(
        '-c', '--compile', action='store_true', default=False,
        help='compile arguments. (default)')

    # |:special:|
    parser.add_argument(
        '-q', '--quiet', action='store_const', const=-2,
        dest='debug', default=0, help='suppress warnings')
    parser.add_argument(
        '-v', '--verbose', action='store_const', const=-1,
        dest='debug', default=0, help='verbose test output')
    parser.add_argument(
        '-d', '--debug', nargs='?', action='store', type=int, metavar='NUM',
        default = 0, const = 1,
        help='show debug information')
    parser.add_argument(
        '-t', '--test', action='store_true',
        help='run doc tests')
    class AdHocAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            map(lambda opt: setattr(namespace, opt, False),
                ('implode', 'explode', 'extract', 'template'))
            setattr(namespace, option_string[2:], True)
            setattr(namespace, 'adhoc_arg', values)
    parser.add_argument(
        '--implode', nargs=0, action=AdHocAction, default=False,
        help='implode script with adhoc')
    parser.add_argument(
        '--explode', nargs='?', action=AdHocAction, type=str, metavar='DIR',
        default=False, const='__adhoc__',
        help='explode script with adhoc in directory DIR'
        ' (default: `__adhoc__`)')
    parser.add_argument(
        '--extract', nargs='?', action=AdHocAction, type=str, metavar='DIR',
        default=False, const = '.',
        help='extract files to directory DIR (default: `.`)')
    parser.add_argument(
        '--template', nargs='?', action=AdHocAction, type=str, metavar='NAME',
        default=False, const = '-',
        help='extract named template to standard output. default NAME is ``-``')
    parser.add_argument(
        '-h', '--help', action='store_true',
        help="display this help message")
    # |:special:|
    parser.add_argument(
        '--documentation', action='store_true',
        help="display module documentation.")
    parser.add_argument(
        '--install', action='store_true',
        help="install adhoc.py script.")
    # |:special:|
    parser.add_argument(
        '--ap-help', action='store_true',
        help="internal help message")
    parser.add_argument(
        'args', nargs='*', metavar='arg',
        #'args', nargs='+', metavar='arg',
        #type=argparse.FileType('r'), default=sys.stdin,
        help='a series of arguments')

    #_parameters = parser.parse_args()
    (_parameters, _pass_opts) = parser.parse_known_args(argv[1:])
    # generate argparse help
    if _parameters.ap_help:
        parser.print_help()
        return 0

    # standard help
    if _parameters.help:
        # |:special:|
        help_msg = __doc__
        help_msg = re.sub(
            '^\\s*[.][.]\\s+_END_OF_HELP:\\s*\n.*(?ms)', '', help_msg)
        sys.stdout.write(adhoc_rst_to_ascii(help_msg).strip() + '\n')
        # |:special:|
        return 0

    _debug = _parameters.debug
    if _debug > 0:
        _verbose = True
        _quiet = False
    elif _debug < 0:
        _verbose = (_debug == -1)
        _quiet = not(_verbose)
        _debug = 0
    _parameters.debug = _debug
    _parameters.verbose = _verbose
    _parameters.quiet = _quiet

    if _debug:
        cmd_line = argv
        sys.stderr.write(sformat(
                "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[\n",
                globals()['dbg_comm'] if 'dbg_comm' in globals() else '# ',
                globals()['dbg_twid'] if 'dbg_twid' in globals() else 9,
                globals()['dbg_fwid'] if 'dbg_fwid' in globals() else 15,
                ':DBG:', 'cmd_line', cmd_line))

    # at least use `quiet` to suppress the setdefaultencoding warning
    setdefaultencoding(quiet=_quiet or _parameters.test)
    # |:opt:| handle options

    # adhoc: implode/explode/extract
    adhoc_export = (_parameters.explode or _parameters.extract)
    adhoc_op = (_parameters.implode or adhoc_export or _parameters.template
                # |:special:|
                or _parameters.documentation
                or _parameters.install
                # |:special:|
                )
    if adhoc_op:
        # |:special:|
        #          compiled   AdHoc RtAdHoc
        # compiled                    v
        # implode     req      req
        # explode     req            req
        # extract     req            req
        # template    req(v)         req
        #
        # uncompiled --- AdHoc ---> implode   --> (compiled)
        # compiled   -- RtAdHoc --> explode   --> __adhoc__
        # compiled   -- RtAdHoc --> extracted --> .
        # compiled   -- RtAdHoc --> template  --> stdout
        # |:special:|
        file_ = __file__
        source = None

        have_adhoc = 'AdHoc' in globals()
        have_rt_adhoc = 'RtAdHoc' in globals()

        # shall adhoc be imported
        if _parameters.implode or not have_rt_adhoc:
            # shall this file be compiled
            adhoc_compile = not (have_rt_adhoc
                                 # |:special:|
                                 or _parameters.documentation
                                 # |:special:|
                                 )
            os_path = os.defpath
            for pv in ('PATH', 'path'):
                try:
                    os_path = os.environ[pv]
                    break
                except KeyError:
                    pass
            os_path = os_path.split(os.pathsep)
            for path_dir in os_path:
                if not path_dir:
                    continue
                if path_dir not in sys.path:
                    sys.path.append(path_dir)
            if not have_adhoc:
                import adhoc
                AdHoc = adhoc.AdHoc
        else:
            adhoc_compile = False
            AdHoc = RtAdHoc

        AdHoc.quiet = _quiet
        AdHoc.verbose = _verbose
        AdHoc.debug = _debug
        AdHoc.include_path.append(os.path.dirname(file_))

        if adhoc_compile:
            ah = AdHoc()
            source = ah.compileFile(file_)
        else:
            source = AdHoc.read_source(file_)

        # implode
        if _parameters.implode:
            # @:adhoc_enable:@
            # if not _quiet:
            #     map(sys.stderr.write,
            #         ["warning: ", os.path.basename(file_),
            #          " already imploded!\n"])
            # @:adhoc_enable:@
            sys.stdout.write(source)
        # explode
        elif (_parameters.explode
              # |:special:|
              or _parameters.install
              # |:special:|
              ):
            # |:special:|
            if _parameters.install:
                _parameters.adhoc_arg = '__adhoc_install__'
            # |:special:|
            AdHoc.export_dir = _parameters.adhoc_arg
            AdHoc.export(file_, source)
            # |:special:|
            README = get_readme(file_, source, as_template=True, transform=False)
            AdHoc.export(file_, README)
            # |:special:|
        # extract
        elif _parameters.extract:
            AdHoc.extract_dir = _parameters.adhoc_arg
            AdHoc.extract(file_, source)
            # |:special:|
            README = get_readme(file_, source, as_template=True, transform=False)
            AdHoc.extract(file_, README)
            # |:special:|
        # template
        elif _parameters.template:
            template_name = _parameters.adhoc_arg
            if not template_name:
                template_name = '-'
            if template_name == 'list':
                sys.stdout.write(
                    '\n'.join(AdHoc.template_table(file_, source)) + '\n')
            # |:special:|
            elif template_name == 'README.txt':
                README = get_readme(file_, source, as_template=True, transform=False)
                sys.stdout.write(AdHoc.get_named_template('README.txt', file_, README))
            # |:special:|
            else:
                template = AdHoc.get_named_template(
                    template_name, file_, source)
                # |:special:|
                template = AdHoc.remove_marker(template, "adhoc_run_time_section")
                # |:special:|
                sys.stdout.write(template)
        # |:special:|
        # documentation
        elif _parameters.documentation:
            sys.stdout.write(get_readme(file_, source))
        # install
        if _parameters.install:
            here = os.path.abspath(os.getcwd())
            os.chdir(AdHoc.export_dir)
            os.system(''.join((sys.executable, " setup.py install")))
            os.chdir(here)
            import shutil
            shutil.rmtree(AdHoc.export_dir, True)
        # |:special:|

        # restore for subsequent calls to main
        if not have_adhoc:
            del(AdHoc)
        return 0

    # run doc tests
    if _parameters.test:
        import doctest
        doctest.testmod(verbose = _verbose)
        return 0

    # |:opt:| handle options
    run(_parameters, _pass_opts)

if __name__ == "__main__":
    #sys.argv.insert(1, '--debug') # |:debug:|
    result = main(sys.argv)
    sys.exit(result)

    # |:here:|

# @:adhoc_uncomment:@
# @:adhoc_template:@ doc/index.rst
#
# AdHoc Module
# ============
#
# .. _END_OF_ADHOC_DOC:
#
# .. automodule:: adhoc
#     :members:
#     :undoc-members:
#     :show-inheritance:
#
# .. _namespace_dict:
#
# NameSpace/NameSpaceDict
# =======================
#
# .. automodule:: namespace_dict
#     :members:
#     :show-inheritance:
# @:adhoc_template:@ doc/index.rst # off
# @:adhoc_uncomment:@

# @:adhoc_uncomment:@
# @:adhoc_template:@ -
# Standard template.
# @:adhoc_template:@
# @:adhoc_uncomment:@

# @:adhoc_uncomment:@
# @:adhoc_template:@ -test
# Test template.
# @:adhoc_template:@
# @:adhoc_uncomment:@

if False:
    pass
    # @:adhoc_include:@ Makefile, MANIFEST.in, README.css, docutils.conf, setup.py

    # @:adhoc_include:@ doc/conf.py, doc/make.bat, doc/Makefile

    # |:here:|

# (progn (forward-line 1) (snip-insert-mode "py.t.ide" t) (insert "\n"))
#
# :ide-menu: Emacs IDE Main Menu - Buffer @BUFFER@
# . M-x `eIDE-menu' (eIDE-menu "z")

# :ide: CSCOPE ON
# . (cscope-minor-mode)

# :ide: CSCOPE OFF
# . (cscope-minor-mode (quote ( nil )))

# :ide: TAGS: forced update
# . (compile (concat "cd /home/ws/project/ws-rfid && make -k FORCED=1 tags"))

# :ide: TAGS: update
# . (compile (concat "cd /home/ws/project/ws-rfid && make -k tags"))

# :ide: +-#+
# . Utilities ()

# :ide: TOC: Generate TOC with py-toc.py
# . (progn (save-buffer) (compile (concat "py-toc.py ./" (file-name-nondirectory (buffer-file-name)) " ")))

# :ide: CMD: Fold region with line continuation
# . (shell-command-on-region (region-beginning) (region-end) "fold --spaces -width 79 | sed 's, $,,;1!s,^, ,;$!s,$,\\\\,'" nil nil nil t)

# :ide: CMD: Fold region and replace with line continuation
# . (shell-command-on-region (region-beginning) (region-end) "fold --spaces --width 79 | sed 's, $,,;1!s,^, ,;$!s,$,\\\\,'" t nil nil t)

# :ide: +-#+
# . Fold ()

# :ide: CMD: Remove 8 spaces and add `>>> ' to region
# . (shell-command-on-region (region-beginning) (region-end) "sed 's,^        ,,;/^[ ]*##/d;/^[ ]*#/{;s,^ *# *,,p;d;};/^[ ]*$/!s,^,>>> ,'" nil nil nil t)

# :ide: CMD: Remove 4 spaces and add `>>> ' to region
# . (shell-command-on-region (region-beginning) (region-end) "sed 's,^    ,,;/^[ ]*##/d;/^[ ]*#/{;s,^ *# *,,p;d;};/^[ ]*$/!s,^,>>> ,'" nil nil nil t)

# :ide: +-#+
# . Doctest ()

# :ide: LINT: Check 80 column width ignoring IDE Menus
# . (let ((args " | /srv/ftp/pub/check-80-col.sh -")) (compile (concat "sed 's,^\\(\\|. \\|.. \\|... \\)\\(:ide\\|[.] \\).*,,;s,^ *. (progn (forward-line.*,,' " (buffer-file-name) " " args " | sed 's,^-," (buffer-file-name) ",'")))

# :ide: LINT: Check 80 column width
# . (let ((args "")) (compile (concat "/srv/ftp/pub/check-80-col.sh " (buffer-file-name) " " args)))

# :ide: +-#+
# . Lint Tools ()

# :ide: DELIM:     |: SYM :|         |:tag:|                standard symbol-tag!
# . (symbol-tag-normalize-delimiter (cons (cons nil "|:") (cons ":|" nil)) t)

# :ide: DELIM:     :: SYM ::         ::fillme::             future standard fill-me tag
# . (symbol-tag-normalize-delimiter (cons (cons nil "::") (cons "::" nil)) t)

# :ide: DELIM:     @: SYM :@         @:fillme:@             adhoc tag
# . (symbol-tag-normalize-delimiter (cons (cons nil "@:") (cons ":@" nil)) t)

# :ide: +-#+
# . Delimiters ()

# :ide: COMPILE: Run with --ap-help
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --ap-help")))

# :ide: COMPILE: Run with --help
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --help")))

# :ide: COMPILE: Run with --test
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --test")))

# :ide: COMPILE: Run with --test --verbose
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --test --verbose")))

# :ide: COMPILE: Run with --debug
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --debug")))

# :ide: +-#+
# . Compile with standard arguments ()

# :ide: OCCUR-OUTLINE: Python Source Code
# . (x-symbol-tag-occur-outline "sec" '("|||:" ":|||") (cons (cons "^\\([ \t\r]*\\(def\\|class\\)[ ]+\\|[A-Za-z_]?\\)" nil) (cons nil "\\([ \t\r]*(\\|[ \t]*=\\)")))

# :ide: MENU-OUTLINE: Python Source Code
# . (x-eIDE-menu-outline "sec" '("|||:" ":|||") (cons (cons "^\\([ \t\r]*\\(def\\|class\\)[ ]+\\|[A-Za-z_]?\\)" nil) (cons nil "\\([ \t\r]*(\\|[ \t]*=\\)")))

# :ide: +-#+
# . Outline ()

# :ide: INFO: SQLAlchemy - SQL Expression Language - Reference
# . (let ((ref-buffer "*sqa-expr-ref*")) (if (not (get-buffer ref-buffer)) (shell-command (concat "w3m -dump -cols " (number-to-string (1- (window-width))) " 'http://www.sqlalchemy.org/docs/05/reference/sqlalchemy/expressions.html'") ref-buffer) (display-buffer ref-buffer t)))

# :ide: INFO: SQLAlchemy - SQL Expression Language - Tutorial
# . (let ((ref-buffer "*sqa-expr-tutor*")) (if (not (get-buffer ref-buffer)) (shell-command (concat "w3m -dump -cols " (number-to-string (1- (window-width))) " 'http://www.sqlalchemy.org/docs/05/sqlexpression.html'") ref-buffer) (display-buffer ref-buffer t)))

# :ide: INFO: SQLAlchemy - Query
# . (let ((ref-buffer "*sqa-query*")) (if (not (get-buffer ref-buffer)) (shell-command (concat "w3m -dump -cols " (number-to-string (1- (window-width))) " 'http://www.sqlalchemy.org/docs/orm/query.html'") ref-buffer) (display-buffer ref-buffer t)))

# :ide: +-#+
# . SQLAlchemy Reference ()

# :ide: INFO: Python - argparse
# . (let ((ref-buffer "*python-argparse*")) (if (not (get-buffer ref-buffer)) (shell-command (concat "w3m -dump -cols " (number-to-string (1- (window-width))) " 'http://docs.python.org/library/argparse.html'") ref-buffer) (display-buffer ref-buffer t)))

# :ide: INFO: Python Documentation
# . (let ((ref-buffer "*w3m*")) (if (get-buffer ref-buffer) (display-buffer ref-buffer t)) (other-window 1) (w3m-goto-url "http://docs.python.org/index.html" nil nil))

# :ide: INFO: Python Reference
# . (let* ((ref-buffer "*python-ref*") (local "/home/ws/project/ws-util/python/reference/PQR2.7.html") (url (or (and (file-exists-p local) local) "'http://rgruet.free.fr/PQR27/PQR2.7.html'"))) (unless (get-buffer ref-buffer) (get-buffer-create ref-buffer) (with-current-buffer ref-buffer (shell-command (concat "snc txt.py.reference 2>/dev/null") ref-buffer) (goto-char (point-min)) (if (eobp) (shell-command (concat "w3m -dump -cols " (number-to-string (1- (window-width))) " " url) ref-buffer)))) (display-buffer ref-buffer t))

# :ide: +-#+
# . Python Reference ()

# :ide: COMPILE: Run with --help
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --help")))

# :ide: COMPILE: Run with --template doc/index.rst
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --template doc/index.rst")))

# :ide: COMPILE: Run with --template test
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --template test")))

# :ide: COMPILE: Run with --template
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --template")))

# :ide: COMPILE: Run with python3 with --template list
# . (progn (save-buffer) (compile (concat "python3 ./" (file-name-nondirectory (buffer-file-name)) " --template list")))

# :ide: COMPILE: Run with --verbose --implode
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) "  --verbose --implode")))

# :ide: COMPILE: Run with --documentation
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --documentation")))

# :ide: COMPILE: make ftp
# . (progn (save-buffer) (compile (concat "make -k ftp")))

# :ide: COMPILE: make doc
# . (progn (save-buffer) (compile (concat "make doc")))

# :ide: COMPILE: Run with --verbose --extract
# . (progn (save-buffer) (shell-command "rm -f README.txt doc/index.rst") (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) "  --verbose --extract")))

# :ide: COMPILE: Run with --template list
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --template list")))

# :ide: COMPILE: Run with python3 with --test
# . (progn (save-buffer) (compile (concat "python3 ./" (file-name-nondirectory (buffer-file-name)) " --test")))

# :ide: COMPILE: Run with python3 w/o args
# . (progn (save-buffer) (compile (concat "python3 ./" (file-name-nondirectory (buffer-file-name)) " ")))

# :ide: COMPILE: Run with --test
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --test")))

# :ide: COMPILE: Run w/o args
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " ")))

# :ide: COMPILE: Run with --verbose
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --verbose")))

# :ide: +-#+
# . Compile ()

#
# Local Variables:
# mode: python
# comment-start: "#"
# comment-start-skip: "#+"
# comment-column: 0
# truncate-lines: t
# End:
