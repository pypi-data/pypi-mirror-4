#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011, 2012, Wolfgang Scherer, <Wolfgang.Scherer at gmx.de>
#
# This file is part of AdHoc.
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
# AdHoc Standalone Python Script Generator
# ########################################
#
# The *AdHoc* compiler can be used as a program (see `Script Usage`_)
# as well as a module (see :class:`adhoc.AdHoc`).
#
# Since the *AdHoc* compiler itself is installed as a compiled *AdHoc*
# script, it serves as its own usage example.
#
# After installation of the *adhoc.py* script, the full source can be
# obtained in directory ``__adhoc__``, by executing::
#
#     adhoc.py --explode
#
# .. @@contents@@
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

  ===================== ==================================================
  -c, --compile         compile file(s) or standard input into output file
                        (default: standard output).
  -d, --decompile       decompile file(s) or standard input into
                        output directory (default ``__adhoc__``).
  -o, --output OUT      output file for --compile/output directory for
                        --decompile.

  -q, --quiet           suppress warnings
  -v, --verbose         verbose test output
  --debug[=NUM]         show debug information

  -h, --help            display this help message
  --documentation       display module documentation.

  --template list       show available templates.
  --template[=NAME]     extract named template to standard
                        output. Default NAME is ``-``.
  --extract[=DIR]       extract adhoc files to directory DIR (default: ``.``)
  --explode[=DIR]       explode script with adhoc in directory DIR
                        (default ``__adhoc__``)
  --implode             implode script with adhoc
  --install             install adhoc.py script

  -t, --test            run doc tests
  ===================== ==================================================

*adhoc.py* is compatible with Python 2.4+ and Python 3. (For Python
<2.6 the packages *stringformat* and *argparse* are needed and
included.)

.. _END_OF_HELP:

.. |=NUM| replace:: ``[=NUM]``

Script Examples
===============

Templates
---------

Sections marked by |adhoc_template| can be retrieved as templates on
standard output.

Additionally, all other files compiled into an adhoc file with one of

================ ======================
|adhoc|          ==> |adhoc_import|
|adhoc_verbatim| ==> |adhoc_template_v|
|adhoc_include|  ==> |adhoc_unpack|
================ ======================

are accessible as templates.

``python adhoc.py --template list`` provides a list of templates:

>>> ign = main('adhoc.py --template list'.split())
================================================= ================================ ================
                     Command                                  Template                   Type
================================================= ================================ ================
adhoc.py --template adhoc_test                    # !adhoc_test                    adhoc_import
adhoc.py --template adhoc_test.sub                # !adhoc_test.sub                adhoc_import
adhoc.py --template argparse_local                # !argparse_local                adhoc_import
adhoc.py --template namespace_dict                # !namespace_dict                adhoc_import
adhoc.py --template stringformat_local            # !stringformat_local            adhoc_import
adhoc.py --template use_case_000_                 # !use_case_000_                 adhoc_import
adhoc.py --template use_case_001_templates_       # !use_case_001_templates_       adhoc_import
adhoc.py --template use_case_002_include_         # !use_case_002_include_         adhoc_import
adhoc.py --template use_case_003_import_          # !use_case_003_import_          adhoc_import
adhoc.py --template use_case_005_nested_          # !use_case_005_nested_          adhoc_import
adhoc.py --template docutils.conf                 # docutils.conf                  adhoc_template_v
adhoc.py --template                               # -                              adhoc_template
adhoc.py --template README.txt                    # README.txt                     adhoc_template
adhoc.py --template col-param-closure             # -col-param-closure             adhoc_template
adhoc.py --template doc/USE_CASES.txt             # doc/USE_CASES.txt              adhoc_template
adhoc.py --template doc/index.rst                 # doc/index.rst                  adhoc_template
adhoc.py --template max-width-class               # -max-width-class               adhoc_template
adhoc.py --template rst-to-ascii                  # -rst-to-ascii                  adhoc_template
adhoc.py --template test                          # -test                          adhoc_template
adhoc.py --template MANIFEST.in                   # !MANIFEST.in                   adhoc_unpack
adhoc.py --template Makefile                      # !Makefile                      adhoc_unpack
adhoc.py --template README.css                    # !README.css                    adhoc_unpack
adhoc.py --template doc/Makefile                  # !doc/Makefile                  adhoc_unpack
adhoc.py --template doc/_static/adhoc-logo-32.ico # !doc/_static/adhoc-logo-32.ico adhoc_unpack
adhoc.py --template doc/adhoc-logo.svg            # !doc/adhoc-logo.svg            adhoc_unpack
adhoc.py --template doc/conf.py                   # !doc/conf.py                   adhoc_unpack
adhoc.py --template doc/make.bat                  # !doc/make.bat                  adhoc_unpack
adhoc.py --template doc/z-massage-index.sh        # !doc/z-massage-index.sh        adhoc_unpack
adhoc.py --template setup.py                      # !setup.py                      adhoc_unpack
================================================= ================================ ================

``python adhoc.py --template`` prints the standard template ``-``
(closing delimiter replaced by ellipsis):

>>> ign = main('./adhoc.py --template'.split()) #doctest: +ELLIPSIS
# @:adhoc_disable... allow modification of exploded sources in original place
sys.path.append('__adhoc__')
# @:adhoc_disable...
<BLANKLINE>
# @:adhoc_run_time... The run-time class goes here
# @:adhoc_run_time_engine... settings enabled at run-time
# @:adhoc_enable...
# RtAdHoc.flat = False
# @:adhoc_enable...
# @:adhoc_run_time_engine...
<BLANKLINE>
#import adhoc                                               # @:adhoc...

``python adhoc.py --template test`` prints the template named ``-test``.
the leading ``-`` signifies disposition to standard output:

>>> ign = main('./adhoc.py --template test'.split())
Test template.

Extract
-------

The default destination for extracting files is the current working
directory.

Files extracted consist of

- packed files generated by |adhoc_include|
- templates generated by |adhoc_verbatim|
- templates with a file destination other than standard output

``python adhoc.py --extract __adhoc_extract__`` unpacks the following files into
directory ``__adhoc_extract__``:

>>> import shutil
>>> ign = main('./adhoc.py --extract __adhoc_extract__'.split())
>>> file_list = []
>>> for dir, subdirs, files in os.walk('__adhoc_extract__'):
...     file_list.extend([os.path.join(dir, file_) for file_ in files])
>>> for file_ in sorted(file_list):
...     printf(file_)
__adhoc_extract__/MANIFEST.in
__adhoc_extract__/Makefile
__adhoc_extract__/README.css
__adhoc_extract__/README.txt
__adhoc_extract__/doc/Makefile
__adhoc_extract__/doc/USE_CASES.txt
__adhoc_extract__/doc/_static/adhoc-logo-32.ico
__adhoc_extract__/doc/adhoc-logo.svg
__adhoc_extract__/doc/conf.py
__adhoc_extract__/doc/index.rst
__adhoc_extract__/doc/make.bat
__adhoc_extract__/doc/z-massage-index.sh
__adhoc_extract__/docutils.conf
__adhoc_extract__/setup.py
__adhoc_extract__/use_case_000_.py
__adhoc_extract__/use_case_001_templates_.py
__adhoc_extract__/use_case_002_include_.py
__adhoc_extract__/use_case_003_import_.py
__adhoc_extract__/use_case_005_nested_.py
>>> shutil.rmtree('__adhoc_extract__')

Export
------

The default destination for exporting files is the
subdirectory ``__adhoc__``.

Files exported consist of

- imported modules generated by |adhoc|
- all files covered in section `Extract`_

``python adhoc.py --explode __adhoc_explode__`` unpacks the following files into
directory ``__adhoc_explode__``:

>>> import shutil
>>> ign = main('./adhoc.py --explode __adhoc_explode__'.split())
>>> file_list = []
>>> for dir, subdirs, files in os.walk('__adhoc_explode__'):
...     file_list.extend([os.path.join(dir, file_) for file_ in files])
>>> for file_ in sorted(file_list):
...     printf(file_)
__adhoc_explode__/MANIFEST.in
__adhoc_explode__/Makefile
__adhoc_explode__/README.css
__adhoc_explode__/README.txt
__adhoc_explode__/adhoc.py
__adhoc_explode__/adhoc_test/__init__.py
__adhoc_explode__/adhoc_test/sub/__init__.py
__adhoc_explode__/argparse_local.py
__adhoc_explode__/doc/Makefile
__adhoc_explode__/doc/USE_CASES.txt
__adhoc_explode__/doc/_static/adhoc-logo-32.ico
__adhoc_explode__/doc/adhoc-logo.svg
__adhoc_explode__/doc/conf.py
__adhoc_explode__/doc/index.rst
__adhoc_explode__/doc/make.bat
__adhoc_explode__/doc/z-massage-index.sh
__adhoc_explode__/docutils.conf
__adhoc_explode__/namespace_dict.py
__adhoc_explode__/rt_adhoc.py
__adhoc_explode__/setup.py
__adhoc_explode__/stringformat_local.py
__adhoc_explode__/use_case_000_.py
__adhoc_explode__/use_case_001_templates_.py
__adhoc_explode__/use_case_002_include_.py
__adhoc_explode__/use_case_003_import_.py
__adhoc_explode__/use_case_005_nested_.py
>>> shutil.rmtree('__adhoc_explode__')

File Permissions
================

- File mode is restored.
- File ownership is not restored.
- File modification times are restored.

  Since only naive datetimes are recorded, this only works correctly
  within the same timezone.

.. @:adhoc_index_only:@

AdHoc Module
============

