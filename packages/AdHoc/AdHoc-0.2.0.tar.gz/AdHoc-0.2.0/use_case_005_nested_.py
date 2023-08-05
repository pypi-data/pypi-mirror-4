#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012, Wolfgang Scherer, <Wolfgang.Scherer at gmx.de>
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
"""\
use_case_005_nested_.py - Use case `Nested Templates` with documentation.

======  ====================
usage:  use_case_005_nested_.py [OPTIONS]
or      import use_case_005_nested_
======  ====================

Options
=======

  --documentation       generate USE_CASE.txt documentation.
  --template            generate bare script template.
  --compile             adhoc compile script.

  -h, --help            display this help message

Without any options, the script does that the documentation says.

Output is the same for uncompiled and compiled script.
"""
# @:adhoc_uncomment:@
# @:adhoc_template:@ -intro
# Nested Templates
# ----------------
#
# Since AdHoc sections are defined with the same tag denoting start
# and end, it may not be obvious how nested templates can be realized.
#
# There are several different ways to achieve section nesting:
#
# - `Alternate Tag Symbols`_
# - `Alternate Tag Delimiters`_
# - replace strings and extract templates
#
# @:adhoc_template:@
# @:adhoc_uncomment:@

# --------------------------------------------------
# |||:sec:||| Example
# --------------------------------------------------

# @:adhoc_indent:@ +4
# <:adhoc_indent:> +4
# <:adhoc_template:> -example
# @:adhoc_uncomment:@
# @:adhoc_template:@ -doc
# Documentation
# =============
#
# Summary
#
# @:adhoc_x_full_doc:@ -details
# @:adhoc_template:> -details
# Details
# -------
#
# Lengthy explanation ...
#
# @:adhoc_template:>
# @:adhoc_x_full_doc:@
# Conclusion
# ----------
#
# Good!
#
# @:adhoc_x_full_doc:@
# @:adhoc_template:>
# Because ...
#
# @:adhoc_template:>
# @:adhoc_x_full_doc:@
# @:adhoc_template:@
# @:adhoc_uncomment:@
# <:adhoc_template:> -example
# <:adhoc_indent:>
# @:adhoc_indent:@

# --------------------------------------------------
# |||:sec:||| Generator
# --------------------------------------------------

uc_descr_beg = (
    '# <:' 'adhoc_uncomment:>\n'
    '# o:' 'adhoc_template:>\n'
    '# i:' 'adhoc_template:>\n'
    )
uc_descr_out = (
    '# i:' 'adhoc_template:>\n'
    )
uc_descr_end = (
    '# o:' 'adhoc_template:>\n'
    '# <:' 'adhoc_uncomment:>\n'
    )
uc_code_beg = (
    '# i:' 'adhoc_indent:> 4\n'
    '# <:' 'adhoc_template:>\n'
    )
uc_code_end = (
    '# <:' 'adhoc_template:>\n'
    '# i:' 'adhoc_indent:>\n'
    )
macros = {
    'uc_descr_beg': uc_descr_beg,
    'uc_descr_out': uc_descr_out,
    'uc_descr_end': uc_descr_end,
    'uc_code_beg': uc_code_beg,
    'uc_code_end': uc_code_end,
    }

