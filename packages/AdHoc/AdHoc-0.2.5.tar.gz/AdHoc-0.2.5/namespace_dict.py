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
namespace_dict.py - dictionary based namespace

======  ====================
usage:  namespace_dict.py [OPTIONS]
or      import namespace_dict
======  ====================

Options
=======

  --template            extract minimized version of :class:`NameSpaceNS`

  -q, --quiet           suppress warnings
  -v, --verbose         verbose test output
  -d, --debug=NUM       show debug information
  -h, --help            display this help message

  --template list       show available templates.
  --template=NAME       extract named template to standard
                        output. Default NAME is `-`.
  --extract=DIR         extract adhoc files to directory DIR (default: `.`)
  --explode=DIR         explode script with adhoc in directory DIR
                        (default `__adhoc__`)
  --implode             implode script with adhoc

  -t, --test            run doc tests

Description
===========

The namespace functions are wrapped in class :class:`NameSpaceNS`,
which itself serves as a namespace container.

The namespace class generator :meth:`NameSpaceNS.namespace` is
exported as :class:`NameSpaceMeta`.

A namespace class inheriting from object, without dict interface is
defined as :class:`NameSpace`.

A namespace class inheriting from object, with complete dict interface
is defined as :class:`NameSpaceDict`.

The `--template` option

This implementation is compatible with Python 2.4+ and Python 3.

Examples
========

>>> ns = NameSpace()
>>> ns.attrib = 'value'
>>> ns.attrib2 = 'value2'
>>> printf(str(vars(ns)))
{'attrib2': 'value2', 'attrib': 'value'}

While a normal dict has special attributes

>>> dict().__setattr__ #doctest: +ELLIPSIS
<method-wrapper ...>

the namespace dict special attributes are hidden:

>>> ns.__setattr__ #doctest: +ELLIPSIS
Traceback (most recent call last):
...
AttributeError: 'namespace_' object has no attribute '__setattr__'

The only special attributes supported are

- `__dict__` to access the namespace dictionary

  This allows access to the dictionary via :func:`vars`:

  >>> vars(ns)['another'] = 'entry'
  >>> printf(str(vars(ns)))
  {'attrib2': 'value2', 'attrib': 'value', 'another': 'entry'}

- `_property_` to access the namespace class object

    >>> ns._property_.__class__.__name__
    'NameSpace'

    >>> ns._property_.__class__.__base__.__name__
    'namespace_'

- `__class__` to access the namespace closure class

  >>> ns.__class__.__name__
  'namespace_'

  >>> ns.__class__.__base__.__name__
  'object'