.. @:adhoc_index_only:@
"""

# @:adhoc_uncomment:@
# @:adhoc_template:@ doc/index.rst
#
# Purpose
# =======
#
# *AdHoc* provides python scripts with
#
# - template facilities
# - default file generation
# - standalone module inclusion
#
# @:adhoc_index_only:@
# See also `Use Cases`_.
#
# @:adhoc_index_only:@
# *AdHoc* has been designed to provide an implode/explode cycle:
#
# ========  =======  =========  =======  =========
# source_0                               xsource_0
# source_1  implode             explode  xsource_1
# ...       ------>  script.py  ------>  ...
# source_n                               xsource_n
# ========  =======  =========  =======  =========
#
# where ``xsource_i === source_i``. I.e., ``diff source_i xsource_i``
# does not produce any output.
#
# Quickstart
# ==========
#
# module.py:
#
#     | # -\*- coding: utf-8 -\*-
#     | mvar = 'value'
#
# script.py:
#
#     | # -\*- coding: utf-8 -\*-
#     | # |adhoc_run_time|
#     | import module # |adhoc|
#     | print('mvar: ' + module.mvar)
#
# Compilation::
#
#     adhoc.py --compile script.py >/tmp/script-compiled.py
#
# Execution outside source directory::
#
#     cd /tmp && python script-compiled.py
#
# shows::
#
#     mvar: value
#
# Decompilation::
#
#     cd /tmp && \
#     mkdir -p __adhoc__ && \
#     adhoc.py --decompile <script-compiled.py >__adhoc__/script.py
#
# .. |@:| replace:: ``@:``
# .. |:@| replace:: ``:@``
# .. |adhoc_run_time| replace:: |@:|\ ``adhoc_run_time``\ |:@|
# .. |adhoc| replace:: |@:|\ ``adhoc``\ |:@|
#
# Description
# ===========
#
# The *AdHoc* compiler/decompiler parses text for tagged lines and
# processes them as instructions.
#
# The minimal parsed entity is a tagged line, which is any line
# containing a recognized *AdHoc* tag.
#
# All *AdHoc* tags are enclosed in delimiters (default: |@:| and |:@|). E.g:
#
#   |@:|\ adhoc\ |:@|
#
# Delimiters come in several flavors, namely line and section
# delimiters and a set of macro delimiters. By default, line and
# section delimiters are the same, but they can be defined separately.
#
# `Flags`_ are tagged lines, which denote a single option or
# command. E.g.:
#
#   | import module     # |@:|\ adhoc\ |:@|
#   | # |@:|\ adhoc_self\ |:@| my_module_name
#
# `Sections`_ are tagged line pairs, which delimit a block of
# text. The first tagged line opens the section, the second tagged
# line closes the section. E.g.:
#
#   | # |@:|\ adhoc_enable\ |:@|
#   | # disabled_command()
#   | # |@:|\ adhoc_enable\ |:@|
#
# `Macros`_ have their own delimiters (default: |@m| and |m>|). E.g.:
#
#   | # |@m|\ MACRO_NAME\ |m>|
#
# The implementation is realized as class :class:`adhoc.AdHoc` which
# is mainly used as a namespace. The run-time part of
# :class:`adhoc.AdHoc` -- which handles module import and file export
# -- is included verbatim as class :class:`RtAdHoc` in the generated
# output.
#
# Flags
# -----
#
# :|adhoc_run_time|:
#     The place where the *AdHoc* run-time code is added.  This flag must
#     be present in files, which use the |adhoc| import feature.  It
#     is not needed for the enable/disable features.
#
#     This flag is ignored, if double commented. E.g.:
#
#       | # # |adhoc_run_time|
#
# :|adhoc| [force] [flat | full]:
#     Mark import line for run-time compilation.
#
#     If ``force`` is specified, the module is imported, even if it
#     was imported before.
#
#     If ``flat`` is specified, the module is not recursively
#     exported.
#
#     If ``full`` is specified, the module is recursively
#     exported. (This parameter takes priority over ``flat``).
#
#     If neither ``flat`` nor ``full`` are specified,
#     :attr:`adhoc.AdHoc.flat` determines the export scope.
#
#     This flag is ignored, if the line is commented out. E.g.:
#
#       | # import module  # |adhoc|
#
# .. _adhoc_include:
#
# :|adhoc_include| file_spec, ...:
#     Include files for unpacking. ``file_spec`` is one of
#
#     :file:
#       ``file`` is used for both input and output.
#
#     :file ``from`` default-file:
#       ``file`` is used for input and output. if ``file`` does not
#       exist, ``default-file`` is used for input.
#
#     :source-file ``as`` output-file:
#       ``source-file`` is used for input. ``output-file`` is used for
#       output. If ``source-file`` does not exist, ``output-file`` is
#       used for input also.
#
#     This flag is ignored, if double commented. E.g.:
#
#       | # # |adhoc_include| file
#
# :|adhoc_verbatim| [flags] file_spec, ...:
#     Include files for verbatim extraction. See adhoc_include_ for
#     ``file_spec``.
#
#     The files are included as |adhoc_template_v| sections. *file* is used
#     as *export_file* mark. If *file* is ``--``, the template disposition
#     becomes standard output.
#
#     Optional flags can be any combination of ``[+|-]NUM`` for
#     indentation and ``#`` for commenting. E.g.:
#
#       | # |adhoc_verbatim| +4# my_file from /dev/null
#
#     *my_file* (or ``/dev/null``) is read, commented and indented 4
#     spaces.
#
#     If the |adhoc_verbatim| tag is already indented, the specified
#     indentation is subtracted.
#
#     This flag is ignored, if double commented. E.g.:
#
#       | # # |adhoc_verbatim| file
#
# :|adhoc_self| name ...:
#     Mark name(s) as currently compiling.  This is useful, if
#     ``__init__.py`` imports other module parts. E.g:
#
#       | import pyjsmo             # |@:|\ adhoc\ |:@|
#
#     where ``pyjsmo/__init__.py`` contains:
#
#       | # |@:|\ adhoc_self\ |:@| pyjsmo
#       | from pyjsmo.base import * # |@:|\ adhoc\ |:@|
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
#     A comment char and exactly one space are added to non-blank
#     lines in these sections.
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
# :|adhoc_template_v| export_file:
#     Variation of |adhoc_template|. Automatically generated by |adhoc_verbatim|.
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
#     Added sections are marked as such by the compiler. Removal is
#     done when exporting.
#
#     Before compilation, existing |adhoc_remove| tags are renamed to
#     |adhoc_remove_|.
#
#     After automatically added |adhoc_remove| sections have been
#     removed during export, remaining |adhoc_remove_| tags are
#     renamed to |adhoc_remove| again.
#
#     .. note:: Think twice, before removing material from original
#        sources at compile time. It will violate the condition
#        ``xsource_i === source_i``.
#
# :|adhoc_run_time_engine|:
#     The run-time class :class:`RtAdHoc` is enclosed in this special
#     template section.
#
#     It is exported as ``rt_adhoc.py`` during export.
#
# Macros
# ------
#
# Macros are defined programmatically::
#
#     AdHoc.macros[MACRO_NAME] = EXPANSION_STRING
#
# A macro is invoked by enclosing a MACRO_NAME in
# :attr:`adhoc.AdHoc.macro_call_delimiters`. (Default: |@m|, |m>|).
#
# :|MACRO_NAME|:
#     Macro call.
#
# Internal
# --------
#
# :|adhoc_run_time_class|:
#     Marks the beginning of the run-time class.  This is only
#     recognized in the *AdHoc* programm/module.
#
# :|adhoc_run_time_section|:
#     All sections are concatenated and used as run-time code.  This is
#     only recognized in the *AdHoc* programm/module.
#
# In order to preserve the ``xsource_i === source_i`` bijective
# condition, macros are expanded/collapsed with special macro
# definition sections. (See :attr:`adhoc.AdHoc.macro_xdef_delimiters`;
# Default: |<m|, |m@|).
#
# :|adhoc_macro_call|:
#     Macro call section.
#
# :|adhoc_macro_expansion|:
#     Macro expansion section.
#
# @:adhoc_template:@ doc/index.rst # off
# @:adhoc_uncomment:@

# @:adhoc_uncomment:@
# @:adhoc_template:@ doc/index.rst
# @:adhoc_index_only:@
#
# .. include:: USE_CASES.txt
# @:adhoc_index_only:@
#
# AdHoc Script
# ============
# @:adhoc_index_only:@
#
# .. automodule:: adhoc
#     :members:
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
#
# @:adhoc_index_only:@
# @:adhoc_template:@ doc/index.rst # off
# @:adhoc_uncomment:@

# @:adhoc_uncomment:@
# @:adhoc_template:@ doc/index.rst
#
# .. |adhoc_self| replace:: |@:|\ ``adhoc_self``\ |:@|
# .. |adhoc_include| replace:: |@:|\ ``adhoc_include``\ |:@|
# .. |adhoc_verbatim| replace:: |@:|\ ``adhoc_verbatim``\ |:@|
# .. |adhoc_compiled| replace:: |@:|\ ``adhoc_compiled``\ |:@|
# .. |adhoc_enable| replace:: |@:|\ ``adhoc_enable``\ |:@|
# .. |adhoc_disable| replace:: |@:|\ ``adhoc_disable``\ |:@|
# .. |adhoc_template| replace:: |@:|\ ``adhoc_template``\ |:@|
# .. |adhoc_template_v| replace:: |@:|\ ``adhoc_template_v``\ |:@|
# .. |adhoc_uncomment| replace:: |@:|\ ``adhoc_uncomment``\ |:@|
# .. |adhoc_indent| replace:: |@:|\ ``adhoc_indent``\ |:@|
# .. |adhoc_import| replace:: |@:|\ ``adhoc_import``\ |:@|
# .. |adhoc_unpack| replace:: |@:|\ ``adhoc_unpack``\ |:@|
# .. |adhoc_remove| replace:: |@:|\ ``adhoc_remove``\ |:@|
# .. |adhoc_remove_| replace:: |@:|\ ``adhoc_remove_``\ |:@|
# .. |adhoc_run_time_class| replace:: |@:|\ ``adhoc_run_time_class``\ |:@|
# .. |adhoc_run_time_section| replace:: |@:|\ ``adhoc_run_time_section``\ |:@|
# .. |adhoc_run_time_engine| replace:: |@:|\ ``adhoc_run_time_engine``\ |:@|
# .. |@m| replace:: ``@|:``
# .. |m>| replace:: ``:|>``
# .. |<m| replace:: ``<|:``
# .. |m@| replace:: ``:|@``
# .. |MACRO_NAME| replace:: |@m|\ ``MACRO_NAME``\ |m>|
# .. |adhoc_macro_call| replace:: |<m|\ ``adhoc_macro_call``\ |m@|
# .. |adhoc_macro_expansion| replace:: |<m|\ ``adhoc_macro_expansion``\ |m@|
#
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

dbg_comm = ((('dbg_comm' in globals()) and (globals()['dbg_comm'])) or ('# '))
dbg_twid = ((('dbg_twid' in globals()) and (globals()['dbg_twid'])) or (9))
dbg_fwid = ((('dbg_fwid' in globals()) and (globals()['dbg_fwid'])) or (23))

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
def strclean(value):
    '''Make a copy of any structure with all strings converted to
    native strings.

    :func:`strclean` is good for :meth:`__str__` methods.

    It is needed for doctest output that should be compatible with
    both python2 and python3.

    The output structure is not necessarily an exact copy of the input
    structure, since objects providing iterator or item interfaces are
    only copied through those!
    '''
    if isstring(value):
        return _nativestr(value)
    if hasattr(value, 'items'):
        try:
            out = type(value)()
        except:
            (t, e, tb) = sys.exc_info() # |:debug:|
            printf(''.join(traceback.format_tb(tb)), file=sys.stderr)
            printe('OOPS: ' + t.__name__ + ': ' + str(e) + ' [' + str(value.__class__.__name__) + '] [' + str(value) + ']')
        for k, v in value.items():
            out[strclean(k)] = strclean(v)
        return out
    if hasattr(value, '__iter__') or hasattr(value, 'iter'):
        if isinstance(value, tuple):
            out = []
        else:
            out = type(value)()
        for e in value:
            out.append(strclean(e))
        if isinstance(value, tuple):
            out = type(value)(out)
        return out
    return value

# (progn (forward-line 1) (snip-insert-mode "py.f.issequence" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.b.logging" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.b.ordereddict" t) (insert "\n"))

# (progn (forward-line 1) (snip-insert-mode "py.main.pyramid.activate" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.main.project.libdir" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.main.sql.alchemy" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.main.sql.ws" t) (insert "\n"))

# The standard template should be something useful

# @:adhoc_uncomment:@
# @:adhoc_template:@ -
# # @:adhoc_disable:@ allow modification of exploded sources in original place
sys.path.append('__adhoc__')
# # @:adhoc_disable:@
# @:adhoc_template:@
# @:adhoc_uncomment:@

# @:adhoc_run_time:@
# @:adhoc_template:@ -

# @:adhoc_run_time:@ The run-time class goes here
# @:adhoc_run_time_engine:@ settings enabled at run-time
# @:adhoc_enable:@
# # RtAdHoc.flat = False
# # @:adhoc_template:@
# RtAdHoc.flat = False
# # @:adhoc_template:@ -
# @:adhoc_enable:@
# @:adhoc_run_time_engine:@

#import adhoc                                               # @:adhoc:@
# @:adhoc_template:@

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
            printf('error: (adhoc) stringformat missing.'
                   ' Try *easy_install stringformat*.', file=sys.stderr)
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
        commstr = ((('dbg_comm' in globals()) and (globals()['dbg_comm'])) or ('# '))

    dbg_twid = ((('dbg_twid' in globals()) and (globals()['dbg_twid'])) or (9))
    if tag is None:
        tag = ':DBG:'

    max_wid = 0
    for key in dict_.keys():
        _wid = len(key)
        if max_wid < _wid:
            max_wid = _wid

    dbg_fwid = ((('dbg_fwid' in globals()) and (globals()['dbg_fwid'])) or (max_wid))
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

# @:adhoc_run_time_section:@ START
import sys
import os
import re

try:
    from cStringIO import StringIO as _AdHocBytesIO, StringIO as _AdHocStringIO
except ImportError:
    from io import BytesIO as _AdHocBytesIO, StringIO as _AdHocStringIO

# @:adhoc_run_time_section:@ off
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

AH_CHECK_SOURCE = '''\
not in section
# >:cmd:< arg0 arg1 # comment
# <:tag:> on
in section
# >:cmd:< arg2 arg3 # comment
in section
# <:tag:> off
not in section
# <:tag2:> on
in section
in section
# <:tag2:> off
not in section
'''

# @:adhoc_run_time_section:@ on
# @:adhoc_run_time_class:@
class AdHoc(object):                                     # |||:cls:|||
    # @:adhoc_run_time_section:@ off
    """
    :class:`AdHoc` is mainly used as a namespace, which is partially
    included verbatim as :class:`RtAdHoc` in the generated output.

    It is only instantiated for compiling adhoc output
    (:meth:`compileFile`, :meth:`compile`).

    **Attributes**

    The following class attrbutes determine the operation of AdHoc:

    - :attr:`line_delimiters`
    - :attr:`section_delimiters`
    - :attr:`template_process_hooks`
    - :attr:`extra_templates`
    - :attr:`export_dir`
    - :attr:`extract_dir`
    - :attr:`flat`
    - :attr:`frozen`
    - :attr:`quiet`
    - :attr:`verbose`
    - :attr:`debug`

    Run-time class attributes can be set like this:

    | # |adhoc_run_time|
    | # |adhoc_enable|
    | # RtAdHoc.flat = False
    | # RtAdHoc.frozen = True
    | # |adhoc_enable|

    or like this:

    | # |adhoc_run_time|
    | if 'RtAdHoc' in globals():
    |     RtAdHoc.flat = False
    |     RtAdHoc.frozen = True

    **Low-Level Functions**

    :meth:`adhoc_tag` constructs a delimited tag or tag regular
    expression:

    >>> adhoc_tag = AdHoc.adhoc_tag
    >>> delimiters = ('<:', ':>')

    >>> tag_sym = 'my_tag'
    >>> adhoc_tag(tag_sym, delimiters)
    '<:my_tag:>'

    >>> tag_rx = 'my_[^:]+'
    >>> adhoc_tag(tag_rx, delimiters, is_re=True)
    '\\\\<\\\\:my_[^:]+\\\\:\\\\>'

    :meth:`tag_split` splits a string into tagged line parts and
    untagged parts.

    :meth:`adhoc_parse_line` splits a tagged line into a tag symbol and
    additional arguments:

    >>> adhoc_parse_line = AdHoc.adhoc_parse_line
    >>> tagged_line = 'anything # <:my_tag:>  additonal arguments # end comment'

    >>> adhoc_parse_line(tagged_line, tag_sym, delimiters)
    ('my_tag', 'additonal arguments # end comment')

    >>> adhoc_parse_line(tagged_line, tag_rx, delimiters, is_re=True)
    ('my_tag', 'additonal arguments # end comment')

    >>> adhoc_parse_line(tagged_line, tag_rx, delimiters, is_re=True, strip_comment=True)
    ('my_tag', 'additonal arguments')

    **Low-Level Convenience Functions**

    *Tag Generation*

    :meth:`line_tag`, :meth:`section_tag`

    >>> class ah(AdHoc):
    ...     line_delimiters = ('>:', ':<')
    ...     section_delimiters = ('<:', ':>')

    >>> ah.line_tag('tag-symbol')
    '>:tag-symbol:<'

    >>> ah.line_tag('tag.?rx', True)
    '\\\\>\\\\:tag.?rx\\\\:\\\\<'

    >>> ah.section_tag('tag-symbol')
    '<:tag-symbol:>'

    >>> ah.section_tag('tag.?rx', True)
    '\\\\<\\\\:tag.?rx\\\\:\\\\>'

    *Tagged Line/Section Retrieval*

    :meth:`tag_lines`, :meth:`tag_partition`, :meth:`tag_sections`

    >>> source = AH_CHECK_SOURCE

    >>> line_tag = ah.line_tag('cmd')
    >>> tagged_lines = ah.tag_lines(source, line_tag)
    >>> adhoc_dump_list(tagged_lines, 40)
    #   :DBG:   elt[0]                 : ]'# >:cmd:< arg0 arg1 # comment\\n'[
    #   :DBG:   elt[1]                 : ]'# >:cmd:< arg2 arg3 # comment\\n'[

    >>> is_re = True
    >>> section_tag_rx = ah.section_tag('tag.?', is_re=is_re)
    >>> body, sections = ah.tag_partition(source, section_tag_rx, is_re=is_re)
    >>> adhoc_dump_list(body, 40)
    #   :DBG:   elt[0]                 : ]'not in section\\n# >:cmd:< arg0 arg1 #  ...'[
    #   :DBG:   elt[1]                 : ]'not in section\\n'[
    #   :DBG:   elt[2]                 : ]'not in section\\n'[
    >>> adhoc_dump_list(sections, 40)
    #   :DBG:   elt[0]                 : ]'in section\\n# >:cmd:< arg2 arg3 # comm ...'[
    #   :DBG:   elt[1]                 : ]'in section\\nin section\\n'[

    >>> body, sections = ah.tag_partition(source, section_tag_rx, is_re=is_re, headline=True)
    >>> adhoc_dump_sections(sections, 40)
    #   :DBG:   section[0]             : ]['# <:tag:> on\\n', 'in section\\n# >:cmd:< arg2 arg3 # comm ...'][
    #   :DBG:   section[1]             : ]['# <:tag2:> on\\n', 'in section\\nin section\\n'][

    >>> sections = ah.tag_sections(source, section_tag_rx, is_re=is_re, headline=True)
    >>> adhoc_dump_sections(sections, 40)
    #   :DBG:   section[0]             : ]['# <:tag:> on\\n', 'in section\\n# >:cmd:< arg2 arg3 # comm ...'][
    #   :DBG:   section[1]             : ]['# <:tag2:> on\\n', 'in section\\nin section\\n'][

    *Tagged Line Parsing*

    - :meth:`line_tag_parse`, :meth:`line_tag_strip`
    - :meth:`section_tag_parse`, :meth:`section_tag_strip`

    >>> strclean(ah.line_tag_parse(tagged_lines[0], 'cmd'))
    ('cmd', 'arg0 arg1 # comment')

    >>> strclean(ah.line_tag_strip(tagged_lines[0], 'cmd', strip_comment=True))
    'arg0 arg1'

    >>> strclean(ah.section_tag_parse(sections[1][0], 'tag.?', is_re=True))
    ('tag2', 'on')

    >>> strclean(ah.section_tag_strip(sections[1][0], 'tag.?', is_re=True))
    'on'

    **Tagged Line/Section Transformations**

    - :meth:`transform_lines`, :meth:`transform_sections`
    - :meth:`line_tag_rename`, :meth:`line_tag_remove`
    - :meth:`section_tag_rename`, :meth:`section_tag_remove`
    - :meth:`indent_sections`
    - :meth:`enable_sections`, :meth:`disable_transform`, :meth:`disable_sections`
    - :meth:`remove_sections`

    **IO Functions**

    - :meth:`check_coding`
    - :meth:`decode_source`, :meth:`encode_source`
    - :meth:`read_source`, :meth:`write_source`
    - :meth:`check_xfile`
    - :meth:`pack_file`, :meth:`unpack_file`

    **Run-Time Unpack/Import Interface**

    - :meth:`unpack_`
    - :meth:`import_`, :meth:`module_setup`

    **Export Tools**

    - :meth:`std_source_param`
    - :meth:`export_source`

    **Extract Interface**

    - :meth:`unpack`
    - :meth:`extract`

    **Export Interface**

    - :meth:`export__`, :meth:`export_`, :meth:`export`

    **Dump Interface (Import/Unpack Substitute)**

    - :meth:`dump__`, :meth:`dump_`, :meth:`dump_file`

    **Macro Interface**

    Naive macro expansion would violate the condition
    ``xsource_i === source_i``.

    Here is a simple macro system which preserves the bijectivity
    condition. It is quite useful for conditional templating. (See
    `Use Cases`_ generator scripts).

    *Limitations*

    - Macro expansions are not prefixed with the current indentation
    - Macros cannot be nested

    *Attributes*

    - :attr:`macro_call_delimiters`

      Delimiters for macros, e.g.: ``@|:MACRO_NAME:|>``

    - :attr:`macro_xdef_delimiters`

      Delimiters for macro expansion, e.g.::

          # <|:adhoc_macro_call\x3a|@
          # @|:MACRO_NAME:|>
          # <|:adhoc_macro_call\x3a|@
          # <|:adhoc_macro_expansion\x3a|@
          The macro definition ...
          The macro definition ...
          # <|:adhoc_macro_expansion\x3a|@

    - :attr:`macros`

      Macro definitions.

    *Methods*

    - :meth:`expand_macros`
    - :meth:`has_expanded_macros`
    - :meth:`activate_macros`
    - :meth:`collapse_macros`

    **Template Interface**

    - :meth:`std_template_param`
    - :meth:`get_templates`
    - :meth:`template_list`, :meth:`col_param_closure`, :meth:`template_table`
    - :meth:`get_named_template`
    - :meth:`extract_templates`

    **Template Extraction (uncompiled)**

    - Expand and activate macros for uncompiled source
    - Activate macros on compiled source

    **Compile**

    - Expand macros before compilation

    **Export**

    - Collapse macros on export of compiled source.

    **Compilation Attributes**

    - :attr:`include_path`

    **Compilation Interface**

    - :meth:`setup_tags`
    - :meth:`strquote`
    - :meth:`adhoc_run_time_sections_from_string`
    - :meth:`adhoc_run_time_section_from_file`
    - :meth:`adhoc_get_run_time_section`
    - :meth:`prepare_run_time_section`
    - :meth:`verbatim_`
    - :meth:`include_`
    - :meth:`encode_module_`
    - :meth:`compile_`

    **User API**

    - :meth:`encode_include`
    - :meth:`encode_module`
    - :meth:`compile`
    - :meth:`compileFile`

    .. \\|:here:|
    """
    # @:adhoc_run_time_section:@ on
    # @:adhoc_run_time_section:@ off
    # --------------------------------------------------
    # ||:sec:|| Attributes
    # --------------------------------------------------

    # @:adhoc_run_time_section:@ on
    line_delimiters = ('@:', ':@')
    # @:adhoc_run_time_section:@ off
    '''Tag delimiters for lines.'''
    # @:adhoc_run_time_section:@ on
    section_delimiters = ('@:', ':@')
    # @:adhoc_run_time_section:@ off
    '''Tag delimiters for sections.'''
    # @:adhoc_run_time_section:@ on

    template_process_hooks = {}
    # @:adhoc_run_time_section:@ off
    '''Dictionary of ``template-name, hook-function`` items.

    If the name of a template section matches an item in this
    dictionary, the ``hook-function`` is called::

        section = hook-function(cls, section, tag, template_name)
    '''
    # @:adhoc_run_time_section:@ on
    extra_templates = []
    # @:adhoc_run_time_section:@ off
    '''List of additional templates::

        [(name, type), ...]
    '''
    # @:adhoc_run_time_section:@ on

    export_dir = '__adhoc__'
    # @:adhoc_run_time_section:@ off
    '''Export directory (for :meth:`export`, ``--explode``).'''
    # @:adhoc_run_time_section:@ on
    extract_dir = '.'
    # @:adhoc_run_time_section:@ off
    '''Export directory (for :meth:`extract`, ``--extract``).'''
    # @:adhoc_run_time_section:@ on
    flat = True
    # @:adhoc_run_time_section:@ off
    '''If True, do not export files recursively.'''
    # @:adhoc_run_time_section:@ on
    forced = False
    # @:adhoc_run_time_section:@ off
    '''If True, allow duplicate imports.'''
    # @:adhoc_run_time_section:@ on

    frozen = False
    # @:adhoc_run_time_section:@ off
    '''If True, do not attempt to load modules from external
    sources (\\|:todo:| not implemented).'''
    # @:adhoc_run_time_section:@ on

    quiet = False
    # @:adhoc_run_time_section:@ off
    '''If True, suppress warnings.'''
    # @:adhoc_run_time_section:@ on
    verbose = False
    # @:adhoc_run_time_section:@ off
    '''If True, display messages.'''
    # @:adhoc_run_time_section:@ on
    debug = False
    # @:adhoc_run_time_section:@ off
    '''If True, display debug messages.'''
    # @:adhoc_run_time_section:@ on

    include_path = []
    # @:adhoc_run_time_section:@ off
    '''Search path for include files. Only relevant during compilation.'''
    # @:adhoc_run_time_section:@ on
    export_need_init = {}
    export_have_init = {}
    extract_warn = False

    # @:adhoc_run_time_section:@ off
    # --------------------------------------------------
    # ||:sec:|| Low-Level Functions
    # --------------------------------------------------

    # @:adhoc_run_time_section:@ on
    def _adhoc_string_util():
        # @:adhoc_run_time_section:@ off
        '''Define string utilities.

        - static method :meth:`isstring`
        - unicode type :attr:`uc_type`
        - static method :meth:`uc`
        '''
        # @:adhoc_run_time_section:@ on
        def isstring(obj):
            return isinstance(obj, basestring)
        try:
            isstring("")
        except NameError:
            def isstring(obj):
                return isinstance(obj, str) or isinstance(obj, bytes)
        def _uc(string):
            return unicode(string, 'utf-8')
        try:
            _uc("")
        except NameError:
            _uc = lambda x: x
        uc_type = type(_uc(""))
        def uc(value):
            if isstring(value) and not isinstance(value, uc_type):
                return _uc(value)
            return value
        return staticmethod(isstring), uc_type, staticmethod(uc)

    isstring, uc_type, uc = _adhoc_string_util()

    @staticmethod
    def adhoc_tag(symbol_or_re, delimiters, is_re=False):    # |:fnc:|
        # @:adhoc_run_time_section:@ off
        '''Make a tag from symbol_or_re and delimiters.

        :param symbol_or_re: symbol string or regular expresssion.
        :param delimiters: tuple of delimiter strings
          ``(prefix, suffix)``.
        :param is_re: if True, escape the delimiters for regular
          expressions.
        '''
        # @:adhoc_run_time_section:@ on
        ldlm = delimiters[0]
        rdlm = delimiters[1]
        if is_re:
            ldlm = re.escape(ldlm)
            rdlm = re.escape(rdlm)
        return ''.join((ldlm, symbol_or_re, rdlm))

    @classmethod
    def tag_split(cls, string, tag, is_re=False):            # |:fnc:|
        # @:adhoc_run_time_section:@ off
        """Split string with tag line.

        :returns:
          a list of tuples with a flag and a section::

            [(is_tag, section), ... ]

        **Example**

        >>> source = AH_CHECK_SOURCE
        >>> printf(str(source), end='')
        not in section
        # >:cmd:< arg0 arg1 # comment
        # <:tag:> on
        in section
        # >:cmd:< arg2 arg3 # comment
        in section
        # <:tag:> off
        not in section
        # <:tag2:> on
        in section
        in section
        # <:tag2:> off
        not in section

        **Split on literal tag**

        >>> is_re = False
        >>> tag = AdHoc.adhoc_tag('tag', ('<:', ':>'), is_re)
        >>> parts = AdHoc.tag_split(source, tag, is_re)
        >>> adhoc_dump_sections(parts, 40)
        #   :DBG:   section[0]             : ][False, 'not in section\\n# >:cmd:< arg0 arg1 #  ...'][
        #   :DBG:   section[1]             : ][True, '# <:tag:> on\\n'][
        #   :DBG:   section[2]             : ][False, 'in section\\n# >:cmd:< arg2 arg3 # comm ...'][
        #   :DBG:   section[3]             : ][True, '# <:tag:> off\\n'][
        #   :DBG:   section[4]             : ][False, 'not in section\\n# <:tag2:> on\\nin secti ...'][

        **Split on tag regexp**

        >>> is_re = True
        >>> tag = AdHoc.adhoc_tag('tag.?', ('<:', ':>'), is_re)
        >>> parts = AdHoc.tag_split(source, tag, is_re)
        >>> adhoc_dump_sections(parts, 40)
        #   :DBG:   section[0]             : ][False, 'not in section\\n# >:cmd:< arg0 arg1 #  ...'][
        #   :DBG:   section[1]             : ][True, '# <:tag:> on\\n'][
        #   :DBG:   section[2]             : ][False, 'in section\\n# >:cmd:< arg2 arg3 # comm ...'][
        #   :DBG:   section[3]             : ][True, '# <:tag:> off\\n'][
        #   :DBG:   section[4]             : ][False, 'not in section\\n'][
        #   :DBG:   section[5]             : ][True, '# <:tag2:> on\\n'][
        #   :DBG:   section[6]             : ][False, 'in section\\nin section\\n'][
        #   :DBG:   section[7]             : ][True, '# <:tag2:> off\\n'][
        #   :DBG:   section[8]             : ][False, 'not in section\\n'][

        **Assemble section**

        >>> section = []
        >>> in_section = False
        >>> for part in parts:
        ...     if part[0]:
        ...         in_section = not in_section
        ...         continue
        ...     if in_section:
        ...         section.append(part[1])
        >>> section = ''.join(section)
        >>> printf(str(section), end='')
        in section
        # >:cmd:< arg2 arg3 # comment
        in section
        in section
        in section
        """
        # @:adhoc_run_time_section:@ on
        if not is_re:
            tag = re.escape(tag)
        ro = re.compile(''.join(('^[^\n]*(', tag, ')[^\n]*$')), re.M)
        result = []
        last_end = 0
        string = cls.decode_source(string)
        for mo in re.finditer(ro, string):
            start = mo.start(0)
            end = mo.end(0)
            result.append((False, string[last_end:start]))
            result.append((True, string[start:end+1]))
            last_end = end+1
        result.append((False, string[last_end:]))
        return result

    @classmethod
    def adhoc_parse_line(cls, tagged_line, symbol_or_re=None, # |:clm:|
                         delimiters=None, is_re=False, strip_comment=None):
        # @:adhoc_run_time_section:@ off
        """Parse a tagged line into tag-symbol and argument parts.

        :returns: a tuple ``(tag-symbol, tag-arguments)``.

        :param tagged_line: string to be parsed.
        :param symbol_or_re: symbol string or regular expresssion to
          be parsed, default is any sequence of characters except the
          first character of the suffix delimiter.
        :param delimiters: tuple of delimiter strings
          ``(prefix, suffix)``. Default is :attr:`line_delimiters`.
        :param strip_comment: If True, remove trailing ``#`` comment
          from arguments. Default: False.

        >>> tagged_line = ' # @:' 'adhoc_test' ':@   arg1 arg2  # comment'
        >>> AdHoc.adhoc_parse_line(tagged_line)
        ('adhoc_test', 'arg1 arg2  # comment')

        >>> AdHoc.adhoc_parse_line(tagged_line, 'adhoc_.*', is_re=True)
        ('adhoc_test', 'arg1 arg2  # comment')

        >>> AdHoc.adhoc_parse_line(tagged_line, strip_comment=True)
        ('adhoc_test', 'arg1 arg2')

        >>> AdHoc.adhoc_parse_line(tagged_line.replace('@', '<'))
        ('', '# <:adhoc_test:<   arg1 arg2  # comment')

        >>> AdHoc.adhoc_parse_line(tagged_line.replace('@', '|'), delimiters=('|:', ':|'))
        ('adhoc_test', 'arg1 arg2  # comment')
        """
        # @:adhoc_run_time_section:@ on
        if delimiters is None:
            delimiters = cls.line_delimiters
        if symbol_or_re is None:
            dlm = delimiters[1]
            if dlm:
                symbol_or_re = ''.join(('[^', dlm[0], ']+'))
            else:
                symbol_or_re = ''.join(('[^\\s]+'))
            is_re = True
        if not is_re:
            symbol_or_re = re.escape(symbol_or_re)
        tag_rx = cls.adhoc_tag(''.join(('(', symbol_or_re, ')')), delimiters, is_re=True)
        mo = re.search(tag_rx, tagged_line)
        if mo:
            ptag = mo.group(1)
        else:
            ptag = ''
        strip_rx = ''.join(('^.*', tag_rx, '\\s*'))
        tag_arg = re.sub(strip_rx, '', tagged_line).strip()
        if strip_comment:
            tag_arg = re.sub('\\s*#.*', '', tag_arg)
        return (ptag, tag_arg)

    # @:adhoc_run_time_section:@ off
    # --------------------------------------------------
    # ||:sec:|| Low-Level Convenience Functions
    # --------------------------------------------------

    # @:adhoc_run_time_section:@ on
    @classmethod
    def set_delimiters(cls, line_delimiters=None, section_delimiters=None): # |:clm:|
        # @:adhoc_run_time_section:@ off
        '''Set line/section delimiters.

        :returns: saved delimiter state suitable for
          :meth:`reset_delimiters`.

        :param line_delimiters: the line delimiters. If None, line
          delimiters are not changed.
        :param section_delimiters: the section delimiters. If None,
          `line_delimiters` is used.

        If both `line_delimiters` and `section_delimiters` are None,
        the delimiter state is returned without any modification to
        the current delimiters.

        >>> AdHoc.set_delimiters()
        (('@:', ':@'), ('@:', ':@'))

        >>> sv = AdHoc.inc_delimiters()
        >>> sv
        (('@:', ':@'), ('@:', ':@'))

        >>> AdHoc.set_delimiters()
        (('@@:', ':@@'), ('@@:', ':@@'))

        >>> AdHoc.reset_delimiters(sv)
        >>> AdHoc.set_delimiters()
        (('@:', ':@'), ('@:', ':@'))

        >>> AdHoc.set_delimiters(('<:', ':>'))
        (('@:', ':@'), ('@:', ':@'))

        >>> AdHoc.set_delimiters()
        (('<:', ':>'), ('<:', ':>'))

        >>> AdHoc.reset_delimiters(sv)
        >>> AdHoc.set_delimiters()
        (('@:', ':@'), ('@:', ':@'))

        '''
        # @:adhoc_run_time_section:@ on
        delimiter_state = (cls.line_delimiters, cls.section_delimiters)
        if line_delimiters is None:
            line_delimiters = delimiter_state[0]
            if section_delimiters is None:
                section_delimiters = delimiter_state[1]
        elif section_delimiters is None:
            section_delimiters = line_delimiters
        cls.line_delimiters, cls.section_delimiters = (
            line_delimiters, section_delimiters)
        return delimiter_state

    @classmethod
    def reset_delimiters(cls, delimiter_state):              # |:clm:|
        # @:adhoc_run_time_section:@ off
        '''Reset line/section delimiters from saved state.

        :param delimiter_state: delimiter state as returned by
          :meth:`set_delimiters`.
        '''
        # @:adhoc_run_time_section:@ on
        cls.line_delimiters, cls.section_delimiters = delimiter_state

    @classmethod
    def inc_delimiters(cls):                                 # |:clm:|
    # @:adhoc_run_time_section:@ off
        '''Duplicate outer delimiter characters.

        :returns: saved delimiter state suitable for
          :meth:`reset_delimiters`.

        E.g.::

            "@:", ":@" => "@@:", ":@@"

        See :meth:`set_delimiters` for doctest example.
        '''
        # @:adhoc_run_time_section:@ on

        inc_first = lambda dlm: (((not dlm) and ('')) or (dlm[0] + dlm))
        inc_last = lambda dlm: (((not dlm) and ('')) or (dlm + dlm[-1]))
        outer_delimiters = [(inc_first(dlm[0]), inc_last(dlm[1]))
                            for dlm in (cls.line_delimiters,
                                        cls.section_delimiters)]
        return cls.set_delimiters(*outer_delimiters)

    @classmethod
    def line_tag(cls, symbol_or_re, is_re=False):            # |:clm:|
        # @:adhoc_run_time_section:@ off
        '''Make a line tag from symbol or regular expression.

        :returns: unicode string.

        :param symbol_or_re: symbol string or regular expresssion.
        :param is_re: if True, escape the delimiters for regular
          expressions.
        '''
        # @:adhoc_run_time_section:@ on
        return cls.adhoc_tag(symbol_or_re, cls.line_delimiters, is_re)

    @classmethod
    def section_tag(cls, symbol_or_re, is_re=False):         # |:clm:|
        # @:adhoc_run_time_section:@ off
        '''Make a section tag from symbol or regular expression.

        :returns: unicode string.

        :param symbol_or_re: symbol string or regular expresssion.
        :param is_re: if True, escape the delimiters for regular
          expressions.
        '''
        # @:adhoc_run_time_section:@ on
        return cls.adhoc_tag(symbol_or_re, cls.section_delimiters, is_re)

    @classmethod
    def tag_lines(cls, string, tag, is_re=False):            # |:clm:|
        # @:adhoc_run_time_section:@ off
        """Get lines matching tag.

        :returns: list of tag lines.

        See :meth:`tag_split`.
        """
        # @:adhoc_run_time_section:@ on
        result = []
        for section in cls.tag_split(string, tag, is_re):
            if section[0]:
                result.append(section[1])
        return result

    @classmethod
    def tag_partition(cls, string, tag, is_re=False, headline=False): # |:clm:|
        # @:adhoc_run_time_section:@ off
        '''Split the string into body parts and sections.

        If `headline` is True, the starting tag line is included for
        sections.'''
        # @:adhoc_run_time_section:@ on
        in_section = False
        body_parts = []
        sections = []
        tagged_line = ''
        for section in cls.tag_split(string, tag, is_re):
            if section[0]:
                in_section = not in_section
                tagged_line = section[1]
                continue
            if in_section:
                if headline:
                    sections.append((tagged_line, section[1]))
                else:
                    sections.append(section[1])
            else:
                body_parts.append(section[1])
        return body_parts, sections

    @classmethod
    def tag_sections(cls, string, tag, is_re=False, headline=False): # |:clm:|
        # @:adhoc_run_time_section:@ off
        '''Split the string into sections.

        If `headline` is True, the starting tag line is included.

        See :meth:`tag_partition`.
        '''
        # @:adhoc_run_time_section:@ on
        body_parts, sections = cls.tag_partition(string, tag, is_re, headline)
        return sections

    @classmethod
    def line_tag_parse(cls, tagged_line, symbol_or_re=None, is_re=False, # |:clm:|
                       strip_comment=None):
        # @:adhoc_run_time_section:@ off
        """Parse a line tag line into tag-symbol and argument parts.

        :returns: a tuple ``(tag-symbol, tag-arguments)``.

        See :meth:`adhoc_parse_line`.
        """
        # @:adhoc_run_time_section:@ on
        return cls.adhoc_parse_line(tagged_line, symbol_or_re, cls.line_delimiters,
                                    is_re, strip_comment=strip_comment)

    @classmethod
    def line_tag_strip(cls, tagged_line, symbol_or_re=None, is_re=False, # |:clm:|
                       strip_comment=None):
        # @:adhoc_run_time_section:@ off
        """Remove tag and optionally comment from line tag line.

        :returns: tag arguments.

        See :meth:`adhoc_parse_line`.
        """
        # @:adhoc_run_time_section:@ on
        return cls.line_tag_parse(tagged_line, symbol_or_re, is_re, strip_comment)[1]

    @classmethod
    def section_tag_parse(cls, tagged_line, symbol_or_re=None, is_re=False, # |:clm:|
                       strip_comment=None):
        # @:adhoc_run_time_section:@ off
        """Parse a section tag line into tag-symbol and argument parts.

        :returns: a tuple ``(tag-symbol, tag-arguments)``.

        See :meth:`adhoc_parse_line`.
        """
        # @:adhoc_run_time_section:@ on
        return cls.adhoc_parse_line(tagged_line, symbol_or_re, cls.section_delimiters,
                                    is_re, strip_comment=strip_comment)

    @classmethod
    def section_tag_strip(cls, tagged_line, symbol_or_re=None, is_re=False, # |:clm:|
                       strip_comment=None):
        # @:adhoc_run_time_section:@ off
        """Remove tag and optionally comment from section tag line.

        :returns: tag arguments.

        See :meth:`adhoc_parse_line`.
        """
        # @:adhoc_run_time_section:@ on
        return cls.section_tag_parse(tagged_line, symbol_or_re, is_re, strip_comment)[1]

    # @:adhoc_run_time_section:@ off
    # --------------------------------------------------
    # ||:sec:|| Tagged Line/Section Transformations
    # --------------------------------------------------

    # @:adhoc_run_time_section:@ on
    @classmethod
    def transform_lines(cls, transform, string,              # |:clm:|
                        symbol_or_re, is_re=False, delimiters=None):
        # @:adhoc_run_time_section:@ off
        """Split string into line tag lines and other sections; call
        transform callback on each tagged line.

        :returns: transformed string.

        :param transform: callback which receives argument ``tagged-line``.
        """
        # @:adhoc_run_time_section:@ on
        if delimiters is None:
            delimiters = cls.line_delimiters
        result = []
        in_section = False
        for section in cls.tag_split(
            string, cls.adhoc_tag(symbol_or_re, delimiters, is_re), is_re):
            blob = section[1]
            if section[0]:
                in_section = not in_section
                blob = transform(blob)
            result.append(blob)
        string = ''.join(result)
        return string

    @classmethod
    def transform_sections(cls, transform, string,           # |:clm:|
                           symbol_or_re, is_re=False):
        # @:adhoc_run_time_section:@ off
        """Split string into sections and call transform callback on each section.

        :returns: transformed string.

        :param transform: callback which receives and returns
          arguments ``section``, ``headline``.
        """
        # @:adhoc_run_time_section:@ on
        result = []
        in_section = False
        headline = ''
        for section in cls.tag_split(
            string, cls.section_tag(symbol_or_re, is_re), is_re):
            blob = section[1]
            if section[0]:
                in_section = not in_section
                if in_section:
                    headline = blob
                    continue
            elif in_section:
                blob, headline = transform(blob, headline)
                result.append(headline)
            result.append(blob)
        string = ''.join(result)
        return string

    @classmethod
    def line_tag_rename(cls, string, symbol_or_re, renamed, is_re=False, delimiters=None): # |:clm:|
        # @:adhoc_run_time_section:@ off
        '''Rename tag-symbol.

        Default tag delimiters are :attr:`line_delimiters`.

        >>> tpl = AdHoc.get_named_template("col-param-closure")

        .. >>> printf(str(AdHoc.line_tag_rename(tpl, "adhoc_run_time_section", "should_be_kept")))
        '''
        # @:adhoc_run_time_section:@ on
        if is_re:
            transform = lambda blob: re.sub(symbol_or_re, renamed, blob)
        else:
            transform = lambda blob: blob.replace(symbol_or_re, renamed)
        return cls.transform_lines(transform, string, symbol_or_re, is_re, delimiters)

    @classmethod
    def line_tag_remove(cls, string, symbol_or_re, is_re=False, delimiters=None): # |:clm:|
        # @:adhoc_run_time_section:@ off
        '''Remove tagged lines.

        Default tag delimiters are :attr:`line_delimiters`.

        >>> tpl = AdHoc.get_named_template("col-param-closure")

        .. >>> printf(str(AdHoc.line_tag_remove(tpl, "adhoc_run_time_section")))
        '''
        # @:adhoc_run_time_section:@ on
        transform = lambda blob: ''
        return cls.transform_lines(transform, string, symbol_or_re, is_re, delimiters)

    @classmethod
    def section_tag_rename(cls, string, symbol_or_re, renamed, is_re=False): # |:clm:|
        # @:adhoc_run_time_section:@ off
        '''Rename tag-symbol of lines tagged with :attr:`section_delimiters`.

        >>> tpl = AdHoc.get_named_template("col-param-closure")
        >>> res = AdHoc.section_tag_rename(tpl, "adhoc_run_time_section", "should_be_kept")
        >>> res = '\\n'.join(res.splitlines()[:4])
        >>> printf(str(res)) #doctest: +ELLIPSIS
            # @:should_be_kept:@ on
            @classmethod
            def col_param_closure(cls):...
                # @:should_be_kept:@ off
        '''
        # @:adhoc_run_time_section:@ on
        if is_re:
            transform = lambda blob: re.sub(symbol_or_re, renamed, blob)
        else:
            transform = lambda blob: blob.replace(symbol_or_re, renamed)
        return cls.transform_lines(transform, string, symbol_or_re, is_re, cls.section_delimiters)

    @classmethod
    def section_tag_remove(cls, string, symbol_or_re, is_re=False): # |:clm:|
        # @:adhoc_run_time_section:@ off
        '''Remove lines tagged with :attr:`section_delimiters`.

        >>> tpl = AdHoc.get_named_template("col-param-closure")
        >>> res = AdHoc.section_tag_remove(tpl, "adhoc_run_time_section")
        >>> res = '\\n'.join(res.splitlines()[:4])
        >>> printf(str(res)) #doctest: +ELLIPSIS
            @classmethod
            def col_param_closure(cls):...
                ...Closure for setting up maximum width, padding and separator
                for table columns.
        '''
        # @:adhoc_run_time_section:@ on
        transform = lambda blob: ''
        return cls.transform_lines(transform, string, symbol_or_re, is_re, cls.section_delimiters)

    @classmethod
    def indent_sections(cls, string, symbol_or_re, is_re=False): # |:clm:|
        # @:adhoc_run_time_section:@ off
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
        for section in cls.tag_split(
            string, cls.section_tag(symbol_or_re, is_re), is_re):
            blob = section[1]
            if section[0]:
                in_section = not in_section
                if in_section:
                    tag_arg = cls.section_tag_strip(blob)
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
    def enable_sections(cls, string, symbol_or_re, is_re=False): # |:clm:|
        # @:adhoc_run_time_section:@ off
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
        transform = lambda blob, hl: (enable_ro.sub(enable_sub, blob), hl)
        return cls.transform_sections(transform, string, symbol_or_re, is_re)

    adhoc_rx_tab_check = re.compile('^([ ]*\t)', re.M)
    adhoc_rx_disable_simple = re.compile('^', re.M)
    adhoc_rx_min_indent_check = re.compile('^([ ]*)([^ \t\r\n]|$)', re.M)

    @classmethod
    def disable_transform(cls, section, headline=None):      # |:clm:|
        # @:adhoc_run_time_section:@ off
        '''Disable section transform callback.'''
        # @:adhoc_run_time_section:@ on
        if not section:
            return (section, headline)

        if cls.adhoc_rx_tab_check.search(section):
            # tabs are evil
            if cls.verbose:
                list(map(sys.stderr.write,
                         ('# dt: evil tabs: ', repr(section), '\n')))
            return (
                cls.adhoc_rx_disable_simple.sub(
                    '# ', section.rstrip()) + '\n',
                headline)

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
                #leave blank lines blank
                dsection.append('\n')
            else:
                dsection.extend((indent, '# ', rest, '\n'))
        return (''.join(dsection), headline)

    @classmethod
    def disable_sections(cls, string, symbol_or_re, is_re=False): # |:clm:|
        # @:adhoc_run_time_section:@ off
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
        <BLANKLINE>
          # line 3
          @:adhoc_disable_check:@
          suffix
        '''
        # @:adhoc_run_time_section:@ on
        return cls.transform_sections(
            cls.disable_transform, string, symbol_or_re, is_re)

    @classmethod
    def remove_sections(cls, string, symbol_or_re, is_re=False): # |:clm:|
        # @:adhoc_run_time_section:@ off
        '''Remove sections.'''
        # @:adhoc_run_time_section:@ on
        ah_retained, ah_removed = cls.tag_partition(
            string, cls.section_tag(symbol_or_re, is_re), is_re)
        return ''.join(ah_retained)

    # @:adhoc_run_time_section:@ off
    # --------------------------------------------------
    # ||:sec:|| IO Functions
    # --------------------------------------------------

    # @:adhoc_run_time_section:@ on
    @staticmethod
    def check_coding(source):                                # |:fnc:|
        # @:adhoc_run_time_section:@ off
        '''Determine coding for source.

        :returns: coding type for string.

        :param source: source string/unicode.

        If the ``source`` string contains a coding specification
        within the first two lines, the specified coding is used,
        otherwise, ``UTF-8`` is returned.
        '''
        # @:adhoc_run_time_section:@ on
        if source:
            eol_seen = 0
            for c in source:
                if isinstance(c, int):
                    lt_ = lambda a, b: a < b
                    chr_ = lambda a: chr(a)
                else:
                    lt_ = lambda a, b: True
                    chr_ = lambda a: a
                break
            check = []
            for c in source:
                if lt_(c, 127):
                    check.append(chr_(c))
                if c == '\n':
                    eol_seen += 1
                    if eol_seen == 2:
                        break
            check = ''.join(check)
            mo = re.search('-[*]-.*coding:\\s*([^;\\s]+).*-[*]-', check)
        else:
            mo = None
        if mo:
            coding = mo.group(1)
        else:
            coding = 'utf-8'
        return coding

    @classmethod
    def decode_source(cls, source):                          # |:clm:|
        # @:adhoc_run_time_section:@ off
        '''Decode source to unicode.

        :param source: source string (may already be unicode).

        If the ``source`` string contains a coding specification
        within the first two lines, the specified coding is used,
        otherwise, ``UTF-8`` is applied.
        '''
        # @:adhoc_run_time_section:@ on
        if not source:
            return cls.uc('')
        if not isinstance(source, cls.uc_type) and hasattr(source, 'decode'):
            source = source.decode(cls.check_coding(source))
        return source

    @classmethod
    def encode_source(cls, source):                          # |:clm:|
        # @:adhoc_run_time_section:@ off
        '''Encode source from unicode.

        :param source: source string (may already be encoded).

        If the ``source`` string contains a coding specification
        within the first two lines, the specified coding is used,
        otherwise, ``UTF-8`` is applied.
        '''
        # @:adhoc_run_time_section:@ on
        if not source:
            return ''.encode('utf-8')
        if isinstance(source, cls.uc_type) and hasattr(source, 'encode'):
            source = source.encode(cls.check_coding(source))
        return source

    @classmethod
    def read_source(cls, file_, decode=True):                # |:clm:|
        # @:adhoc_run_time_section:@ off
        '''Read source from file.

        :returns: unicode string.

        :param file_: If None, empty or ``-``, sys.stdin is used,
          otherwise the file is read from ``file_`` and decoded with
          :meth:`decode_source`.
        '''
        # @:adhoc_run_time_section:@ on
        source = None
        if not file_ or file_ == '-':
            # Python3 has a buffer attribute for binary input.
            if hasattr(sys.stdin, 'buffer'):
                source = sys.stdin.buffer.read()
            else:
                source = sys.stdin.read()
        else:
            try:
                sf = open(file_, 'rb')
                source = sf.read()
                sf.close()
            except IOError:
                for module in sys.modules.values():
                    if (module
                        and hasattr(module, '__file__')
                        and module.__file__ == file_):
                        if (hasattr(module, '__adhoc__')
                            and hasattr(module.__adhoc__, 'source')):
                            source = module.__adhoc__.source
                            break
        if source is None:
            raise IOError('source not found for `' + str(file_) + '`')
        if decode:
            return cls.decode_source(source)
        return source

    @classmethod
    def write_source(cls, file_, source, mtime=None, mode=None): # |:clm:|
        # @:adhoc_run_time_section:@ off
        '''Write source to file.

        :param file_: If None, empty or ``-``, sys.stdout is used,
          otherwise the file is written to ``file_`` after encoding
          with :meth:`encode_source`.
        '''
        # @:adhoc_run_time_section:@ on
        esource = cls.encode_source(source)
        if not file_ or file_ == '-':
            # @:adhoc_run_time_section:@ off
            # For Python2, sys.stdout is effectively binary, so source
            # can be pre-encoded.
            #
            # With Python3 sys.stdout does automatic encoding (which
            # is unwanted).
            # Normal sys.stdout has a buffer member which allows
            # binary output, but not during doctest.
            # @:adhoc_run_time_section:@ on
            if hasattr(sys.stdout, 'buffer'):
                sys.stdout.buffer.write(esource)
            else:
                try:
                    sys.stdout.write(esource)
                except TypeError:
                    sys.stdout.write(source)
        else:
            sf = open(file_, 'wb')
            sf.write(esource)
            sf.close()
            if mode is not None:
                os.chmod(file_, mode)
            if mtime is not None:
                import datetime
                if cls.isstring(mtime):
                    try:
                        date, ms = mtime.split('.')
                    except ValueError:
                        date = mtime
                        ms = 0
                    mtime = cls.strptime(date, '%Y-%m-%dT%H:%M:%S')
                    mtime += datetime.timedelta(microseconds=int(ms))
                if isinstance(mtime, datetime.datetime):
                    # @:adhoc_run_time_section:@ off
                    # import calendar
                    # if mtime.utcoffset() is not None:
                    #     mtime = mtime - mtime.utcoffset()
                    # millis = int(calendar.timegm(mtime.timetuple()) * 1000 +
                    #                mtime.microsecond / 1000)
                    # ts = float(millis) / 1000
                    # @:adhoc_run_time_section:@ on
                    ts = int(mtime.strftime("%s"))
                else:
                    ts = mtime
                os.utime(file_, (ts, ts))

    @classmethod
    def check_xfile(cls, file_, xdir=None):                  # |:clm:|
        # @:adhoc_run_time_section:@ off
        '''Prepare extraction of a file.

        :returns: None, if the file already exists. Otherwise, the
          file directory is created and the absolute path name of the
          file is returned.

        :param file_: filename.
        :param xdir: extraction directory. If it is `None`,
          :attr:`extract_dir` is used.

        If ``file_`` is `None`, empty or ``-``, the filename ``-`` is
        returned.

        If ``file_`` starts with a slash ``/``, ``xdir`` is ignored,
        otherwise, ``xdir`` is prepended to ``file_``.
        '''
        # @:adhoc_run_time_section:@ on
        if xdir is None:
            xdir = cls.extract_dir
        if not file_:
            file_ = '-'
        if file_ == '-':
            return file_
        file_ = os.path.expanduser(file_)
        if os.path.isabs(file_):
            xfile = file_
        else:
            xfile = os.path.join(xdir, file_)
        xfile = os.path.abspath(xfile)
        if os.path.exists(xfile):
            # do not overwrite files
            if (cls.extract_warn or (cls.verbose)) and not cls.quiet:
                list(map(sys.stderr.write, (
                    "# xf: ", cls.__name__, ": warning file `", file_,
                    "` exists. skipping ...\n")))
            return None
        xdir = os.path.dirname(xfile)
        if not os.path.exists(xdir):
            os.makedirs(xdir)
        return xfile

    @classmethod
    def pack_file(cls, source, zipped=True):                 # |:clm:|
        # @:adhoc_run_time_section:@ off
        '''Optionally gzip a file and base64-encode it.

        :returns: base64-encoded unicode string.

        :param source: string to be packed.
        :param zipped: if True, gzip ``source`` before
          base64-encoding. (Default: True).
        '''
        # @:adhoc_run_time_section:@ on
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

    @classmethod
    def unpack_file(cls, source64, zipped=True, decode=True): # |:clm:|
        # @:adhoc_run_time_section:@ off
        '''Base64-decode a file and optionally ungzip it.

        :returns: unicode string if ``decode`` is True.

        :param source64: base64 encoded unicode string to be unpacked.
        :param zipped: if True, ungzip ``source`` after
          base64-decoding. (Default: True).
        '''
        # @:adhoc_run_time_section:@ on
        import base64, gzip
        # @:adhoc_run_time_section:@ off
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
            # @:adhoc_run_time_section:@ off
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
        if decode:
            source = cls.decode_source(source)
        # @:adhoc_run_time_section:@ off
        if cls.debug:
            printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5:>7d}[ ]{6!s}[",
                    dbg_comm, dbg_twid, dbg_fwid,
                    ':DBG:', 'source', len(source), repr(source)[:80]))

        # @:adhoc_run_time_section:@ on
        return source

    # @:adhoc_run_time_section:@ off
    # --------------------------------------------------
    # ||:sec:|| Run-Time Unpack/Import Interface
    # --------------------------------------------------

    # @:adhoc_run_time_section:@ on
    @classmethod
    def unpack_(cls, mod_name=None, file_=None, mtime=None, # |:clm:||:api_fi:|
                mode=None, zipped=True, flat=None, source64=None):
        # @:adhoc_run_time_section:@ off
        """Unpack adhoc'ed file, if it does not exist."""
        # @:adhoc_run_time_section:@ on
        xfile = cls.check_xfile(file_, cls.extract_dir)
        if xfile is None:
            return
        if cls.verbose:
            list(map(sys.stderr.write,
                     ("# xf: ", cls.__name__, ": unpacking `", file_, "`\n")))
        source = cls.unpack_file(source64, zipped=zipped, decode=False)
        cls.write_source(xfile, source, mtime, mode)

    @classmethod
    def strptime(cls, date_string, format_):                 # |:clm:|
        # @:adhoc_run_time_section:@ off
        """Python 2.4 compatible"""
        # @:adhoc_run_time_section:@ on
        import datetime
        if hasattr(datetime.datetime, 'strptime'):
            strptime_ = datetime.datetime.strptime
        else:
            import time
            strptime_ = lambda date_string, format_: (
                datetime.datetime(*(time.strptime(date_string, format_)[0:6])))
        return strptime_(date_string, format_)

    @classmethod
    def import_(cls, mod_name=None, file_=None, mtime=None, # |:clm:||:api_fi:|
                mode=None, zipped=True, flat=None, source64=None):
        # @:adhoc_run_time_section:@ off
        """Import adhoc'ed module."""
        # @:adhoc_run_time_section:@ on
        import datetime
        import time

        module = cls.module_setup(mod_name)

        if mtime is None:
            mtime = datetime.datetime.fromtimestamp(0)
        else:
            # mtime=2011-11-23T18:04:26[.218506], zipped=True, flat=None, source64=
            try:
                date, ms = mtime.split('.')
            except ValueError:
                date = mtime
                ms = 0
            mtime = cls.strptime(date, '%Y-%m-%dT%H:%M:%S')
            mtime += datetime.timedelta(microseconds=int(ms))

        source = cls.unpack_file(source64, zipped=zipped, decode=False)

        # @:adhoc_run_time_section:@ off
        # |:todo:| add to parent module
        # @:adhoc_run_time_section:@ on
        mod_parts = mod_name.split('.')
        mod_child = mod_parts[-1]
        parent = '.'.join(mod_parts[:-1])
        # @:adhoc_run_time_section:@ off
        printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'parent', parent))

        # @:adhoc_run_time_section:@ on
        old_mtime = module.__adhoc__.mtime
        module = cls.module_setup(mod_name, file_, mtime, source, mode)
        if len(parent) > 0:
            setattr(sys.modules[parent], mod_child, module)

        if module.__adhoc__.mtime != old_mtime:
            # @:adhoc_run_time_section:@ off
            printf(sformat('{0}Executing source', dbg_comm))
            # @:adhoc_run_time_section:@ on
            source = cls.encode_source(module.__adhoc__.source)
            exec(source, module.__dict__)
        # @:adhoc_run_time_section:@ off

        msg = (((mod_name in sys.modules) and ('YES')) or ('NO'))
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
    def module_setup(cls, module=None, file_=None, mtime=None, # |:clm:||:api_fi:|
                     source=None, mode=None):
        # @:adhoc_run_time_section:@ off
        '''Setup module for `AdHoc`.
        \\|:todo:| various modes are possible:
        - always use newest version (development) (currently implemented)
        - always use adhoc\'ed version (freeze) (not implemented)
        '''
        # @:adhoc_run_time_section:@ on
        m = 'ms: '
        class Attr:                                          # |:cls:|
            pass

        import types, datetime, os
        if not isinstance(module, types.ModuleType):
            mod_name = module
            if mod_name is None:
                mod_name = __name__
            try:
                if mod_name not in sys.modules:
                    # @:adhoc_run_time_section:@ off
                    if cls.verbose:
                        printe(sformat('{0}{1}__import__({2})',
                                       dbg_comm, m, mod_name))
                    # @:adhoc_run_time_section:@ on
                    __import__(mod_name)
                module = sys.modules[mod_name]
            except (ImportError, KeyError):
                # @:adhoc_run_time_section:@ off
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
            mode_set = mode
            if hasattr(module, '__file__'):
                module_file = module.__file__
                if module_file.endswith('.pyc'):
                    module_file = module_file[:-1]
                if os.access(module_file, os.R_OK):
                    stat = os.stat(module_file)
                    mtime_set = datetime.datetime.fromtimestamp(
                        stat.st_mtime)
                    mode_set = stat.st_mode
            if mtime_set is None:
                # the info is marked as very outdated
                mtime_set = datetime.datetime.fromtimestamp(0)
            adhoc.mtime = mtime_set
            adhoc.mode = mode_set
        else:
            adhoc = module.__adhoc__

        if (mtime > adhoc.mtime
            or not hasattr(module, '__file__')):
            if file_ is not None:
                setattr(module, '__file__', file_)
                if os.access(file_, os.R_OK):             # |:api_fi:|
                    stat = os.stat(file_)
                    adhoc.mtime = datetime.datetime.fromtimestamp(
                        stat.st_mtime)
                    adhoc.mode = stat.st_mode
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
                adhoc.mode = mode

        if not hasattr(adhoc, 'source'):
            try:
                file_ = module.__file__
                file_, source = cls.std_source_param(file_, source)
                adhoc.source = source
            except (AttributeError, IOError):
                # @:adhoc_run_time_section:@ off
                # if hasattr(module, '__path__'): # |:debug:|
                #     list(map(sys.stderr.write,
                #         ('module path: ', module.__path__, '\n')))
                # else:
                #     sys.stderr.write('no module.__path__\n')
                #     list(map(sys.stderr.write,
                #         [''.join((attr, str(value), "\n")) for attr, value in
                #          filter(lambda i: i[0] != '__builtins__',
                #                 sorted(vars(module).items()))]))
                if cls.verbose:
                    (t, e, tb) = sys.exc_info()
                    import traceback
                    printe(''.join(traceback.format_tb(tb)), end='')
                    printe(sformat('{0}: {1}', t.__name__, e))
                    del(tb)
                # @:adhoc_run_time_section:@ on
                pass

        return module

    # @:adhoc_run_time_section:@ off
    # --------------------------------------------------
    # ||:sec:|| Export Tools
    # --------------------------------------------------

    # @:adhoc_run_time_section:@ on
    @classmethod
    def std_source_param(cls, file_=None, source=None): # |:clm:||:api_fi:|
        # @:adhoc_run_time_section:@ off
        '''Setup standard source parameters.

        :returns: tuple ``( file_, source )``

        :param file_: If None, `__file__` is used. If it ends with
          ``.pyc``, it is transformed to ``.py``.
        :param source: If None, the result of :meth:`read_source` is
          used.
        '''
        # @:adhoc_run_time_section:@ on
        if file_ is None:
            file_ = __file__
        if file_.endswith('.pyc'):
            file_ = file_[:-1]
        if source is None:
            source = cls.read_source(file_)
        return (file_, source)

    @classmethod
    def export_source(cls, string, no_remove=False, no_disable=False): # |:clm:|
        # @:adhoc_run_time_section:@ off
        '''
        ============================ =========================
        check for |adhoc_remove|     sections and remove them!
        check for |adhoc_import|     sections and remove them!
        check for |adhoc_unpack|     sections and remove them!
        check for |adhoc_template_v| sections and remove them!
        check for |adhoc_disable|    sections and enable them!
        check for |adhoc_enable|     sections and disable them!
        check for |adhoc_remove_|    section markers and rename them!
        ============================ =========================
        '''
        # @:adhoc_run_time_section:@ on
        string = cls.collapse_macros(string)
        if not no_remove:
            string = cls.remove_sections(string, 'adhoc_remove')
        string = cls.remove_sections(string, 'adhoc_import')
        string = cls.remove_sections(string, 'adhoc_unpack')
        string = cls.remove_sections(string, 'adhoc_template_v')
        if not no_disable:
            string = cls.enable_sections(string, 'adhoc_disable')
            string = cls.disable_sections(string, 'adhoc_enable')
        if not no_remove:
            string = cls.section_tag_rename(string, 'adhoc_remove_', 'adhoc_remove')
        return string

    # @:adhoc_run_time_section:@ off
    # --------------------------------------------------
    # ||:sec:|| Extract Interface
    # --------------------------------------------------

    # @:adhoc_run_time_section:@ on
    @classmethod
    def unpack(cls, file_=None, source=None):                # |:clm:|
        # @:adhoc_run_time_section:@ off
        """Unpack all adhoc'ed files in |adhoc_unpack| sections."""
        # @:adhoc_run_time_section:@ on
        file_, source = cls.std_source_param(file_, source)
        source_sections, unpack_sections = cls.tag_partition(
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
                # @:adhoc_run_time_section:@ off
                sys.stderr.write(''.join((unpack_section, "\n")))
                # @:adhoc_run_time_section:@ on
        cls.extract_warn = sv_extract_warn

    @classmethod
    def extract(cls, file_=None, source=None):               # |:clm:|
        # @:adhoc_run_time_section:@ off
        """Unpack all adhoc'ed files in |adhoc_unpack| sections and
        extract all templates."""
        # @:adhoc_run_time_section:@ on
        cls.unpack(file_, source)
        cls.extract_templates(file_, source, export=True)

    # @:adhoc_run_time_section:@ off
    # --------------------------------------------------
    # ||:sec:|| Export Interface
    # --------------------------------------------------

    # @:adhoc_run_time_section:@ on
    @classmethod
    def export__(cls, mod_name=None, file_=None, mtime=None, # |:clm:||:api_fi:|
                 mode=None, zipped=True, flat=None, source64=None):
        source = cls.unpack_file(source64, zipped=zipped, decode=False)
        # @:adhoc_run_time_section:@ off
        if cls.debug:
            sys.stderr.write(
                ''.join(("# xp: ", cls.__name__, ".export__ for `",
                         file_, "`\n")))
        # @:adhoc_run_time_section:@ on
        if file_ is None:
            return
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

        cls.export_(source, module_file, mtime, mode, flat)

    @classmethod
    def export_(cls, source, file_, mtime, mode, flat=None): # |:clm:|
        cflat = cls.flat
        if flat is None:
            flat = cflat
        cls.flat = flat
        if not flat:
            # extract to export directory
            sv_extract_dir = cls.extract_dir
            cls.extract_dir = cls.export_dir
            cls.extract(file_, source)
            cls.extract_dir = sv_extract_dir

            source_sections, import_sections = cls.tag_partition(
                source, cls.section_tag('adhoc_import'))
            source = cls.export_source(''.join(source_sections))
            export_call = ''.join((cls.__name__, '.export__'))

            xfile = cls.check_xfile(file_, cls.export_dir)
            if xfile is not None:
                cls.write_source(xfile, source, mtime, mode)
                if cls.verbose:
                    list(map(sys.stderr.write,
                             ("# xp: ", cls.__name__, ".export_ for `", file_,
                              "` using `", export_call,"`\n")))

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
                    # @:adhoc_run_time_section:@ off
                    sys.stderr.write(''.join((import_section, "\n")))
                    # @:adhoc_run_time_section:@ on
        else:
            xfile = cls.check_xfile(file_, cls.export_dir)
            if xfile is not None:
                cls.write_source(xfile, source, mtime, mode)
                if cls.verbose:
                    list(map(sys.stderr.write,
                             ("# xp: ", cls.__name__, ".export_ for `", file_,
                              "` using `", export_call,"`\n")))
        cls.flat = cflat

    # @:adhoc_run_time_section:@ off
    default_engine = False

    # @:adhoc_run_time_section:@ on
    @classmethod
    def export(cls, file_=None, source=None):                # |:clm:|
        file_, source = cls.std_source_param(file_, source)
        # @:adhoc_run_time_section:@ off
        # |:todo:| this chaos needs cleanup (cls.import_/cls.export__)
        # @:adhoc_run_time_section:@ on
        sv_import = cls.import_
        cls.import_ = cls.export__

        file_ = os.path.basename(file_)
        # @:adhoc_run_time_section:@ off
        if cls.verbose:
            list(map(sys.stderr.write,
                     ("# xp: ", cls.__name__, ".export for `", file_, "`\n")))
        # @:adhoc_run_time_section:@ on
        cls.export_(source, file_, None, None, False)
        sv_extract_dir = cls.extract_dir
        cls.extract_dir = cls.export_dir
        engine_tag = cls.section_tag('adhoc_run_time_engine')
        engine_source = cls.export_source(
            source, no_remove=True, no_disable=True)
        engine_source = cls.get_named_template(
            None, file_, engine_source, tag=engine_tag, ignore_mark=True)
        # @:adhoc_run_time_section:@ off
        if cls.default_engine and not engine_source:
            state = cls.set_delimiters(('@:', ':@'))
            ah = cls()
            engine_source = ah.prepare_run_time_section()
            engine_source = cls.get_named_template(
                None, file_, engine_source, tag=engine_tag, ignore_mark=True)
            cls.reset_delimiters(state)
        # @:adhoc_run_time_section:@ on
        if engine_source:
            efile = cls.check_xfile('rt_adhoc.py')
            if efile is not None:
                cls.write_source(efile, engine_source)
        cls.extract_dir = sv_extract_dir
        for init_dir in cls.export_need_init:
            if not cls.export_have_init[init_dir]:
                if cls.verbose:
                    list(map(sys.stderr.write,
                             ("# xp: create __init__.py in `", init_dir, "`\n")))
                inf = open(os.path.join(
                    cls.export_dir, init_dir, '__init__.py'), 'w')
                inf.write('')
                inf.close()
        cls.import_ = sv_import

    # @:adhoc_run_time_section:@ off
    # --------------------------------------------------
    # ||:sec:|| Dump Interface (Import/Unpack Substitute)
    # --------------------------------------------------

    # @:adhoc_run_time_section:@ on
    @classmethod
    def dump__(cls, mod_name=None, file_=None, mtime=None, # |:clm:||:api_fi:|
               mode=None, zipped=True, flat=None, source64=None):
        if cls.verbose:
            list(map(sys.stderr.write,
                     ("# xf: ", cls.__name__, ": dumping `", file_, "`\n")))
        source = cls.unpack_file(source64, zipped=zipped, decode=False)
        return source

    @classmethod
    def dump_(cls, dump_section, dump_type=None):            # |:clm:|
        if dump_type is None:
            dump_type = 'adhoc_import'
        if not dump_section:
            return ''
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
            # @:adhoc_run_time_section:@ off
            sys.stderr.write(''.join((dump_section, "\n")))
            # @:adhoc_run_time_section:@ on
        return dump_dict['unpacked']

    @classmethod
    def dump_file(cls, match, file_=None, source=None, tag=None, # |:clm:|
                  is_re=False):
        file_, source = cls.std_source_param(file_, source)
        if tag is None:
            tag = cls.section_tag('(adhoc_import|adhoc_update)', is_re=True)
            is_re = True
        source_sections, dump_sections = cls.tag_partition(
            source, tag, is_re, headline=True)
        dump_call = ''.join((cls.__name__, '.dump_'))
        for dump_section in dump_sections:
            tagged_line = dump_section[0]
            dump_section = dump_section[1]
            tag_arg = cls.section_tag_strip(tagged_line)
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
                # @:adhoc_run_time_section:@ off
                sys.stderr.write(''.join((dump_section, "\n")))
                # @:adhoc_run_time_section:@ on

    # @:adhoc_run_time_section:@ off
    # --------------------------------------------------
    # ||:sec:|| Macros
    # --------------------------------------------------

    # @:adhoc_run_time_section:@ on
    macro_call_delimiters = ('@|:', ':|>')
    # @:adhoc_run_time_section:@ off
    """Macro delimiters"""
    # @:adhoc_run_time_section:@ on
    macro_xdef_delimiters = ('<|:', ':|@')
    # @:adhoc_run_time_section:@ off
    """Macro expansion delimiters"""
    # @:adhoc_run_time_section:@ on
    macros = {}
    # @:adhoc_run_time_section:@ off
    """Macros"""
    # @:adhoc_run_time_section:@ on

    @classmethod
    def expand_macros(cls, source, macro_call_dlm=None, macro_xdef_dlm=None): # |:clm:|
        # @:adhoc_run_time_section:@ off
        """
        >>> AdHoc.macros['uc_descr_end'] = (
        ...     '# o:' 'adhoc_template:>\\n'
        ...     '# <:' 'adhoc_uncomment:>\\n'
        ...     )

        >>> macro_source = '# ' + AdHoc.adhoc_tag('uc_descr_end', AdHoc.macro_call_delimiters) + '\\n'
        >>> ign = sys.stdout.write(macro_source) #doctest: +ELLIPSIS
        # @|:uc_descr_end...:|>

        >>> ign = sys.stdout.write(AdHoc.expand_macros(macro_source)) #doctest: +ELLIPSIS
        # <|:adhoc_macro_call...:|@
        # @|:uc_descr_end...:|>
        # <|:adhoc_macro_call...:|@
        # <|:adhoc_macro_expansion...:|@
        # o:adhoc_template...:>
        # <:adhoc_uncomment...:>
        # <|:adhoc_macro_expansion...:|@

        """
        # @:adhoc_run_time_section:@ on
        if macro_call_dlm is None:
            macro_call_dlm = cls.macro_call_delimiters
        if macro_xdef_dlm is None:
            macro_xdef_dlm = cls.macro_xdef_delimiters
        import re
        for macro_name, macro_expansion in cls.macros.items():
            macro_tag = cls.adhoc_tag(macro_name, macro_call_dlm, False)
            macro_tag_rx = cls.adhoc_tag(macro_name, macro_call_dlm, True)
            macro_call = ''.join(('# ', macro_tag, '\n'))
            macro_call_rx = ''.join(('^[^\n]*', macro_tag_rx, '[^\n]*\n'))
            mc_tag = ''.join(('# ', cls.adhoc_tag('adhoc_macro_call', macro_xdef_dlm, False), "\n"))
            mx_tag = ''.join(('# ', cls.adhoc_tag('adhoc_macro_expansion', macro_xdef_dlm, False), "\n"))
            xdef = ''.join((
                mc_tag,
                macro_call,
                mc_tag,
                mx_tag,
                macro_expansion,
                mx_tag,
                ))
            rx = re.compile(macro_call_rx, re.M)
            source = rx.sub(xdef, source)
        return source

    @classmethod
    def has_expanded_macros(cls, source, macro_xdef_dlm=None): # |:clm:|
        # @:adhoc_run_time_section:@ off
        """
        """
        # @:adhoc_run_time_section:@ on
        if macro_xdef_dlm is None:
            macro_xdef_dlm = cls.macro_xdef_delimiters
        mx_tag = cls.adhoc_tag('adhoc_macro_expansion', macro_xdef_dlm, False)
        me_count = len(cls.tag_lines(source, mx_tag))
        return me_count > 0

    @classmethod
    def activate_macros(cls, source, macro_call_dlm=None, macro_xdef_dlm=None): # |:clm:|
        # @:adhoc_run_time_section:@ off
        """
        """
        # @:adhoc_run_time_section:@ on
        if macro_xdef_dlm is None:
            macro_xdef_dlm = cls.macro_xdef_delimiters
        if not cls.has_expanded_macros(source, macro_xdef_dlm):
            source = cls.expand_macros(source, macro_call_dlm, macro_xdef_dlm)
        sv = cls.set_delimiters (macro_xdef_dlm)
        source = cls.remove_sections(source, 'adhoc_macro_call')
        source = cls.section_tag_remove(source, 'adhoc_macro_expansion')
        cls.reset_delimiters(sv)
        return source

    @classmethod
    def collapse_macros(cls, source, macro_xdef_dlm=None):   # |:clm:|
        # @:adhoc_run_time_section:@ off
        """
        """
        # @:adhoc_run_time_section:@ on
        if macro_xdef_dlm is None:
            macro_xdef_dlm = cls.macro_xdef_delimiters
        if cls.has_expanded_macros(source, macro_xdef_dlm):
            sv = cls.set_delimiters (macro_xdef_dlm)
            source = cls.section_tag_remove(source, 'adhoc_macro_call')
            source = cls.remove_sections(source, 'adhoc_macro_expansion')
            cls.reset_delimiters(sv)
        return source

    # @:adhoc_run_time_section:@ off
    # --------------------------------------------------
    # ||:sec:|| Template Interface
    # --------------------------------------------------

    # @:adhoc_run_time_section:@ on
    @classmethod
    def std_template_param(cls, file_=None, source=None,     # |:clm:|
                           tag=None, is_re=False, all_=False):
        # @:adhoc_run_time_section:@ off
        '''Setup standard template parameters.

        :param tag: If None, section tag `adhoc_template(_v)?` is
          used.

        See :meth:`std_source_param` for `file_` and `source`.
        '''
        # @:adhoc_run_time_section:@ on
        file_, source = cls.std_source_param(file_, source)
        if tag is None:
            is_re=True
            if all_:
                tag = cls.section_tag('adhoc_(template(_v)?|import|unpack)', is_re=is_re)
            else:
                tag = cls.section_tag('adhoc_template(_v)?', is_re=is_re)
        source = cls.activate_macros(source)
        return (file_, source, tag, is_re)

    @classmethod
    def get_templates(cls, file_=None, source=None,          # |:clm:|
                      tag=None, is_re=False,
                      ignore_mark=False, all_=False):
        # @:adhoc_run_time_section:@ off
        '''Extract templates matching section tag.

        :param ignore_mark: If True, all templates are mapped to
          standard output name ``-``.
        :param tag: If None, `adhoc_template` is used.
        '''
        # @:adhoc_run_time_section:@ on
        file_, source, tag, is_re = cls.std_template_param(
            file_, source, tag, is_re, all_)
        source = cls.enable_sections(source, 'adhoc_uncomment')
        source = cls.indent_sections(source, 'adhoc_indent')
        source_sections, template_sections = cls.tag_partition(
            source, tag, is_re=is_re, headline=True)
        templates = {}
        for template_section in template_sections:
            tagged_line = template_section[0]
            section = template_section[1]
            tag, tag_arg = cls.section_tag_parse(tagged_line)
            if not tag_arg:
                tag_arg = '-'
            if tag_arg in cls.template_process_hooks:
                section = cls.template_process_hooks[tag_arg](cls, section, tag, tag_arg)
            if ignore_mark:
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
    def template_list(cls, file_=None, source=None,          # |:clm:|
                      tag=None, is_re=False, all_=False):
        # @:adhoc_run_time_section:@ off
        """Sorted list of templates.

        See :meth:`std_template_param` for `file_`, `source`, `tag`, `is_re`.

        .. @:adhoc_disable:@

        >>> for tpl in AdHoc.template_list():
        ...     printf(tpl)
        -
        README.txt
        -col-param-closure
        doc/USE_CASES.txt
        doc/index.rst
        -max-width-class
        -rst-to-ascii
        -test

        >>> for tpl in AdHoc.template_list(all_=True):
        ...     printf(strclean(tpl))
        ('-', 'adhoc_template')
        ('README.txt', 'adhoc_template')
        ('-col-param-closure', 'adhoc_template')
        ('doc/USE_CASES.txt', 'adhoc_template')
        ('doc/index.rst', 'adhoc_template')
        ('-max-width-class', 'adhoc_template')
        ('-rst-to-ascii', 'adhoc_template')
        ('-test', 'adhoc_template')

        .. @:adhoc_disable:@
        """
        # @:adhoc_run_time_section:@ on
        file_, source, tag, is_re = cls.std_template_param(
            file_, source, tag, is_re, all_)
        templates = cls.get_templates(file_, source, tag, is_re, all_=all_)
        if all_:
            templates.update([(k, ('', v)) for k, v in cls.extra_templates])
            result = list(sorted(
                [(k, v[1]) for k, v in templates.items()],
                key=lambda kt: '||'.join((
                    kt[1],
                    (((not (kt[0].startswith('-') or kt[0].startswith('!')))
                      and (kt[0]))
                     or (kt[0][1:]))))))
        else:
            templates.update(filter(
                lambda tdef: (tdef[1] == 'adhoc_template'
                              or tdef[1] == 'adhoc_template_v'),
                cls.extra_templates))
            result = list(sorted(
                templates.keys(),
                key=lambda kt: '||'.join((
                    (((not (kt.startswith('-') or kt.startswith('!')))
                      and (kt)) or (kt[1:]))))))
        return result

    # @:adhoc_run_time_section:@ off
    # @:adhoc_template:@ -col-param-closure
    # @:adhoc_run_time_section:@ on
    @classmethod
    def col_param_closure(cls):                              # |:clm:|
        # @:adhoc_run_time_section:@ off
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
        ...     (((paddings[indx] is None) and (col))
        ...      or ((paddings[indx][:int((mws[indx]-len(col))/2)]
        ...           + col + paddings[indx])[:mws[indx]]))
        ...     for indx, col in enumerate(cols)]
        >>> pad_cols = lambda cols: [
        ...     (((paddings[indx] is None) and (col))
        ...      or ((col + paddings[indx])[:mws[indx]]))
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
        def set_(col):                                       # |:clo:|
            lc = len(col)
            if mw[0] < lc:
                mw[0] = lc
                mw[1] = " " * lc
                mw[2] = "=" * lc
            return col
        def get_():                                          # |:clo:|
            return mw
        return set_, get_
    # @:adhoc_run_time_section:@ off
    # @:adhoc_template:@ -col-param-closure
    # @:adhoc_run_time_section:@ on

    @classmethod
    def template_table(cls, file_=None, source=None,         # |:clm:|
                       tag=None, is_re=False):
        # @:adhoc_run_time_section:@ off
        '''Table of template commands.

        See :meth:`std_template_param` for `file_`, `source`, `tag`, `is_re`.
        '''
        # @:adhoc_run_time_section:@ on
        file_, source, tag, is_re = cls.std_template_param(
            file_, source, tag, is_re, all_=True)
        # Parse table
        table = []
        tpl_arg_name = (lambda t: (((not (t.startswith('-') or t.startswith('!'))) and (t)) or (t[1:])))
        col_param = [cls.col_param_closure() for i in range(3)]
        table.append((col_param[0][0]('Command'), col_param[1][0]('Template'), col_param[2][0]('Type')))
        table.extend([(col_param[0][0](''.join((
            os.path.basename(file_), ' --template ',
            tpl_arg_name(t[0]))).rstrip()),
                       col_param[1][0](''.join(('# ', t[0])).rstrip()),
                       col_param[2][0](''.join((t[1])).rstrip()),
                       )
                      for t in cls.template_list(file_, source, tag, is_re, all_=True)])
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
    def get_named_template(cls, name=None, file_=None, source=None, # |:clm:|
                           tag=None, is_re=False, ignore_mark=False):
        # @:adhoc_run_time_section:@ off
        '''Extract templates matching section tag and name.

        :param name: Template name. If None, standard output name ``-`` is used.
        :param tag: If None, `adhoc_template(_v)?` is used.
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
        file_, source, tag, is_re = cls.std_template_param(
            file_, source, tag, is_re, all_=True)
        templates = cls.get_templates(
            file_, source, tag, is_re=is_re, ignore_mark=ignore_mark, all_=True)
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
    def extract_templates(cls, file_=None, source=None,      # |:clm:|
                          tag=None, is_re=False, ignore_mark=False,
                          export=False):
        # @:adhoc_run_time_section:@ off
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
        ...     tag=AdHoc.section_tag("adhoc_template_check"))
                A template ...
                continued
                Another interleaved

        >>> rt_section = AdHoc.get_templates(
        ...     __file__, None,
        ...     tag=AdHoc.section_tag("adhoc_run_time_section"),
        ...     ignore_mark=True)
        >>> rt_section = ''.join(rt_section.values())

        .. >>> printf(rt_section)
        '''
        # @:adhoc_run_time_section:@ on
        file_, source, tag, is_re = cls.std_template_param(
            file_, source, tag, is_re)
        templates = cls.get_templates(
            file_, source, tag, is_re=is_re, ignore_mark=ignore_mark)
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

    # @:adhoc_run_time_section:@ off

    # --------------------------------------------------
    # ||:sec:|| COMPILER DATA
    # --------------------------------------------------

    # tags are generated from symbols on init
    run_time_flag = None                      # line
    import_flag = None                        # line
    include_flag = None                       # line
    verbatim_flag = None                      # line
    compiled_flag = None                      # line
    run_time_class_flag = None                # line

    rt_engine_section_tag = None              # section
    indent_section_tag = None                 # section
    uncomment_section_tag = None              # section
    enable_section_tag = None                 # section
    disable_section_tag = None                # section
    remove_section_tag = None                 # section
    import_section_tag = None                 # section
    unpack_section_tag = None                 # section
    template_v_section_tag = None             # section
    template_section_tag = None               # section
    run_time_section_tag = None               # section

    run_time_section = None

    run_time_flag_symbol = 'adhoc_run_time'   # line
    import_flag_symbol = 'adhoc'              # line
    include_flag_symbol = 'adhoc_include'     # line
    verbatim_flag_symbol = 'adhoc_verbatim'   # line
    compiled_flag_symbol = 'adhoc_compiled'   # line
    run_time_class_symbol = 'adhoc_run_time_class' # line

    rt_engine_section_symbol = 'adhoc_run_time_engine' # section
    indent_section_symbol = 'adhoc_indent'             # section
    uncomment_section_symbol = 'adhoc_uncomment'       # section
    enable_section_symbol = 'adhoc_enable'             # section
    disable_section_symbol = 'adhoc_disable'           # section
    remove_section_symbol = 'adhoc_remove'             # section
    import_section_symbol = 'adhoc_import'             # section
    unpack_section_symbol = 'adhoc_unpack'             # section
    template_v_section_symbol = 'adhoc_template_v'     # section
    template_section_symbol = 'adhoc_template'         # section
    run_time_section_symbol = 'adhoc_run_time_section' # section

    run_time_class_prefix = 'Rt'
    import_function = 'AdHoc.import_'
    modules = {}
    compiling = []

    file_include_template = (                             # |:api_fi:|
        "{ind}"
        "# {stg}\n{ind}"
        "{rtp}{ahc}("
        "{mod},"
        " file_={fnm},\n{ina}"
        " mtime={mtm},"
        " mode={fmd},\n{ina}"
        " zipped={zip},"
        " flat={flt},"
        " source64=\n"
        "{src}"
        ")\n{ind}"
        "# {etg}\n"
        )

    # --------------------------------------------------
    # ||:sec:|| Setup
    # --------------------------------------------------

    def __init__(self):                                      # |:mth:|
        self.modules = {}
        self.compiling = []
        self.setup_tags()
        self.run_time_section = self.prepare_run_time_section().rstrip() + '\n'

    @classmethod
    def setup_tags(cls):                                     # |:mth:|
        cls.run_time_flag = cls.line_tag(cls.run_time_flag_symbol)
        cls.import_flag = cls.line_tag(cls.import_flag_symbol)
        cls.verbatim_flag = cls.line_tag(cls.verbatim_flag_symbol)
        cls.include_flag = cls.line_tag(cls.include_flag_symbol)
        cls.compiled_flag = cls.line_tag(cls.compiled_flag_symbol)
        cls.run_time_class_flag = cls.line_tag(cls.run_time_class_symbol)

        cls.rt_engine_section_tag = cls.section_tag(cls.rt_engine_section_symbol)
        cls.indent_section_tag = cls.section_tag(cls.indent_section_symbol)
        cls.uncomment_section_tag = cls.section_tag(cls.uncomment_section_symbol)
        cls.enable_section_tag = cls.section_tag(cls.enable_section_symbol)
        cls.disable_section_tag = cls.section_tag(cls.disable_section_symbol)
        cls.remove_section_tag = cls.section_tag(cls.remove_section_symbol)
        cls.import_section_tag = cls.section_tag(cls.import_section_symbol)
        cls.unpack_section_tag = cls.section_tag(cls.unpack_section_symbol)
        cls.template_v_section_tag = cls.section_tag(cls.template_v_section_symbol)
        cls.template_section_tag = cls.section_tag(cls.template_section_symbol)
        cls.run_time_section_tag = cls.section_tag(
            cls.run_time_section_symbol)

    # --------------------------------------------------
    # ||:sec:|| Tools
    # --------------------------------------------------

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

    # --------------------------------------------------
    # ||:sec:|| Run-Time Section
    # --------------------------------------------------

    @classmethod
    def adhoc_run_time_sections_from_string(cls, string, symbol): # |:clm:|
        tag = sformat('(#[ \t\r]*)?{0}', cls.section_tag(symbol, is_re=True))
        def_sections = cls.tag_sections(string, tag, is_re=True)
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
                sformat('# {0}\n', cls.remove_section_tag),
                sformat('# {0}\n', cls.rt_engine_section_tag),
                sformat('# -*- coding: utf-8 -*-\n'),
                sformat('# {0} {1}\n', cls.compiled_flag,
                                     datetime.datetime.now(),
                                     # |:todo:| add input filename
                                     ),
                prolog,
                ''.join(def_sections),
                epilog,
                sformat('# {0}\n', cls.rt_engine_section_tag),
                sformat('# {0}\n', cls.remove_section_tag),
                ))
        return def_

    @classmethod
    def prepare_run_time_section(cls):                       # |:mth:|
        rts = cls.adhoc_get_run_time_section(
            cls.run_time_section_symbol)
        rtc_sections = cls.tag_split(
            rts, cls.run_time_class_flag)
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
                              + cls.run_time_class_prefix
                              + blob[mo.end(0):])
                        done = True
                    else:
                        #transform.append(use_next)
                        pass
                use_next = False
            transform.append(blob)
        transform.append(sformat('# {0}\n', cls.remove_section_tag))
        transform.append(sformat('# {0}\n', cls.rt_engine_section_tag))
        transform.append(sformat('# {0}\n', cls.rt_engine_section_tag))
        transform.append(sformat('# {0}\n', cls.remove_section_tag))
        rts = ''.join(transform)
        if not done:
            raise AdHocError(
                sformat('run-time class(tag) `{0}` not found in:\n{1}',
                        cls.run_time_class_flag, rts))
        return rts

    # --------------------------------------------------
    # ||:sec:|| Internal Includer (verbatim)
    # --------------------------------------------------

    def verbatim_(self, string, name=None):                  # |:mth:|
        '''Entry point for verbatim inclusion.

        :returns: string with verbatim included files.

        :param string: input string, with |adhoc_verbatim| flags.
        :param name: ignored. (API compatibility with
          :meth:`AdHoc.compile_`).

        .. note:: double commented flags, e.g. ``##``
           |adhoc_verbatim|, are ignored.

        .. \\|:here:|

        >>> section = """\\
        ... some
        ...     @:""" """adhoc_verbatim:@ {flags} my_verbatim{from_}
        ... text\\
        ... """

        >>> adhoc = AdHoc()

        **Non-existent File**

        >>> sv_quiet = AdHoc.quiet
        >>> AdHoc.quiet = True
        >>> source = adhoc.verbatim_(sformat(section, flags="-2#", from_=""))
        >>> printf(source) #doctest: +ELLIPSIS
        some
            @:adhoc_verbatim... -2# my_verbatim
        text
        >>> AdHoc.quiet = sv_quiet

        **Empty File**

        >>> source = adhoc.verbatim_(sformat(section, flags="", from_=" from /dev/null"))
        >>> printf(source) #doctest: +ELLIPSIS
        some
            @:adhoc_verbatim...  my_verbatim from /dev/null
            # @:adhoc_remove...
            # @:adhoc_indent... -4
            # @:adhoc_template_v... my_verbatim
            # @:adhoc_template_v...
            # @:adhoc_indent...
            # @:adhoc_remove...
        text

        **Empty file, with negative indent, commented**

        >>> source = adhoc.verbatim_(sformat(section, flags="-2#", from_=" from /dev/null"))
        >>> printf(source) #doctest: +ELLIPSIS
        some
            @:adhoc_verbatim... -2# my_verbatim from /dev/null
          # @:adhoc_remove...
          # @:adhoc_uncomment...
          # @:adhoc_indent... -2
          # @:adhoc_template_v... my_verbatim
          # @:adhoc_template_v...
          # @:adhoc_indent...
          # @:adhoc_uncomment...
          # @:adhoc_remove...
        text

        **Empty file, with overflowing negative indent, commented**

        >>> source = adhoc.verbatim_(sformat(section, flags="-8#", from_=" from /dev/null"))
        >>> printf(source) #doctest: +ELLIPSIS
        some
            @:adhoc_verbatim... -8# my_verbatim from /dev/null
        # @:adhoc_remove...
        # @:adhoc_uncomment...
        # @:adhoc_template_v... my_verbatim
        # @:adhoc_template_v...
        # @:adhoc_uncomment...
        # @:adhoc_remove...
        text

        **Existing file, without newline at end of file, commented.**

        >>> mvf = open("my_verbatim", "w")
        >>> ign = mvf.write("no end of line")
        >>> mvf.close()
        >>> source = adhoc.verbatim_(sformat(section, flags="-4#", from_=""))
        >>> printf(source) #doctest: +ELLIPSIS
        some
            @:adhoc_verbatim... -4# my_verbatim
        # @:adhoc_remove...
        # @:adhoc_uncomment...
        # @:adhoc_template_v... my_verbatim
        # no end of line
        # @:adhoc_template_v...
        # @:adhoc_uncomment...
        # @:adhoc_remove...
        text

        **Existing file, with extra newline at end of file, commented.**

        >>> mvf = open("my_verbatim", "w")
        >>> ign = mvf.write("extra end of line\\n\\n")
        >>> mvf.close()
        >>> source = adhoc.verbatim_(sformat(section, flags="-4#", from_=""))
        >>> printf(source) #doctest: +ELLIPSIS
        some
            @:adhoc_verbatim... -4# my_verbatim
        # @:adhoc_remove...
        # @:adhoc_uncomment...
        # @:adhoc_template_v... my_verbatim
        # extra end of line
        <BLANKLINE>
        # @:adhoc_template_v...
        # @:adhoc_uncomment...
        # @:adhoc_remove...
        text

        **Existing file, without newline at end of file, not commented.**

        >>> mvf = open("my_verbatim", "w")
        >>> ign = mvf.write("no end of line")
        >>> mvf.close()
        >>> source = adhoc.verbatim_(sformat(section, flags="-4", from_=""))
        >>> printf(source) #doctest: +ELLIPSIS
        some
            @:adhoc_verbatim... -4 my_verbatim
        # @:adhoc_remove...
        # @:adhoc_template_v... my_verbatim
        no end of line
        # @:adhoc_template_v...
        # @:adhoc_remove...
        text

        **Existing file, with extra newline at end of file, not commented.**

        >>> mvf = open("my_verbatim", "w")
        >>> ign = mvf.write("extra end of line\\n\\n")
        >>> mvf.close()
        >>> source = adhoc.verbatim_(sformat(section, flags="", from_=""))
        >>> printf(source) #doctest: +ELLIPSIS
        some
            @:adhoc_verbatim... my_verbatim
            # @:adhoc_remove...
            # @:adhoc_indent:@ -4
            # @:adhoc_template_v... my_verbatim
            extra end of line
        <BLANKLINE>
            # @:adhoc_template_v...
            # @:adhoc_indent:@
            # @:adhoc_remove...
        text

        **Existing file, but override with source /dev/null.**

        >>> source = adhoc.verbatim_(sformat(section, flags="/dev/null as", from_=""))
        >>> printf(source) #doctest: +ELLIPSIS
        some
            @:adhoc_verbatim... /dev/null as my_verbatim
            # @:adhoc_remove...
            # @:adhoc_indent... -4
            # @:adhoc_template_v... my_verbatim
            # @:adhoc_template_v...
            # @:adhoc_indent...
            # @:adhoc_remove...
        text

        **Existing file, override with non-existing source /not-here/.**

        >>> if os.path.exists("not-here"):
        ...     os.unlink("not-here")
        >>> source = adhoc.verbatim_(sformat(section, flags="not-here as", from_=""))
        >>> printf(source) #doctest: +ELLIPSIS
        some
            @:adhoc_verbatim... not-here as my_verbatim
            # @:adhoc_remove...
            # @:adhoc_indent... -4
            # @:adhoc_template_v... my_verbatim
            extra end of line
        <BLANKLINE>
            # @:adhoc_template_v...
            # @:adhoc_indent...
            # @:adhoc_remove...
        text

        >>> os.unlink("my_verbatim")
        '''
        m = 'is: '

        import datetime

        # # check for @: adhoc_compiled :@
        # adhoc_compiled_lines = self.tag_lines(
        #     string, self.line_tag('adhoc_compiled'))
        # if len(adhoc_compiled_lines) > 0:
        #     sys.stderr.write(sformat(
        #         '{0}{1}' 'warning: {2} already AdHoc\'ed `{3}`\n',
        #         dbg_comm, m, name, adhoc_compiled_lines[0].rstrip()))
        #     return string

        # handle @: adhoc_verbatim :@
        result = []
        verbatim_cmd_parts = self.tag_split(string, self.verbatim_flag)
        for part in verbatim_cmd_parts:
            verbatim_def = part[1]
            result.append(verbatim_def)
            if part[0]:
                # skip commented verbatim includes
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
                    verbatim_spec2 = re.split('\\s+as\\s+', verbatim_spec)
                    default = None
                    source = None
                    output = None
                    flags = None
                    if len(verbatim_spec1) > 1:
                        output = verbatim_spec1[0]
                        default = verbatim_spec1[1]
                        fields = re.split('\\s+', output, 1)
                        if len(fields) > 1:
                            flags = fields[0]
                            output = fields[1]
                        else:
                            flags = ''
                        source = output
                    if len(verbatim_spec2) > 1:
                        source = verbatim_spec2[0]
                        output = verbatim_spec2[1]
                        fields = re.split('\\s+', source, 1)
                        if len(fields) > 1:
                            flags = fields[0]
                            source = fields[1]
                        else:
                            flags = ''
                        default = output
                    if flags is None:
                        source = verbatim_spec
                        fields = re.split('\\s+', source, 1)
                        if len(fields) > 1:
                            flags = fields[0]
                            source = fields[1]
                        else:
                            flags = ''
                            source = fields[0]
                        default = source
                        output = source
                    verbatim_specs.append([flags, source, default, output])

                for verbatim_spec in verbatim_specs:
                    vflags = verbatim_spec.pop(0)
                    ifile = verbatim_spec.pop()
                    found = False
                    for lfile in verbatim_spec:
                        lfile = os.path.expanduser(lfile)
                        blfile = lfile
                        for include_dir in self.include_path:
                            if not os.path.exists(lfile):
                                if not (os.path.isabs(blfile)):
                                    lfile = os.path.join(include_dir, blfile)
                                    continue
                            break
                        if os.path.exists(lfile):
                            stat = os.stat(lfile)
                            mtime = datetime.datetime.fromtimestamp(
                                stat.st_mtime)
                            mode = stat.st_mode

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
                                tag = self.indent_section_tag
                                start_tags.insert(
                                    0, ''.join((tag, ' ', str(-tindent))))
                                end_tags.append(tag)
                                prefix.insert(0, ' ' * tindent)
                                tag_prefix.insert(0, ' ' * tindent)

                            if '#' in vflags:
                                tag = self.uncomment_section_tag
                                start_tags.insert(0, tag)
                                end_tags.append(tag)
                                exp_source, hl = self.disable_transform(exp_source)

                            tag = self.remove_section_tag
                            start_tags.insert(0, tag)
                            end_tags.append(tag)

                            tag = self.section_tag('adhoc_template_v')
                            start_tags.append(''.join((tag, ' ', ifile)))
                            end_tags.insert(0,tag)

                            prefix = ''.join(prefix)
                            tag_prefix = ''.join(tag_prefix)
                            if prefix and exp_source:
                                if exp_source.endswith('\n'):
                                    exp_source = exp_source[:-1]
                                exp_source = re.sub('^(?m)', prefix, exp_source)
                            if exp_source and not exp_source.endswith('\n'):
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
                        list(map(sys.stderr.write,
                                 ("# if: ", self.__class__.__name__,
                                  ": warning verbatim file `", ifile,
                                  "` not found from `",
                                  ', '.join(verbatim_spec), "`\n")))
        #adhoc_dump_list(result)
        return ''.join(result)

    # --------------------------------------------------
    # ||:sec:|| Internal Includer (packed)
    # --------------------------------------------------

    def include_(self, string, name=None, zipped=True, flat=None): # |:mth:|
        '''Entry point for inclusion.

        :returns: string with packed included files.

        :param string: input string, with |adhoc_include| flags.
        :param name: ignored. (API compatibility with
          :meth:`AdHoc.compile_`).
        :param zipped: if True, :mod:`gzip` included files.

        .. note:: double commented flags, e.g. ``##``
           |adhoc_include|, are ignored.

        .. \\|:here:|

        >>> section = """\\
        ... some
        ... @:""" """adhoc_include:@ Makefile
        ... text\\
        ... """

        .. @:adhoc_disable:@

        >>> adhoc = AdHoc()
        >>> source = adhoc.include_(section)
        >>> printf(source) #doctest: +ELLIPSIS
        some
        @:adhoc_include... Makefile
        # @:adhoc_unpack...
        RtAdHoc.unpack_(None, file_='Makefile',
            mtime='...', mode=...,
            zipped=True, flat=None, source64=
        ...
        # @:adhoc_unpack...
        text

        .. @:adhoc_disable:@
        '''
        m = 'is: '

        import datetime

        # # check for @: adhoc_compiled :@
        # adhoc_compiled_lines = self.tag_lines(
        #     string, self.line_tag('adhoc_compiled'))
        # if len(adhoc_compiled_lines) > 0:
        #     sys.stderr.write(sformat(
        #         '{0}{1}' 'warning: {2} already AdHoc\'ed `{3}`\n',
        #         dbg_comm, m, name, adhoc_compiled_lines[0].rstrip()))
        #     return string

        # handle @: adhoc_include :@
        result = []
        include_cmd_sections = self.tag_split(string, self.include_flag)
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
                    include_spec1 = re.split('\\s+from\\s+', include_spec)
                    include_spec2 = re.split('\\s+as\\s+', include_spec)
                    default = None
                    source = None
                    output = None
                    if len(include_spec1) > 1:
                        output = include_spec1[0]
                        default = include_spec1[1]
                        source = output
                    if len(include_spec2) > 1:
                        source = include_spec2[0]
                        output = include_spec2[1]
                        default = output
                    if source is None:
                        source = include_spec
                        output = source
                        default = source
                    include_specs.append([source, default, output])

                for include_spec in include_specs:
                    ifile = include_spec.pop()
                    found = False
                    for lfile in include_spec:
                        lfile = os.path.expanduser(lfile)
                        blfile = lfile
                        for include_dir in self.include_path:
                            if not os.path.exists(lfile):
                                if not (os.path.isabs(blfile)):
                                    lfile = os.path.join(include_dir, blfile)
                                    continue
                            break
                        if os.path.exists(lfile):
                            stat = os.stat(lfile)
                            mtime = datetime.datetime.fromtimestamp(
                                stat.st_mtime)
                            mode = stat.st_mode

                            exp_source = self.read_source(lfile, decode=False)
                            source64 = self.pack_file(exp_source, zipped)
                            output = self.strquote(source64, indent)
                            file_include_args = dict([    # |:api_fi:|
                                ('ind', indent),
                                ('ina', ''.join((indent, "   "))),
                                ('stg', ''.join((self.unpack_section_tag, ' !', ifile))),
                                ('etg', self.unpack_section_tag),
                                ('rtp', self.run_time_class_prefix),
                                ('ahc', 'AdHoc.unpack_'),
                                ('mod', 'None'),
                                ('fnm', repr(str(ifile))),
                                ('mtm', (((mtime is not None)
                                          and repr(mtime.isoformat()))
                                         or repr(mtime))),
                                ('fmd', (mode is not None and sformat('int("{0:o}", 8)', mode)) or mode),
                                ('zip', zipped),
                                ('flt', flat),
                                ('src', output.rstrip()),
                            ])
                            output = sformat(
                                self.file_include_template,
                                **file_include_args
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
                        list(map(sys.stderr.write,
                                 ("# if: ", self.__class__.__name__,
                                  ": warning include file `",
                                  ifile, "` not found from `",
                                  ', '.join(include_spec), "`\n")))
        #adhoc_dump_list(result)
        return ''.join(result)

    # --------------------------------------------------
    # ||:sec:|| Internal Compiler
    # --------------------------------------------------

    def encode_module_(                                      # |:mth:|
        self, module, for_=None, indent='', zipped=True, flat=None, forced=None):
        m = 'gm: '

        if for_ is None:
            for_ = self.import_function

        if forced is None:
            forced = self.forced

        module = self.module_setup(module)
        module_name = module.__name__

        # no multiple occurences
        if (not forced
            and (module_name in self.modules
                 or module_name in self.compiling)):
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
                parent_module, for_, indent, zipped, flat, forced))

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
            return ''.join(result)

        # recursive!
        exp_source = self.compile_(source, module_file, for_, zipped, forced)
        source64 = self.pack_file(exp_source, zipped)
        output = self.strquote(source64, indent)

        mtime = module.__adhoc__.mtime
        mode = module.__adhoc__.mode
        # |:todo:| make Rt prefix configurable
        file_include_args = dict([                        # |:api_fi:|
            ('ind', indent),
            ('ina', ''.join((indent, "   "))),
            ('stg', ''.join((self.import_section_tag, ' !', module_name))),
            ('etg', self.import_section_tag),
            ('rtp', self.run_time_class_prefix),
            ('ahc', for_),
            ('mod', repr(module.__name__)),
            ('fnm', (((module_file is not None)
                      and repr(str(os.path.relpath(module_file))))
                     or module_file)),
            ('mtm', (((mtime is not None)
                      and repr(mtime.isoformat()))
                     or repr(mtime))),
            ('fmd', (mode is not None and sformat('int("{0:o}", 8)', mode)) or mode),
            ('zip', zipped),
            ('src', output.rstrip()),
            ('flt', flat),
            ])
        output = sformat(
            self.file_include_template,
            **file_include_args
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
                 zipped=True, forced=None):
        '''Entry point for compilation.

        :returns: string with fully compiled adhoc source. Includes
          run-time class, imports, packed includes, verbatim includes,
          enabled/disabled sections.

        :param string: input string, with |adhoc| flags.
        :param name: for messages.
        :param for_: :class:`RtAdHoc` method call.
        :param zipped: if True, :mod:`gzip` included files.

        .. note:: for |adhoc|, commented lines, e.g.
           ``# import module # @:``\\ ``adhoc:@``, are ignored.

        .. \\|:here:|
        '''
        m = 'cs: '
        if name is None:
            name = repr(string[:50])
        # check for @: adhoc_compiled :@
        string = self.expand_macros(string)
        adhoc_compiled_lines = self.tag_lines(
            string, self.line_tag('adhoc_compiled'))
        if len(adhoc_compiled_lines) > 0:
            if not self.quiet:
                list(map(sys.stderr.write,
                         ('# ', m,  'warning: ', name, ' already AdHoc\'ed `',
                          adhoc_compiled_lines[0].rstrip(), '`\n',)))
            return string

        # check for @: adhoc_self :@ (should not be taken from any templates)
        adhoc_self_tag = self.line_tag('adhoc_self')
        adhoc_self_lines = self.tag_lines(
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

        # check for @: adhoc_remove :@
        string = self.section_tag_rename(string, 'adhoc_remove', 'adhoc_remove_')

        # check for @: adhoc_verbatim :@ (templates can define the run-time flag, includes, imports)
        string = self.verbatim_(string, name)

        # search for @: adhoc_run_time :@ and put run-time section there!
        result = []
        ah_run_time_sections = self.tag_split(
            string, self.line_tag(self.run_time_flag_symbol))
        good = False
        for section in ah_run_time_sections:
            config_def = section[1]
            if not good and section[0]:
                # ignore double commented tagged lines
                if not re.match('\\s*#\\s*#', config_def):
                    config_def = sformat('{0}{1}',
                        config_def, self.run_time_section)
                    good = True
            result.append(config_def)
        string = ''.join(result)

        # check for @: adhoc_include :@
        string = self.include_(string, name, zipped)

        # handle @: adhoc :@ imports
        result = []
        import_cmd_sections = self.tag_split(string, self.import_flag)
        if not good and len(import_cmd_sections) > 1:
            adhoc_dump_sections(import_cmd_sections)
            raise AdHocError(sformat('{0} not found',
                    self.line_tag(self.run_time_flag_symbol)))
        for section in import_cmd_sections:
            import_def = section[1]
            if section[0]:
                # skip commented imports
                if re.match('\\s*#', import_def):
                    if self.verbose:
                        printe(sformat(
                            '{0}{1}Skipping disabled `{2}`',
                            dbg_comm, m, import_def.rstrip()))
                    result.append(import_def)
                    continue
                import_args = self.line_tag_strip(import_def, self.import_flag_symbol)
                module = ''
                mo = re.match(
                    '(\\s*)from\\s+([a-zA-Z_][.0-9a-zA-Z_]*)\\s+'
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
                    module_flat = ((('flat' in import_args.lower().split()) and (True)) or (None))
                    module_flat = ((('full' in import_args.lower().split()) and (False)) or (module_flat))
                    module_forced = ((('force' in import_args.lower().split()) and (True)) or (forced))
                    source = self.encode_module_(module, for_, indent, zipped, module_flat, module_forced)
                    import_def = sformat('{0}{1}',source, import_def)
                else:
                    if self.verbose:
                        list(map(sys.stderr.write,
                                 ('# ', m, 'warning: no import found! `',
                                  import_def.rstrip(), '`\n')))
            result.append(import_def)
        string = ''.join(result)

        # These are last, to avoid enabling/disabling the wrong imports etc.

        # check for @: adhoc_enable :@
        string = self.enable_sections(string, 'adhoc_enable')
        # check for @: adhoc_disable :@
        string = self.disable_sections(string, 'adhoc_disable')

        #adhoc_dump_list(result)
        return string

    # --------------------------------------------------
    # ||:sec:|| User API
    # --------------------------------------------------

    def encode_include(                                      # |:mth:|
        self, file_, as_=None, indent='', zipped=True):
        m = 'if: '

    def encode_module(                                       # |:mth:|
        self, module, for_=None, indent='', zipped=True, flat=None, forced=None):
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
        return self.encode_module_(module, for_, indent, zipped, flat, forced)

    def compile(self, string, name=None, for_=None,          # |:mth:|
                zipped=True, forced=None):
        '''Compile a string into adhoc output.'''
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
        return self.compile_(string, name, for_, zipped, forced)
    # @:adhoc_run_time_section:@ on

    def compileFile(self, file_name, for_=None, zipped=True, forced=None): # |:mth:|
        # @:adhoc_run_time_section:@ off
        """Compile a file into adhoc output.

        Since a module that has RtAdHoc defined is already adhoc'ed,
        the run-time RtAdHoc method returns the file source as is.
        """
        # @:adhoc_run_time_section:@ on
        # @:adhoc_run_time_section:@ off
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
        # @:adhoc_run_time_section:@ off
        source = self.compile_(source, file_name, for_, zipped, forced)
        # @:adhoc_run_time_section:@ on
        return source
    # @:adhoc_run_time_section:@ END

# (progn (forward-line -1) (insert "\n") (snip-insert-mode "py.s.class" t) (backward-symbol-tag 2 "fillme" "::"))

# --------------------------------------------------
# |||:sec:||| FUNCTIONS
# --------------------------------------------------

# (progn (forward-line 1) (snip-insert-mode "py.f.hl" t) (insert "\n"))
hlr = None
def hlcr(title=None, tag='|||' ':CHP:|||', rule_width=50, **kwargs): # ||:fnc:||
    comm = ((('dbg_comm' in globals()) and (globals()['dbg_comm'])) or ('# '))
    dstr = []
    dstr.append(''.join((comm, '-' * rule_width)))
    if title:
        dstr.append(sformat('{0}{2:^{1}} {3!s}',
                comm, ((('dbg_twid' in globals()) and (globals()['dbg_twid'])) or (9)),
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

def adhoc_dump_list(list_, max_wid=None):                  # ||:fnc:||
    if max_wid is None:
        max_wid = 78
    for indx, elt in enumerate(list_):
        elt = str(elt)
        if len(elt) > max_wid:
            elt = elt[:max_wid-3] + ' ...'
        printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                dbg_comm, dbg_twid, dbg_fwid, ':DBG:', sformat('elt[{0}]', indx), repr(elt)))

def adhoc_dump_sections(sections, max_wid=None):           # ||:fnc:||
    if max_wid is None:
        max_wid = 78
    for indx, section in enumerate(sections):
        cut_section = list(section)
        if len(cut_section[1]) > max_wid:
            cut_section[1] = cut_section[1][:max_wid-3] + ' ...'
        printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                dbg_comm, dbg_twid, dbg_fwid, ':DBG:', sformat('section[{0}]', indx), strclean(cut_section)))

