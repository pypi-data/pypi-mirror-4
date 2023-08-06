# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013 Rocky Bernstein
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
import imp, os, sys
def get_srcdir(level=1):
    """Get directory of caller as an absolute file name. *level* is
    the number of frames to look back.  So for import file which is
    really doing work on behalf of *its* caller, we go back 2.

    NB: f_code.co_filenames and thus this code kind of broken for
    zip'ed eggs circa Jan 2009
    """

    caller = sys._getframe(level)
    filename = caller.f_code.co_filename
    filename = os.path.normcase(os.path.dirname(os.path.abspath(filename)))
    return os.path.realpath(filename)

def get_src(level=1):
    """Get caller filename as an absolute file name. *level* is
    the number of frames to look back.  So for import file which is
    really doing work on behalf of *its* caller, we go back 2.

    NB: f_code.co_filenames and thus this code kind of broken for
    zip'ed eggs circa Jan 2009
    """
    caller = sys._getframe(level)
    filename = caller.f_code.co_filename
    filename = os.path.normcase(os.path.abspath(filename))
    return os.path.realpath(filename)


def get_namespace(top_name, srcdir):
    """Return a compound 'import' string e.g. "a.b.c" based on *srcdir* and
    *top_name*.  Note: we assume packages don't have subdirectories
    with the same name as the package. E.g. pydbg.pydbg or
    pydbg.foo.pydbg is forbidden.
    """
    srcdirs = srcdir.split(os.path.sep)
    if top_name in srcdirs:
        srcdirs.reverse()
        prefix = srcdirs[:srcdirs.index(top_name)]
        prefix.reverse()
        if len(prefix) > 0:
            return "%s.%s" % (top_name, '.'.join(prefix))
        else:
            return top_name
        pass
    return None

def path2abspath(path, call_level):
    '''Turn path into an absolute file name.'''
    alldots = False
    if path is None:
        srcdir = get_srcdir(call_level)
    elif os.path.sep == path[0]:
        srcdir = path
    else:
        # Check for ., .., ...
        if '.' == path[0]:
            alldots = True
            i = 1
            pardir = '.'
            for i in range(1,len(path)):
                if path[i] != '.':
                    path = path[i:]
                    alldots = False
                    break
                pardir = os.path.join(pardir, os.path.pardir)
                pass
            if alldots:
                srcdir = os.path.abspath(os.path.join(get_srcdir(call_level),
                                                      pardir))
            else:
                srcdir = os.path.abspath(os.path.join(get_srcdir(call_level),
                                                      pardir, path))
                pass
            pass
        else:
            srcdir = os.path.abspath(os.path.join(get_srcdir(call_level),
                                                      '.', path))
        pass
    return srcdir

def import_relative(import_name, path=None, top_name=None):
    """Import `import_name' using `path' as the location to start
    looking for it.  If `path' is not given, we'll look starting in
    the directory where the import_relative was issued. In contrast to
    __import__() which this uses, we alway return the last import
    module when a compound import (e.g. a.b.c) is given.  Sorry, we
    don't do "from lists", global or local variables here.

    TODO: add a package/namespace parameter for which to add the name under.
    """

    srcdir = path2abspath(path, 3)

    if top_name:
        namespace = get_namespace(top_name, srcdir)
    else:
        namespace = None
        pass

    import_modules = import_name.split('.')
    top_module = import_modules[0]
    top_file_prefix = os.path.join(srcdir, top_module)

    if namespace:
        namespaced_top_module = "%s.%s" % (namespace, top_module)
    else:
        namespaced_top_module = top_module
        pass

    mod = sys.modules.get(namespaced_top_module)
    if not mod or not mod.__file__.startswith(top_file_prefix):

        # If any of the following calls raises an exception,
        # there's a problem we can't handle -- let the caller handle it.

        try:
            fp, pathname, description = imp.find_module(top_module, [srcdir])
        except ImportError:
            raise ImportError("No module %s found in %s" %
                              (top_module, srcdir))
        module_save = None
        if sys.modules.get(namespaced_top_module):
            # Temporarily nuke module so we will have to find it anew using
            # our hacked sys.path.
            fn = sys.modules[namespaced_top_module].__file__
            if not fn.startswith(os.path.join(srcdir, top_module)):
                module_save = sys.modules[namespaced_top_module]
                del sys.modules[namespaced_top_module]
                pass
            pass
        try:
            try:
                mod = imp.load_module(namespaced_top_module, fp, pathname,
                                      description)
            except (SystemError, ImportError):
                mod = imp.load_module(top_module, fp, pathname, description)
                pass

            sys.modules[namespaced_top_module] = mod
        finally:
            # Since we may exit via an exception, close fp explicitly.
            if fp:
                fp.close()
                pass
            if module_save:
                sys.modules[top_module] = module_save
            elif namespace and top_module in sys.modules:
                del sys.modules[top_module]
                pass
            pass
        pass

    # find_module module doesn't seem to work for compounds,
    # e.g. imp.find_module('a.b', '/path/to/a').  Maybe when I
    # understand 'knee' from:
    # http://docs.python.org/library/imputil.html better. (It seems
    # to be a translation into Python of its C code).
    #
    # Until then, So we'll use this hacky method which doesn't deal
    # with "from .. import .. as .." renaming which would need to look
    # at __name__.

    prefix = namespaced_top_module
    prev   = mod
    del import_modules[0]
    for mod_name in import_modules:
        prefix += '.' + mod_name
        if namespace:
            namespaced_prefix = "%s.%s" % (namespace, prefix)
        else:
            namespaced_prefix = prefix
            pass
        module_save = None
        if sys.modules.get(namespaced_prefix):
            # Temporarily nuke module so we will have to find it anew using
            # our hacked sys.path.
            fn = sys.modules[namespaced_prefix].__file__
            if not fn.startswith(os.path.join(srcdir, top_module)):
                module_save = sys.modules[namespaced_prefix]
                del sys.modules[namespaced_prefix]
                pass
            pass
        try:
            next_mod = __import__(prefix, None, None, ['__bogus__'])
            if namespace:
                sys.modules[namespaced_prefix] = next_mod
                pass
        finally:
            if module_save:
                sys.modules[prefix] = module_save
            elif namespace and prefix in sys.modules:
                del sys.modules[prefix]
                pass
            pass

        if hasattr(next_mod, '__path__'):
            np = next_mod.__path__
            np[0], np[-1] = np[-1], np[0]
            pass
        setattr(prev, mod_name, next_mod)
        prev = next_mod
        pass

    return prev

# Demo it
if __name__=='__main__':
    print(path2abspath('.', 2))
    print(get_namespace('pydbg', '/src/pydbg/pydbg'))
    Mtest = import_relative('test.os2.path', '.', 'import-relative')

    print(get_namespace('pydbg', '/src/pydbg/pydbg/processor/commands'))

    Mimport_relative = import_relative('import_relative')
    print(Mimport_relative)
    print(Mimport_relative.__name__)
    print(Mimport_relative.__file__)
    # The 2nd time around, we should have info cached.
    # Can you say Major Major?
    import_relative2 = Mimport_relative.import_relative('import_relative',
                                                        '.')


    # Originally done with os.path, But nosetest seems to use this.
    os2_path = Mimport_relative.import_relative('os2.path', 'test',
                                                'import_relative')
    print(os2_path)
    print(os2_path.__name__)
    print(os2_path.__file__)
    print(os2_path.me)
    # Warning. I've destroyed the real os.
    pass