Module Members
==============
"""

# --------------------------------------------------
# |||:sec:||| COMPATIBILITY
# --------------------------------------------------

import sys
# (progn (forward-line 1) (snip-insert-mode "py.b.printf" t) (insert "\n"))
# adapted from http://www.daniweb.com/software-development/python/code/217214
try:
    printf = eval("print") # python 3.0 case
except SyntaxError:
    printf_dict = dict()
    try:
        exec("from __future__ import print_function\nprintf=print", printf_dict)
        printf = printf_dict["printf"] # 2.6 case
    except SyntaxError:
        def printf(*args, **kwd): # 2.4, 2.5, define our own Print function
            fout = kwd.get("file", sys.stdout)
            w = fout.write
            if args:
                w(str(args[0]))
            sep = kwd.get("sep", " ")
            for a in args[1:]:
                w(sep)
                w(str(a))
            w(kwd.get("end", "\n"))
    del printf_dict

# (progn (forward-line 1) (snip-insert-mode "py.b.sformat" t) (insert "\n"))
try:
    ('{0}').format(0)
    def sformat (fmtspec, *args, **kwargs):
        return fmtspec.format(*args, **kwargs)
except AttributeError:
    try:
        import stringformat
    except ImportError:
        try:
            import stringformat_local as stringformat
        except ImportError:
            printf('error: (nd) stringformat missing. Try `easy_install stringformat`.', file=sys.stderr)
    def sformat (fmtspec, *args, **kwargs):
        return stringformat.FormattableString(fmtspec).format(
            *args, **kwargs)

# (progn (forward-line 1) (snip-insert-mode "py.f.isstring" t) (insert "\n"))
# hide from 2to3
exec('''
def isstring(obj):
    return isinstance(obj, basestring)
''')
try:
    isstring("")
except NameError:
    def isstring(obj):
        return isinstance(obj, str) or isinstance(obj, bytes)

# (progn (forward-line 1) (snip-insert-mode "py.b.dict_items" t) (insert "\n"))
try:
    getattr(dict(), 'iteritems')
    ditems  = lambda d: getattr(d, 'iteritems')()
    dkeys   = lambda d: getattr(d, 'iterkeys')()
    dvalues = lambda d: getattr(d, 'itervalues')()
except AttributeError:
    ditems  = lambda d: getattr(d, 'items')()
    dkeys   = lambda d: getattr(d, 'keys')()
    dvalues = lambda d: getattr(d, 'values')()

import os
import re

# --------------------------------------------------
# |||:sec:||| CONFIGURATION
# --------------------------------------------------

__all__ = [
    'NameSpace',
    'NameSpaceDict',
    'NameSpaceMeta',
    'NameSpaceNS',
    ]

dbg_comm = ((('dbg_comm' in globals()) and (globals()['dbg_comm'])) or ('# '))
dbg_twid = ((('dbg_twid' in globals()) and (globals()['dbg_twid'])) or (9))
dbg_fwid = ((('dbg_fwid' in globals()) and (globals()['dbg_fwid'])) or (20))

# (progn (forward-line 1) (snip-insert-mode "py.b.dbg.setup" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.b.strings" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.f.strclean" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.f.issequence" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.b.logging" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.b.ordereddict" t) (insert "\n"))

# (progn (forward-line 1) (snip-insert-mode "py.main.pyramid.activate" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.main.project.libdir" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.main.sql.alchemy" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.main.sql.ws" t) (insert "\n"))

# @:adhoc_run_time:@
#import adhoc                                               # @:adhoc:@

# (progn (forward-line 1) (snip-insert-mode "py.b.posix" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.b.os.system.sh" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.b.prog.path" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.b.line.loop" t) (insert "\n"))

# --------------------------------------------------
# |||:sec:||| CLASSES
# --------------------------------------------------

# (progn (forward-line 1) (snip-insert-mode "py.c.placeholder.template" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.c.key.hash.ordered.dict" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.c.progress" t) (insert "\n"))

# (progn (forward-line -1) (insert "\n") (snip-insert-mode "py.s.class" t) (backward-symbol-tag 2 "fillme" "::"))

# --------------------------------------------------
# |||:sec:||| NAMESPACE CLOSURES
# --------------------------------------------------

import weakref

# @:adhoc_template:@ -
class NameSpaceNS(object):                                 # ||:cls:||
    # @:adhoc_template:@
    '''Class based namespace for dict based namespace.

    The dictonary interface of the namespace dict can be exposed on 3
    levels:

    1. expose_dict=0: No dict interface
    2. expose_dict=1: dict interface for namespace object
    3. expose_dict=2: dict interface for namespace class object
    '''

    # @:adhoc_template:@ -
    @staticmethod
    def no_attrib_msg(cls, name):                            # |:fnc:|
        msg = ("'", cls.__name__, "'",
               " object has no attribute '", name, "'")
        return ''.join(msg)

    @staticmethod
    def no_set_attrib_msg(cls, name):                        # |:fnc:|
        return "can't set attribute"

    @staticmethod
    def no_del_attrib_msg(cls, name):                        # |:fnc:|
        return "can't delete attribute"

    @staticmethod
    def property_closure(obj, expose_dict):                # ||:clo:||
        # @:adhoc_template:@
        '''Namespace class object property closure.'''
        # @:adhoc_template:@ -
        prop = weakref.ref(obj)
        cls = obj.__class__
        result = []
        def __getattr__(obj, name):                          # |:clm:|
            return super(cls, prop()).__getattribute__(name)
        result.append(__getattr__)
        def __setattr__(obj, name, value):                   # |:clm:|
            super(cls, prop()).__setattr__(name, value)
        result.append(__setattr__)
        def __delattr__(obj, name):                          # |:clm:|
            super(cls, prop()).__delattr__(name)
        result.append(__delattr__)
        if expose_dict > 1:
            def __cmp__(self, *args, **kwargs):
                return prop().__cmp__(*args, **kwargs)
            result.append(__cmp__)
            def __contains__(self, *args, **kwargs):
                return prop().__contains__(*args, **kwargs)
            result.append(__contains__)
            def __delitem__(self, *args, **kwargs):
                return prop().__delitem__(*args, **kwargs)
            result.append(__delitem__)
            def __eq__(self, *args, **kwargs):
                return prop().__eq__(*args, **kwargs)
            result.append(__eq__)
            def __ge__(self, *args, **kwargs):
                return prop().__ge__(*args, **kwargs)
            result.append(__ge__)
            def __getitem__(self, *args, **kwargs):
                return prop().__getitem__(*args, **kwargs)
            result.append(__getitem__)
            def __gt__(self, *args, **kwargs):
                return prop().__gt__(*args, **kwargs)
            result.append(__gt__)
            def __hash__(self, *args, **kwargs):
                return prop().__hash__(*args, **kwargs)
            result.append(__hash__)
            def __iter__(self, *args, **kwargs):
                return prop().__iter__(*args, **kwargs)
            result.append(__iter__)
            def __le__(self, *args, **kwargs):
                return prop().__le__(*args, **kwargs)
            result.append(__le__)
            def __len__(self, *args, **kwargs):
                return prop().__len__(*args, **kwargs)
            result.append(__len__)
            def __lt__(self, *args, **kwargs):
                return prop().__lt__(*args, **kwargs)
            result.append(__lt__)
            def __ne__(self, *args, **kwargs):
                return prop().__ne__(*args, **kwargs)
            result.append(__ne__)
            def __setitem__(self, *args, **kwargs):
                return prop().__setitem__(*args, **kwargs)
            result.append(__setitem__)
            def __sizeof__(self, *args, **kwargs):
                return prop().__sizeof__(*args, **kwargs)
            result.append(__sizeof__)
        return result

    @classmethod
    def property_(nsc, obj, expose_dict):                  # ||:clg:||
        # @:adhoc_template:@
        '''Property instance generator.'''
        # @:adhoc_template:@ -
        class property__(object):                            # |:ccl:|
            if expose_dict > 1:
                __getattribute__, __setattr__, __delattr__, \
                __cmp__, __contains__, __delitem__, __eq__, \
                __ge__, __getitem__, __gt__, __hash__, __iter__, \
                __le__, __len__, __lt__, __ne__, __setitem__, __sizeof__, \
                = (nsc.property_closure(obj, expose_dict))
            else:
                __getattribute__, __setattr__, __delattr__, \
                = (nsc.property_closure(obj, expose_dict))
        return property__()

    ignore_dict_attrs = [
        '__getattribute__',
        '__init__',
        '__new__',
        '__repr__',
        ]

    # @:adhoc_template:@
    known_dict_attrs = []

    # @:adhoc_template:@ -
    @classmethod
    def namespace_closure(nsc, expose_dict):               # ||:clo:||
        # @:adhoc_template:@
        '''Namespace closure.'''
        # @:adhoc_template:@ -
        ns = {}
        props = {
            '__dict__': ns
            # __class__
            # _property_
            }
        def __property_init__(obj, cls):                     # |:clm:|
            # @:adhoc_template:@
            '''Setup special __class__ and _property_ properties for object.'''
            # @:adhoc_template:@ -
            #            cls = object.__getattribute__(obj, '__class__')
            props['__class__'] = cls
            props['_property_'] = nsc.property_(obj, expose_dict)
            return cls

        def __getattr__(obj, name):                          # |:clm:|
            # @:adhoc_template:@
            '''Get attribute from namespace dict.

            Special properties `__dict__`, `__class__`, `_property_` come
            from property dict.
            '''
            # @:adhoc_template:@ -
            try:
                return props[name]
            except KeyError:
                pass
            # allow dictionary access
            if expose_dict:
                if (name not in nsc.ignore_dict_attrs
                    and name in ns.__class__.__dict__):
                    # @:adhoc_template:@
                    # if name not in nsc.known_dict_attrs: # |:debug:| show used attributes
                    #     nsc.known_dict_attrs.append(name)
                    # @:adhoc_template:@ -
                    return getattr(ns, name)
            try:
                return ns[name]
            except KeyError:
                raise AttributeError(
                    nsc.no_attrib_msg(props['__class__'], name))

        def __setattr__(obj, name, value):                   # |:clm:|
            # @:adhoc_template:@
            '''Set attribute in namespace dict.

            If special property __dict__ is set, the namespace dict is
            cleared and updated from value.

            Special properties `__class__` and `_property_` cannot be set.
            '''
            # @:adhoc_template:@ -
            if name in props:
                if name == '__dict__':
                    ns.clear()
                    ns.update(value)
                else:
                    raise AttributeError(
                        nsc.no_set_attrib_msg(props['__class__'], name))
            else:
                ns[name] = value

        def __delattr__(obj, name):                          # |:clm:|
            # @:adhoc_template:@
            '''Delete attribute in namespace dict.

            Special properties `__dict__`, `__class__`, `_property_`
            cannot be deleted.
            '''
            # @:adhoc_template:@ -
            if name in props:
                raise AttributeError(
                    nsc.no_del_attrib_msg(props['__class__'], name))
            try:
                del(ns[name])
            except KeyError:
                raise AttributeError(
                    nsc.no_attrib_msg(props['__class__'], name))
        return __getattr__, __setattr__, __delattr__, __property_init__

    @classmethod
    def namespace(nsc, for_=object, expose_dict=0):        # ||:clg:||
        # @:adhoc_template:@
        '''Namespace (meta-) class generator.'''
        # @:adhoc_template:@ -
        class namespace_(for_):                              # |:ccl:|
            __getattribute__, __setattr__, __delattr__, _ns_prop_init_ =(
                nsc.namespace_closure(expose_dict))
            # exposed dict interface
            if expose_dict:
                def __contains__(self, *args, **kwargs):
                    return getattr(self.__dict__, '__contains__')(*args, **kwargs)
                def __delitem__(self, *args, **kwargs):
                    return getattr(self.__dict__, '__delitem__')(*args, **kwargs)
                def __eq__(self, *args, **kwargs):
                    return getattr(self.__dict__, '__eq__')(*args, **kwargs)
                def __ge__(self, *args, **kwargs):
                    return getattr(self.__dict__, '__ge__')(*args, **kwargs)
                def __getitem__(self, *args, **kwargs):
                    return getattr(self.__dict__, '__getitem__')(*args, **kwargs)
                def __gt__(self, *args, **kwargs):
                    return getattr(self.__dict__, '__gt__')(*args, **kwargs)
                def __hash__(self, *args, **kwargs):
                    return getattr(self.__dict__, '__hash__')(*args, **kwargs)
                def __iter__(self, *args, **kwargs):
                    return getattr(self.__dict__, '__iter__')(*args, **kwargs)
                def __le__(self, *args, **kwargs):
                    return getattr(self.__dict__, '__le__')(*args, **kwargs)
                def __len__(self, *args, **kwargs):
                    return getattr(self.__dict__, '__len__')(*args, **kwargs)
                def __lt__(self, *args, **kwargs):
                    return getattr(self.__dict__, '__lt__')(*args, **kwargs)
                def __ne__(self, *args, **kwargs):
                    return getattr(self.__dict__, '__ne__')(*args, **kwargs)
                def __setitem__(self, *args, **kwargs):
                    return getattr(self.__dict__, '__setitem__')(*args, **kwargs)
                def __sizeof__(self, *args, **kwargs):
                    return getattr(self.__dict__, '__sizeof__')(*args, **kwargs)
                def clear(self, *args, **kwargs):
                    return getattr(self.__dict__, 'clear')(*args, **kwargs)
                def copy(self, *args, **kwargs):
                    return getattr(self.__dict__, 'copy')(*args, **kwargs)
                def fromkeys(self, *args, **kwargs):
                    return getattr(self.__dict__, 'fromkeys')(*args, **kwargs)
                def get(self, *args, **kwargs):
                    return getattr(self.__dict__, 'get')(*args, **kwargs)
                def items(self, *args, **kwargs):
                    return getattr(self.__dict__, 'items')(*args, **kwargs)
                def keys(self, *args, **kwargs):
                    return getattr(self.__dict__, 'keys')(*args, **kwargs)
                def pop(self, *args, **kwargs):
                    return getattr(self.__dict__, 'pop')(*args, **kwargs)
                def popitem(self, *args, **kwargs):
                    return getattr(self.__dict__, 'popitem')(*args, **kwargs)
                def setdefault(self, *args, **kwargs):
                    return getattr(self.__dict__, 'setdefault')(*args, **kwargs)
                def update(self, *args, **kwargs):
                    return getattr(self.__dict__, 'update')(*args, **kwargs)
                def values(self, *args, **kwargs):
                    return getattr(self.__dict__, 'values')(*args, **kwargs)
                _ns_for_py2_ = hasattr(dict.__dict__, 'iteritems')
                if _ns_for_py2_:
                    def __cmp__(self, *args, **kwargs):
                        return getattr(self.__dict__, '__cmp__')(*args, **kwargs)
                    def has_key(self, *args, **kwargs):
                        return getattr(self.__dict__, 'has_key')(*args, **kwargs)
                    def iteritems(self, *args, **kwargs):
                        return getattr(self.__dict__, 'iteritems')(*args, **kwargs)
                    def iterkeys(self, *args, **kwargs):
                        return getattr(self.__dict__, 'iterkeys')(*args, **kwargs)
                    def itervalues(self, *args, **kwargs):
                        return getattr(self.__dict__, 'itervalues')(*args, **kwargs)
                    def viewitems(self, *args, **kwargs):
                        return getattr(self.__dict__, 'viewitems')(*args, **kwargs)
                    def viewkeys(self, *args, **kwargs):
                        return getattr(self.__dict__, 'viewkeys')(*args, **kwargs)
                    def viewvalues(self, *args, **kwargs):
                        return getattr(self.__dict__, 'viewvalues')(*args, **kwargs)

            def __init__(self, *args, **kwargs):             # |:ccm:|
                for_.__getattribute__(self, '_ns_prop_init_')(namespace_)
                for_.__init__(self, *args, **kwargs)
        return namespace_

NameSpaceMeta = NameSpaceNS.namespace                      # ||:cls:|| generator
'''Namespace (meta-) class generator.

NameSpaceMeta(for_=object, expose_dict=0)
'''

class NameSpace(NameSpaceMeta()):
    # @:adhoc_template:@
    '''Namespace class inheriting from object, without dict interface.

    Defined as: ``class NameSpace(NameSpaceMeta()):``'''
    # @:adhoc_template:@ -
    pass

class NameSpaceDict(NameSpaceMeta(expose_dict=2)):
    # @:adhoc_template:@
    '''Namespace class inheriting from object, with complete dict interface.

    Defined as: ``class NameSpace(NameSpaceMeta(expose_dict=2)):``'''
    # @:adhoc_template:@ -
    pass

# @:adhoc_template:@

# --------------------------------------------------
# |||:sec:||| FUNCTIONS
# --------------------------------------------------

# (progn (forward-line 1) (snip-insert-mode "py.f.hl" t) (insert "\n"))
hlr = None
def hlcr(title=None, tag='|||' ':CHP:|||', rule_width=50, **kwargs): # ||:fnc:||
    comm = ((('dbg_comm' in globals()) and (globals()['dbg_comm'])) or ('# '))
    dstr = []
    dstr.append(''.join((comm, '-' * rule_width)))
    if title:
        dstr.append(sformat('{0}{2:^{1}} {3!s}',
                comm, ((('dbg_twid' in globals()) and (globals()['dbg_twid'])) or (9)),
                tag, title))
        dstr.append(''.join((comm, '-' * rule_width)))
    return '\n'.join(dstr)

def hlsr(title=None, tag='||' ':SEC:||', rule_width=35, **kwargs): # |:fnc:|
    return hlcr(title, tag, rule_width)

def hlssr(title=None, tag='|' ':INF:|', rule_width=20, **kwargs): # |:fnc:|
    return hlcr(title, tag, rule_width)

def hlc(*args, **kwargs):                                    # |:fnc:|
    for line in hlcr(*args, **kwargs).splitlines():
        printe(line, **kwargs)

def hls(*args, **kwargs):                                    # |:fnc:|
    for line in hlsr(*args, **kwargs).splitlines():
        printe(line, **kwargs)

def hlss(*args, **kwargs):                                   # |:fnc:|
    for line in hlssr(*args, **kwargs).splitlines():
        printe(line, **kwargs)

def hl(*args, **kwargs):                                     # |:fnc:|
    for line in hlr(*args, **kwargs).splitlines():
        printe(line, **kwargs)

def hl_lvl(level=0):                                         # |:fnc:|
    global hlr
    if level == 0:
        hlr = hlssr
    elif level == 1:
        hlr = hlsr
    else:
        hlr = hlcr

hl_lvl(0)

# (progn (forward-line 1) (snip-insert-mode "py.f.single.quote" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.f.remove.match" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.f.printenv" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.f.uname-s" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.f.printe" t) (insert "\n"))
def printe(*args, **kwargs):                               # ||:fnc:||
    kwargs['file'] = kwargs.get('file', sys.stderr)
    printf(*args, **kwargs)

# (progn (forward-line 1) (snip-insert-mode "py.f.dbg.squeeze" t) (insert "\n"))
# (progn (forward-line 1) (snip-insert-mode "py.f.dbg.indent" t) (insert "\n"))

# (progn (forward-line -1) (insert "\n") (snip-insert-mode "py.s.func" t) (backward-symbol-tag 2 "fillme" "::"))

class NameSpaceCheck(object):                              # ||:cls:||

    def __init__(self, *args, **kwargs):                     # |:mth:|
        printf('# NameSpaceCheck.__init__ called')
        printe(sformat(
            "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
            dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'args', args))
        printe(sformat(
            "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
            dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'kwargs', kwargs))
        prop = self._property_
        self.args = args
        self.kwargs = kwargs
        super(NameSpaceCheck, self).__init__()

    def method(self):                                        # |:mth:|
        printf('# NameSpaceCheck.method called')
        self._property_.method2()

    def method2(self):                                       # |:mth:|
        printf('# NameSpaceCheck.method2 called')

    def __del__(self):                                       # |:mth:|
        printf('# BYE, BYE from NameSpaceCheck')
        printe(sformat(
            "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
            dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'vars(self)', vars(self)))

def check_namespace_features(expose_dict=0):               # ||:fnc:||
    hl(sformat('Check namespace features (expose_dict={0})',
               expose_dict))
    class nsdc (NameSpaceMeta(NameSpaceCheck, expose_dict)):
        pass
    nsd = nsdc('arg0', 'arg1', kwarg0='kw', kwarg1='kw')

    nsd._property_.method()

    if expose_dict > 1:
        nsd._property_['dict'] = 'access'
        nsd._property_['keys'] = 'prop keys'
        keys = nsd._property_['keys']
        printe(sformat(
            "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
            dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'prop keys', keys))

    if expose_dict:
        keys = nsd._property_.keys()
        printe(sformat(
            "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
            dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'prop keys()', keys))

        nsd['keys'] = 'nsd keys'
        keys = nsd['keys']
        printe(sformat(
            "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
            dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'nsd keys', keys))
        keys = nsd.keys()
        printe(sformat(
            "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
            dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'nsd keys()', keys))

        nsd.keys = 'nsd attr keys'
        keys = nsd['keys']
        printe(sformat(
            "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
            dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'nsd attr keys', keys))

    nsd.keys = 'nsd attr keys'
    keys = nsd.keys
    printe(sformat(
        "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
        dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'nsd attr keys', keys))

    return

# --------------------------------------------------
# |||:sec:||| DICT ATTRIBUTES
# --------------------------------------------------

# |:here:|

python2_dict_attrs = [
    '__cmp__',
    '__contains__',
    '__delitem__', # AttributeError
#    '__doc__' # None,
    '__eq__',
    '__ge__',
    '__getitem__',
    '__gt__',
    '__hash__',
    '__iter__',
    '__le__',
    '__len__',
    '__lt__',
    '__ne__',
    '__setitem__', # AttributeError
    '__sizeof__',
    'clear', # AttributeError
    'copy',
    'fromkeys', # AttributeError
    'get',
    'has_key',
    'items',
    'iteritems',
    'iterkeys',
    'itervalues',
    'keys',
    'pop', # AttributeError
    'popitem', # AttributeError
    'setdefault', # AttributeError
    'update', # AttributeError
    'values',
    'viewitems', # AttributeError
    'viewkeys', # AttributeError
    'viewvalues', # AttributeError
    ]

python3_dict_attrs = [
    '__contains__',
    '__delitem__', # AttributeError
#    '__doc__' # None,
    '__eq__',
    '__ge__',
    '__getitem__',
    '__gt__',
#    '__hash__' # None,
    '__iter__',
    '__le__',
    '__len__',
    '__lt__',
    '__ne__',
    '__setitem__', # AttributeError
    '__sizeof__',
    'clear', # AttributeError
    'copy',
    'fromkeys', # AttributeError
    'get',
    'items',
    'keys',
    'pop', # AttributeError
    'popitem', # AttributeError
    'setdefault', # AttributeError
    'update', # AttributeError
    'values',
    ]

python2_unique = [
    '__cmp__',
    '__hash__',
    'has_key',
    'iteritems',
    'iterkeys',
    'itervalues',
    'viewitems',
    'viewkeys',
    'viewvalues',
    ]
python3_unique = [
    ]

# direct class lookup:                    # |:info:|
#   :DBG:   dict op             : ]__cmp__     [ attribs used: ][][
#   :DBG:   dict op             : ]__contains__[ attribs used: ][][
#   :DBG:   dict op             : ]__delitem__ [ attribs used: ][][
#   :DBG:   dict op             : ]__getitem__ [ attribs used: ][][
#   :DBG:   dict op             : ]__iter__    [ attribs used: ][][
#   :DBG:   dict op             : ]__len__     [ attribs used: ][][
#   :DBG:   dict op             : ]__setitem__ [ attribs used: ][][

# lookup via __getattribute__:            # |:info:|
#   :DBG:   dict op             : ]clear       [ attribs used: ]['clear'][
#   :DBG:   dict op             : ]copy        [ attribs used: ]['copy'][
#   :DBG:   dict op             : ]fromkeys    [ attribs used: ]['fromkeys'][
#   :DBG:   dict op             : ]get         [ attribs used: ]['get'][
#   :DBG:   dict op             : ]items       [ attribs used: ]['items'][
#   :DBG:   dict op             : ]keys        [ attribs used: ]['keys'][
#   :DBG:   dict op             : ]pop         [ attribs used: ]['pop'][
#   :DBG:   dict op             : ]popitem     [ attribs used: ]['popitem'][
#   :DBG:   dict op             : ]setdefault  [ attribs used: ]['setdefault'][
#   :DBG:   dict op             : ]update      [ attribs used: ]['update'][
#   :DBG:   dict op             : ]values      [ attribs used: ]['values'][

def show_dict_methods(as_methods=False):                   # ||:fnc:||

    # |:debug:| find Python2/3 unique methods
    # printf('python2_unique')
    # for attr in python2_dict_attrs:
    #     if attr not in python3_dict_attrs:
    #         python2_unique.append(attr)
    #         printe(sformat("        '{0}',", attr))
    # printf('python3_unique')
    # for attr in python3_dict_attrs:
    #     if attr not in python2_dict_attrs:
    #         python3_unique.append(attr)
    #         printe(sformat("        '{0}',", attr))
    # printf('done')

    known_dict_attrs = python2_dict_attrs

    ignore_dict_attrs = [
        '__getattribute__',
        '__init__',
        '__new__',
        '__repr__',
        ]

    # |:here:|
    for dattr in sorted(dict.__dict__):
        if dattr in ignore_dict_attrs:
            continue
        try:
            avalue = getattr(dict.__dict__, dattr)
            if hasattr(avalue, '__call__'):
                if not as_methods:
                    printe(sformat("    '{0}',", dattr))
            else:
                if not as_methods:
                    printe(sformat("#    '{0}' # {1},", dattr, avalue))
                continue
        except AttributeError:
            if not as_methods:
                printe(sformat("    '{0}', # AttributeError", dattr))
        if as_methods:
            printe(sformat("""\
            def {0}(self, *args, **kwargs):
                return getattr(self.__dict__, '{0}')(*args, **kwargs)
            """, dattr))

def check_dict_methods():                                  # ||:fnc:||
    da_check_ = []

    da_checked = []
    def da_check_init():
        del(da_check_[:])
        NameSpaceNS.known_dict_attrs = []
        da_check_.append(list(NameSpaceNS.known_dict_attrs))

    def da_check_report(for_='dict.something'):
        da_checked.append(for_)
        old_known = da_check_[0]
        new_attribs = []
        for attr in NameSpaceNS.known_dict_attrs:
            if attr not in old_known:
                new_attribs.append(attr)
        printe(sformat(
            "{0}{3:^{1}} {4:<{2}s}: ]{5!s:<12s}[ attribs used: ]{6!s}[",
            dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'dict op', for_, list(sorted(new_attribs))))

    ns = NameSpace()

    # |:here:|

    da_check_init()
    ns['setitem1'] = 'setitem value'
    ns['setitem2'] = 'setitem value'
    ns['setitem3'] = 'setitem value'
    ns['setitem4'] = 'setitem value'
    da_check_report('__setitem__')
    da_checked.extend(('__hash__',))

    da_check_init()
    x = ns['setitem1']
    da_check_report('__getitem__')

    da_check_init()
    del(ns['setitem4'])
    da_check_report('__delitem__')

    da_check_init()
    if 'some' in ns:
        pass
    da_check_report('__contains__')

    da_check_init()
    for x in ns:
        pass
    da_check_report('__iter__')

    da_check_init()
    x = len(ns)
    da_check_report('__len__')
    da_checked.extend(('__sizeof__',))

    da_check_init()
    for x in sorted(ns):
        pass
    da_check_report('__cmp__')
    da_checked.extend(('__eq__', '__ge__', '__gt__', '__le__', '__lt__', '__ne__',))

    da_check_init()
    for x in ns.keys():
        pass
    da_check_report('keys')

    da_check_init()
    for x in ns.values():
        pass
    da_check_report('values')

    da_check_init()
    for x in ns.items():
        pass
    da_check_report('items')

    it = list(ns.items())
    da_check_init()
    ns.update(it)
    da_check_report('update')

    da_check_init()
    pop = ns.get('setitem6', 'None')
    da_check_report('get')

    da_check_init()
    pop = ns.setdefault('setitem1', 'None')
    da_check_report('setdefault')

    da_check_init()
    pop = ns.fromkeys(['a', 'b', 'c'])
    da_check_report('fromkeys')

    da_check_init()
    pop = ns.pop('setitem1')
    printe(sformat(
        "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
        dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'pop', pop))
    da_check_report('pop')

    da_check_init()
    pop = ns.popitem()
    da_check_report('popitem')

    try:
        # python2 unique
        da_check_init()
        it = ns.iterkeys()
        da_check_report('iterkeys')
        da_check_init()
        it = ns.itervalues()
        da_check_report('itervalues')
        da_check_init()
        it = ns.iteritems()
        da_check_report('iteritems')
        da_check_init()
        it = ns.viewkeys()
        da_check_report('viewkeys')
        da_check_init()
        it = ns.viewvalues()
        da_check_report('viewvalues')
        da_check_init()
        it = ns.viewitems()
        da_check_report('viewitems')
    except AttributeError:
        da_checked.extend(('iterkeys', 'itervalues', 'iteritems', ))
        da_checked.extend(('viewkeys', 'viewvalues', 'viewitems', ))
        da_checked.extend(('has_key',))

    da_check_init()
    cp = ns.copy()
    da_check_report('copy')

    da_check_init()
    ns.clear()
    da_check_report('clear')

    for attr in python2_dict_attrs:
        if attr not in da_checked:
            printe(sformat(
                "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
                dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'unchecked', attr))
    # |:here:|

def run(parameters, pass_opts):                            # ||:fnc:||
    """Application runner, when called as __main__."""

    # (progn (forward-line 1) (snip-insert-mode "py.bf.sql.ws" t) (insert "\n"))
    # (progn (forward-line 1) (snip-insert-mode "py.bf.file.arg.loop" t) (insert "\n"))

    class x(object):                                       # ||:cls:||
        def get_prop(name):                                  # |:mth:|
            return 'prop'
        def set_prop(name, value):                           # |:mth:|
            return
        prop = property(get_prop)

    #x().prop = 55
    #delattr(x(), 'prop')

    # show_dict_methods()
    # check_dict_methods()
    # exit(0)
    # |:here:|

    ns = NameSpace()
    ns2 = NameSpace()

                                                             # |:sec:|
    hl('Basic namespace features')
    printe(sformat(
        "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
        dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'ns.__class__',
        ns.__class__.__name__))

    printe(sformat(
        "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
        dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'is..(ns, dict)',
        isinstance(ns, dict)))

    printe(sformat(
        "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
        dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'is..(vars(ns), dict)',
        isinstance(vars(ns), dict)))

    check_namespace_features(0)
    check_namespace_features(1)
    check_namespace_features(2)

    hl('Set attributes on two namespaces (each is separate!)') # |:sec:|
    ns.test = 55
    ns2.test2 = -5
    printe(sformat(
        "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
        dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'ns.test', ns.test))
    printe(sformat(
        "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
        dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'ns2.test2', ns2.test2))

    printe(sformat(
        "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
        dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'vars(ns)', vars(ns)))
    printe(sformat(
        "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
        dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'vars(ns2)', vars(ns2)))

    hl('Set attributes via vars()') # |:sec:|

    vars(ns)['hello'] = True
    vars(ns)['world'] = True
    printe(sformat(
        "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
        dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'vars(ns)', vars(ns)))

    hl('Access to the namespace class object')               # |:sec:|
    prop = ns._property_
    printe(sformat(
        "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
        dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'ns._property_', prop))
    printe(sformat(
        "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
        dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'prop.__class__',
        prop.__class__))

    prop.new_attr = 'new_attr'
    printe(sformat(
        "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
        dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'prop.new_attr', prop.new_attr))
    printe(sformat(
        "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
        dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'prop.__dict__', prop.__dict__))

    hl('The namespaces are not affected')                    # |:sec:|
    printe(sformat(
        "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
        dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'vars(ns)', vars(ns)))
    printe(sformat(
        "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
        dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'vars(ns2)', vars(ns2)))

    hl('Set special property __dict__')                      # |:sec:|
    new_dict = {'new': 0, 'dict': 1}
    ns.__dict__ = new_dict
    printe(sformat(
        "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
        dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'vars(ns)', vars(ns)))
    printe(sformat(
        "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
        dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'new_dict', new_dict))
    ns.test = 'needed for delattr test'
    printe(sformat(
        "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
        dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'ns.test', ns.test))
    printe(sformat(
        "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
        dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'vars(ns)', vars(ns)))
    printe(sformat(
        "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
        dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'new_dict', new_dict))

    hl('Set special attribute __class__')                    # |:sec:|
    try:
        ns.__class__ = "can't do this"
    except AttributeError:
        (t, e, tb) = sys.exc_info()
        import traceback
        printe(''.join(traceback.format_tb(tb)), end='')
        printe(sformat('{0}: {1}', t.__name__, e))
        del(tb)
        pass

    hl('Delete `test` attribute')                            # |:sec:|
    delattr(ns, 'test')
    printe(sformat(
        "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[",
        dbg_comm, dbg_twid, dbg_fwid, ':DBG:', 'vars(ns)', vars(ns)))

    hl('Access non-existent attribute test')                 # |:sec:|
    try:
        ns.test
    except AttributeError:
        (t, e, tb) = sys.exc_info()
        import traceback
        printe(''.join(traceback.format_tb(tb)), end='')
        printe(sformat('{0}: {1}', t.__name__, e))
        del(tb)
        pass

    hl('Delete non-existent attribute test')                 # |:sec:|
    try:
        delattr(ns, 'test')
    except AttributeError:
        (t, e, tb) = sys.exc_info()
        import traceback
        printe(''.join(traceback.format_tb(tb)), end='')
        printe(sformat('{0}: {1}', t.__name__, e))
        del(tb)
        pass

    hl('Delete special attribute __dict__')                  # |:sec:|
    try:
        delattr(ns, '__dict__')
    except AttributeError:
        (t, e, tb) = sys.exc_info()
        import traceback
        printe(''.join(traceback.format_tb(tb)), end='')
        printe(sformat('{0}: {1}', t.__name__, e))
        del(tb)
        pass

    # |:here:|
    pass

# --------------------------------------------------
# |||:sec:||| MAIN
# --------------------------------------------------

_quiet = False
_verbose = False
_debug = False

# (progn (forward-line 1) (snip-insert-mode "py.f.setdefaultencoding" t) (insert "\n"))
file_encoding_is_clean = True
def setdefaultencoding(encoding=None, quiet=False):
    if file_encoding_is_clean:
        return
    if encoding is None:
        encoding='utf-8'
    try:
        isinstance('', basestring)
        if not hasattr(sys, '_setdefaultencoding'):
            if not quiet:
                printf('''\
Add this to /etc/python2.x/sitecustomize.py,
or put it in local sitecustomize.py and adjust PYTHONPATH=".:${PYTHONPATH}"::

    try:
        import sys
        setattr(sys, '_setdefaultencoding', getattr(sys, 'setdefaultencoding'))
    except AttributeError:
        pass

Running with reload(sys) hack ...
''', file=sys.stderr)
            reload(sys)
            setattr(sys, '_setdefaultencoding',
                    getattr(sys, 'setdefaultencoding'))
        sys._setdefaultencoding(encoding)
    except NameError:
        # python3 already has utf-8 default encoding ;-)
        pass

def main(argv):                                            # ||:fnc:||
    global _quiet, _debug, _verbose
    global RtAdHoc, AdHoc

    _parameters = None
    _pass_opts = []
    try:
        import argparse
    except ImportError:
        try:
            import argparse_local as argparse
        except ImportError:
            printe('error: argparse missing. Try `easy_install argparse`.')
            sys.exit(1)

    parser = argparse.ArgumentParser(add_help=False)
    # parser.add_argument('--sum', dest='accumulate', action='store_const',
    #                    const=sum, default=max,
    #                    help='sum the integers (default: find the max)')
    # |:opt:| add options
    parser.add_argument(
        '-q', '--quiet', action='store_const', const=-2,
        dest='debug', default=0, help='suppress warnings')
    parser.add_argument(
        '-v', '--verbose', action='store_const', const=-1,
        dest='debug', default=0, help='verbose test output')
    parser.add_argument(
        '-d', '--debug', nargs='?', action='store', type=int, metavar='NUM',
        default = 0, const = 1,
        help='show debug information')
    parser.add_argument(
        '-t', '--test', action='store_true',
        help='run doc tests')
    class AdHocAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            map(lambda opt: setattr(namespace, opt, False),
                ('implode', 'explode', 'extract', 'template'))
            setattr(namespace, option_string[2:], True)
            setattr(namespace, 'adhoc_arg', values)
    parser.add_argument(
        '--implode', nargs=0, action=AdHocAction, default=False,
        help='implode script with adhoc')
    parser.add_argument(
        '--explode', nargs='?', action=AdHocAction, type=str, metavar='DIR',
        default=False, const='__adhoc__',
        help='explode script with adhoc in directory DIR'
        ' (default: `__adhoc__`)')
    parser.add_argument(
        '--extract', nargs='?', action=AdHocAction, type=str, metavar='DIR',
        default=False, const = '.',
        help='extract files to directory DIR (default: `.`)')
    parser.add_argument(
        '--template', nargs='?', action=AdHocAction, type=str, metavar='NAME',
        default=False, const = '-',
        help='extract named template to standard output. default NAME is ``-``')
    parser.add_argument(
        '-h', '--help', action='store_true',
        help="display this help message")
    parser.add_argument(
        '--ap-help', action='store_true',
        help="internal help message")
    parser.add_argument(
        'args', nargs='*', metavar='arg',
        #'args', nargs='+', metavar='arg',
        #type=argparse.FileType('r'), default=sys.stdin,
        help='a series of arguments')
    #_parameters = parser.parse_args()
    (_parameters, _pass_opts) = parser.parse_known_args(argv[1:])
    # generate argparse help
    if _parameters.ap_help:
        parser.print_help()
        return 0
    # standard help
    if _parameters.help:
        sys.stdout.write(__doc__)
        return 0

    _debug = _parameters.debug
    if _debug > 0:
        _verbose = True
        _quiet = False
    elif _debug < 0:
        _verbose = (_debug == -1)
        _quiet = not(_verbose)
        _debug = 0
    _parameters.debug = _debug
    _parameters.verbose = _verbose
    _parameters.quiet = _quiet

    if _debug:
        cmd_line = argv
        sys.stderr.write(sformat(
                "{0}{3:^{1}} {4:<{2}s}: ]{5!s}[\n",
                ((('dbg_comm' in globals()) and (globals()['dbg_comm'])) or ('# ')),
                ((('dbg_twid' in globals()) and (globals()['dbg_twid'])) or (9)),
                ((('dbg_fwid' in globals()) and (globals()['dbg_fwid'])) or (15)),
                ':DBG:', 'cmd_line', cmd_line))

    # at least use `quiet` to suppress the setdefaultencoding warning
    setdefaultencoding(quiet=_quiet or _parameters.test)
    # |:opt:| handle options

    # adhoc: implode/explode/extract
    adhoc_export = (_parameters.explode or _parameters.extract)
    adhoc_op = (_parameters.implode or adhoc_export or _parameters.template)
    if adhoc_op:
        file_ = __file__
        source = None

        have_adhoc = 'AdHoc' in globals()
        have_rt_adhoc = 'RtAdHoc' in globals()

        # shall adhoc be imported
        if _parameters.implode or not have_rt_adhoc:
            # shall this file be compiled
            adhoc_compile = not (have_rt_adhoc)
            os_path = os.defpath
            for pv in ('PATH', 'path'):
                try:
                    os_path = os.environ[pv]
                    break
                except KeyError:
                    pass
            os_path = os_path.split(os.pathsep)
            for path_dir in os_path:
                if not path_dir:
                    continue
                if path_dir not in sys.path:
                    sys.path.append(path_dir)
            if not have_adhoc:
                try:
                    import adhoc
                    AdHoc = adhoc.AdHoc
                except ImportError:
                    adhoc_compile = False
                    try:
                        from rt_adhoc import RtAdHoc as Adhoc
                    except ImportError:
                        pass
        else:
            adhoc_compile = False
            AdHoc = RtAdHoc

        AdHoc.quiet = _quiet
        AdHoc.verbose = _verbose
        AdHoc.debug = _debug
        AdHoc.include_path.append(os.path.dirname(file_))

        if adhoc_compile:
            ah = AdHoc()
            source = ah.compileFile(file_)
        else:
            file_, source = AdHoc.std_source_param(file_)

        # implode
        if _parameters.implode:
            # @:adhoc_enable:@
            # if not _quiet:
            #     map(sys.stderr.write,
            #         ["warning: ", os.path.basename(file_),
            #          " already imploded!\n"])
            # @:adhoc_enable:@
            AdHoc.write_source('-', source)
        # explode
        elif _parameters.explode:
            AdHoc.export_dir = _parameters.adhoc_arg
            AdHoc.export(file_, source)
        # extract
        elif _parameters.extract:
            AdHoc.extract_dir = _parameters.adhoc_arg
            AdHoc.extract(file_, source)
        # template
        elif _parameters.template:
            template_name = _parameters.adhoc_arg
            if not template_name:
                template_name = '-'
            if template_name == 'list':
                sys.stdout.write(
                    '\n'.join(AdHoc.template_table(file_, source)) + '\n')
            else:
                template = AdHoc.get_named_template(
                    template_name, file_, source)
                AdHoc.write_source('-', template)

        # restore for subsequent calls to main
        if not have_adhoc:
            del(AdHoc)
        return 0

    # run doc tests
    if _parameters.test:
        import doctest
        doctest.testmod(verbose = _verbose)
        return 0

    # |:opt:| handle options
    run(_parameters, _pass_opts)

if __name__ == "__main__":
    #sys.argv.insert(1, '--debug') # |:debug:|
    result = main(sys.argv)
    sys.exit(result)

    # |:here:|

# (progn (forward-line 1) (snip-insert-mode "py.t.ide" t) (insert "\n"))
#
# :ide-menu: Emacs IDE Main Menu - Buffer @BUFFER@
# . M-x `eIDE-menu' (eIDE-menu "z")

# :ide: CSCOPE ON
# . (cscope-minor-mode)

# :ide: CSCOPE OFF
# . (cscope-minor-mode (quote ( nil )))

# :ide: TAGS: forced update
# . (compile (concat "cd /home/ws/project/ws-rfid && make -k FORCED=1 tags"))

# :ide: TAGS: update
# . (compile (concat "cd /home/ws/project/ws-rfid && make -k tags"))

# :ide: +-#+
# . Utilities ()

# :ide: TOC: Generate TOC with py-toc.py
# . (progn (save-buffer) (compile (concat "py-toc.py ./" (file-name-nondirectory (buffer-file-name)) " ")))

# :ide: CMD: Fold region with line continuation
# . (shell-command-on-region (region-beginning) (region-end) "fold --spaces -width 79 | sed 's, $,,;1!s,^, ,;$!s,$,\\\\,'" nil nil nil t)

# :ide: CMD: Fold region and replace with line continuation
# . (shell-command-on-region (region-beginning) (region-end) "fold --spaces --width 79 | sed 's, $,,;1!s,^, ,;$!s,$,\\\\,'" t nil nil t)

# :ide: +-#+
# . Fold ()

# :ide: CMD: Remove 8 spaces and add `>>> ' to region
# . (shell-command-on-region (region-beginning) (region-end) "sed 's,^        ,,;/^[ ]*##/d;/^[ ]*#/{;s,^ *# *,,p;d;};/^[ ]*$/!s,^,>>> ,'" nil nil nil t)

# :ide: CMD: Remove 4 spaces and add `>>> ' to region
# . (shell-command-on-region (region-beginning) (region-end) "sed 's,^    ,,;/^[ ]*##/d;/^[ ]*#/{;s,^ *# *,,p;d;};/^[ ]*$/!s,^,>>> ,'" nil nil nil t)

# :ide: +-#+
# . Doctest ()

# :ide: LINT: Check 80 column width ignoring IDE Menus
# . (let ((args " | /srv/ftp/pub/check-80-col.sh -")) (compile (concat "sed 's,^\\(\\|. \\|.. \\|... \\)\\(:ide\\|[.] \\).*,,;s,^ *. (progn (forward-line.*,,' " (buffer-file-name) " " args " | sed 's,^-," (buffer-file-name) ",'")))

# :ide: LINT: Check 80 column width
# . (let ((args "")) (compile (concat "/srv/ftp/pub/check-80-col.sh " (buffer-file-name) " " args)))

# :ide: +-#+
# . Lint Tools ()

# :ide: DELIM:     @: SYM :@         @:fillme:@             adhoc tag
# . (symbol-tag-normalize-delimiter (cons (cons nil "@:") (cons ":@" nil)) t)

# :ide: +-#+
# . Delimiters ()

# :ide: COMPILE: Run with --ap-help
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --ap-help")))

# :ide: COMPILE: Run with --help
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --help")))

# :ide: COMPILE: Run with --test
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --test")))

# :ide: COMPILE: Run with --test --verbose
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --test --verbose")))

# :ide: COMPILE: Run with --debug
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --debug")))

# :ide: +-#+
# . Compile with standard arguments ()

# :ide: OCCUR-OUTLINE: Python Source Code
# . (x-symbol-tag-occur-outline "sec" '("|||:" ":|||") (cons (cons "^\\([ \t\r]*\\(def\\|class\\)[ ]+\\|[A-Za-z_]?\\)" nil) (cons nil "\\([ \t\r]*(\\|[ \t]*=\\)")))

# :ide: MENU-OUTLINE: Python Source Code
# . (x-eIDE-menu-outline "sec" '("|||:" ":|||") (cons (cons "^\\([ \t\r]*\\(def\\|class\\)[ ]+\\|[A-Za-z_]?\\)" nil) (cons nil "\\([ \t\r]*(\\|[ \t]*=\\)")))

# :ide: +-#+
# . Outline ()

# :ide: INFO: SQLAlchemy - SQL Expression Language - Reference
# . (let ((ref-buffer "*sqa-expr-ref*")) (if (not (get-buffer ref-buffer)) (shell-command (concat "w3m -dump -cols " (number-to-string (1- (window-width))) " 'http://www.sqlalchemy.org/docs/05/reference/sqlalchemy/expressions.html'") ref-buffer) (display-buffer ref-buffer t)))

# :ide: INFO: SQLAlchemy - SQL Expression Language - Tutorial
# . (let ((ref-buffer "*sqa-expr-tutor*")) (if (not (get-buffer ref-buffer)) (shell-command (concat "w3m -dump -cols " (number-to-string (1- (window-width))) " 'http://www.sqlalchemy.org/docs/05/sqlexpression.html'") ref-buffer) (display-buffer ref-buffer t)))

# :ide: INFO: SQLAlchemy - Query
# . (let ((ref-buffer "*sqa-query*")) (if (not (get-buffer ref-buffer)) (shell-command (concat "w3m -dump -cols " (number-to-string (1- (window-width))) " 'http://www.sqlalchemy.org/docs/orm/query.html'") ref-buffer) (display-buffer ref-buffer t)))

# :ide: +-#+
# . SQLAlchemy Reference ()

# :ide: INFO: Python - argparse
# . (let ((ref-buffer "*python-argparse*")) (if (not (get-buffer ref-buffer)) (shell-command (concat "w3m -dump -cols " (number-to-string (1- (window-width))) " 'http://docs.python.org/library/argparse.html'") ref-buffer) (display-buffer ref-buffer t)))

# :ide: INFO: Python Documentation
# . (let ((ref-buffer "*w3m*")) (if (get-buffer ref-buffer) (display-buffer ref-buffer t)) (other-window 1) (w3m-goto-url "http://docs.python.org/index.html" nil nil))

# :ide: INFO: Python Reference
# . (let* ((ref-buffer "*python-ref*") (local "/home/ws/project/ws-util/python/reference/PQR2.7.html") (url (or (and (file-exists-p local) local) "'http://rgruet.free.fr/PQR27/PQR2.7.html'"))) (unless (get-buffer ref-buffer) (get-buffer-create ref-buffer) (with-current-buffer ref-buffer (shell-command (concat "snc txt.py.reference 2>/dev/null") ref-buffer) (goto-char (point-min)) (if (eobp) (shell-command (concat "w3m -dump -cols " (number-to-string (1- (window-width))) " " url) ref-buffer)))) (display-buffer ref-buffer t))

# :ide: +-#+
# . Python Reference ()

# @:adhoc_disable:@
# :ide: COMPILE: Run with --verbose --implode >namespace_dict_imploded.py
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --verbose --implode >namespace_dict_imploded.py")))
# @:adhoc_disable:@

# :ide: COMPILE: Run with --template list
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --template list")))

# :ide: COMPILE: Run with --template
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --template")))

# :ide: COMPILE: Run with python3 --test
# . (progn (save-buffer) (compile (concat "python3 ./" (file-name-nondirectory (buffer-file-name)) "  --test")))

# :ide: COMPILE: Run with python3 w/o args
# . (progn (save-buffer) (compile (concat "python3 ./" (file-name-nondirectory (buffer-file-name)) " ")))

# :ide: COMPILE: Run with --test
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --test")))

# :ide: COMPILE: Run w/o args
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " ")))

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