def catch_stdout():                                        # ||:fnc:||
    """Install a string IO as `sys.stdout`.

    :returns: a state variable that is needed by
      :func:`restore_stdout` to retrieve the output as string.
    """
    output_sio = _AdHocStringIO()
    sv_stdout = sys.stdout
    sys.stdout = output_sio
    return (sv_stdout, output_sio)

def restore_stdout(state):                                 # ||:fnc:||
    """Restore capturing `sys.stdout` and get captured output.

    :returns: captured output as string.

    :param state: state variable obtained from :func:`catch_stdout`.
    """
    sys.stdout, output_sio = state
    output = output_sio.getvalue()
    output_sio.close()
    return output

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
# @:adhoc_template:@
# @:adhoc_uncomment:@

# @:adhoc_template:@ -rst-to-ascii
RST_HEADER = '''\
.. -*- mode: rst; coding: utf-8 -*-
.. role:: mod(strong)
.. role:: func(strong)
.. role:: class(strong)
.. role:: attr(strong)
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

def rst_to_ascii(string, header_footer=False):             # ||:fnc:||
    '''Convert ReST documentation to ASCII.'''
    string = re.sub(
        '^\\s*[.][.]\\s*(note|warning|attention)::(?im)', '\\1:', string)
    string = re.sub(
        '^\\s*[.][.]\\s*automodule::[^\\n]*\\n(\\s[^\\n]+\\n)*\\n(?m)',
        '', string + '\n\n')
    string = re.sub('^\\s*[.][.]([^.][^\\n]*|)\\n(?m)', '', string)
    string = re.sub('\\\\\\*', '*', string)
    string = re.sub('^(\\s*)\\|(\\s|$)(?m)', '\\1', string)
    if header_footer:
        string = ''.join((RST_HEADER, string, RST_FOOTER))
    string = re.sub('\\n\\n\\n+', '\\n\\n', string)
    return string
# @:adhoc_template:@

# --------------------------------------------------
# |||:sec:||| SYMBOL-TAG TOOLS
# --------------------------------------------------

def compile_(files=None):                                  # ||:fnc:||
    '''Compile files or standard input.'''
    if files is None:
        files = []
    if len(files) == 0:
        files.append('-')
    compiled_files = []
    for file_ in files:
        sys_path = sys.path
        file_dir = os.path.abspath(os.path.dirname(file_))
        sys.path.insert(0, file_dir)
        ah = AdHoc()
        compiled = ah.compileFile(file_)
        compiled_files.append(compiled)
        sys.path = sys_path
    return ''.join(map(lambda c:
                       (((c.endswith('\n')) and (c)) or (''.join((c, '\n')))),
                       compiled_files))

# --------------------------------------------------
# |||:sec:||| TEST
# --------------------------------------------------

doc_index_rst_tag_symbols = ('adhoc_index_only',)

def tpl_hook_doc_index_rst(cls, section, tag, tag_arg):    # ||:fnc:||
    tag_sym_rx = '|'.join([re.escape(tag_sym) for tag_sym in doc_index_rst_tag_symbols])
    return cls.section_tag_remove(section, tag_sym_rx, is_re=True)

def tpl_hook_readme(cls, section, tag, tag_arg):           # ||:fnc:||
    section = section.replace('@@contents@@', 'contents::')
    tag_sym_rx = '|'.join([re.escape(tag_sym) for tag_sym in doc_index_rst_tag_symbols])
    return cls.remove_sections(section, tag_sym_rx, is_re=True)

def adhoc_rst_to_ascii(string):                            # ||:fnc:||
    '''Transform ReST documentation to ASCII.'''
    string = rst_to_ascii(string)
    string = string.replace('|@:|\\\\? ', '@:')
    string = string.replace('\\\\? |:@|', ':@')
    string = string.replace('|@:|', '`@:`')
    string = string.replace('|:@|', '`:@`')
    string = re.sub('^:[|]_?(adhoc[^|]*)_?[|]([^:]*):(?m)', '@:\\1:@\\2', string)
    string = re.sub('[|]_?(adhoc[^|]*)_?[|]', '@:\\1:@', string)
    return string

def inc_template_marker(cls, as_template=False):           # ||:fnc:||
    sv = AdHoc.inc_delimiters()
    template_tag = ''.join((
        '# ', AdHoc.section_tag('adhoc_template_v'),
        ' ', as_template, '\n'))
    AdHoc.reset_delimiters(sv)
    return template_tag

def get_readme(file_=None, source=None, as_template=False, transform=True): # ||:fnc:||
    file_, source = AdHoc.std_source_param(file_, source)

    template_name = 'doc/index.rst'
    tpl_hooks = AdHoc.template_process_hooks
    AdHoc.template_process_hooks = {template_name: tpl_hook_readme}
    template = AdHoc.get_named_template(template_name, file_, source)
    AdHoc.template_process_hooks = tpl_hooks

    template = template + '\n\n' + __doc__ + '\n'
    template = AdHoc.remove_sections(template, 'adhoc_index_only')

    if transform:
        template = adhoc_rst_to_ascii(template).strip() + '\n'
    if as_template:
        template_tag = inc_template_marker(AdHoc, as_template)
        output = []
        output.append(template_tag)
        output.append(RST_HEADER)
        output.append(template)
        output.append(RST_FOOTER)
        output.append(template_tag)
        template = ''.join(output)
    return template

def get_use_cases(as_template=None):                       # ||:fnc:||
    output = []
    if as_template is not None:
        template_tag = inc_template_marker(AdHoc, as_template)
    else:
        template_tag = ''
    output.append(template_tag)
    import use_case_000_ as use_case                       # @:adhoc:@
    state = catch_stdout()
    use_case.main('script --docu'.split())
    output.append(restore_stdout(state))
    import use_case_001_templates_ as use_case             # @:adhoc:@
    state = catch_stdout()
    use_case.main('script --docu'.split())
    output.append(restore_stdout(state))
    import use_case_002_include_ as use_case               # @:adhoc:@
    state = catch_stdout()
    use_case.main('script --docu'.split())
    output.append(restore_stdout(state))
    import use_case_003_import_ as use_case                # @:adhoc:@
    state = catch_stdout()
    use_case.main('script --docu'.split())
    output.append(restore_stdout(state))
    import use_case_005_nested_ as use_case                # @:adhoc:@
    state = catch_stdout()
    use_case.main('script --docu'.split())
    output.append(restore_stdout(state))
    output.append(template_tag)
    output = ''.join(output)
    return output

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

import adhoc_test.sub                                # @:adhoc:@ force

def adhoc_check_modules():                                 # ||:fnc:||

    hl_lvl(0)
    hlc('adhoc_check_modules')

    printf(sformat('{0}--------------------------------------------------',
                   dbg_comm))
    msg = ((('adhoc_test' in sys.modules) and ('SEEN')) or ('NOT SEEN'))
    printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                   dbg_comm, dbg_twid, dbg_fwid, ':DBG:',
                   'PRE  sub import', 'adhoc_test ' + msg))
    msg = ((('adhoc_test' in sys.modules) and ('SEEN')) or ('NOT SEEN'))
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

    >>> state = catch_stdout()
    >>> adhoc_check_module_setup()
    >>> contents = restore_stdout(state)
    >>> contents = re.sub('(mtime.*\\])[^[]*(\\[)', r'\\1\\2', contents)
    >>> contents = re.sub(' at 0x([0-9a-f]+)', '', contents)
    >>> contents = re.sub(r'adhoc\\.pyc', 'adhoc.py', contents)
    >>> contents = '\\n'.join([l.strip() for l in contents.splitlines()])

    .. >>> ign = open('adhoc_check_module_setup.t', 'w').write(
    .. ...     re.sub('^(?m)', '    ', contents)
    .. ...     .replace('\\\\', '\\\\\\\\') + '\\n')

    .. @:adhoc_expected:@ adhoc_check_module_setup.e

    >>> printf(contents, end='') #doctest: +ELLIPSIS
    # --------------------------------------------------
    # |||:CHP:||| adhoc_check_module_setup
    # --------------------------------------------------
    # -----------------------------------
    # ||:SEC:|| no:module:found
    # -----------------------------------
    #   :DBG:   module                 : ]['__adhoc__', '__doc__', '__name__'...][
    # ------------------------------
    #   :DBG:   __adhoc__              : ]...
    #   :DBG:   __doc__                : ]None[
    ...
    # --------------------
    #  |:INF:|  no:module:found.__adhoc__
    # --------------------
    #   :DBG:   __adhoc__              : ]...
    # ------------------------------
    #   :DBG:   __module__             : ]<module 'no:module:found' (built-in)>[
    #   :DBG:   mode                   : ]...[
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
    #   :DBG:   __file__               : ]...adhoc_test/sub/__init__.py...[
    ...
    # --------------------
    #  |:INF:|  adhoc_test.sub.__adhoc__
    # --------------------
    #   :DBG:   __adhoc__              : ]...
    # ------------------------------
    #   :DBG:   __module__             : ]<module 'adhoc_test.sub' from...
    ...
    #   :DBG:   source                 : ]...# -*- coding: utf-8 -*-\\n\\nADHOC_TEST_SUB_IMPORTED = True\\n...[
    # -----------------------------------
    # ||:SEC:|| adhoc
    # -----------------------------------
    #   :DBG:   adhoc                  : ]...
    # ------------------------------
    #   :DBG:   AH_CHECK_SOURCE          : ]...
    ...
    #   :DBG:   AdHoc                    : ]<class 'adhoc.AdHoc'>[
    #   :DBG:   AdHocError               : ]...adhoc.AdHocError...[
    ...
    #   :DBG:   RST_HEADER               : ]...
    ...
    #   :DBG:   __adhoc__                : ]...
    ...
    #   :DBG:   __file__                 : ].../adhoc.py...[
    #   :DBG:   __name__                 : ]adhoc[
    ...
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
    #   :DBG:   adhoc_rst_to_ascii       : ]<function adhoc_rst_to_ascii>[
    #   :DBG:   adhoc_run_time_module    : ]<function adhoc_run_time_module>[
    #   :DBG:   adhoc_test               : ]<module 'adhoc_test' from '...adhoc_test/__init__.py...'>[
    #   :DBG:   base64                   : ]<module 'base64' from '.../base64.py...'>[
    #   :DBG:   catch_stdout             : ]<function catch_stdout>[
    #   :DBG:   compile_                 : ]<function compile_>[
    #   :DBG:   dbg_comm                 : ]# [
    #   :DBG:   dbg_fwid                 : ]23[
    #   :DBG:   dbg_twid                 : ]9[
    #   :DBG:   dict_dump                : ]<function dict_dump>[
    #   :DBG:   ditems                   : ]<function <lambda>>[
    #   :DBG:   dkeys                    : ]<function <lambda>>[
    #   :DBG:   doc_index_rst_tag_symbols: ]('adhoc_index_only',)[
    #   :DBG:   dump_attr                : ]<function dump_attr>[
    #   :DBG:   dvalues                  : ]<function <lambda>>[
    #   :DBG:   file_encoding_is_clean   : ]True[
    #   :DBG:   get_readme               : ]<function get_readme>[
    #   :DBG:   get_use_cases            : ]<function get_use_cases>[
    #   :DBG:   hl                       : ]<function hl>[
    #   :DBG:   hl_lvl                   : ]<function hl_lvl>[
    #   :DBG:   hlc                      : ]<function hlc>[
    #   :DBG:   hlcr                     : ]<function hlcr>[
    #   :DBG:   hlr                      : ]<function hlssr>[
    #   :DBG:   hls                      : ]<function hls>[
    #   :DBG:   hlsr                     : ]<function hlsr>[
    #   :DBG:   hlss                     : ]<function hlss>[
    #   :DBG:   hlssr                    : ]<function hlssr>[
    #   :DBG:   inc_template_marker      : ]<function inc_template_marker>[
    #   :DBG:   isstring                 : ]<function isstring>[
    #   :DBG:   main                     : ]<function main>[
    #   :DBG:   mw_                      : ]<class 'adhoc.mw_'>[
    #   :DBG:   mwg_                     : ]<class 'adhoc.mwg_'>[
    #   :DBG:   namespace_dict           : ]<module 'namespace_dict' from '...namespace_dict.py...'>[
    #   :DBG:   nativestr                : ]<function nativestr>[
    #   :DBG:   os                       : ]<module 'os' from '.../os.py...'>[
    #   :DBG:   printe                   : ]<function printe>[
    #   :DBG:   printf                   : ]<...function print...>[
    #   :DBG:   re                       : ]<module 're' from '.../re.py...'>[
    #   :DBG:   restore_stdout           : ]<function restore_stdout>[
    #   :DBG:   rst_to_ascii             : ]<function rst_to_ascii>[
    #   :DBG:   run                      : ]<function run>[
    #   :DBG:   setdefaultencoding       : ]<function setdefaultencoding>[
    #   :DBG:   sformat                  : ]<function sformat>[
    ...
    #   :DBG:   sys                      : ]<module 'sys' (built-in)>[
    #   :DBG:   tpl_hook_doc_index_rst   : ]<function tpl_hook_doc_index_rst>[
    #   :DBG:   tpl_hook_readme          : ]<function tpl_hook_readme>[
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
    #   :DBG:   mode                   : ]...[
    #   :DBG:   mtime                  : ][
    #   :DBG:   source                 : ]#!/usr/bin/env python\\n# -*- coding: utf-8 -*-\\n# Copyright (C) 2011, 2012, Wolfgang Scherer,
    ...

    .. @:adhoc_expected:@ adhoc_check_module_setup.e
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
    import adhoc_test.sub                                  # @:adhoc:@
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

    # @: adhoc_enable:@
    if not (parameters.compile or parameters.decompile):
        parameters.compile = True
    # @: adhoc_enable:@

    if not parameters.args:
        parameters.args = '-'
    if _debug:
        printe(sformat(
            "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
            dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'parameters.args', parameters.args))

    # |:here:|
    if parameters.compile:
        output = parameters.output
        if _verbose:
            printe(sformat(
                "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                dbg_comm, dbg_twid, dbg_fwid, ':INF:', 'output', output))
        if output is None:
            output = '-'
        compiled = compile_(parameters.args)
        if _debug:
            printe(sformat(
                "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'compiled', compiled))
        AdHoc.write_source(output, compiled)
        return

    if parameters.decompile:
        AdHoc.default_engine = True
        export_dir = parameters.output
        if export_dir is not None:
            AdHoc.export_dir = export_dir
        if _verbose:
            printe(sformat(
                "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                dbg_comm, dbg_twid, dbg_fwid, ':INF:', 'export_dir', export_dir))
        for file_ in parameters.args:
            AdHoc.export(file_)
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

        import_cmd_sections = AdHoc.tag_lines(
            myself, AdHoc.line_tag('adhoc'))
        printf(sformat("{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                       dbg_comm, dbg_twid, dbg_fwid, ':DBG:',
                       'import_cmd_sections', import_cmd_sections))

        import_cmd_sections = AdHoc.tag_split(
            myself, AdHoc.line_tag('adhoc'))
        adhoc_dump_sections(import_cmd_sections)

        pass
    # |:here:|
    # @:adhoc_disable:@

    # @:adhoc_disable:@ -more_development_tests
    # @:adhoc_remove:@
    ah_retained, ah_removed = AdHoc.tag_partition(
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
    class AdHocAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            list(map(lambda opt: setattr(namespace, opt, False),
                     ('implode', 'explode', 'extract', 'template', 'compile', 'decompile')))
            setattr(namespace, option_string[2:], True)
            setattr(namespace, 'adhoc_arg', values)
    parser.add_argument(
        '-c', '--compile', nargs=0, action=AdHocAction, default=False,
        help='compile file(s) or standard input into file OUT (default standard output).')
    parser.add_argument(
        '-d', '--decompile', nargs=0, action=AdHocAction, default=False,
        help='decompile file(s) or standard input into DIR (default __adhoc__).')
    parser.add_argument(
        '-o', '--output', action='store', type=str, default=None,
        help='output file/directory for --compile/--decompile.')

    # |:special:|
    parser.add_argument(
        '-q', '--quiet', action='store_const', const=-2,
        dest='debug', default=0, help='suppress warnings')
    parser.add_argument(
        '-v', '--verbose', action='store_const', const=-1,
        dest='debug', default=0, help='verbose test output')
    parser.add_argument(
        '--debug', nargs='?', action='store', type=int, metavar='NUM',
        default = 0, const = 1,
        help='show debug information')
    parser.add_argument(
        '-t', '--test', action='store_true',
        help='run doc tests')
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
        '--expected', nargs='?', action=AdHocAction, type=str, metavar='DIR',
        default=False, const = '.',
        help='extract expected output to directory DIR (default: `.`)')
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
                ((('dbg_comm' in globals()) and (globals()['dbg_comm'])) or ('# ')),
                ((('dbg_twid' in globals()) and (globals()['dbg_twid'])) or (9)),
                ((('dbg_fwid' in globals()) and (globals()['dbg_fwid'])) or (15)),
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
                or _parameters.expected
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
                try:
                    import adhoc
                    AdHoc = adhoc.AdHoc
                except ImportError:
                    adhoc_compile = False
                    try:
                        from rt_adhoc import RtAdHoc as Adhoc
                    except ImportError:
                        pass
            # |:special:|
            AdHoc.flat = False
            # |:special:|
        else:
            adhoc_compile = False
            AdHoc = RtAdHoc

        AdHoc.quiet = _quiet
        AdHoc.verbose = _verbose
        AdHoc.debug = _debug
        AdHoc.include_path.append(os.path.dirname(file_))
        AdHoc.extra_templates = [
            ('README.txt', 'adhoc_template'),
            ('doc/USE_CASES.txt', 'adhoc_template'),
            ]
        AdHoc.template_process_hooks = {'doc/index.rst': tpl_hook_doc_index_rst}

        if adhoc_compile:
            ah = AdHoc()
            source = ah.compileFile(file_)
        else:
            file_, source = AdHoc.std_source_param(file_)

        # implode
        if _parameters.implode:
            # @:adhoc_enable:@
            # if not _quiet:
            #     list(map(sys.stderr.write,
            #         ["warning: ", os.path.basename(file_),
            #          " already imploded!\n"]))
            # @:adhoc_enable:@
            AdHoc.write_source('-', source)
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
            README = get_readme(file_, source, as_template='README.txt', transform=False)
            USE_CASES = get_use_cases(as_template='doc/USE_CASES.txt')
            sv = AdHoc.inc_delimiters()
            AdHoc.export(file_, README)
            AdHoc.export(file_, USE_CASES)
            AdHoc.reset_delimiters(sv)
            # |:special:|
        # extract
        elif _parameters.extract:
            AdHoc.extract_dir = _parameters.adhoc_arg
            AdHoc.extract(file_, source)
            # |:special:|
            # imports, that should be extracted
            for imported in (
                'use_case_000_',
                'use_case_001_templates_',
                'use_case_002_include_',
                'use_case_003_import_',
                'use_case_005_nested_',
                ):
                ximported = ''.join((imported, '.py'))
                ximported = AdHoc.check_xfile(ximported)
                if ximported:
                    simported = AdHoc.get_named_template(imported, file_)
                    AdHoc.write_source(ximported, simported)
            README = get_readme(file_, source, as_template='README.txt', transform=False)
            USE_CASES = get_use_cases(as_template='doc/USE_CASES.txt')
            sv = AdHoc.inc_delimiters()
            AdHoc.extract(file_, README)
            AdHoc.extract(file_, USE_CASES)
            AdHoc.reset_delimiters(sv)
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
                README = get_readme(file_, source, as_template=template_name, transform=False)
                sv = AdHoc.inc_delimiters()
                AdHoc.write_source('-', AdHoc.get_named_template(template_name, file_, README))
                AdHoc.reset_delimiters(sv)
            elif template_name == 'doc/USE_CASES.txt':
                USE_CASES = get_use_cases()
                AdHoc.write_source('-', USE_CASES)
            # |:special:|
            else:
                template = AdHoc.get_named_template(
                    template_name, file_, source)
                # |:special:|
                template = AdHoc.section_tag_remove(template, "adhoc_run_time_section")
                # |:special:|
                AdHoc.write_source('-', template)
        # |:special:|
        # expected
        elif _parameters.expected:
            AdHoc.extract_dir = _parameters.adhoc_arg
            AdHoc.extract_templates(file_, source, AdHoc.section_tag('adhoc_expected'))
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
# @:adhoc_template:@ -test
# Test template.
# @:adhoc_template:@
# @:adhoc_uncomment:@

if False:
    pass
    # @:adhoc_verbatim:@ # docutils.conf

    # |:info:| The following list is kept in sync with MANIFEST.in.
    # This makes it easier to avoid discrepancies between installation
    # from source distribution vs. installation from compiled script.

    # @:adhoc_include:@ MANIFEST.in
    # @:adhoc_include:@ Makefile
    # @:adhoc_include:@ README.css
    #                   README.txt is generated
    #                   adhoc.py is this file
    #                   argparse_local.py is imported
    # @:adhoc_include:@ doc/Makefile
    # @:adhoc_include:@ doc/_static/adhoc-logo-32.ico
    # @:adhoc_include:@ doc/adhoc-logo.svg
    # @:adhoc_include:@ doc/conf.py
    #                   doc/index.rst is generated
    # @:adhoc_include:@ doc/make.bat
    # @:adhoc_include:@ doc/z-massage-index.sh
    #                   docutils.conf is included above
    #                   namespace_dict.py is imported
    # @:adhoc_include:@ setup.py
    #                   stringformat_local.py is imported
    #                   use_case_00?_* is imported
    #                   adhoc_test is imported
    #                   dist/adhoc.py is generated

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
# . (x-symbol-tag-occur-outline "sec" '("||:" ":||") (cons (cons "^\\([ \t\r]*\\(def\\|class\\)[ ]+\\|[A-Za-z_]?\\)" nil) (cons nil "\\([ \t\r]*(\\|[ \t]*=\\)")))

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

# :ide: COMPILE: Run with --decompile dist/xx_adhoc.py
# . (progn (save-buffer) (compile (concat "rm -rf __adhoc__; cp -p dist/adhoc.py dist/xx_adhoc.py; python ./" (file-name-nondirectory (buffer-file-name)) " --decompile dist/xx_adhoc.py")))

# :ide: COMPILE: Run with cat dist/adhoc.py | --decompile
# . (progn (save-buffer) (compile (concat "rm -rf __adhoc__; cat dist/adhoc.py | python ./" (file-name-nondirectory (buffer-file-name)) " --decompile")))

# :ide: COMPILE: Run with cat /dev/null | --decompile
# . (progn (save-buffer) (compile (concat "rm -rf __adhoc__; cat /dev/null | python ./" (file-name-nondirectory (buffer-file-name)) " --decompile")))

# :ide: COMPILE: Run with cat /dev/null | --compile
# . (progn (save-buffer) (compile (concat "cat /dev/null | python ./" (file-name-nondirectory (buffer-file-name)) " --compile")))

# :ide: COMPILE: Run with cat /dev/null |
# . (progn (save-buffer) (compile (concat "cat /dev/null | python ./" (file-name-nondirectory (buffer-file-name)) " ")))

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

# :ide: COMPILE: Run with --verbose --extract
# . (progn (save-buffer) (shell-command "rm -f README.txt doc/index.rst") (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) "  --verbose --extract")))

# :ide: COMPILE: Run with --verbose --template README.txt
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --verbose --template README.txt")))

# :ide: COMPILE: make doc
# . (progn (save-buffer) (compile (concat "make doc")))

# :ide: COMPILE: Run with --template list
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --template list")))

# :ide: COMPILE: Run with python3 with --test
# . (progn (save-buffer) (compile (concat "python3 ./" (file-name-nondirectory (buffer-file-name)) " --test")))

# :ide: COMPILE: Run with python3 w/o args
# . (progn (save-buffer) (compile (concat "python3 ./" (file-name-nondirectory (buffer-file-name)) " ")))

# :ide: COMPILE: Run with --expected
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --expected")))

# :ide: COMPILE: Run with --test
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --test")))

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
