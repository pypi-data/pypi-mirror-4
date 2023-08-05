# -*- makefile -*-

top_srcdir = .
srcdir = .
bindir = /usr/local/bin

PYTHON_SOURCES =
PYTHON_SOURCES += adhoc.py

ADHOC_PY_DEPS += Makefile README.css docutils.conf setup.py
ADHOC_PY_DEPS += doc/conf.py doc/make.bat doc/Makefile
ADHOC_PY_DEPS += stringformat_local.py
ADHOC_PY_DEPS += argparse_local.py
ADHOC_PY_DEPS += namespace_dict.py
ADHOC_PY_DEPS += $(USE_CASE_TXT_DEPS)

USE_CASE_TXT_DEPS += use_case_000_.py
USE_CASE_TXT_DEPS += use_case_001_templates_.py
USE_CASE_TXT_DEPS += use_case_002_include_.py
USE_CASE_TXT_DEPS += use_case_003_import_.py
USE_CASE_TXT_DEPS += use_case_005_nested_.py

EXTRA_DIST =

CLEANFILES =
CLEANFILES += $(PYTHON_PROGRAMS)
CLEANFILES += MANIFEST
CLEANFILES += *.pyc
CLEANFILES += use_case_000.py
CLEANFILES += use_case_001_templates.py
CLEANFILES += use_case_002_include.py
CLEANFILES += use_case_003_import.py
CLEANFILES += use_case_005_nested.py
CLEANFILES += uc000 uc001 uc002 uc003 uc005
CLEANFILES += adhoc_check_module_setup.e
CLEANFILES += adhoc_check_module_setup.t

PYTHON_PROGRAMS = $(patsubst %,dist/%,$(PYTHON_SOURCES))

DISTFILES =
DISTFILES += Makefile
DISTFILES += $(PYTHON_SOURCES)
DISTFILES += $(PYTHON_PROGRAMS)
DISTFILES += $(EXTRA_DIST)

dist/%.py: %.py adhoc.py
	dist/adhoc.py --compile $< >$@
	chmod 755 $@

default: all

all: $(DISTFILES) all-local

all-local: README.txt README.html doc/index.rst doc/USE_CASES.txt

clean:
	test -z '$(CLEANFILES)' || rm -rf $(CLEANFILES)

install-local: all
	mkdir -p $(bindir)
	@(						\
	list='$(PYTHON_PROGRAMS)'; test -z "$$list" ||	\
	for prog in $$list; do				\
	  echo "cp -p $$prog $(bindir)";		\
	  cp -p $$prog $(bindir);			\
	done;						\
	)

install: install-local ftp

dist:

tags-rc:
	gen_tags.sh --template
tags:
	gen_tags.sh --force

dist:
	mkdir -p $@

dist/adhoc.py: adhoc.py $(ADHOC_PY_DEPS)
	mkdir -p dist
	python adhoc.py --compile $< >$@ || (rm -f $@; exit 1)
	chmod 755 $@

ftp:
	test ! -w /srv/ftp/pub ||			\
	( $(MAKE) bindir=/srv/ftp/pub install-local )

README.html: README.txt README.css
	rst2html.py --cloak-email-addresses $< > $@

README.txt: adhoc.py
	python adhoc.py --template=$@ >$@

doc/index.rst: adhoc.py
	python adhoc.py --template=$@ >$@

doc/USE_CASES.txt: adhoc.py $(USE_CASE_TXT_DEPS)
	python adhoc.py --template=$@ >$@

.PHONY: doc
doc: all
	( cd doc && $(MAKE) html)

# |:here:|
# :ide-menu: Emacs IDE Main Menu - Buffer @BUFFER@
# . M-x `eIDE-menu' ()(eIDE-menu "z")

# :ide: COMPILE: tags
# . (let ((args "tags")) (compile (concat "make -k " args)))

# :ide: COMPILE: dist
# . (let ((args "dist")) (compile (concat "make -k " args)))

# :ide: COMPILE: install
# . (let ((args "install")) (compile (concat "make -k " args)))

# :ide: COMPILE: ftp
# . (let ((args "ftp")) (compile (concat "make -k " args)))

# :ide: COMPILE: doc
# . (let ((args "doc")) (compile (concat "make -k " args)))

# :ide: COMPILE: clean
# . (let ((args "clean")) (compile (concat "make -k " args)))

# :ide: COMPILE: Standard
# . (let ((args "")) (compile (concat "make -k " args)))
