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
use_case_000_.py - Use cases Intro, use case `Generic Initialization` with documentation.

======  ====================
usage:  use_case_000_.py [OPTIONS]
or      import use_case_000_
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

def sformat(fmt, *args, **kwargs):
    return fmt.format(*args, **kwargs)

def printe(*args, **kwargs):
    sys.stderr.write(' '.join(args))
    sys.stderr.write('\n')

dbg_comm = globals()['dbg_comm'] if 'dbg_comm' in globals() else '# '
dbg_twid = globals()['dbg_twid'] if 'dbg_twid' in globals() else 9
dbg_fwid = globals()['dbg_fwid'] if 'dbg_fwid' in globals() else 15

# --------------------------------------------------
# @|:uc_descr_beg:|>
# Use Cases
# =========
#
# The initial incentive for the :mod:`adhoc` compiler was to have a
# means for including development libraries that are not ready for
# `PyPI`_ (and maybe never will). (See `Module Imports`_).
#
# The problem with these libraries is that they are not available on
# all systems and may not be worth the effort of a full-blown
# :mod:`distutils` package.
#
# If the API is heavily in flux, it is also nice to be able to take an
# arbitrary stable snapshot without version fiddling and carry
# everything around in a self-contained single file script. This
# eliminates the need to follow API changes in support libraries
# immediately.
#
# Creating a Python script instead of an archive eliminates the
# installation step.
#
# Including the importer/extractor as verbatim code eliminates the
# need for a run-time system to be installed. (See `Generic AdHoc
# Initialization`_).
#
# Modifications of the main script can be made trivially.
#
# The export mechanism allows arbitrary modifications of the main
# script and all adhoc'ed imports.
#
# The ``adhoc.py`` compiler script is only needed, if an exported
# script should be compiled again.
#
# Non-Module `Included Files`_ and `Template Extraction`_ are logical
# expansions of the basic concept.
#
# .. note:: Self-referential stuff gets pretty hilarious after a while
#    ...  The script for generating the use case documentation has
#    some two and a half layers of template tagging ``:)``
#
# .. _`PyPI`: http://pypi.python.org
#
# @|:uc_descr_out:|>
# @|:uc_descr_end:|>

# --------------------------------------------------
# @|:uc_descr_beg:|>
# Generic AdHoc Initialization
# ----------------------------
#
# If only automatic import and unpacking features are used, the
# standard initialization with a |adhoc_run_time| tag is sufficient.
# This includes the export, extract and template features, if only
# used in the compiled script.
#
# However, it is convenient that the uncompiled, compiled and exported
# versions of a script behave identically (especially for templates).
# That is the purpose of this generic initialization example.
#
# The use case documentation generator scripts contain an example
# :func:`main` function, which compiles/uncompiles the script on
# demand.
#
# A more complete example can be found in the command line argument
# evaluation part of the :func:`main` function in
# ``namespace_dict.py``
#
# The most complex example is available in the command line argument
# evaluation part of the :func:`main` function in ``adhoc.py``.

# @|:uc_descr_out:|>
# @|:uc_descr_end:|>

# --------------------------------------------------
# |||:sec:||| Tag Description
# --------------------------------------------------

# u:adhoc_
#   standard tag replacement to avoid template generation on
#   extraction.
#
# <:adhoc_
#   meta tags for example template
#
# i:adhoc_
#   meta tags for input documentation
#
# o:adhoc_
#   meta tags for output documentation
#
# t:adhoc_
#   example template indent
#

# --------------------------------------------------
# |||:sec:||| Document Macros
# --------------------------------------------------

# Usage of input/output description sections:
#
# @|: uc_descr_beg :|>
#
# Describe input
#
# @|: uc_descr_out :|>
#
# Describe output
#
# @|: uc_descr_end :|>

# @:adhoc_template:@ -macros
uc_descr_beg = (
    '# <:' 'adhoc_uncomment:>\n'
    '# o:' 'adhoc_template:>\n'
    '# i:' 'adhoc_template:>\n'
    )
# @:adhoc_template:@
"""
**Complete Example**

Macro::

    # @|:uc_descr_beg...:|>
    # INPUT
    # @|:uc_descr_out...:|>
    # OUTPUT
    # @|:uc_descr_end...:|>

Effective input source::

    # <:adhoc_uncomment...:>
    # <:adhoc_template...:>
    # INPUT
    # <:adhoc_template...:>
    # OUTPUT
    # <:adhoc_uncomment...:>

Effective output source::

    # <:adhoc_uncomment...:>
    # <:adhoc_template...:>
    # <:adhoc_template...:>
    # INPUT
    # <:adhoc_template...:>
    # OUTPUT
    # <:adhoc_template...:>
    # <:adhoc_uncomment...:>

**uc_descr_beg Only**

Effective input source::

    # <:adhoc_uncomment...:>
    # <:adhoc_template...:>

Effective output source::

    # <:adhoc_uncomment...:>
    # <:adhoc_template...:>
    # <:adhoc_template...:>
"""

