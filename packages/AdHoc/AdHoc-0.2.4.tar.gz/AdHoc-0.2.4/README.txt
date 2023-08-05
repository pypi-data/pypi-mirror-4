.. -*- mode: rst; coding: utf-8 -*-
.. role:: mod(strong)
.. role:: func(strong)
.. role:: class(strong)
.. role:: attr(strong)
.. role:: meth(strong)

AdHoc Standalone Python Script Generator
########################################

The `AdHoc` compiler can be used as a program (see `Script Usage`_)
as well as a module (see :class:`adhoc.AdHoc`).

Since the `AdHoc` compiler itself is installed as a compiled `AdHoc`
script, it serves as its own usage example.

After installation of the `adhoc.py` script, the full source can be
obtained in directory ``__adhoc__``, by executing::

    adhoc.py --explode


Purpose
=======

`AdHoc` provides python scripts with

- template facilities
- default file generation
- standalone module inclusion

`AdHoc` has been designed to provide an implode/explode cycle:

========  =======  =========  =======  =========
source_0                               xsource_0
source_1  implode             explode  xsource_1
...       ------>  script.py  ------>  ...
source_n                               xsource_n
========  =======  =========  =======  =========

where ``xsource_i === source_i``. I.e., ``diff source_i xsource_i``
does not produce any output.

Quickstart
==========

module.py:

    | # -\*- coding: utf-8 -\*-
    | mvar = 'value'

script.py:

    | # -\*- coding: utf-8 -\*-
    | # |adhoc_run_time|
    | import module # |adhoc|
    | print('mvar: ' + module.mvar)

Compilation::

    adhoc.py --compile script.py >/tmp/script-compiled.py

Execution outside source directory::

    cd /tmp && python script-compiled.py

shows::

    mvar: value

Decompilation::

    cd /tmp && \
    mkdir -p __adhoc__ && \
    adhoc.py --decompile <script-compiled.py >__adhoc__/script.py

.. |@:| replace:: `@:`
.. |:@| replace:: `:@`
.. |adhoc_run_time| replace:: |@:|\ `adhoc_run_time`\ |:@|
.. |adhoc| replace:: |@:|\ `adhoc`\ |:@|

Description
===========

The `AdHoc` compiler/decompiler parses text for tagged lines and
processes them as instructions.

The minimal parsed entity is a tagged line, which is any line
containing a recognized `AdHoc` tag.

All `AdHoc` tags are enclosed in delimiters (default: |@:| and |:@|). E.g:

  |@:|\ adhoc\ |:@|

Delimiters come in several flavors, namely line and section
delimiters and a set of macro delimiters. By default, line and
section delimiters are the same, but they can be defined separately.

`Flags`_ are tagged lines, which denote a single option or
command. E.g.:

  | import module     # |@:|\ adhoc\ |:@|
  | # |@:|\ adhoc_self\ |:@| my_module_name

`Sections`_ are tagged line pairs, which delimit a block of
text. The first tagged line opens the section, the second tagged
line closes the section. E.g.:

  | # |@:|\ adhoc_enable\ |:@|
  | # disabled_command()
  | # |@:|\ adhoc_enable\ |:@|

`Macros`_ have their own delimiters (default: |@m| and |m>|). E.g.:

  | # |@m|\ MACRO_NAME\ |m>|

The implementation is realized as class :class:`adhoc.AdHoc` which
is mainly used as a namespace. The run-time part of
:class:`adhoc.AdHoc` -- which handles module import and file export
-- is included verbatim as class :class:`RtAdHoc` in the generated
output.

Flags
-----

:|adhoc_run_time|:
    The place where the `AdHoc` run-time code is added.  This flag must
    be present in files, which use the |adhoc| import feature.  It
    is not needed for the enable/disable features.

