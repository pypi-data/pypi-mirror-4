Introduction
============

This document describes the pre-defined parsing rules available to
parsers written in the Omega language. Everything should be covered, but
there won't be much explanation of when a thing is useful; for a gentler
introduction see the [[Tutorial]]. Most of the basic library rules
come directly from Alessandro Warth's
[OMeta](http://tinlizzie.org/~awarth/ometa/) library for Squeak and
JavaScript, but sometimes there are differences to better integrate
Omega with Python. For information on syntax of Omega, see the
[[Language]] reference.

All the usage examples below will be run in the following environment:

    >>> from omega import BaseParser

Because these are built-in rules and they all have the same syntax as
far as Omega is concerned, they'll be demonstrated by invoking them from
Python instead of from inside Omega. For a complete discussion of referring to
these rules from within parsing rules written in Omega, see "Invocations" in
the [[Language]] reference. For information on referring to them from within
parsing rules written in Python, see the [[API]] reference.

Builtin rules
=============

These rules are available to every parser that inherits from
`omega.BaseParser`.

anything
--------

- Arguments: None
- Matches: any single item
- Value: the item matched

The `anything` rule is one of the fundamentals that other rules are
built on. It matches any single item, and only fails if the parser is
at the end of the stream. For example:

    >>> BaseParser('a').anything()
    'a'
    >>> BaseParser('').anything()
    Traceback (most recent call last):
        ...
    BacktrackException: 0:Unexpected EOF

apply
-----

- Arguments: 
    - `name`, the name of a rule to invoke
    - All subsequent arguments are passed to the rule being invoked
- Matches: whatever the named rule matches
- Value: the value returned by the named rule

Like Python's `apply()` function, the `apply` rule invokes another rule,
optionally passing it extra parameters. For example, the 'seq' rule can be
invoked directly:

    >>> BaseParser('a').seq('a')
    'a'

...or invoked indirectly through `apply`:

    >>> BaseParser('a').apply('seq', 'a')
    'a'

This is particularly useful if you define a rule that takes another rule name
as a parameter:

    >>> class DemoParser(BaseParser):
    ...     __grammar = """
    ...             listOfX :x = '[' apply(x):head (',' apply(x))*:tail ']'
    ...                     -> ([head] + tail);
    ...
    ...             char = '"' :c '"' -> (c);
    ...             listOfItem = listOfX('char');
    ...         """
    >>> DemoParser.match('["a","b","c"]')
    ['a', 'b', 'c']

Here, the rule `listOfX` is defined to take a rule-name as a parameter, then
uses the `apply` rule multiple times to parse an entire list of whatever name
it was given.

empty
-----

- Arguments: None
- Matches: always
- Value: The empty string (`''`)

The `empty` rule always matches, and consumes no input. It's useful as the
base-case for a recursive rule definition, like this:

    >>> class DemoParser(BaseParser):
    ...     __grammar = """
    ...             nestedBrackets = '(' nestedBrackets:x ')'
    ...                     -> ('(' + x + ')')
    ...                 | empty
    ...                 ;
    ...         """
    >>> DemoParser.match('(((())))')
    '(((())))'

end
---

- Arguments: None
- Matches: at the end of the input sequence
- Value: The Python value `None`

The `end` rule matches only at the end of the input sequence. This is not
so useful in practice, since when you call the `.match()` method on
a parser class it already checks that the parsing rule consumes all the
input. However, it may be useful if you need to invoke parsing rules
directly, outside the context of `.match()`.

exactly
-------

- Arguments:
    - `item`, any Python object
- Matches: if the next single item in the sequence being parsed is equal to the
  given item
- Value: the object passed in

The `exactly` rule checks that the next item in the sequence being parsed is
equal to the given item, according to the standard Python equality operator.
It's useful for situations where a regular expression might use
a back-reference, like this:

    >>> class DemoParser(BaseParser):
    ...     __grammar = """
    ...             replaceCommand = 's'
    ...                     anything:delimiter
    ...                     (~exactly(delimiter) anything)*:original
    ...                     exactly(delimiter)
    ...                     (~exactly(delimiter) anything)*:replacement
    ...                     exactly(delimiter)
    ...                         -> ('replace',
    ...                                 "".join(original),
    ...                                 "".join(replacement))
    ...                     ;
    ...         """

This rule recognises search-and-replace commands of the form "`s/a/b/`" where
`a` is the text to be replaced, `b` is the replacement text, and `/` is any
single character:

    >>> DemoParser.match("s/a/b/")
    ('replace', 'a', 'b')

The first character after the `s` is taken as the delimiter, so if you need to
replace a string containing `/` you can use any other convenient character as
the delimiter:

    >>> DemoParser.match("s#1/2#5/8#")
    ('replace', '1/2', '5/8')

seq
---

- Arguments:
    - `target`, any sequence of items
- Matches: each item of the sequence `target` in turn
- Value: the sequence passed in

The `seq` rule takes a sequence of _n_ items, and compares it to the
next _n_ items of the sequence being parsed. It compares each pair of
items with the standard Python equality operator. It matches as long as
each pair of items is equal, and as long as it doesn't hit the end of
the stream.

`seq` will match single items, or sequences of items against the
sequence being parsed:

    >>> BaseParser('a').seq('a')
    'a'
    >>> BaseParser('abc').seq('abc')
    'abc'

Here, we give `seq` a sequence whose first item is a string, but the
first item of the sequence being parsed is a single character.
Therefore, it does not match:

    >>> BaseParser('abc').seq(('abc',))
    Traceback (most recent call last):
        ...
    BacktrackException: 1:Got 'a', expected 'abc'

If `seq` hits the end of the stream while it's still checking items from
the sequence it was given, it fails to match:

    >>> BaseParser('ab').seq('abc')
    Traceback (most recent call last):
        ...
    BacktrackException: 2:Unexpected EOF

token
-----

*This is a compatibility alias for `seq`.*
