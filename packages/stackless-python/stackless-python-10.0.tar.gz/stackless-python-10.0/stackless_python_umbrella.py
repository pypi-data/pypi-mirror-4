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

'''
Common code of the Stackless Python installer.
'''

DEFAULT_DEPENDENCY_LINKS = [ "http://bitbucket.org/akruis/slp-installer/downloads" ]

# previous versions had version numbers 2.7.xx
# technically a version 3.x would be fine, but people will 
# confuse this with Python3. Therefore I start with version 10.
INSTALLER_VERSION = (10,0)

def get_stackless_package():
    """
    Compute the required Stackless-Python package.
    
    This method returns a string pair (name, version-specifier). 
    If the package :mod:`stackless` is already available, the method
    returns (None,None). 
    """
    from distutils.util import get_platform
    from distutils import log
    import sys
    
    # Python version check
    try:
        import stackless
    except ImportError:
        # fine, it is not Stackless Python or pypy
        pass
    else:
        log.info("Your Python version already provides the package 'stackless'")
        return None,None
    
    reqVersionMin = '.'.join(map(str,sys.version_info[:3]))
    vi = list(sys.version_info[:3])
    vi[-1] += 1
    reqVersionMax = '.'.join(map(str,vi))
    reqVersion = ">=%s,<%s" % (reqVersionMin, reqVersionMax)
    
    ucs = 4 if sys.maxunicode >> 16 else 2
    
    platform = get_platform()
    
    # check for PyPy. It uses the same platform values as CPython
    if getattr(sys, 'pypy_version_info', None):
        # older PyPy without stackless 
        raise RuntimeError("PyPy is not supported")
    
    # Jython
    elif platform.startswith("java"):
        raise NotImplementedError("Platform %s not yet supported" % (platform,))

    # Naming scheme
    #  - "stackless_installer" fixed
    #  - "C..." configuration details, currently only the ucs setting
    #  - "platform"
    installer = "stackless_installer_C%d_%s" % (ucs, platform.replace("-", "_"))

    return installer, reqVersion

def get_dependency_links(installer, reqVersion):
    return DEFAULT_DEPENDENCY_LINKS