:|adhoc| [force] [flat | full]:
    Mark import line for run-time compilation.

    If ``force`` is specified, the module is imported, even if it
    was imported before.

    If ``flat`` is specified, the module is not recursively
    exported.

    If ``full`` is specified, the module is recursively
    exported. (This parameter takes priority over ``flat``).

    If neither ``flat`` nor ``full`` are specified,
    :attr:`adhoc.AdHoc.flat` determines the export scope.

    This flag is ignored, if the line is commented out. E.g.:

      | # import module  # |adhoc|

.. _adhoc_include:

:|adhoc_include| file_spec, ...:
    Include files for unpacking. ``file_spec`` is one of

    :file:
      ``file`` is used for both input and output.

    :file ``from`` default-file:
      ``file`` is used for input and output. if ``file`` does not
      exist, ``default-file`` is used for input.

    :source-file ``as`` output-file:
      ``source-file`` is used for input. ``output-file`` is used for
      output. If ``source-file`` does not exist, ``output-file`` is
      used for input also.

    This flag is ignored, if double commented. E.g.:

      | # # |adhoc_include| file

:|adhoc_verbatim| [flags] file_spec, ...:
    Include files for verbatim extraction. See adhoc_include_ for
    ``file_spec``.

    The files are included as |adhoc_template_v| sections. `file` is used
    as `export_file` mark. If `file` is ``--``, the template disposition
    becomes standard output.

    Optional flags can be any combination of ``[+|-]NUM`` for
    indentation and ``#`` for commenting. E.g.:

      | # |adhoc_verbatim| +4# my_file from /dev/null

    `my_file` (or `/dev/null`) is read, commented and indented 4
    spaces.

    If the |adhoc_verbatim| tag is already indented, the specified
    indentation is subtracted.

    This flag is ignored, if double commented. E.g.:

      | # # |adhoc_verbatim| file

:|adhoc_self| name ...:
    Mark name(s) as currently compiling.  This is useful, if
    `__init__.py` imports other module parts. E.g:

      | import pyjsmo             # |@:|\ adhoc\ |:@|

    where ``pyjsmo/__init__.py`` contains:

      | # |@:|\ adhoc_self\ |:@| pyjsmo
      | from pyjsmo.base import * # |@:|\ adhoc\ |:@|

:|adhoc_compiled|:
    If present, no compilation is done on this file. This flag is
    added by the compiler to the run-time version.

Sections
--------

:|adhoc_enable|:
    Leading comment char and exactly one space are removed from lines
    in these sections.

:|adhoc_disable|:
    A comment char and exactly one space are added to non-blank
    lines in these sections.

:|adhoc_template| -mark | export_file:
    If mark starts with ``-``, the output disposition is standard output
    and the template is ignored, when exporting.

    Otherwise, the template is written to output_file during export.

    All template parts with the same mark/export_file are concatenated
    to a single string.

:|adhoc_template_v| export_file:
    Variation of |adhoc_template|. Automatically generated by |adhoc_verbatim|.

:|adhoc_uncomment|:
    Treated like |adhoc_enable| before template output.

:|adhoc_indent| [+|-]NUM:
    Add or remove indentation before template output.

:|adhoc_import|:
    Imported files are marked as such by the compiler. There is no
    effect during compilation.

:|adhoc_unpack|:
    Included files are marked as such by the compiler. There is no
    effect during compilation.

:|adhoc_remove|:
    Added sections are marked as such by the compiler. Removal is
    done when exporting.

    Before compilation, existing |adhoc_remove| tags are renamed to
    |adhoc_remove_|.

    After automatically added |adhoc_remove| sections have been
    removed during export, remaining |adhoc_remove_| tags are
    renamed to |adhoc_remove| again.

    .. note:: Think twice, before removing material from original
       sources at compile time. It will violate the condition
       ``xsource_i === source_i``.

:|adhoc_run_time_engine|:
    The run-time class :class:`RtAdHoc` is enclosed in this special
    template section.

    It is exported as ``rt_adhoc.py`` during export.

Macros
------

Macros are defined programmatically::

    AdHoc.macros[MACRO_NAME] = EXPANSION_STRING

