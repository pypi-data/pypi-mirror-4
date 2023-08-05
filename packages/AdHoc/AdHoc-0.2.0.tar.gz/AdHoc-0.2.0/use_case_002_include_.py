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
use_case_002_include_.py - Use case `Included Files` with documentation.

======  ====================
usage:  use_case_002_include_.py [OPTIONS]
or      import use_case_002_include_
======  ====================

Options
=======

  --documentation       generate USE_CASE.txt documentation.
  --template            generate bare script template.
  --compile             adhoc compile script.

  -h, --help            display this help message

Without any options, the script does that the documentation say.

Output is the same for uncompiled and compiled script.
"""
# @|:uc_descr_beg:|>
# Included Files
# --------------
#
# Included files are optionally zipped and base64-encoded.  They can
# be automatically unpacked, or unpacked via the
# :meth:`adhoc.AdHoc.extract` and
# :meth:`adhoc.AdHoc.get_named_template` mechanisms.
#
# The following Python script include the files ``included1`` and
# ``included2``.  ``included1`` is automatically unpacked, if it does
# not already exist, whereas ``included2`` is only available for
# explicit extraction.
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

INCLUDE1 = """\
# -*- coding: latin1 -*-
abc äöü
fill it up a little ...
"""

INCLUDE2 = """\
# -*- coding: utf-8 -*-
abc äöü
fill it up a little ...
"""

INCLUDES = {
    'include1': INCLUDE1,
    'include2': INCLUDE2,
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
                for include, isource in INCLUDES.items():
                    if not os.path.exists(include):
                        if hasattr(isource, 'decode'):
                            isource = isource.decode('utf-8')
                        RtAdHoc.write_source(include, isource)
                compiled = RtAdHoc().compile(source.replace('u:' 'adhoc_', '@:' 'adhoc_'))
                for include in INCLUDES:
                    os.unlink(include)
            if argv[1].startswith('--c'):
                RtAdHoc.write_source('-', compiled.replace('@:' 'adhoc_', 'u:' 'adhoc_'))
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

# @|:uc_descr_beg:|>
# **Uncompiled Script**
#
# The script starts with `Generic AdHoc Initialization`_::
#
# @|:uc_descr_out:|>
# **Compiled Script**
#
# @|:uc_descr_end:|>

# @|:uc_code_beg:|>
# o:adhoc_template:>
# @:adhoc_run_time:@

# o:adhoc_template:>
# @|:uc_code_end:|>

# i:adhoc_indent:> 4
# t:adhoc_template:>
# o:adhoc_template:>
# i:adhoc_template:>
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

# i:adhoc_template:>
# o:adhoc_template:>
# t:adhoc_template:>
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
# @|:uc_descr_beg:|>
# ``include1`` is marked for inclusion at compile time.  Since it is
# supposed to exist anyway, no special care is taken to extract it in
# the uncompiled script::
#
# @|:uc_descr_out:|>
# ``include1`` is automatically extracted in the compiled script::
#
# @|:uc_descr_end:|>

# <:adhoc_template:>
    # u:adhoc_include:@ include1

# <:adhoc_template:>

# @|:uc_descr_beg:|>
# ``include2`` is marked for inclusion at compile time::
#
# @|:uc_descr_out:|>
# The ``if False`` before ``include2`` prevents automatic extraction::
#
# @|:uc_descr_end:|>

# <:adhoc_template:>
    if False:
        pass
        # u:adhoc_include:@ include2

# <:adhoc_template:>

    sv = RtAdHoc.section_delimiters
    RtAdHoc.section_delimiters = ('u:', ':@')

# @|:uc_descr_beg:|>
# There is actually nothing to extract in the uncompiled script::
#
# @|:uc_descr_out:|>
# In the compiled script, ``include2`` will now also be extracted,
# since :meth:`adhoc.AdHoc.extract` finds all sections tagged with
# ``adhoc_unpack``::
#
# @|:uc_descr_end:|>

# <:adhoc_template:>
    RtAdHoc.quiet = True
    RtAdHoc.extract(__file__)

# <:adhoc_template:>

    RtAdHoc.section_delimiters = sv

# t:adhoc_indent:>

# :ide: COMPILE: Run with --compile
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --compile")))

# :ide: COMPILE: Run with --compile >use_case_002_include.py
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --compile >use_case_002_include.py")))

# :ide: COMPILE: Run with --template
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --template")))

# :ide: COMPILE: Run with --doc
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --doc")))

# :ide: COMPILE: Run with --doc | diff
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --doc | ( if test -r uc002; then echo 'DIFF'; diff -u uc002 -; else echo 'STORE'; cat >uc002; fi)")))

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