# @:adhoc_template:@ -macros
uc_descr_out = (
    '# i:' 'adhoc_template:>\n'
    )
# @:adhoc_template:@
"""
Effective input source::

    # <:adhoc_template...:>

Effective output source::

    # <:adhoc_template...:>
"""

# @:adhoc_template:@ -macros
uc_descr_end = (
    '# o:' 'adhoc_template:>\n'
    '# <:' 'adhoc_uncomment:>\n'
    )
# @:adhoc_template:@
"""
Effective input source::

    # <:adhoc_uncomment...:>

Effective output source::

    # <:adhoc_template...:>
    # <:adhoc_uncomment...:>
"""

# @:adhoc_template:@ -macros
uc_code_beg = (
    '# i:' 'adhoc_indent:> 4\n'
    '# <:' 'adhoc_template:>\n'
    )
# @:adhoc_template:@
"""
For the --template run, indentation is dropped!
Otherwise, input and output versions are identical.
"""

# @:adhoc_template:@ -macros
uc_code_end = (
    '# <:' 'adhoc_template:>\n'
    '# i:' 'adhoc_indent:>\n'
    )
# @:adhoc_template:@

# @:adhoc_template:@ -macros
macros = {
    'uc_descr_beg': uc_descr_beg,
    'uc_descr_out': uc_descr_out,
    'uc_descr_end': uc_descr_end,
    'uc_code_beg': uc_code_beg,
    'uc_code_end': uc_code_end,
    }
# @:adhoc_template:@

# --------------------------------------------------
# |||:sec:||| Generator
# --------------------------------------------------

def catch_stdout():                                        # ||:fnc:||
    """Install a string IO as `sys.stdout`.

    :returns: a state variable that is needed by
      :func:`restore_stdout` to retrieve the output as string.
    """
    global _AdHocStringIO
    if not '_AdHocStringIO' in globals():
        _AdHocStringIO = adhoc._AdHocStringIO
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

def main(argv):
    '''compiler and help/example/documentation extractor'''
    global RtAdHoc
    RtAdHoc.macros = macros

    if len(argv) > 1:
        if argv[1].startswith('-h') or argv[1].startswith('--h'):
            print(__doc__)
            return 1
        if (argv[1] == '--test'):
            import doctest
            doctest.testmod()
            return 0
        # @:adhoc_enable:@
        # if (argv[1].startswith('--e')):
        #     export_dir = '__use_case_export__'
        #     import shutil
        #     if os.path.exists(export_dir):
        #         shutil.rmtree(export_dir)
        #     RtAdHoc.export_dir = export_dir
        #     RtAdHoc.export(__file__)
        #     return 0
        # @:adhoc_enable:@
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
                if len(argv) > 2:
                    name = argv[2]
                    docu_input = RtAdHoc.get_named_template(name, source=docu_input)
                    sys.stdout.write(docu_input)
                    return 1
                # switch to meta tags
                sv = RtAdHoc.set_delimiters(('<:', ':>'))
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
                compiled = RtAdHoc().compile(source)
            if argv[1].startswith('--c'):
                RtAdHoc.write_source('-', compiled)
                return 1
            if argv[1].startswith('--d'):
                # switch to meta tags
                state = catch_stdout()
                main('script --template'.split())
                script = restore_stdout(state)

                sv = RtAdHoc.set_delimiters (('<:', ':>'))
                indent_tag_sym = 'adhoc_indent'
                indent_tag = RtAdHoc.section_tag(indent_tag_sym)
                script = ''.join((
                    '# ' + indent_tag + ' 4\n',
                    script,
                    '# ' + indent_tag + '\n',
                    ))
                script = RtAdHoc.indent_sections(script, indent_tag_sym)
                script = RtAdHoc.section_tag_remove(script, indent_tag_sym)
                docu_input = RtAdHoc.activate_macros(source)
                docu_input = docu_input.replace(RtAdHoc.section_tag('adhoc_x_script'), script.rstrip())
                docu_input = docu_input.replace('i:' 'adhoc_', '<:' 'adhoc_')
                docu_input = docu_input.replace('u:' 'adhoc_', '@:' 'adhoc_')
                docu_input = RtAdHoc.get_named_template(source=docu_input)
                docu_input = RtAdHoc.line_tag_remove(docu_input, '[^:]+', True, ('o:', ':>'))
                RtAdHoc.write_source('-', docu_input)

                compiled = RtAdHoc.activate_macros(compiled)
                docu_input = compiled
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
# **Overview**
#
# The entire initialization code looks like this::
#
# <:adhoc_x_script:>
#
# **Uncompiled Script**
#
# The script starts with the AdHoc run-time declaration ::
#
# @|:uc_descr_out:|>
# **Compiled Script**
#
# After adhoc compilation, the run-time class is added and the script
# is modified to::
#
# @|:uc_descr_end:|>

