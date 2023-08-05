#!/bin/sh

# z-massage-index.sh - Add stuff to HTML (post-build step)

# usage: z-massage-index.sh [file ...]
#
# Example:
#     z-massage-index.sh <README.html >index.html

# Copyright (C) 2012, Wolfgang Scherer, <Wolfgang.Scherer at gmx.de>
# Sponsored by WIEDENMANN SEILE GMBH, http://www.wiedenmannseile.de
#
# This file is part of Wiedenmann Docutils Extensions.
#
:  # script help
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

# --------------------------------------------------
# |||:sec:||| FUNCTIONS
# --------------------------------------------------

usage ()
{
    script_help="script-help"
    ( "${script_help}" ${1+"$@"} "${0}" ) 2>/dev/null \
    || ${SED__PROG-sed} -n '3,/^[^#]/{;/^[^#]/d;p;}' "${0}";
}

# (progn (forward-line 1)(snip-insert-mode "^sh_f.awk_var_escape_setup$" t))
bs_escape ()
{
    printf "%s\n" "${*}" | ${SED__PROG-sed} 's,\\,\\\\,g'
}

no_bs_escape ()
{
    printf "%s\n" "${*}"
}

awk_var_escape_setup ()
{
    # It seems most awk's interpret backslashes in `-v var=value',
    # however, mawk(1) does not
    # |:DBG:| escape_it (original-awk): [bs_escape]
    # |:DBG:| escape_it (awk)         : [bs_escape]
    # |:DBG:| escape_it (gawk)        : [bs_escape]
    # |:DBG:| escape_it (nawk)        : [bs_escape]
    # |:DBG:| escape_it (mawk)        : [no_bs_escape]
    escape_it="no_bs_escape"
    AWK_VAR_ESCAPE_CHECK="${1-'\.'}"
    AWK_VAR_ESCAPE_RESULT="$( ${AWK__PROG-awk} -v check="${AWK_VAR_ESCAPE_CHECK}" -- 'BEGIN { print check; }' 2>/dev/null </dev/null )"
    test x"${AWK_VAR_ESCAPE_CHECK}" = x"${AWK_VAR_ESCAPE_RESULT}" || escape_it="bs_escape"
    AWK_VAR_ESCAPE_RESULT="$( ${AWK__PROG-awk} -v check="$( ${escape_it} "${AWK_VAR_ESCAPE_CHECK}" )" -- 'BEGIN { print check; }' 2>/dev/null </dev/null )"
    if test x"${AWK_VAR_ESCAPE_CHECK}" != x"${AWK_VAR_ESCAPE_RESULT}"
    then
        printf >&2 "%s\n" 'error: get another awk(1).'
        exit 1
    fi
}

test x"${1+set}" = xset && \
case "${1}" in
-\?|-h|--help) usage; exit 0;;
--docu) usage --full; exit 0;;
esac

# --------------------------------------------------
# |||:sec:||| MAIN
# --------------------------------------------------

JS_BITBUCKET='<script type="text/javascript"><!--
      // Add a trailing slash to the URL, if it does not end in `.html'\'' or `/'\''.
      // Elegant solution from David Chambers [Atlassian]
      if (!/(\.html|\/)$/.test(location.pathname)) {
          location.pathname += '\''/'\'';
      }
      //--></script>'

# |:here:|

awk_var_escape_setup "${JS_BITBUCKET}"
${AWK__PROG-awk} -v JS_BITBUCKET="$( ${escape_it} "${JS_BITBUCKET}" )" -- '
{
    print;
}
/<[Hh][Ee][Aa][Dd][^>]*>/ {
    print JS_BITBUCKET;
}
' ${1+"$@"}

exit # |||:here:|||

#
# :ide-menu: Emacs IDE Main Menu - Buffer @BUFFER@
# . M-x `eIDE-menu' (eIDE-menu "z")

# :ide: SNIP: insert OPTION LOOP
# . (snip-insert-mode "sh_b.opt-loop" nil t)

# :ide: SHELL: Run with --docu
# . (progn (save-buffer) (shell-command (concat "sh " (file-name-nondirectory (buffer-file-name)) " --docu")))

# :ide: SHELL: Run with --help
# . (progn (save-buffer) (shell-command (concat "sh " (file-name-nondirectory (buffer-file-name)) " --help")))

# :ide: SHELL: Run w/o args
# . (progn (save-buffer) (shell-command (concat "sh " (file-name-nondirectory (buffer-file-name)) " ")))

# :ide: COMPILE: Run with `cat README.html | ... | tee index.html | diff'
# . (progn (save-buffer) (compile (concat "cat README.html | python ./" (file-name-nondirectory (buffer-file-name)) " | tee index.html | diff -ubB README.html -")))

# :ide: COMPILE: Run with `cat README.html | ... | tee index.html | diff'
# . (progn (save-buffer) (compile (concat "cat README.html | sh ./" (file-name-nondirectory (buffer-file-name)) " | tee index.html | diff -ubB README.html -")))

#
# Local Variables:
# mode: sh
# comment-start: "#"
# comment-start-skip: "#+"
# comment-column: 0
# End:
# mmm-classes: (here-doc ide-entries)