A macro is invoked by enclosing a MACRO_NAME in
:attr:`adhoc.AdHoc.macro_call_delimiters`. (Default: |@m|, |m>|).

:|MACRO_NAME|:
    Macro call.

Internal
--------

:|adhoc_run_time_class|:
    Marks the beginning of the run-time class.  This is only
    recognized in the `AdHoc` programm/module.

:|adhoc_run_time_section|:
    All sections are concatenated and used as run-time code.  This is
    only recognized in the `AdHoc` programm/module.

In order to preserve the ``xsource_i === source_i`` bijective
condition, macros are expanded/collapsed with special macro
definition sections. (See :attr:`adhoc.AdHoc.macro_xdef_delimiters`;
Default: |<m|, |m@|).

:|adhoc_macro_call|:
    Macro call section.

:|adhoc_macro_expansion|:
    Macro expansion section.


AdHoc Script
============

.. |adhoc_self| replace:: |@:|\ `adhoc_self`\ |:@|
.. |adhoc_include| replace:: |@:|\ `adhoc_include`\ |:@|
.. |adhoc_verbatim| replace:: |@:|\ `adhoc_verbatim`\ |:@|
.. |adhoc_compiled| replace:: |@:|\ `adhoc_compiled`\ |:@|
.. |adhoc_enable| replace:: |@:|\ `adhoc_enable`\ |:@|
.. |adhoc_disable| replace:: |@:|\ `adhoc_disable`\ |:@|
.. |adhoc_template| replace:: |@:|\ `adhoc_template`\ |:@|
.. |adhoc_template_v| replace:: |@:|\ `adhoc_template_v`\ |:@|
.. |adhoc_uncomment| replace:: |@:|\ `adhoc_uncomment`\ |:@|
.. |adhoc_indent| replace:: |@:|\ `adhoc_indent`\ |:@|
.. |adhoc_import| replace:: |@:|\ `adhoc_import`\ |:@|
.. |adhoc_unpack| replace:: |@:|\ `adhoc_unpack`\ |:@|
.. |adhoc_remove| replace:: |@:|\ `adhoc_remove`\ |:@|
.. |adhoc_remove_| replace:: |@:|\ `adhoc_remove_`\ |:@|
.. |adhoc_run_time_class| replace:: |@:|\ `adhoc_run_time_class`\ |:@|
.. |adhoc_run_time_section| replace:: |@:|\ `adhoc_run_time_section`\ |:@|
.. |adhoc_run_time_engine| replace:: |@:|\ `adhoc_run_time_engine`\ |:@|
.. |@m| replace:: `@|:`
.. |m>| replace:: `:|>`
.. |<m| replace:: `<|:`
.. |m@| replace:: `:|@`
.. |MACRO_NAME| replace:: |@m|\ `MACRO_NAME`\ |m>|
.. |adhoc_macro_call| replace:: |<m|\ `adhoc_macro_call`\ |m@|
.. |adhoc_macro_expansion| replace:: |<m|\ `adhoc_macro_expansion`\ |m@|



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
                        output directory (default `__adhoc__`).
  -o, --output OUT      output file for --compile/output directory for
                        --decompile.

  -q, --quiet           suppress warnings
  -v, --verbose         verbose test output
  --debug[=NUM]         show debug information

  -h, --help            display this help message
  --documentation       display module documentation.

  --template list       show available templates.
  --template[=NAME]     extract named template to standard
                        output. Default NAME is `-`.
  --extract[=DIR]       extract adhoc files to directory DIR (default: `.`)
  --explode[=DIR]       explode script with adhoc in directory DIR
                        (default `__adhoc__`)
  --implode             implode script with adhoc
  --install             install adhoc.py script

  -t, --test            run doc tests
  ===================== ==================================================

`adhoc.py` is compatible with Python 2.5+ and Python 3. (For Python
2.5 the packages `stringformat` and `argparse` are needed and
included.)

.. _END_OF_HELP:

.. |=NUM| replace:: `[=NUM]`

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
=========================================== ========================== ================
                  Command                            Template                Type
