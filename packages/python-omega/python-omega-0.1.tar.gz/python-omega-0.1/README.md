The Omega Parsing Framework
===========================

- **Author:** Timothy Allen <screwtape@froup.com>
- **Website:** https://gitorious.org/python-omega/
- **Mailing-list:** <python.omega@librelist.com>
- **Licence:** The Omega package and all associated documentation and example
  code are placed under the GNU GPLv3. See the included file `LICENCE` for
  details.

Introduction
------------

Omega is a framework designed to help you build parsers for text and binary
data. It creates a recursive-descent/Parsing-Expression-Grammar parser given
a description of the file-format in the concise Omega language, but if your
file-format can't be described in pure Omega, it's easy to extend with Python.

For example, here's a very simple parser for arithmetic expressions:

    >>> import omega
    >>> class ArithmeticParser(omega.BaseParser):
    ...     __grammar = """
    ...             digit = '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7'
    ...                     | '8' | '9' ;
    ...             term = digit+:ds -> (int("".join(ds)))
    ...                     | '(' sum:s ')' -> (s)
    ...                     ;
    ...             product = term:a '*' product:b -> (a * b)
    ...                     | term:a '/' product:b -> (a / b)
    ...                     | term
    ...                     ;
    ...             sum = product:a '+' sum:b -> (a + b)
    ...                     | product:a '-' sum:b -> (a - b)
    ...                     | product
    ...                     ;
    ...         """

And here it is in action:

    >>> ArithmeticParser.match("1")
    1
    >>> ArithmeticParser.match("1+1")
    2
    >>> ArithmeticParser.match("6*9")
    54
    >>> ArithmeticParser.match("2+3*4")
    14
    >>> ArithmeticParser.match("(2+3)*4")
    20

Omega is heavily based on ideas from Alessandro Warth's [OMeta package][1] for
Smalltalk and JavaScript, but translated to fit as naturally as possible into
Python.

[1]: http://tinlizzie.org/~awarth/ometa/

Requirements
------------

Omega is a pure-Python package, and requires only Python 2.7 to be installed.
It will likely be ported to Python 3.0 in the near future.

What's In The Box
-----------------

- `README.md` is this file.
- `TODO.md` is a list of possible future additions to the package.
- `LICENCE` is the full text of the licence this software is released under,
  the GPLv3.
- `setup.py` is the standard Python packaging script.
- `docs` is a subdirectory containing all the documentation for Omega,
  including language and library references, a Python API reference, and
  a tutorial.
- `examples` is a subdirectory containing various self-contained example
  parsers written in Omega.
- `omega` is the Python package itself.

Installation
------------

Omega uses the standard `distutils` packaging system for Python, so if you have
a source tarball, you should be able to install it with:

    python setup.py install

...and of course all the other standard `distutils` commands are available.

Documentation
-------------

The complete documentation is packaged with Omega source releases, and is also
available online at https://gitorious.org/python-omega/pages/Home
