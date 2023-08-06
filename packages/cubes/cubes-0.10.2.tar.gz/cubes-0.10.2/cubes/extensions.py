# -*- coding=utf -*-

import sys



ext_namespaces = {
            "backends": {},
            "formatters": {},
            "searchers": {}
        }


# Slicer Config
# formatters=

def load_module_extensions(namespace, names):
    pass

def load_class_extensions(namespace, names)

def get_extension(namespace, name):
    """Gets an extension object. Examples:

    >>> get_extension("backends", "sql") 
    >>> get_extension("formatters", "cross_table")

    """

    try:
        objects = ext_namespaces[namespace]
    except KeyError:
        raise CubesError("Unknown extensions namespace '%s'" % namespace)

    if name in objects:
        return objects[name]


def module_loader(name, wrapper=None):
    # try to find within wrapper module
    if wrapper:
        full_name = "%s.%s" % (wrapper, name)
        if full_name in sys.modules:
            return full_name

    # try absolute module
    if name in sys.modules:
        return sys.modules[name]

    # Try to load absolute module
    if wrapper:
        try:
            __import__(full_name)
        except Exception as e:
            raise CubesError("Can not load extension module '%s', reason: %s"
                    % (full_name, e))

def get_backend(backend_name):
    """Finds the backend with name `backend_name`. First try to find backend
    relative to the cubes.backends.* then search full path. """

    backend_name = backend_aliases.get(backend_name, backend_name)
    backend = sys.modules.get("cubes.backends."+backend_name)

    if not backend:
        # Then try to find a module with full module path name
        try:
            backend = sys.modules[backend_name]
        except KeyError as e:
            raise Exception("Unable to find backend module %s (%s)" % (backend_name, e))

    if not hasattr(backend, "create_workspace"):
        raise NotImplementedError("Backend %s does not implement create_workspace" % backend_name)

    return backend