### show code for input only:

# @|:uc_code_beg:|>
# o:adhoc_template:>
# @:adhoc_run_time:@

# o:adhoc_template:>
# @|:uc_code_end:|>

### show description as code for output only:

# i:adhoc_indent:> 4
# @|:uc_descr_beg:|>
# @|:uc_descr_out:|>
# class RtAdHoc (object):
#     ...

# @|:uc_descr_end:|>
# i:adhoc_indent:>

# --------------------------------------------------
# @|:uc_descr_beg:|>
# The uncompiled script uses modules :mod:`adhoc` or :mod:`rt_adhoc`
# for class :class:`RtAdHoc`.
#
# @|:uc_descr_out:|>
# Since :class:`RtAdHoc` is incorporated verbatim, there is no need to
# import :mod:`adhoc` or :mod:`rt_adhoc` anymore::
#
# @|:uc_descr_end:|>

# --------------------------------------------------
# @|:uc_descr_beg:|>
#
# Add executable search path to Python module search path::
#
# @|:uc_descr_out:|>
# @|:uc_descr_end:|>

# @|:uc_code_beg:|>
# @:adhoc_disable:@
import os
import sys
os_path = os.defpath
if 'PATH' in os.environ:
    os_path = os.environ['PATH']
sys_path = sys.path
sys.path.extend(os_path.split(os.pathsep))
# @|:uc_code_end:|>

# --------------------------------------------------
# @|:uc_descr_beg:|>
#
# Import :mod:`adhoc` and use class :class:`adhoc.AdHoc` as
# :class:`RtAdHoc`::
#
# @|:uc_descr_out:|>
# @|:uc_descr_end:|>

# @|:uc_code_beg:|>
try:
    import adhoc
    from adhoc import AdHoc as RtAdHoc
# @|:uc_code_end:|>

# --------------------------------------------------
# @|:uc_descr_beg:|>
#
# Use exported :mod:`rt_adhoc` module, if :mod:`adhoc` is not
# available::
#
# @|:uc_descr_out:|>
# @|:uc_descr_end:|>

# @|:uc_code_beg:|>
except ImportError:
    try:
        import rt_adhoc
        from rt_adhoc import RtAdHoc
# @|:uc_code_end:|>

# --------------------------------------------------
# @|:uc_descr_beg:|>
#
# Let the script continue, even if :class:`RtAdHoc` is not available:
#
#     ::
#
# @|:uc_descr_out:|>
# @|:uc_descr_end:|>

# @|:uc_code_beg:|>
    except ImportError:
        pass
# @|:uc_code_end:|>

# --------------------------------------------------
# @|:uc_descr_beg:|>
#
# Restore the standard module search path::
#
# @|:uc_descr_out:|>
# @|:uc_descr_end:|>

# @|:uc_code_beg:|>
sys.path = sys_path
# @:adhoc_disable:@

# @|:uc_code_end:|>
# --------------------------------------------------
# generator meta program
if __name__ == '__main__':
    as_module = False
    main(sys.argv) and exit(0)
else:
    as_module = True
if not as_module:
    pass

# --------------------------------------------------
# @|:uc_descr_beg:|>
# From here on, RtAdHoc can be used for both the uncompiled and compiled version of the script.
#
# @|:uc_descr_out:|>
# The rest of the script is unmodified.
#
# @|:uc_descr_end:|>

# :ide: COMPILE: Run with --template macros
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --template macros")))

# :ide: COMPILE: Run with --compile
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --compile")))

# :ide: COMPILE: Run with --export; diff
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --export; diff -u use_case_000_.py __use_case_export__/" (file-name-nondirectory (buffer-file-name)))))

# :ide: COMPILE: Run with --compile >use_case_000.py && --export &&  diff && rm
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --compile >use_case_000.py && python use_case_000.py --export && diff -u use_case_000_.py __use_case_export__/use_case_000.py && rm -rf __use_case_export__")))

# :ide: COMPILE: Run with --compile >use_case_000.py
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --compile >use_case_000.py")))

# :ide: COMPILE: Run with --template
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --template")))

# :ide: COMPILE: Run with --doc
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --doc")))

# :ide: COMPILE: Run with --doc | diff
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --doc | ( if test -r uc000; then echo 'DIFF'; diff -u uc000 -; else echo 'STORE'; cat >uc000; fi)")))

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
