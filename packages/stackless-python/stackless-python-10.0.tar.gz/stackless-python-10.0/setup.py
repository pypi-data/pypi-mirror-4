#
# Copyright 2013 Anselm Kruis
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

# (I choose the Apache License, because the Python Software Foundation 
# requires this license for contributions. See http://www.python.org/psf/contrib/)

"""
Installer for Stackless Python
==============================

This distribution helps you to install `Stackless Python <http://www.stackless.com>`_.

Because Stackless Python is a variant of the CPython interpreter,
it can't be installed as a `Python Egg <http://peak.telecommunity.com/DevCenter/PythonEggs>`_.
Fortunately this does not mean that there is no way to install Stackless Python using 
commonly used installation methods like 
`setuptools <http://peak.telecommunity.com/DevCenter/setuptools>`_, 
`distribute <http://http://pythonhosted.org/distribute/index.html>`_ or 
`pip <http://www.pip-installer.org>`_. It is just a bit involved.

The installation of Stackless Python is a two step 
process:

1. Install *stackless-python* (this distribution). It is a very 
   lightweight "umbrella"-installer and mostly selects
   the appropriate "stackless_installer" distribution for the next step.
2. Install a "stackless_installer" distribution 
   that contains Stackless Python compiled for the current platform. 
   
How does it work in detail? 

Dynamic Requirements
--------------------

Usually Python Eggs declare their requirements statically within their egg-info
directory. This helps tools like easy_install and pip to manage dependencies. 
Unfortunately the *stackless-python* distribution must compute the requirement
during installation and therefore can't declare the dependency in advance.

Fortunately packaging *stackless-python* as a sdist using the ancient :mod:`distutils` instead 
of :mod:`setuptools` helps, because distutils does not create the egg-info structure at 
all. During installation, if easy_install or pip encounter such a sdist, they 
execute ``setup.py egg-info`` to compute the egg info dynamically.

The *stackless-python* setup.py checks if the current python is suitable 
for a Stackless installation and computes the name of the "stackless_installer" 
distribution. The name depends on the current platform, the Python version 
and on the unicode character size (UCS2 or UCS4). See function :func:`get_stackless_package`
for details. 

Setup Requirements
------------------

Usually easy_install or pip first install a distribution and then install the requirements
of the distribution. This is fine for run-time requirements. In our case we need the requiremnet 
during installation and declare a so called *setup-requirement*. This kind of requirement
gets installed during the installation of a Python-Egg only.  

Dependency Links
----------------

Over time we will need several different "stackless_installer" distributions. One for each
release of Stackless and supported platform. To keep control about the naming of these
distributions and to avoid namespace clutter on PyPi, *stackless-python* uses 
a dependency link to download the stackless_installer distributions direct from 
a web server. 

How to build stackless-python sdist
-----------------------------------

Run ``python -S setup.py check sdist``. The flag ``-S`` is important, because 
it disables :mod:`setuptools` and enforces the fall back to :mod:`distutils`.

"""
from __future__ import absolute_import

import sys
try:
    from setuptools import setup
    from setuptools.command.install_lib import install_lib
except ImportError:
    from distutils.core import setup
    from distutils.command.install_lib import install_lib
from distutils import log

from stackless_python_umbrella import INSTALLER_VERSION, get_dependency_links, get_stackless_package

installerVersionStr = ".".join(map(str,INSTALLER_VERSION))

# the installation of the module stackless_python_umbrella ensures, that 
# the install_lib command runs during the installation of this distribution
class InstallWithScript(install_lib):
    def run(self):
        result = install_lib.run(self)
        if not self.dry_run:
            dist = get_stackless_package()[0]
            from distutils import spawn
            cmd = [sys.executable, 
                   "-c", 
                   """import sys;from pkg_resources import load_entry_point;sys.exit(load_entry_point('%s', 'console_scripts', 'install-stackless')())""" % dist
                   ]
            spawn.spawn(cmd, search_path=0, verbose=self.verbose, dry_run=self.dry_run)
            log.info("Installed Stackless Python")
        return result



# various variables for setup(...)
cmdclass={}
setup_requires = []
dependency_links = []

installer, reqVersion = get_stackless_package() 
if installer is not None:
    cmdclass['install_lib'] = InstallWithScript
    setup_requires.append(installer+reqVersion)
    dependency_links.extend(get_dependency_links(installer, reqVersion))
       
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
    setup_requires = setup_requires, 
    #install_requires = setup_requires,  # uncomment to install the installer permanently 
    requires = [], # no requirements
    dependency_links = dependency_links,
    py_modules = ['stackless_python_umbrella'],
    long_description=open("README.rst").read(),
    classifiers=[
          "License :: OSI Approved :: Apache Software License", # for this umbrella installer
          "Programming Language :: Python",
          "Programming Language :: Python :: Implementation :: Stackless", 
          "Operating System :: Microsoft :: Windows",
          "Operating System :: POSIX :: Linux",
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Developers",
          "Topic :: Software Development :: Interpreters",
      ],
      keywords='stackless',
      license='Apache License, Version 2.0',
    )