def main(argv):
    '''compiler and help/example/documentation extractor'''
    global RtAdHoc
    RtAdHoc.macros = macros
    
    if len(argv) > 1:
        if argv[1].startswith('-h') or argv[1].startswith('--h'):
            print(__doc__)
            return 1
        if (argv[1].startswith('--c')
            or argv[1].startswith('--d')
            or argv[1].startswith('--t')
            or argv[1].startswith('--r')):
            file_, source = RtAdHoc.std_source_param(__file__)
            if 'adhoc' not in globals() and 'rt_adhoc' not in globals():
                compiled = source
                source = RtAdHoc.export_source(source)
            else:
                if 'adhoc' not in globals():
                    # this will most certainly fail
                    from adhoc import AdHoc as RtAdHoc
                    RtAdHoc.macros = macros
                compiled = None
            if argv[1].startswith('--t'):
                template(RtAdHoc.activate_macros(source))
                return 1
                # switch to meta tags
                sv = RtAdHoc.set_delimiters (('<:', ':>'))
                docu_input = RtAdHoc.activate_macros(source)
                docu_input = docu_input.replace('t:' 'adhoc', '<:' 'adhoc')
                docu_input = docu_input.replace('u:' 'adhoc', '@:' 'adhoc')
                docu_input = RtAdHoc.get_named_template(source=docu_input)
                docu_input = RtAdHoc.line_tag_remove(docu_input, '[^:]+', True, ('o:', ':>'))
                docu_input = RtAdHoc.line_tag_remove(docu_input, '[^:]+', True, ('i:', ':>'))
                RtAdHoc.write_source('-', docu_input)
                RtAdHoc.reset_delimiters(sv)
                return 1
            if compiled is None:
                compiled = RtAdHoc().compile(source)
            if argv[1].startswith('--c'):
                RtAdHoc.write_source('-', compiled)
                return 1
            if argv[1].startswith('--d'):
                documentation()
                return 1
                # switch to meta tags
                sv = RtAdHoc.set_delimiters (('<:', ':>'))
                docu_input = RtAdHoc.activate_macros(source)
                docu_input = docu_input.replace('i:' 'adhoc', '<:' 'adhoc')
                docu_input = docu_input.replace('u:' 'adhoc', '@:' 'adhoc')
                docu_input = RtAdHoc.get_named_template(source=docu_input)
                docu_input = RtAdHoc.line_tag_remove(docu_input, '[^:]+', True, ('o:', ':>'))
                RtAdHoc.write_source('-', docu_input)

                docu_input = RtAdHoc.activate_macros(compiled)
                docu_input = docu_input.replace('i:' 'adhoc', '<:' 'adhoc')
                docu_input = docu_input.replace('o:' 'adhoc', '<:' 'adhoc')
                docu_input = docu_input.replace('u:' 'adhoc', '@:' 'adhoc')
                docu_input = RtAdHoc.get_named_template(source=docu_input)
                RtAdHoc.write_source('-', docu_input)
                RtAdHoc.reset_delimiters(sv)
                return 1
        map(sys.stderr.write, ('error: unknown option `', str(argv[1]), '`\n'))
        exit(1)
    return 0

# --------------------------------------------------
# |||:sec:||| Setup
# --------------------------------------------------

# @:adhoc_template:@ -generic-init
# @:adhoc_run_time:@
# @:adhoc_disable:@
# Get RtAdHoc from adhoc or rt_adhoc
import os
import sys
os_path = os.defpath
if 'PATH' in os.environ:
    os_path = os.environ['PATH']
sys_path = sys.path
sys.path.extend(os_path.split(os.pathsep))
try:
    import adhoc
    from adhoc import AdHoc as RtAdHoc
except ImportError:
    try:
        from rt_adhoc import RtAdHoc
    except ImportError:
        pass
sys.path = sys_path
# @:adhoc_disable:@
# @:adhoc_template:@ -generic-init

@classmethod
def __getstate__(cls):
    attribs = (
        'line_delimiters',
        'section_delimiters',
        )
    state = {}
    for attrib in attribs:
        state[attrib] = getattr(cls, attrib)
    return state

@classmethod
def __setstate__(cls, state):
    for attrib, value in state.items():
        setattr(cls, attrib, value)

@classmethod
def set_delimiters(cls, line_delimiters, section_delimiters=None):
    state = cls.__getstate__()
    if section_delimiters is None:
        section_delimiters = line_delimiters
    cls.line_delimiters = line_delimiters
    cls.section_delimiters = section_delimiters
    return state

reset_delimiters = __setstate__

def print_template(cls, name, source=None):
    tpl = cls.get_named_template(name, __file__, source)
    cls.write_source('-', tpl)

if not hasattr(RtAdHoc, '__getstate__'):
    RtAdHoc.__getstate__ = __getstate__
    RtAdHoc.__setstate__ = __setstate__

if not hasattr(RtAdHoc, 'set_delimiters'):
    RtAdHoc.set_delimiters = set_delimiters
    RtAdHoc.reset_delimiters = reset_delimiters

# --------------------------------------------------
# |||:sec:||| Documentation
# --------------------------------------------------

def template(source=None):                                 # ||:fnc:||
    if source is None:
        source = RtAdHoc.read_source(__file__)

    # state = RtAdHoc.set_delimiters('<:', ':>')
    # parts = []
    # parts.append(''.join((RtAdHoc.section_tag('adhoc_indent'), ' -4\n')))
    # parts.append(''.join((RtAdHoc.section_tag('adhoc_template'), ' -\n')))
    # parts.append(source)
    # parts.append(''.join((RtAdHoc.section_tag('adhoc_template'), ' -\n')))
    # parts.append(''.join((RtAdHoc.section_tag('adhoc_indent'), '\n')))
    # source = RtAdHoc.get_named_template('-', None, ''.join(parts))
    # RtAdHoc.reset_delimiters(state)

    source = source.replace('<:' 'adhoc', '@:' 'adhoc')
    source = source.replace('@:' 'adhoc_indent' ':@ -0', '@:' 'adhoc_indent' ':@ -4')

    print_template(RtAdHoc, '-generic-init', source)
    RtAdHoc.write_source('-', '\n')
    print_template(RtAdHoc, '-alt-sym1', source)
    print_template(RtAdHoc, '-alt-sym2', source)
    print_template(RtAdHoc, '-alt-sym3', source)
    print_template(RtAdHoc, '-alt-sym4', source)
    print_template(RtAdHoc, '-alt-sym5', source)
    print_template(RtAdHoc, '-alt-sym6', source)
    RtAdHoc.write_source('-', '\n')
    print_template(RtAdHoc, '-alt-dlm1', source)
    print_template(RtAdHoc, '-alt-dlm2', source)
    print_template(RtAdHoc, '-alt-dlm3', source)
    print_template(RtAdHoc, '-alt-dlm4', source)
    print_template(RtAdHoc, '-alt-dlm5', source)

def documentation():                                       # ||:fnc:||
    print_template(RtAdHoc, '-intro')

    example_delimiters = ('<:', ':>')
    state = RtAdHoc.set_delimiters(example_delimiters)
    example_raw = RtAdHoc.get_named_template('-example', __file__)
    RtAdHoc.reset_delimiters(state)

    # printe(sformat(
    #     "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
    #     dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'example_raw', example_raw))
    # exit(0)                             # |:debug:|

    full_doc_delimiters = ('@:', ':>')
    state = RtAdHoc.set_delimiters(full_doc_delimiters)
    example1 = RtAdHoc.section_tag_remove(example_raw, 'adhoc_template')
    RtAdHoc.reset_delimiters(state)

    example2 = RtAdHoc.section_tag_remove(example_raw, 'adhoc_x_full_doc')

    # |:here:|
    # @:adhoc_uncomment:@
    # @:adhoc_indent:@ -4
    # <:adhoc_template:@ -alt-sym1
    # @:adhoc_template:@ -alt-sym1
    # Alternate Tag Symbols
    # ~~~~~~~~~~~~~~~~~~~~~
    #
    # Consider some detailed documentation::
    #
    # @:adhoc_template:@
    # <:adhoc_template:@
    # @:adhoc_indent:@
    print_template(RtAdHoc, '-alt-sym1')
    RtAdHoc.write_source('-', example1)

    # @:adhoc_indent:@ -4
    # <:adhoc_template:@ -alt-sym2
    # @:adhoc_template:@ -alt-sym2
    #
    # The raw template::
    #
    # @:adhoc_template:@
    # <:adhoc_template:@
    # @:adhoc_indent:@
    # @:adhoc_indent:@ -0
    # @:adhoc_template:@ -alt-sym2
    template_raw = RtAdHoc.get_named_template('-doc', __file__)
    # @:adhoc_template:@
    # @:adhoc_indent:@

    template_raw = RtAdHoc.get_named_template('-doc', None, example1)
    print_template(RtAdHoc, '-alt-sym2')

    # @:adhoc_indent:@ -4
    # <:adhoc_template:@ -alt-sym3
    # @:adhoc_template:@ -alt-sym3
    #
    # is easily split into parts of different scope::
    #
    # @:adhoc_template:@
    # <:adhoc_template:@
    # @:adhoc_indent:@
    # @:adhoc_indent:@ -0
    # @:adhoc_template:@ -alt-sym3
    full_doc_tag_sym = 'adhoc_x_full_doc'
    full_doc_tag = RtAdHoc.section_tag(full_doc_tag_sym)
    # @:adhoc_template:@
    # @:adhoc_indent:@
    print_template(RtAdHoc, '-alt-sym3')

    # @:adhoc_indent:@ -4
    # <:adhoc_template:@ -alt-sym4
    # @:adhoc_template:@ -alt-sym4
    #
    # by removing all tagged detail sections::
    #
    # @:adhoc_template:@
    # <:adhoc_template:@
    # @:adhoc_indent:@
    # @:adhoc_indent:@ -0
    # @:adhoc_template:@ -alt-sym4
    short_doc = RtAdHoc.remove_sections(template_raw, full_doc_tag_sym)
    # @:adhoc_template:@
    # @:adhoc_indent:@
    # @:adhoc_indent:@ -4
    # <:adhoc_template:@ -alt-sym4
    # @:adhoc_template:@ -alt-sym4
    #
    # providing for a short summary::
    #
    # @:adhoc_template:@
    # <:adhoc_template:@
    # @:adhoc_indent:@
    print_template(RtAdHoc, '-alt-sym4')
    RtAdHoc.write_source('-', short_doc)

    # @:adhoc_indent:@ -4
    # <:adhoc_template:@ -alt-sym5
    # @:adhoc_template:@ -alt-sym5
    #
    # by extracting sub-templates::
    #
    # @:adhoc_template:@
    # <:adhoc_template:@
    # @:adhoc_indent:@
    # @:adhoc_indent:@ -0
    # @:adhoc_template:@ -alt-sym5
    details = RtAdHoc.get_named_template('-details', None, template_raw, full_doc_tag)
    # @:adhoc_template:@
    # @:adhoc_indent:@
    # @:adhoc_indent:@ -4
    # <:adhoc_template:@ -alt-sym5
    # @:adhoc_template:@ -alt-sym5
    #
    # providing for a details higlight::
    #
    # @:adhoc_template:@
    # <:adhoc_template:@
    # @:adhoc_indent:@
    print_template(RtAdHoc, '-alt-sym5')
    RtAdHoc.write_source('-', details)

    # @:adhoc_indent:@ -4
    # <:adhoc_template:@ -alt-sym6
    # @:adhoc_template:@ -alt-sym6
    #
    # and by removing sub-template tag lines::
    #
    # @:adhoc_template:@
    # <:adhoc_template:@
    # @:adhoc_indent:@
    # @:adhoc_indent:@ -0
    # @:adhoc_template:@ -alt-sym6
    full_doc = RtAdHoc.section_tag_remove(template_raw, full_doc_tag_sym)
    # @:adhoc_template:@
    # @:adhoc_indent:@
    # @:adhoc_indent:@ -4
    # <:adhoc_template:@ -alt-sym6
    # @:adhoc_template:@ -alt-sym6
    #
    # providing the full documentation (full_doc)::
    #
    # @:adhoc_template:@
    # <:adhoc_template:@
    # @:adhoc_indent:@
    print_template(RtAdHoc, '-alt-sym6')
    RtAdHoc.write_source('-', full_doc)

    # @:adhoc_uncomment:@

    # |:here:|
    # @:adhoc_uncomment:@
    # @:adhoc_indent:@ -4
    # <:adhoc_template:@ -alt-dlm1
    # @:adhoc_template:@ -alt-dlm1
    # Alternate Tag Delimiters
    # ~~~~~~~~~~~~~~~~~~~~~~~~
    #
    # The same documentation tagged with different tag delimiters::
    #
    # @:adhoc_template:@
    # <:adhoc_template:@
    # @:adhoc_indent:@
    print_template(RtAdHoc, '-alt-dlm1')
    RtAdHoc.write_source('-', example2)

    # @:adhoc_indent:@ -4
    # <:adhoc_template:@ -alt-dlm2
    # @:adhoc_template:@ -alt-dlm2
    #
    # After getting the raw template::
    #
    # @:adhoc_template:@
    # <:adhoc_template:@
    # @:adhoc_indent:@
    # @:adhoc_indent:@ -0
    # <:adhoc_template:@ -alt-dlm2
    # @:adhoc_template:@ -alt-dlm2
    template_raw = RtAdHoc.get_named_template('-doc', __file__)
    # @:adhoc_template:@
    # <:adhoc_template:@
    # @:adhoc_indent:@
    template_raw = RtAdHoc.get_named_template('-doc', None, example2)
    print_template(RtAdHoc, '-alt-dlm2')

    # @:adhoc_indent:@ -4
    # <:adhoc_template:@ -alt-dlm3
    # @:adhoc_template:@ -alt-dlm3
    #
    # the delimiters are changed for the documentation detail sections::
    #
    # @:adhoc_template:@
    # <:adhoc_template:@
    # @:adhoc_indent:@
    # @:adhoc_indent:@ -0
    # @:adhoc_template:@ -alt-dlm3
    full_doc_delimiters = ('@:', ':>')
    state = RtAdHoc.set_delimiters(full_doc_delimiters)
    # @:adhoc_template:@
    # @:adhoc_indent:@
    RtAdHoc.reset_delimiters(state)
    print_template(RtAdHoc, '-alt-dlm3')

    # @:adhoc_indent:@ -4
    # <:adhoc_template:@ -alt-dlm4
    # @:adhoc_template:@ -alt-dlm4
    #
    # and the same parts as with `Alternate Tag Symbols`_ are generated::
    #
    # @:adhoc_template:@
    # <:adhoc_template:@
    # @:adhoc_indent:@
    # @:adhoc_indent:@ -0
    # @:adhoc_template:@ -alt-dlm4
    short_doc = RtAdHoc.remove_sections(template_raw, 'adhoc_template')
    details = RtAdHoc.get_named_template('-details', None, template_raw)
    full_doc = RtAdHoc.section_tag_remove(template_raw, 'adhoc_template')
    # @:adhoc_template:@
    # @:adhoc_indent:@
    print_template(RtAdHoc, '-alt-dlm4')

    # @:adhoc_indent:@ -4
    # <:adhoc_template:@ -alt-dlm5
    # @:adhoc_template:@ -alt-dlm5
    #
    # It is good practice to restore the previous delimiter set::
    #
    # @:adhoc_template:@
    # <:adhoc_template:@
    # @:adhoc_indent:@
    # @:adhoc_indent:@ -0
    # @:adhoc_template:@ -alt-dlm5
    RtAdHoc.reset_delimiters(state)
    # @:adhoc_template:@
    # <:adhoc_template:@
    # @:adhoc_indent:@
    print_template(RtAdHoc, '-alt-dlm5')

# --------------------------------------------------
# |||:sec:||| Script
# --------------------------------------------------

if __name__ == '__main__':
    as_module = False
    main(sys.argv) and exit(0)
else:
    as_module = True
if not as_module:
    pass

# :ide: COMPILE: Run with --compile
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --compile")))

# :ide: COMPILE: Run with --compile >use_case_005_nested.py
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --compile >use_case_005_nested.py")))

# :ide: COMPILE: Run with --template
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --template")))

# :ide: COMPILE: Run with --doc
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --doc")))

# :ide: COMPILE: Run with --doc | diff
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --doc | ( if test -r uc005; then echo 'DIFF'; diff -u uc005 -; else echo 'STORE'; cat >uc005; fi)")))

# :ide: COMPILE: Run with --help
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --help")))

# :ide: COMPILE: Run with python3
# . (progn (save-buffer) (compile (concat "python3 ./" (file-name-nondirectory (buffer-file-name)) "")))

# :ide: COMPILE: Run w/o args
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) "")))

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
