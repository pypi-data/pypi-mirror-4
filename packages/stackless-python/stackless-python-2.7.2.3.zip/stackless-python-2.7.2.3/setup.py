from distutils.core import setup
from distutils.util import get_platform, byte_compile
from distutils.command.install_data import install_data
from distutils.command.build_clib import build_clib
from distutils.command.install_lib import install_lib
from distutils.command.install_scripts import install_scripts

# from distutils.command import build
from distutils import log
from distutils import filelist

import sysconfig


import sys
from os.path import join, normpath, dirname, basename, abspath
from os import remove as os_remove
from os import __file__ as os__file__

from zipfile import PyZipFile

stacklessVersion = (2,7,2)
installerVersion = (3,)

stacklessVersionStr = ".".join(map(str,stacklessVersion))
installerVersionStr = ".".join(map(str,stacklessVersion + installerVersion))

if sys.version_info[:3] not in ((2, 7, 2), (2,7,3)):
    print 'ERROR: Stackless Python %s requires Python %s to run.' % (stacklessVersionStr, stacklessVersionStr)
    sys.exit(1)

pyAndVersion="python" + str(stacklessVersion[0]) + str(stacklessVersion[1])

platform = get_platform()
distRoot = dirname(__file__)

scripts = []
libraries = []
data_files=[]
packages=[]
py_modules = []
cmdclass = {}

class my_build_clib(build_clib):
    """A build_clib command with a hook option to build data targets""" 
    def build_libraries(self, libraries):
        realLibs = libraries[:]
        if self.distribution.data_files is None:
            self.distribution.data_files = []
        for (i,lib) in enumerate(libraries):
            lib_name, buildInfo = lib
            buildMethod = buildInfo.get('build_method')
            if buildMethod:
                del realLibs[i]
                getattr(self, buildMethod)(lib_name, buildInfo)
        
        # call the super method
        return build_clib.build_libraries(self, realLibs)

    def build_pythonzip_win32(self, name, build_info):
        """Build the library archive for windows"""
        target = join(self.build_clib, name)
        self.mkpath(self.build_clib)
        log.info("creating library archiv %s", target)
        if not self.dry_run:
            try:
                os_remove(target)
            except OSError, e:
                pass
                # print >> sys.stderr, "Failed to remove %s: %s" % (fullZipName, e)
            with PyZipFile(target, 'w') as myzip:
                myzip.debug = self.debug
                for source in build_info['sources']:
                    myzip.writepy(source)
        self.distribution.data_files.append((build_info['install_dir'], [target]))

    # Build the shared library for Linux
    
    EPREFIX="/EXEC_PREFIX-DOES-NOT-EXSIST"
    PREFIX="/PREFIX-DOES-NOT-EXSIST"
    
    def _setValueInBytes(self, bytes, marker, value):
        lMarker = len(marker)
        lValue  = len(value)
        if lMarker < lValue:
            marker += "-" * (lValue - lMarker)
            l = lValue
        else:
            value += "\x00" * (lMarker - lValue)
            l = lMarker
        assert len(marker) == len(value)
        assert len(marker) == l
            
        i = 0
        while True:
            i = bytes.find(marker, i)
            if -1 == i:
                break
            bytes[i:i+l] = value
            bytes[i+l] = 0

            
    def build_pylib_linux(self, name, build_info):
        source = build_info['sources'][0]
        with open(source, "rb") as s:
            lib = bytearray(s.read())
        self._setValueInBytes(lib, self.PREFIX, sysconfig.get_config_var("prefix"))
        self._setValueInBytes(lib, self.EPREFIX, sysconfig.get_config_var("exec_prefix"))
        
        target = join(self.build_clib, basename(source))
        self.mkpath(self.build_clib)
        log.info("creating library %s", target)
        if not self.dry_run:
            with open(target, "wb") as t:
                t.write(lib)
        self.distribution.data_files.append((build_info['install_dir'], [target]))

