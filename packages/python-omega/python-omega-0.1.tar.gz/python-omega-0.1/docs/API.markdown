Introduction
============

This document describes the Python side of the Omega library; how to
define and use an Omega parser from within a Python program, what
customisations are available, and creating hybrid parsers where some of
the parsing rules are implemented in Omega and some in Python.

All the usage examples below will be run in the following environment:

    >>> from omega import BaseParser

Parsing Basics
==============

The core idea of Omega, as inherited from Alessandro Warth's
[OMeta] (http://tinlizzie.org/~awarth/ometa/), is that a parser should be
represented as an object, and each parsing rule should be a method on that
object. As well as giving the parser a convenient place to keep its state,
this also means that behaviour-sharing mechanisms like class inheritance
are available. Thus, an Omega parser is any class that inherits from
Omega's `BaseParser` class.

Here, we define a simple class that matches the single letter 'a'. 

    >>> class DemoParser(BaseParser):
    ...     __grammar = """
    ...             rule = 'a' -> 'matched!';
    ...         """

Note that the parser is just a Python class that inherits from BaseParser:

    >>> DemoParser
    <class '__main__.DemoParser'>
    >>> issubclass(DemoParser, BaseParser)
    True

Also, the `format` parsing rule has become a method on that class:

    >>> DemoParser.rule
    <unbound method DemoParser.rule>

The normal way to use a parser object is via the `.match()` class method
(note that this means you can never have a parsing rule named `match`, or
else it would override the class method!). Continuing from the previous
example:

    >>> DemoParser.match('a')
    'matched!'

We gave the `.match()` class method a sequence to parse, it ran the
parsing rules over the sequence and returned the information the rules
extracted. (For more details on `.match()`, see the reference below.)

Advanced Parser Definition
==========================

The `BaseParser` class provides runtime support for the parsing machinery,
but also allows you to customise certain aspects of the runtime's
behaviour.

Setting the default parsing rule
--------------------------------

When the `.match()` class method is called without specifying a particular
parsing rule, it uses the "default" parsing rule. Specifically, it uses
the parsing rule named in the `_start` class property. The rules for how
`_start` gets set are somewhat intricate:

`BaseParser` has `_start` set to `None`.

    >>> print BaseParser._start
    None

If a parser class explicitly sets `_start`, Omega will not mess with it.

    >>> class A(BaseParser):
    ...     _start = "foo"
    >>> A._start
    'foo'

If a parser class does not explicitly set `_start`, but a parent class has
set `_start` to something other than `None`, Omega will not mess with it.
This means that you can inherit from an existing parser, add and override
parsing rules without messing up the defaults.

    >>> class B(A):
    ...     pass
    >>> B._start
    'foo'

If a parser class defines rules in Omega (by setting the `__grammar` class
property), does not explicitly set `_start`, and the value of `_start`
inherited from the parent class is `None`, then `_start` will be set to
the name of the last rule defined in the Omega source code.

    >>> class DemoParser(BaseParser):
    ...     __grammar = """
    ...             rule = 'a';
    ...         """
    >>> DemoParser._start
    'rule'

If a parser class defines rules in Omega (by setting the `__grammar` class
property), and explicitly sets `_start` to `None`, Omega will not mess
with it. This means that you can create a library of parsing rules that
a user can inherit from, and let Omega pick a sensible default rule from
the user's grammar.

    >>> class DemoParser(BaseParser):
    ...     _start = None
    ...     __grammar = """
    ...             rule = 'a';
    ...         """
    >>> print DemoParser._start
    None

Customising backtracking state
------------------------------

Omega's parsing machinery is based on the Parsing Expression Grammar
algorithm, which means it does a lot of backtracking; it could potentially
parse a sequence almost to the end before deciding to backtrack and try
some other approach. If your parser class maintains any state outside of
the values returned by parse rules (for example, a parser for
an indentation-level-based language like Python would need to keep track
of 'current indentation level') then you need to make sure the Omega
parsing machinery correctly saves and restores that state when
backtracking occurs.

The `BaseParser` class provides two methods named `._makeState()` and
`._setState()` that provide for backtracking. For a full description of
these methods, see the API Reference below, but in summary:

- `._makeState()` is called at a point the parser thinks it might want to
  backtrack to later. It returns a tuple representing the parser's state.
- `._setState()` is called when the parser wants to backtrack, and it is
  given a tuple previously returned by `._makeState()`.

The tuples produced and consumed by `._makeState()` and `._setState()`
have as their first two components the sequence being parsed, and the
current position within that sequence. However, no assumptions are made
about the total length of the tuple; you are free to override
`._makeState()` to add extra items to the end of the tuple as long as you
also modify `._setState()` to remove them before calling the superclass.

It's also possible, though usually a bad idea, to obtain a state with
`._makeState()`, change the sequence or position, and pass the result
to`._setState()` later.

**Note 1:** because of Python's behaviour with multiple inheritance, you
shouldn't assume that `super()` will always call the implementation in
`BaseParser` even if that's the only class you inherit from. Always append
to and slice from the state tuple relative to last item; you don't know
what other parser state might be in there.

**Note 2:** Parser state is also used in the packrat cache Omega uses, so
parser state must be completely immutable so it can be used as
a dictionary key. Generally, that means you need to be able to represent
your parser state with tuples, strings and integers; no lists or dicts.

Advanced Parser Use
===================

Although the `.match()` class method is the right choice for most uses of
a parser, there may be situations where you want to instantiate a parser
and call parsing rules directly. 

    >>> class DemoParser(BaseParser):
    ...     __grammar = """
    ...             one_a = 'a';
    ...             many_as = one_a+;
    ...             any_bs = 'b'*;
    ...         """

Constructing a parser is easy enough - you just pass the sequence you want
to parse, then you can call parser rules as methods, which return the
value they parse:

    >>> dp = DemoParser("aaa")
    >>> dp.many_as()
    ['a', 'a', 'a']

The parser is not reset after each parsing rule is invoked; if you invoke
a rule that succeeds, then invoke another, the second one picks up where the
first finished:

    >>> dp = DemoParser("aaaaaa")
    >>> dp.one_a()
    'a'
    >>> dp.one_a()
    'a'
    >>> dp.many_as()
    ['a', 'a', 'a', 'a']

This also implies that if you invoke a parse rule that does not consume the
entire sequence, you won't be informed about trailing, unrecognised data:

    >>> dp = DemoParser("aaa")
    >>> dp.any_bs()
    []

However, if you invoke a parsing rule that fails to match, the parser
will be left in an undefined state, and no further rules should be invoked. If
you want to restore some previous state and try again, that's a big clue that
you probably should be writing a new parsing rule for your class rather than
poking at it from outside. See "Python-based Parsing Rules" below for details.

If you need to parse some inner portion of a larger sequence, you can
optionally pass a starting index to the constructor:

    >>> dp = DemoParser("aaaa", 2)
    >>> dp.many_as()
    ['a', 'a']

Since parting started at index 2, the `many_as` rule only matched the `a`s
at index 2 and 3.

Python-based Parsing Rules
==========================

Implementing basic parsing rules
--------------------------------

The Omega parsing machinery has certain expectations about the behaviour
of parsing rules; some of these are hinted at elsewhere but here they are
in detail:

- Parsing rules must be methods of a parser object.
- Parsing rules must have a name that begins with an alphabetic character
  (no numbers or underscores) - that is, all parsing rules are public
  methods.
- A parsing rule may have any number of parameters. However, because the
  behaviour of the rule probably depends on the content of the parameters,
  the parameters are stored in the packrat cache, so all parameters need
  to be immutable values.
- A parsing rule examines the input stream by calling other parsing rules,
  which are also methods on the same object. In particular, the `anything`
  parsing rule is the best way to get the next item from the sequence
  being parsed.
- If a parsing rule decides it does not match the sequence at the current
  position, it should call the `._backtrack()` method to raise the
  backtrack exception and initiate backtracking. See the description in
  the API reference below for details.

To illustrate these principles, here's a non-trivial Python-based parsing
rule that recognises the text inside a Python comment; that is, text
beginning with the `#` character and continuing until the next newline
character, symbolised as `\n`:

    >>> class PythonBasedParser(BaseParser):
    ...     # Because this parser does not define any rules in Omega,
    ...     # we need to set the staring rule manually.
    ...     _start = "py_comment"
    ...
    ...     def py_comment(self):
    ...         # Here we check that our comment starts with '#'
    ...         # and backtrack if it does not.
    ...         if self.anything() != '#':
    ...             self._backtrack("Expected '#'")
    ...         
    ...         # The res variable will be used to store the text of the
    ...         # comment as we uncover it.
    ...         res = []
    ...         
    ...         # Keep reading characters until we reach a newline.
    ...         # Notice that we don't have to care about detecting the
    ...         # end of the input stream: self.anything() will initiate
    ...         # backtracking if that happens.
    ...         while True:
    ...             c = self.anything()
    ...             if c == '\n':
    ...                 break
    ...             res.append(c)
    ...
    ...         # We have found a valid comment, return it.
    ...         return "".join(res)

Nobody would actually write this code in a real parser, of course - for
this particular example, Omega could express the same pattern much more
concisely:

    >>> class OmegaBasedParser(BaseParser):
    ...     __grammar = """
    ...             py_comment = '#' (~'\n' anything)*:res '\n'
    ...                     -> ("".join(res));
    ...         """

...but we're trying to demonstrate Omega's Python API here, not the
benefits of Omega.

Let's check both of these parsers against each other. Both demand that
a comment begin with a '#':

    >>> PythonBasedParser.match("not a comment")
    Traceback (most recent call last):
        ...
    BacktrackException: 1:Expected '#'
    >>> OmegaBasedParser.match("not a comment")
    Traceback (most recent call last):
        ...
    BacktrackException: 1:Expected '#'

...both of them demand that a comment end with a '\n':

    >>> PythonBasedParser.match("# not a comment")
    Traceback (most recent call last):
        ...
    BacktrackException: 15:Unexpected EOF
    >>> OmegaBasedParser.match("# not a comment")
    Traceback (most recent call last):
        ...
    BacktrackException: 15:Unexpected EOF

...and both of them accept a properly formatted comment.

    >>> PythonBasedParser.match("# an actual comment\n")
    ' an actual comment'
    >>> OmegaBasedParser.match("# an actual comment\n")
    ' an actual comment'

Implementing flow control
-------------------------

Omega provides many useful operators for quantifying exactly when and
where backtracking can occur, like the Optional, Many and Any quantifiers,
or the Alternative operator. However, these operators are not available to
parsing rules implemented in Python. If your parsing rule needs to specify
this kind of backtracking and quantifying, it's usually a good idea to
break your rule up into sub-rules and have an Omega rule that specifies
how they fit together with all the quantifiers and such. If that really
isn't practical for your parsing rule, here's how to do backtracking for
yourself:

- To "save" the parsing state so that you can backtrack to it later, call
  the `._makeState()` method.
- To detect when a parsing rule you directly or indirectly call has
  decided to backtrack, catch `self._backtrackException`.
- To reset the parsing state to a saved point, call the `._setState()`
  method.

For more information on these methods and properties, see the API
Reference below.

As an example, here is a pure-Python parser:

    >>> class PythonBasedParser(BaseParser):
    ...     # Because this parser does not define any rules in Omega,
    ...     # we need to set the staring rule manually.
    ...     _start = "any_abcs"
    ...
    ...     def any_abcs(self):
    ...         # The res variable will be used to store the text we match
    ...         # as we uncover it.
    ...         res = []
    ...
    ...         while True:
    ...             try:
    ...                 # Save the current parser state so we can come
    ...                 # back to it. Note that because this is done
    ...                 # within the while loop, each time we find a match
    ...                 # we are effectively bumping the saved state
    ...                 # forward past the data we matched.
    ...                 token = self._makeState()
    ...
    ...                 # Invoke the seq parsing rule, which will verify
    ...                 # that the next three items in the input sequence
    ...                 # are 'a', 'b' and 'c'. If they are, the value of
    ...                 # that parsing rule is added to res. If they are
    ...                 # not, backtracking will begin.
    ...                 res.append(self.seq("abc"))
    ...
    ...             except self._backtrackException:
    ...                 # The seq parsing rule failed to match, and so
    ...                 # began backtracking. Let's reset the parser state
    ...                 # to what it was just before we invoked seq, so
    ...                 # our caller can continue parsing the next thing,
    ...                 # and break out of this loop because obviously it
    ...                 # won't match again.
    ...                 self._setState(token)
    ...                 break
    ...
    ...         # We've found all the "abc"s we can find, let's go.
    ...         return res

...and here is the equivalent Omega-based parser.

    >>> class OmegaBasedParser(BaseParser):
    ...     __grammar = """
    ...             any_abcs = seq('abc')*;
    ...         """

Both of them accept zero "abc"s:

    >>> PythonBasedParser.match("")
    []
    >>> OmegaBasedParser.match("")
    []

Both of them match several "abc"s:

    >>> PythonBasedParser.match("abcabcabc")
    ['abc', 'abc', 'abc']
    >>> OmegaBasedParser.match("abcabcabc")
    ['abc', 'abc', 'abc']

If there is a partial match at the end of the sequence, it is not
consumed:

    >>> PythonBasedParser.match("abcab")
    Traceback (most recent call last):
        ...
    UnrecoverableParseError: 3:Found unexpected stuff: expected EOF, found 'ab'...
    >>> OmegaBasedParser.match("abcab")
    Traceback (most recent call last):
        ...
    UnrecoverableParseError: 3:Found unexpected stuff: expected EOF, found 'ab'...

Non-linear parsing
------------------

Although parsing traditionally operates in a single pass from the
beginning to the end of the input stream, not all file-formats can be
parsed this way. For example, ZIP and PDF files have their central data
structures at the end of the file, and some text-based formats like HTML
or Python source code have an character encoding declaration somewhere
inside them; to be correct you need to find the encoding declaration then
rewind, re-interpret the input stream according to the character encoding,
then start parsing again. These sorts of things are not easy to integrate
into a traditional parser, but if you're willing to write a little custom
code, you can do it with Omega.

The Omega parsing machinery maintains two instance variables named
`._sequence` and `._position`. `._sequence` refers to the input sequence
that is currently being parsed, while `._position` refers to the position
within that sequence. It's OK to manipulate these properties, as long as
you remember these guidelines:

- Don't manipulate these to implement backtracking for yourself; use the
  `._makeState()` and `._setState()` methods.
- If you change `._sequence` or `._position` you will probably want to set
  them back after you have done whatever special parsing you need.
- If you change `._sequence` you probably ought to set `._position` to
  0 as well.

Parser Class API
================

Here are the methods and properties available on parser classes.

As per Python convention, method or property beginning with two
underscores should only be called, set or read by the class that defines
it, anything beginning with one underscore should only be called, set or
read by the defining class or one that inherits from it, anything
beginning with no underscores can be called, set or read by anyone, and
any method or property not mentioned in the documentation should never be
touched under any circumstances.

Constructor
-----------

- Arguments:
    - `sequence` (any immutable sequence) is the sequence to be parsed.
    - `position` (integer, optional) is the index at which parsing will
      start in the given sequence. If not supplied, defaults to 0.
- Returns: N/A
- Raises: `TypeError` if the value supplied for the `sequence` parameter
  is mutable, not a sequence, or both.

Note that the sequence must be an immutable sequence. This is part of the
parser state that is stored in the packrat cache, which means it needs to
be a type which can be part of a Python dictionary key.

_backtrackException
-------------------

- Type: a subclass of `Exception`. The default value is
  `omega.BacktrackException`.

This is the exception that will be raised by the `._backtrack()` instance
method or by Omega parsing rules that fail to find a match. You can use
this attribute in an `except` clause to catch backtracking exceptions, but
don't raise it directly - call `._backtrack()` since that method
understands how to construct `BacktrackException` instances.

__grammar
---------

- Type: `str`

This property should contain valid parsing rules, written in the Omega
language.

_start
------

- Type: `str`

This property should contain the name of the parsing rule that `.match()`
should invoke by default, or `None`.

See "Setting the default parsing rule" above for details of how and when
Omega manipulates the `_start` property.

match()
-------

- Arguments:
    - `sequence` (any immutable sequence) is the sequence to be parsed.
    - `ruleName` (a string, optional) is the name of the parsing rule that
      the entire sequence is expected to match. If not supplied, the
      default parsing rule is used (see "Setting the default parsing rule"
      above).
- Returns: The value returned by the parsing rule used.
- Raises:
    - A subclass of `omega.ParseError` if the parsing rule used does not
      match the entire sequence given.
    - `ValueError` if `ruleName` is not a string, does not name an
      existing parsing rule, or if it is not provided and the `_start`
      property doesn't meet those criteria.
    - `RuntimeError` if various parsing-state sanity checks fail after the
      parsing rule has returned.

This is intended to be the main entry-point for using a parser. It
constructs a parser object with the given sequence, runs the parsing rules,
checks that the rules matched the entire sequence, and returns the result.

Parser Instance API
===================

Here are the methods and properties available on parser instances.

All these methods and properties start with a single underscore, which
means that they should only be called, set or read by the class that
defines them (`BaseParser`) or a subclass (your parser class). Any method
or property not mentioned in the documentation should never be touched
under any circumstances.

_backtrack()
------------

- Arguments:
    - `message` (a string) should be a human-readable description of why
      parsing has failed.
- Returns: never.
- Raises: 
    - An instance of the class referred to by `._backtrackException`.

If you are implementing a parsing rule in Python and you detect that the
input sequence does not match, this is the method to call. The message
passed will be available as the `.description` attribute on the resulting
exception, and it will be included in the exception message displayed in
tracebacks and so forth.

_makeState()
------------

- Arguments: none.
- Returns: a token describing the current parser state.
- Raises: never.

The token returned by `._makeState()` is a tuple containing
a serialisation of the current parser state. The implementation of
`._makeState()` in `BaseParser` returns a tuple with two elements: the
sequence being parsed, and the current parsing position within that
sequence. However, subclasses of BaseParser are free to extend
`._makeState()` to add any extra state the subclasses require, as long as
they keep the first two elements the same, and as long as they also extend
`._setState()` to match.

See "Customising backtracking state" above for details.

_setState()
-----------

- Arguments:
    - `token` is a value returned from a previous call to `._makeState()`
- Returns: `None`
- Raises: never.

`._setState()` takes a token as returned by `._makeState()` and
deserialises the parser state, resetting the parser instance to the way it
was when `._makeState()` was called.

See "Customising backtracking state" above for details.

_sequence
---------

- Type: (any immutable sequence)

This is the sequence currently being parsed by the parser instance. It is
initially set to the sequence passed to the constructor, but some parsing
rules might temporarily replace it with some other sequence. For example,
there might be a rule which recognises a compressed data stream,
decompresses it, parses the decompressed data, then continues parsing the
original sequence.

See "Non-linear parsing" above for more details.

_position
---------

- Type: `int`

This is an index into `._sequence` representing where the parser is
currently up to in parsing the sequence.

See "Non-linear parsing" above for more details.
