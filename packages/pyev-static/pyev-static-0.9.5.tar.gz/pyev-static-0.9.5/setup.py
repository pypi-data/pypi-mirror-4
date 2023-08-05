import os
import re
import sys
from os.path import join as pjoin
from glob import glob
import shutil

from setuptools import setup, Command, Extension, find_packages
from setuptools.command.sdist import sdist
from setuptools.command.build_ext import build_ext

from utils.bundle import fetch_libev, configure, bundled_version
from utils.detect import detect_ev
from utils.other import temporary_directory


#-----------------------------------------------------------------------------
# Utils
#-----------------------------------------------------------------------------

def dotc(name):
    return os.path.abspath(pjoin('pyev', name + '.c'))


def doth(name):
    return os.path.abspath(pjoin('pyev', name + '.c'))


#-----------------------------------------------------------------------------
# Flags
#-----------------------------------------------------------------------------

bundledir = "bundled"


#-----------------------------------------------------------------------------
# Compiler settings
#-----------------------------------------------------------------------------

def bundled_settings():
    settings = {
       'libraries': [],
       'include_dirs': [pjoin(bundledir, 'libev')],
       'library_dirs': [],
    }
    return settings


def system_settings():
    settings = {
       'libraries': ['ev'],
       'include_dirs': [],
       'library_dirs': [],
    }
    return settings


COMPILER_SETTINGS = {}


#-----------------------------------------------------------------------------
# Default Values
#-----------------------------------------------------------------------------

define_fmt = "\"{0}\""

cmdclass = {}

extensions = []

package_data = {}


#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------


class FetchCommand(Command):
    """Fetch libev sources, that's it."""

    description = "Fetch libev sources into bundled"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # fetch sources for libev extension:
        if not os.path.exists(bundledir):
            os.makedirs(bundledir)
        fetch_libev(bundledir)
        for tarball in glob(pjoin(bundledir, '*.tar.gz')):
            os.remove(tarball)

cmdclass['fetch'] = FetchCommand


class CheckSDist(sdist):
    """Custom sdist that ensures that libev is ready."""

    def run(self):
        # Clean before fetch.
        if os.path.exists(bundledir):
            shutil.rmtree(bundledir)
        self.run_command('fetch')
        sdist.run(self)

cmdclass['sdist'] = CheckSDist


class Configure(Command):
    """Configure command adapted from h5py."""

    description = "Discover libev"

    user_options = []

    def initialize_options(self):
        self.libev = 'system'

    def finalize_options(self):
        pass

    def detect_system_libev(self):
        with temporary_directory() as basedir:
            try:
                config = detect_ev(basedir, **system_settings())
            except Exception:
                etype, evalue, tb = sys.exc_info()
                # print the error as distutils would if we let it raise:
                print ("\nerror: %s\n" % evalue)
            else:
                print ("libev version detected: %s.%s" % config['vers'])
                return config

    def bundle_libev_extension(self):
        if self.distribution.ext_modules and \
           self.distribution.ext_modules[0].name == 'pyev.libev':
            # I've already been run
            return

        self.libev = 'bundled'
        settings = bundled_settings()

        print ("Using bundled libev")

        # fetch sources for libev extension
        fetch = self.distribution.get_command_obj('fetch')
        fetch.run()

        # configure libev
        configure(pjoin(bundledir, 'libev'))

        # find depended libraries
        libev_config = open(pjoin(bundledir, 'libev', 'config.h'), "r").read()
        libraries = [l.lower() for l in set(re.findall("#define HAVE_LIB(\S+) 1",
                                            libev_config))]
        settings['libraries'] = list(set(libraries + settings.get('libraries', [])))

        # register libev as extension
        ext = Extension(
            'pyev.libev',
            sources=[pjoin('utils', 'initlibev.c')],
            define_macros=[('LIBEV_EMBED', '1'),
                           ('EV_MULTIPLICITY', '1')],
            **settings
        )

        # Fix for distribute
        ext._needs_stub = False

        # insert the extension
        self.distribution.ext_modules.insert(0, ext)

        return dict(settings=settings,
                    vers=bundled_version)

    def run(self):
        # Try to build with system wide libev.
        config = self.detect_system_libev()

        if config is None:
            # No system wide found, try to build with bundled version.
            config = self.bundle_libev_extension()

        settings = config['settings']
        modules = self.distribution.ext_modules \
                  if self.libev == 'system' \
                  else self.distribution.ext_modules[1:]
        for ext in modules:
            for attr, value in settings.items():
                setattr(ext, attr, value)

cmdclass['configure'] = Configure


class CheckingBuildExt(build_ext):

    def run(self):
        configure = self.distribution.get_command_obj('configure')
        configure.run()
        return build_ext.run(self)

cmdclass['build_ext'] = CheckingBuildExt


#-----------------------------------------------------------------------------
# Description, version and other meta information.
#-----------------------------------------------------------------------------

re_meta = re.compile(r'__(\w+?)__\s*=\s*(.*)')
re_vers = re.compile(r'VERSION\s*=\s*\((.*?)\)')
re_doc = re.compile(r'^"""(.+?)"""')
rq = lambda s: s.strip("\"'")


def add_default(m):
    attr_name, attr_value = m.groups()
    return ((attr_name, rq(attr_value)),)


def add_version(m):
    v = list(map(rq, m.groups()[0].split(', ')))
    return (('VERSION', '.'.join(v[0:3]) + ''.join(v[3:])),)


def add_doc(m):
    return (('doc', m.groups()[0]),)

pats = {re_meta: add_default,
        re_vers: add_version,
        re_doc: add_doc}
here = os.path.abspath(os.path.dirname(__file__))
meta_fh = open(os.path.join(here, 'pyev/__init__.py'))
try:
    meta = {}
    for line in meta_fh:
        if line.strip() == '# -eof meta-':
            break
        for pattern, handler in pats.items():
            m = pattern.match(line.strip())
            if m:
                meta.update(handler(m))
finally:
    meta_fh.close()


with open('README.rst') as fh:
    long_description = fh.read()


#-----------------------------------------------------------------------------
# Extensions
#-----------------------------------------------------------------------------

extensions.append(
    Extension("pyev._pyev",
              ["src/pyev.c"],
              define_macros=[('PYEV_VERSION',
                              define_fmt.format(meta['VERSION']))],
              **COMPILER_SETTINGS
    )
)


#-----------------------------------------------------------------------------
# Setup
#-----------------------------------------------------------------------------

setup(
    name="pyev-static",
    packages=find_packages(),
    version=meta['VERSION'],
    description=meta['doc'],
    long_description=long_description,
    author=meta['author'],
    author_email=meta['contact'],
    url=meta['homepage'],
    ext_modules=extensions,
    package_data=package_data,
    platforms=["Microsoft Windows", "POSIX"],
    license="BSD License / GNU General Public License (GPL)",
    cmdclass=cmdclass,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: Microsoft :: Windows :: Windows NT/2000",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
    ]
)
