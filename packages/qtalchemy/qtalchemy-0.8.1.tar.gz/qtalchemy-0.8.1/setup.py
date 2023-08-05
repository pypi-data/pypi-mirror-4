#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

import os
import sys
import dircache
import distutils
from distutils.core import Command
from distutils.command.build import build

def needsupdate(src, targ):
    return not os.path.exists(targ) or os.path.getmtime(src) > os.path.getmtime(targ)

class PySideUiBuild:
    def qrc(self, qrc_file, py_file):
        if sys.platform in ('win32', 'cygwin'):
            import PySide
            qrc_compiler = os.path.join(PySide.__path__[0], 'pyside-rcc')
        else:
            qrc_compiler = 'pyside-rcc'
        import subprocess
        rccprocess = subprocess.Popen([qrc_compiler, qrc_file, '-py2', '-o', py_file])
        rccprocess.wait()

    def uic(self, ui_file, py_file):
        if sys.platform in ('win32', 'cygwin'):
            import PySide
            uic_compiler = os.path.join(PySide.__path__[0], 'pyside-uic')
        else:
            uic_compiler = 'pyside-uic'
        import subprocess
        rccprocess = subprocess.Popen([uic_compiler, ui_file, '-o', py_file])
        rccprocess.wait()

class PyQt4UiBuild:
    def qrc(self, qrc_file, py_file):
        import subprocess
        rccprocess = subprocess.Popen(['pyrcc4', qrc_file, '-py2', '-o', py_file])
        rccprocess.wait()

    def uic(self, ui_file, py_file):
        from PyQt4 import uic
        fp = open(py_file, 'w')
        uic.compileUi(ui_file, fp)
        fp.close()

class QtUiBuild(Command, PySideUiBuild):
    description = "build Python modules from Qt Designer .ui files"

    user_options = []
    ui_files = []
    qrc_files = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def compile_ui(self, ui_file, py_file):
        if not needsupdate(ui_file, py_file):
            return
        print("compiling %s -> %s" % (ui_file, py_file))
        try:
            self.uic(ui_file, py_file)
        except Exception, e:
            raise distutils.errors.DistutilsExecError, 'Unable to compile user interface %s' % str(e)
            return
    
    def compile_qrc(self, qrc_file, py_file):
        if not needsupdate(qrc_file, py_file):
            return
        print("compiling %s -> %s" % (qrc_file, py_file))
        try:
            self.qrc(qrc_file, py_file)
        except Exception, e:
            raise distutils.errors.DistutilsExecError, 'Unable to compile resource file %s' % str(e)
            return

    def run(self):
        for f in self.ui_files:
            dir, basename = os.path.split(f)
            self.compile_ui(f, os.path.join(dir, "ui_"+basename.replace(".ui", ".py")))
        for f in self.qrc_files:
            dir, basename = os.path.split(f)
            self.compile_qrc(f, os.path.join(dir, basename.replace(".qrc", "_rc.py")))

QtUiBuild.ui_files = []
QtUiBuild.qrc_files = [os.path.join(dir, f) \
                for dir in ['qtalchemy/widgets', 'qtalchemy'] \
                for f in dircache.listdir(dir) if f.endswith('.qrc')]

class QtAlchemyBuild(build):
    sub_commands = [('build_ui', None)] + build.sub_commands

cmds = {
        'build' : QtAlchemyBuild,
        'build_ui' : QtUiBuild,
       }

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='qtalchemy',
      version='0.8.1',  # also update in qtalchemy/__init__.py
      description='QtAlchemy is a framework for developing GUI database applications using SQLAlchemy and PyQt/PySide.',
      license='LGPLv2+',
      author='Joel B. Mohler',
      author_email='joel@kiwistrawberry.us',
      long_description=read('README.txt'),
      url='https://bitbucket.org/jbmohler/qtalchemy/',
      packages=['qtalchemy',
                'qtalchemy/dialogs',
                'qtalchemy/widgets',
                'qtalchemy/xplatform',
                'qtalchemy/ext',
                'qtalchemy/ext/dataimport'],
      cmdclass = cmds,
      install_requires=['sqlalchemy', 'fuzzyparsers'],
      classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
        "Programming Language :: Python :: 2",
        "Topic :: Database :: Front-Ends",
        "Operating System :: OS Independent"])
