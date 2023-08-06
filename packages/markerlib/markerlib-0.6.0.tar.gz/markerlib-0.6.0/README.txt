
markerlib
=========

Compile or interpret PEP 345 environment markers.

Usage::

    >>> import markerlib
    >>> marker = markerlib.compile("os.name == 'posix'")
    >>> marker(environment=markerlib.default_environment(),
               override={'os.name':'posix'})
    True
    >>> marker(environment=markerlib.default_environment(),
               override={'os.name':'nt'})
    False

The implementation uses the ast to compile environment markers as Python
statements with a limited set of allowed node types.

