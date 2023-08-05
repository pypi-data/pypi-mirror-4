# -*- coding: utf-8 -*-
"""
AdHoc Standalone Package Generator
==================================

AdHoc consists of a single python source file adhoc.py, which can be
used as a program (see Script Usage) as well as a module.

After installation of the binary package, run ``adhoc.py --explode``
to obtain the full source in directory ``__adhoc__``.
"""

from distutils.core import setup
#from setuptools import setup

import os
import sys
import stat

import adhoc
#from adhoc import dbg_comm, dbg_twid, dbg_fwid, printf, printe, sformat # |:debug:|

def capture_stdout(action):
    sv_stdout = sys.stdout
    sio = adhoc._AdHocStringIO()
    sys.stdout = sio
    action()
    captured = sio.getvalue()
    sio.close()
    sys.stdout = sv_stdout
    return captured

package_dir = {'': 'dist'}
if not os.path.exists('dist'):
    os.mkdir('dist')
adhoc_executable = 'dist/adhoc.py'

if 'RtAdHoc' not in vars(adhoc):
    compiled = capture_stdout(lambda: adhoc.main('adhoc.py --implode'.split()))
    out = open(adhoc_executable, 'wb')
    out.write(compiled.encode('utf-8'))
    out.close()
else:
    in_ = open('adhoc.py', 'rb')
    out = open(adhoc_executable, 'wb')
    out.write(in_.read())
    out.close()
    in_.close()

os.chmod(adhoc_executable,
         (stat.S_IRUSR
          | stat.S_IWUSR
          | stat.S_IXUSR
          | stat.S_IRGRP
          | stat.S_IXGRP
          | stat.S_IROTH
          | stat.S_IXOTH ))

state = adhoc.catch_stdout()
adhoc.main('adhoc.py --documentation'.split())
long_description = adhoc.restore_stdout(state)
desc_start = long_description.find('Description')
if desc_start >= 0:
    long_description = long_description[:desc_start]

setup_args = dict(
    name='AdHoc',
    # |:version:|
    version='0.2.6',
    author='Wolfgang Scherer',
    author_email='wolfgang.scherer@gmx.de',
    url='https://bitbucket.org/wolfmanx/adhoc',
    license='GPL',
    description='Standalone Package Generator',
    long_description=long_description,
    classifiers="""\
Development Status :: 4 - Beta
Environment :: Console
Intended Audience :: Developers
License :: OSI Approved :: GNU General Public License (GPL)
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 3
Topic :: Software Development :: Code Generators
Topic :: Software Development :: Libraries :: Python Modules
Topic :: System :: Software Distribution
Topic :: Utilities
Topic :: Text Processing :: Filters
Topic :: Text Processing :: Markup\
""".splitlines(),
#    zip_safe=False, # setuptools
    platforms='any',
    package_dir = package_dir,
#    py_modules=['adhoc'],
    scripts=['dist/adhoc.py'],
#    packages = ['adhoc'],
#    test_suite='tests',
#    package_data={'mypkg': ['data/*.dat']},
#    data_files=[('/etc/init.d', ['init-script']),],
)

if __name__ == '__main__':
    setup(**setup_args)

# :ide: COMPILE: Run w/o args
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " ")))

# :ide: COMPILE: Run with --help-commands
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --help-commands")))

# :ide: COMPILE: Run with python3 bdist
# . (progn (save-buffer) (compile (concat "python3 ./" (file-name-nondirectory (buffer-file-name)) " bdist")))

# :ide: COMPILE: Run with bdist
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " bdist")))

# :ide: COMPILE: Run with sdist
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " sdist")))

# :ide: COMPILE: Run with build
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " build")))

# :ide: COMPILE: Run with --dry-run install
# . (progn (save-buffer) (compile (concat "python ./" (file-name-nondirectory (buffer-file-name)) " --dry-run install")))