class my_install_data(install_data):
    """This install_data command calls build_clib on demand"""
    user_options = install_data.user_options + [
        ('skip-build', None, "skip the build steps"), 
        ]

    def initialize_options(self):
        install_data.initialize_options(self)
        self.skip_build = None

    def finalize_options(self):
        install_data.finalize_options(self)
        # Get all the information we need to install pure Python modules
        # from the umbrella 'install' command 
        self.set_undefined_options('install',
                                   ('skip_build', 'skip_build'),
                                   )

    def run(self):
        self.build()
        return install_data.run(self)
        
    def build(self):
        if not self.skip_build:
            if self.distribution.has_c_libraries():
                self.run_command('build_clib')
         
                                   
cmdclass['build_clib'] = my_build_clib
cmdclass['install_data'] = my_install_data



if "win32" == platform:
    arch="win32"
    assembly="com.stackless."+pyAndVersion
    zipName=pyAndVersion + ".zip"
    zipSrc="Lib"
    fullZipName = join(distRoot, zipName)

    pylib = [join(arch, assembly, assembly+".MANIFEST"),
             join(arch, assembly, pyAndVersion+".dll") ]
    pyexe = [join(arch, 'slpython.exe'), join(arch,'slpythonw.exe')]
    
    pybindest = ''
    pylibdest = assembly


    #print "Datafiles"
    #from pprint import pprint ; pprint(data_files)
    data_files.extend([(pybindest, pyexe),
                       (pylibdest, pylib )])

    libraries.append(
                     (zipName, dict(sources = [ join(distRoot, zipSrc), join(distRoot, zipSrc, "distutils")], 
                                         build_method='build_pythonzip_win32', 
                                         install_dir=pylibdest ))
    )
    

elif "linux-x86_64" == platform:
    arch = platform
    assembly="lib.stackless"
    pylib = join(arch, assembly, "libpython%s.%s.so.1.0sl" % stacklessVersion[:2] )
    pyexe = join(arch, 'slpython%s.%s' % stacklessVersion[:2])
    pybindest = dirname(abspath(sys.executable))
    pylibdest = join(pybindest, assembly)

    stacklessPackages = join(dirname(abspath(os__file__)), "stackless-packages")
        
    libraries.append(
                     ('pylib', dict(sources = [ pylib ], build_method='build_pylib_linux', install_dir=pylibdest ))
    )
    
    scripts.append(pyexe)
    packages.extend(["distutils", "distutils.command"])
    py_modules.extend(['copy_reg', 'pickle', 'platform'])

    
    class my_install_lib(install_lib):
        """This class installs into the stackless-packages directory"""
        def install(self):
            savedInstallDir = self.install_dir
            self.install_dir = stacklessPackages
            try:
                self.mkpath(self.install_dir)
                return install_lib.install(self)
            finally:
                self.install_dir = savedInstallDir
                 
    class my_install_scripts(install_scripts):
        def initialize_options (self):
            install_scripts.initialize_options(self)
            self.install_dir = pybindest
            
    cmdclass['install_lib'] = my_install_lib
    cmdclass['install_scripts'] = my_install_scripts
    
        
else:
    raise NotImplementedError("Platform %s not yet supported" % (platform,))
       
setup(
    cmdclass=cmdclass,
    name='stackless-python',
    version=installerVersionStr,
    description='Installer for Stackless Python',
    author='Christian Tismer',
    author_email='tismer@stackless.com',
    maintainer='Anselm Kruis',
    maintainer_email='a.kruis@science-computing.de',
    url='http://www.stackless.com',
    package_dir = {'': 'Lib'},
    packages=packages,
    py_modules = py_modules,
    libraries = libraries,
    data_files=data_files,
    scripts = scripts, 
    long_description=open("README.rst").read(),
    classifiers=[
          "License :: OSI Approved :: Python Software Foundation License",
          "Programming Language :: Python",
          "Programming Language :: Python :: "+".".join(map(str,stacklessVersion[:2])),
          "Programming Language :: Python :: Implementation :: Stackless", 
          "Operating System :: Microsoft :: Windows :: Windows XP",
          "Operating System :: POSIX :: Linux",
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Developers",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='stackless',
      license='Python Software Foundation License',
      platforms="win32, linux AMD64",
    )
