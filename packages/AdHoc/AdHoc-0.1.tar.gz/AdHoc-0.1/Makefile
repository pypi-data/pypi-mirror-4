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

EXTRA_DIST =

CLEANFILES =
CLEANFILES += $(PYTHON_PROGRAMS)
CLEANFILES += MANIFEST
CLEANFILES += *.pyc

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

all-local: README.txt README.html doc/index.rst

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
	python adhoc.py --template=README.txt >$@

doc/index.rst: adhoc.py
	python adhoc.py --template=doc/index.rst >$@

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
