.. role:: mod(strong)
.. role:: class(strong)
.. role:: func(strong)
.. role:: meth(strong)

AdHoc Standalone Package Generator
##################################

AdHoc consists of a single python source file `adhoc.py`, which can
be used as a program (see `Script Usage`_) as well as a module (See
:class:`adhoc.AdHoc`).

After installation of the binary package, run ``adhoc.py --explode``
to obtain the full source in directory ``__adhoc__``.


Description
===========

`AdHoc` parses text for tagged lines and processes them as instructions.

The minimal parsed entity is a marker line, which is any line
containing a recognized `AdHoc` tag.

Marker lines come in two flavors, namely flags and section delimiters.

All `AdHoc` tags are enclosed in |@:| and |:@|. E.g:

  |@:|\ adhoc\ |:@|

Flags are marker lines, which denote a single option or command (see
`Flags`_). E.g.:

  | import module     # |@:|\ adhoc\ |:@|
  | # |@:|\ adhoc_self\ |:@| my_module_name

Sections are marker line pairs, which delimit a block of text. The
first marker line opens the section, the second marker line closes the
section (see `Sections`_). E.g.:

  | # |@:|\ adhoc_enable\ |:@|
  | # disabled_command()
  | # |@:|\ adhoc_enable\ |:@|

The implementation is realized as class :class:`adhoc.AdHoc` which is mainly
used as a namespace. The runtime part of :class:`adhoc.AdHoc` which handles
module import and file export is included verbatim as class
:class:`RtAdHoc` in the generated output.

Flags
-----

:|adhoc_runtime|:
  The place where the AdHoc runtime code is added.  This flag must be
  present in files, which use the |adhoc| import feature.  It is not
  needed for the enable/disable features.

:|adhoc|:
  Mark import line for run-time compilation.  If the line is commented
  out, the respective module is not compiled.

:|adhoc_include| file [from default-file], ...:
    Include files for unpacking. `file` is the name for extraction. If
    `file` is not found, `default-file` is used for inclusion.

:|adhoc_verbatim| [flags] file [from default-file], ...:
    Include files for verbatim extraction. `file` is the name for
    extraction. If `file` is not found, `default-file` is used for
    inclusion.

    The files are included as |adhoc_template_v| sections. `file` is used
    as `export_file` mark. If `file` is ``--``, the template disposition
    becomes standard output.

    Optional flags can be any combination of ``[+|-]NUM`` for
    indentation and ``#`` for commenting. E.g:

      # |adhoc_verbatim| +4# my_file from /dev/null

    `my_file` (or `/dev/null`) is read, commented and indented 4
    spaces. If the |adhoc_verbatim| tag is already indented, the
    specified indentation is subtracted.

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
    A comment char and exactly one space are added to lines in these
    sections.

:|adhoc_template| -mark | export_file:
    If mark starts with ``-``, the output disposition is standard output
    and the template is ignored, when exporting.

    Otherwise, the template is written to output_file during export.

    All template parts with the same mark/export_file are concatenated
    to a single string.

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
    Added sections are marked as such by the compiler.  The flag is
    renamed to |adhoc_remove_| during compilation.  Which in turn is
    renamed to |adhoc_remove| during export.

Internal
--------

:|adhoc_run_time_class|:
    Marks the beginning of the run-time class.  This is only
    recognized in the AdHoc programm/module.

:|adhoc_run_time_section|:
    All sections are concatenated and used as run-time code.  This is
    only recognized in the AdHoc programm/module.

\|:todo:| make enable/disable RX configurable


.. |@:| replace:: `@:`
.. |:@| replace:: `:@`
.. |adhoc_runtime| replace:: |@:|\ `adhoc_runtime`\ |:@|
.. |adhoc| replace:: |@:|\ `adhoc`\ |:@|
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


AdHoc Script/Module
===================


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
