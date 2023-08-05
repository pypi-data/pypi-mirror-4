# -*- coding: utf8 -*-

from distutils.core import setup
from distutils.extension import Extension
import os
import fnmatch

try:
    import xpkg
except ImportError:
    import warnings
    warnings.warn("no xpkg package found.")


def filter_filenames( filenames, match_list ):
    matched = []
    for name in filenames:
        for p in match_list:
            if fnmatch.fnmatch(name, p):
                matched.append( name )
                break # patterns
    return matched


def find_files(search_root, match_list):
    found = []
    for dirpath, dirnames, filenames in os.walk(search_root, followlinks = True):
        for d in dirnames[:]:
            if d.startswith("."):
                dirnames.remove(d)
        cur_dir_abs = os.path.abspath(dirpath)
        filenames_abs = []
        for name in filenames:
            if os.path.isabs(name):
                filenames_abs.append(name)
            else:
                filenames_abs.append(os.path.join(cur_dir_abs, name))
        found += filter_filenames(filenames_abs, match_list)
    return found



have_cython = False
try:
    from Cython.Distutils import build_ext as _build_ext
    have_cython = True
except ImportError:
    from distutils.command.build_ext import build_ext as _build_ext


class build_ext(_build_ext):
    user_options = _build_ext.user_options + [ ('hadoop_home=', None, 'hadoop home directory'),
                                                ('hadoop_version=', None, 'hadoop version string'),
                                                ('hadoop_delete_recursive=', 0, 'hdfsDelete() has second parameter called recursive'),
                                                ('hadoop_hflush=', 1, 'hdfsHFlush() in hdfs library'),
                                             ]

    def initialize_options (self):
        self.hadoop_version = ''
        self.hadoop_home = ''
        self.hadoop_delete_recursive = 0
        self.hadoop_hflush = 1
        _build_ext.initialize_options(self)

    def run(self):
        for ext in self.extensions:
            ext.define_macros.append(("_CLASSPATH",'"' + ":".join(find_files(self.hadoop_home, ["*.jar"])) + '"' ))
            ext.define_macros.append(("HADOOP_VERSION", self.hadoop_version))

        with open(os.path.join(os.path.dirname(__file__), 'src', 'config.pxi'), 'w') as config:
            config.write('DEF HADOOP_VERSION = "%s"\n' % self.hadoop_version)
            config.write('DEF HADOOP_DELETE_RECURSIVE = %d\n' % int(self.hadoop_delete_recursive))
            config.write('DEF HADOOP_HAS_HFLUSH = %d\n' % int(self.hadoop_hflush))
        _build_ext.run(self)


if have_cython:
    cyhdfs  = Extension('cyhdfs', ['src/cyhdfs.pyx'],
                         libraries = ['hdfs', 'jvm'],
                         language="c++",
                      )
else:
    cyhdfs  = Extension('cyhdfs', ['src/cyhdfs.cpp'],
                         libraries = ['hdfs', 'jvm'],
                         language="c++",
                       )


setup (
        name='cyhdfs',
        version='0.1.2',
        packages= [],
        author='Evgeny Turnaev',
        author_email='turnaev.e@gmail.com',
        url = "https://bitbucket.org/turnaev/cyhdfs",
        description='cyhdfs',
        long_description="""Cython wrapper around libhdfs""",
        keywords = ["hdfs", "cython"],
        license = 'bsd',
        options={'build_pkg': {'name_prefix': True,
                               'python_min_version': 2.7,
                              }},
        classifiers = [
            "Development Status :: 4 - Beta",
            "Environment :: Other Environment",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: BSD License",
            "Operating System :: POSIX :: BSD",
            "Operating System :: POSIX :: Linux",
            "Programming Language :: Cython",
            "Topic :: Software Development :: Libraries :: Application Frameworks",
        ],
        ext_modules=[cyhdfs],
        cmdclass={'build_ext': build_ext}
        )



