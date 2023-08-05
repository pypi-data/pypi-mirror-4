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

# Self-referential stuff gets pretty hilarious after a while ...
# Two and a half layers of template tagging :)
#
# Output is the same for uncompiled and compiled script.
# Output with option --docu is the same for uncompiled and compiled
# script.

def main():
    '''docu extractor'''
    if len(sys.argv) > 1 and sys.argv[1] == '--docu':
        source = RtAdHoc.read_source(__file__)
        if 'adhoc' not in globals():
            compiled = source
            source = RtAdHoc.export_source(source)
        else:
            compiled = None
        RtAdHoc.line_delimiters = ('<:', ':>')
        RtAdHoc.section_delimiters = ('<:', ':>')
        docu_input = RtAdHoc.get_named_template(source=source)
        docu_input = RtAdHoc.line_tag_remove(docu_input, '[^:]+', True, ('x:', ':x'))
        RtAdHoc.write_source('-', docu_input)

        if compiled is None:
            pcompiled = os.popen('python adhoc.py --compile ' + __file__, 'rb')
            compiled = pcompiled.read()
            pcompiled.close()
        compiled = compiled.replace('x:' 'adhoc_template' ':x', '<:' 'adhoc_template' ':>')
        RtAdHoc.write_source('-', RtAdHoc.get_named_template(source=compiled))
        exit(0)

# <:adhoc_uncomment:>
# x:adhoc_template:x
# <:adhoc_template:> -
# Use Cases
# =========
#
# Templates
# ---------
#
# E.g::
#
# <:adhoc_template:>
# x:adhoc_template:x
# <:adhoc_uncomment:>

# <:adhoc_indent:> 4
# <:adhoc_template:> -
# x:adhoc_template:x
# @:adhoc_run_time:@
# x:adhoc_template:x
import os
# @:adhoc_disable:@
# Setup adhoc module as RtAdHoc
import sys
os_path = os.defpath
if 'PATH' in os.environ:
    os_path = os.environ['PATH']
sys.path.extend(os_path.split(os.pathsep))
import adhoc
from adhoc import AdHoc as RtAdHoc
adhoc.__file__ = __file__
# @:adhoc_disable:@
RtAdHoc.quiet = True
RtAdHoc.extract_templates()

rc_file_name = '~/.uc00.rc'
# @:adhoc_template:@ ~/.uc00.rc
# -*- coding: utf-8 -*-
default_value = 'default'
another_value = 'other'
# @:adhoc_template:@

rc_file = os.path.expanduser(rc_file_name)
rc_source = RtAdHoc.read_source(rc_file, decode=False)
exec(rc_source, globals(), locals())

# <:adhoc_template:> -
main()

# <:adhoc_template:>
print('default_value: ' + default_value)
print('another_value: ' + another_value)
# <:adhoc_template:>
# <:adhoc_indent:>

# <:adhoc_uncomment:>
# x:adhoc_template:x
# <:adhoc_template:> -
#
# This will make sure, that the file ``~/.uc00.rc`` exists and that it
# defines the default values.
#
# After adhoc compilation, the run time class is added and the script
# is modified to::
#
#     # ... run-time class skipped ...
#
# <:adhoc_template:>
# x:adhoc_template:x
# <:adhoc_uncomment:>

# :ide: COMPILE: python adhoc.py --compile use_case_000_templates_.py >use_case_000_templates.py
# . (progn (save-buffer) (compile (concat "python adhoc.py --compile use_case_000_templates_.py >use_case_000_templates.py")))

# :ide: COMPILE: Run with --docu
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --docu")))

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