=========================================== ========================== ================
adhoc.py --template adhoc_test              # !adhoc_test              adhoc_import
adhoc.py --template adhoc_test.sub          # !adhoc_test.sub          adhoc_import
adhoc.py --template argparse_local          # !argparse_local          adhoc_import
adhoc.py --template namespace_dict          # !namespace_dict          adhoc_import
adhoc.py --template stringformat_local      # !stringformat_local      adhoc_import
adhoc.py --template use_case_000_           # !use_case_000_           adhoc_import
adhoc.py --template use_case_001_templates_ # !use_case_001_templates_ adhoc_import
adhoc.py --template use_case_002_include_   # !use_case_002_include_   adhoc_import
adhoc.py --template use_case_003_import_    # !use_case_003_import_    adhoc_import
adhoc.py --template use_case_005_nested_    # !use_case_005_nested_    adhoc_import
adhoc.py --template docutils.conf           # docutils.conf            adhoc_template_v
adhoc.py --template                         # -                        adhoc_template
adhoc.py --template README.txt              # README.txt               adhoc_template
adhoc.py --template col-param-closure       # -col-param-closure       adhoc_template
adhoc.py --template doc/USE_CASES.txt       # doc/USE_CASES.txt        adhoc_template
adhoc.py --template doc/index.rst           # doc/index.rst            adhoc_template
adhoc.py --template max-width-class         # -max-width-class         adhoc_template
adhoc.py --template rst-to-ascii            # -rst-to-ascii            adhoc_template
adhoc.py --template test                    # -test                    adhoc_template
adhoc.py --template MANIFEST.in             # !MANIFEST.in             adhoc_unpack
adhoc.py --template Makefile                # !Makefile                adhoc_unpack
adhoc.py --template README.css              # !README.css              adhoc_unpack
adhoc.py --template doc/Makefile            # !doc/Makefile            adhoc_unpack
adhoc.py --template doc/conf.py             # !doc/conf.py             adhoc_unpack
adhoc.py --template doc/make.bat            # !doc/make.bat            adhoc_unpack
adhoc.py --template setup.py                # !setup.py                adhoc_unpack
=========================================== ========================== ================

``python adhoc.py --template`` prints the standard template ``-``:

>>> ign = main('./adhoc.py --template'.split())
Standard template.

``python adhoc.py --template test`` prints the template named ``-test``.
the leading ``-`` signifies disposition to standard output:

>>> ign = main('./adhoc.py --template test'.split())
Test template.

Extract
-------

The default destination for extracting files is the current working
directory.

Files extracted consist of packed files generated by |adhoc_include|,
templates generated by |adhoc_verbatim| and templates with a file
destination other than standard output.

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
__adhoc_extract__/doc/conf.py
__adhoc_extract__/doc/index.rst
__adhoc_extract__/doc/make.bat
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

Files exported consist of imported modules generated by |adhoc| and all
files covered in section `Extract`_.

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
__adhoc_explode__/doc/conf.py
__adhoc_explode__/doc/index.rst
__adhoc_explode__/doc/make.bat
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



.. :ide: COMPILE: render reST as HTML
.. . (let* ((fp (buffer-file-name)) (fn (file-name-nondirectory fp))) (save-match-data (if (string-match-t "[.][^.]*$" fn) (setq fn (replace-match "" nil t fn)))) (let ((args (concat " " fp " | ws_rst2html.py --traceback --cloak-email-addresses | tee " fn ".html "))) (save-buffer) (compile (concat "PATH=\".:$PATH\"; cat " args))))

.. 
.. Local Variables:
.. mode: rst
.. snip-mode: rst
.. truncate-lines: t
.. symbol-tag-symbol-regexp: "[-0-9A-Za-z_#]\\([-0-9A-Za-z_. ]*[-0-9A-Za-z_]\\|\\)"
.. symbol-tag-auto-comment-mode: nil
.. symbol-tag-srx-is-safe-with-nil-delimiters: nil
.. End:
