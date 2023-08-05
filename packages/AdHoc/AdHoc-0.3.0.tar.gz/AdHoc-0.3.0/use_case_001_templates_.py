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
use_case_001_templates_.py - Use case `Templates` with documentation.

======  ====================
usage:  use_case_001_templates_.py [OPTIONS]
or      import use_case_001_templates_
======  ====================

Options
=======

  --documentation       generate USE_CASE.txt documentation.
  --template            generate bare script template.
  --compile             adhoc compile script.

  -h, --help            display this help message

Without any options, the script does what the documentation says.

Output is the same for uncompiled and compiled script.
"""
# @|:uc_descr_beg:|>
# Template Extraction
# -------------------
#
# Templates are useful, if some code snippet is to be executed and
# should also be available to initialize, e.g., RC files.
#
# The following Python script defines a template ``~/.uc00.rc``, which
# is extracted, if it does not already exist.
#
# @|:uc_descr_out:|>
# @|:uc_descr_end:|>

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
"""
Code shown in all parts (indented 4).
"""
uc_code_end = (
    '# <:' 'adhoc_template:>\n'
    '# i:' 'adhoc_indent:>\n'
    )

uc_code_ti_beg = (
    '# t:' 'adhoc_template:>\n'
    '# o:' 'adhoc_template:>\n'
    '# i:' 'adhoc_template:>\n'
    )
"""
Code shown in template and input part.
"""
uc_code_ti_out = (
    '# i:' 'adhoc_template:>\n'
    )
"""
Code shown in output part.
"""
uc_code_ti_end = (
    '# o:' 'adhoc_template:>\n'
    '# t:' 'adhoc_template:>\n'
    )

macros = {
    'uc_descr_beg': uc_descr_beg,
    'uc_descr_out': uc_descr_out,
    'uc_descr_end': uc_descr_end,
    'uc_code_beg': uc_code_beg,
    'uc_code_end': uc_code_end,
    'uc_code_ti_beg': uc_code_ti_beg,
    'uc_code_ti_out': uc_code_ti_out,
    'uc_code_ti_end': uc_code_ti_end,
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
            or argv[1].startswith('--t')):
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
                # switch to meta tags
                sv = RtAdHoc.set_delimiters (('<:', ':>'))
                docu_input = RtAdHoc.activate_macros(source)
                docu_input = docu_input.replace('t:' 'adhoc_', '<:' 'adhoc_')
                docu_input = docu_input.replace('u:' 'adhoc_', '@:' 'adhoc_')
                docu_input = RtAdHoc.get_named_template(source=docu_input)
                docu_input = RtAdHoc.line_tag_remove(docu_input, '[^:]+', True, ('o:', ':>'))
                docu_input = RtAdHoc.line_tag_remove(docu_input, '[^:]+', True, ('i:', ':>'))
                RtAdHoc.write_source('-', docu_input)
                RtAdHoc.reset_delimiters(sv)
                return 1
            if compiled is None:
                compiled = RtAdHoc().compileFile(__file__, source)
            if argv[1].startswith('--c'):
                RtAdHoc.write_source('-', compiled)
                return 1
            if argv[1].startswith('--d'):
                # switch to meta tags
                sv = RtAdHoc.set_delimiters (('<:', ':>'))
                docu_input = RtAdHoc.activate_macros(source)
                docu_input = docu_input.replace('i:' 'adhoc_', '<:' 'adhoc_')
                docu_input = docu_input.replace('u:' 'adhoc_', '@:' 'adhoc_')
                docu_input = RtAdHoc.get_named_template(source=docu_input)
                docu_input = RtAdHoc.line_tag_remove(docu_input, '[^:]+', True, ('o:', ':>'))
                RtAdHoc.write_source('-', docu_input)

                docu_input = RtAdHoc.activate_macros(compiled)
                docu_input = docu_input.replace('i:' 'adhoc_', '<:' 'adhoc_')
                docu_input = docu_input.replace('o:' 'adhoc_', '<:' 'adhoc_')
                docu_input = docu_input.replace('u:' 'adhoc_', '@:' 'adhoc_')
                docu_input = RtAdHoc.get_named_template(source=docu_input)
                RtAdHoc.write_source('-', docu_input)
                RtAdHoc.reset_delimiters(sv)
                return 1
        map(sys.stderr.write, ('error: unknown option `', str(argv[1]), '`\n'))
        exit(1)
    return 0

# --------------------------------------------------
# |||:sec:||| Script
# --------------------------------------------------

# --------------------------------------------------
# @|:uc_descr_beg:|>
# The script starts with `Generic AdHoc Initialization`_::
#
# @|:uc_descr_out:|>
# @|:uc_descr_end:|>

# i:adhoc_indent:> 4
# @|:uc_code_ti_beg:|>
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
        import rt_adhoc
        from rt_adhoc import RtAdHoc
    except ImportError:
        pass
sys.path = sys_path
# @:adhoc_disable:@

# @|:uc_code_ti_out:|>
# @|:uc_code_ti_end:|>
# i:adhoc_indent:>

# meta program
if __name__ == '__main__':
    as_module = False
    main(sys.argv) and exit(0)
else:
    as_module = True
if not as_module:
    pass

# t:adhoc_indent:> -4

# --------------------------------------------------
# @|:uc_descr_beg:|>
# Setup of some default values, enclosed in a template declaration::
#
# @|:uc_descr_out:|>
# @|:uc_descr_end:|>

# u:adhoc_indent:@ -4
# @|:uc_code_ti_beg:|>
    rc_file_name = '~/.uc00.rc'
    # u:adhoc_template:@ ~/.uc00.rc
    # -*- coding: utf-8 -*-
    default_value = 'default'
    another_value = 'other'
    # u:adhoc_template:@

# @|:uc_code_ti_out:|>
# @|:uc_code_ti_end:|>
# u:adhoc_indent:@

# --------------------------------------------------
# @|:uc_descr_beg:|>
# Template extraction makes sure, that the file ``~/.uc00.rc`` exists,
# if the user's home directory is writable::
#
# @|:uc_descr_out:|>
# @|:uc_descr_end:|>

    sv = RtAdHoc.section_delimiters
    RtAdHoc.section_delimiters = ('u:', ':@')

# @|:uc_code_ti_beg:|>
    RtAdHoc.quiet = True
    RtAdHoc.extract_templates(__file__)

# @|:uc_code_ti_out:|>
# @|:uc_code_ti_end:|>

    RtAdHoc.section_delimiters = sv

# --------------------------------------------------
# @|:uc_descr_beg:|>
# Read ``~/.uc00.rc``, if available, and define variables::
#
# @|:uc_descr_out:|>
# @|:uc_descr_end:|>

# @|:uc_code_ti_beg:|>
    rc_file = os.path.expanduser(rc_file_name)
    try:
        rc_source = RtAdHoc.read_source(rc_file, decode=False)
        exec(rc_source, globals(), locals())
    except IOError:
        pass

    print('default_value: ' + default_value)
    print('another_value: ' + another_value)
# @|:uc_code_ti_out:|>

# @|:uc_code_ti_end:|>

# --------------------------------------------------
# t:adhoc_indent:>

# :ide: COMPILE: Run with --compile
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --compile")))

# :ide: COMPILE: Run with --compile >use_case_001_templates.py
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --compile >use_case_001_templates.py")))

# :ide: COMPILE: Run with --template
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --template")))

# :ide: COMPILE: Run with --doc
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --doc")))

# :ide: COMPILE: Run with --doc | diff
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --doc | ( if test -r uc001; then echo 'DIFF'; diff -u uc001 -; else echo 'STORE'; cat >uc001; fi)")))

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
