def _setup_path():
    global __path__
    from pkgutil import extend_path
    from traceback import print_exc
    from sys import exc_info
    path = __path__
    __path__ = extend_path(__path__, __name__)
    additionalDirs = __path__[:]
    for p in path:
        try:
            additionalDirs.remove(p)
        except ValueError:
            print_exc()
            pass
    from imp import find_module
    try:
        (file, pathname, description) = find_module("__init__", additionalDirs)
    except ImportError:
        print_exc()
        pass
    else:
        try:
            try:
                exec file in globals()
            except ImportError:
                raise
            except Exception:
                einfo = exc_info()
                raise ImportError, "Failed to exec file '%s' with exception: %s" % (pathname, einfo[1]), einfo[2]
        finally:
            file.close()
        
_setup_path()
del _setup_path
