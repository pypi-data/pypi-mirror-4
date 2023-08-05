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
use_case_003_import_.py - Use case `Included Files` with documentation.

======  ====================
usage:  use_case_003_import_.py [OPTIONS]
or      import use_case_003_import_
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
# Module Imports
# --------------
#
# Imported modules are optionally zipped and base64-encoded.  They are
# automatically unpacked internally and set up as modules in
# sys.modules as required.
#
# They can also be unpacked via the :meth:`adhoc.AdHoc.extract` and
# :meth:`adhoc.AdHoc.get_named_template` mechanisms.
#
# The following Python script imports the module ``adhoc_test.sub``.
# This also triggers the import of ``adhoc_test``, which is therefore
# also included.
#
# Import compilation is recursive. I.e., if a module contains its own
# adhoc tags, they are also processed.
#
# .. note:: When exported, modules are not recreated at the original
#    locations, but locally below the export directory.
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
                compiled = RtAdHoc().compile(source.replace('u:' 'adhoc', '@:' 'adhoc'))
            if argv[1].startswith('--r'):
                import shutil
                tdir = 'use_case_003_import_test'
                tscript = 'use_case_003_import_.py'
                cwd = os.getcwd()
                if os.path.exists(tdir):
                    shutil.rmtree(tdir)
                if not os.path.exists(tdir):
                    os.mkdir(tdir)
                os.chdir(tdir)
                RtAdHoc.write_source(tscript, compiled.replace('@:' 'adhoc', 'u:' 'adhoc'))
                os.system(''.join((sys.executable, ' ', tscript)))
                os.chdir(cwd)
                if os.path.exists(tdir):
                    shutil.rmtree(tdir)
                return 1
            if argv[1].startswith('--c'):
                RtAdHoc.write_source('-', compiled.replace('@:' 'adhoc', 'u:' 'adhoc'))
                return 1
            if argv[1].startswith('--d'):
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
# ``import adhoc_test.sub`` is marked for inclusion at compile time::
#
# @|:uc_descr_out:|>
# Module ``adhoc_test`` is prepared as module through
# :meth:`adhoc.AdHoc.import_` as requirement before module
# ``adhoc_test.sub`` in the compiled script. The original ``import``
# statement then finds the pre-imported versions::
#
# @|:uc_descr_end:|>

# <:adhoc_template:>
    import adhoc_test.sub # u:adhoc:@

# <:adhoc_template:>

    sv = RtAdHoc.section_delimiters
    RtAdHoc.section_delimiters = ('u:', ':@')

# <:adhoc_uncomment:>
# t:adhoc_template:>
# <:adhoc_template:>
# Expected output is ``adhoc_test.sub.ADHOC_TEST_SUB_IMPORTED: True``::
#
# <:adhoc_template:>
# t:adhoc_template:>
# <:adhoc_uncomment:>

# <:adhoc_template:>
    print('adhoc_test.sub.ADHOC_TEST_SUB_IMPORTED: '
          + str(adhoc_test.sub.ADHOC_TEST_SUB_IMPORTED))

# <:adhoc_template:>

# <:adhoc_uncomment:>
# t:adhoc_template:>
# <:adhoc_template:>
# Expected output is ``adhoc_test.ADHOC_TEST_IMPORTED: True``::
#
# <:adhoc_template:>
# t:adhoc_template:>
# <:adhoc_uncomment:>

# <:adhoc_template:>
    print('adhoc_test.ADHOC_TEST_IMPORTED: '
          + str(adhoc_test.ADHOC_TEST_IMPORTED))

# <:adhoc_template:>

# <:adhoc_uncomment:>
# t:adhoc_template:>
# <:adhoc_template:>
# Setup ``use_case_003_export`` as export directory::
#
# <:adhoc_template:>
# t:adhoc_template:>
# <:adhoc_uncomment:>

# <:adhoc_template:>
    RtAdHoc.quiet = True
    RtAdHoc.export_dir = 'use_case_003_export'
# <:adhoc_template:>
    import shutil
    if os.path.exists(RtAdHoc.export_dir):
        shutil.rmtree(RtAdHoc.export_dir)
# <:adhoc_template:>
    RtAdHoc.export(__file__)

# <:adhoc_template:>

# <:adhoc_uncomment:>
# t:adhoc_template:>
# <:adhoc_template:>
# Show export results::
#
# <:adhoc_template:>
# t:adhoc_template:>
# <:adhoc_uncomment:>

# <:adhoc_template:>
    if os.path.exists(RtAdHoc.export_dir):
        for dir_, subdirs, files in os.walk(RtAdHoc.export_dir):
            for file_ in sorted(files):
                map(sys.stdout.write, (os.path.join(dir_, file_), '\n'))

# <:adhoc_template:>

# @|:uc_descr_beg:|>
# The uncompiled script effectively copies itself into ``use_case_003_export``,
# but does not create the ``adhoc_test`` module::
#
#     use_case_003_export/use_case_003_import_.py
#
# @|:uc_descr_out:|>
# Besides the original version of itself, the compiled script also
# recreates ``adhoc_test`` and ``adhoc_test.sub`` in the export
# directory::
#
#     use_case_003_export/use_case_003_import_.py
#     use_case_003_export/adhoc_test/__init__.py
#     use_case_003_export/adhoc_test/sub/__init__.py
#
# @|:uc_descr_end:|>

    RtAdHoc.section_delimiters = sv

    if os.path.exists(RtAdHoc.export_dir):
        shutil.rmtree(RtAdHoc.export_dir)

# t:adhoc_indent:>

# :ide: COMPILE: Run with --compile
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --compile")))

# :ide: COMPILE: Run with --compile >use_case_003_import.py
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --compile >use_case_003_import.py")))

# :ide: COMPILE: Run with --run-compiled
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --run-compiled")))

# :ide: COMPILE: Run with --template
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --template")))

# :ide: COMPILE: Run with --doc
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --doc")))

# :ide: COMPILE: Run with --doc | diff
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --doc | ( if test -r uc003; then echo 'DIFF'; diff -u uc003 -; else echo 'STORE'; cat >uc003; fi)")))

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
