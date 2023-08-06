Introduction
============

This document describes the syntax of the Omega parsing language, as
currently implemented. Everything should be covered, but there won't be
much explanation of when a thing is useful; for a gentler introduction
see the [[Tutorial]]. Most of the language features come directly from
Alessandro Warth's [OMeta](http://tinlizzie.org/~awarth/ometa/) library
for Squeak and JavaScript, but sometimes there are differences to better
integrate Omega with Python. For information on the pre-defined helper
rules available to Omega-based parsers, see the [[Library]] reference.

All the usage examples below will be run in the following environment:

    >>> from omega import BaseParser

As a brief overview, a "grammar" is a collection of parsing "rules",
a rule is a sequence of "terms", and each term consists of optional
"modifiers" attached to a fundamental "atom".

Host Expressions
================

A 'host expression' is not a specific part of the Omega language, but
there are several parts of Omega that include a host expression as part
of their syntax. Omega accepts a subset of legal Python expressions as
"host expressions", trying to cover as much of Python's syntax as
possible without having to directly import the entire Python expression
syntax into Omega. Here's what can you can use when Omega expects
a "host expression".

- Quoted strings, with both single and double-quotes: `'hello'` or
  `"hello"`
    - Omega understands about backslash-escaped quotes in quoted
      strings.
    - Omega does not understand the special escaping rules of raw
      strings (`r'hello'`).
    - Omega does not understand the special quoting rules of Python's
      triple-quoted strings.
- Expressions grouped in round, square or curly brackets: `(a + b)` or
  `[a, b]` or `{a: b}`
    - Expressions can contain other groups (it makes sure each
      open-bracket is matched with an appropriately-nested
      close-bracket) and strings (brackets inside strings do not affect
      nesting).
    - Expressions can contain other text, like mathematical operators or
      Python names, but these don't affect parsing so they're just
      preserved as-is.

Inside a host expression, as well as self-contained expressions like
literals and Python built-in functions, you can also refer to global
variables in the module where the parsing class was defined, the values
associated with "tagged terms" (see below), any parameters the parsing
rule accepts, and the name `self`, which represents the parser instance
that's doing the parsing. For information about available attributes of
`self`, see the [[API]] reference.

Comments
========

A comment can appear anywhere whitespace is legal in an Omega grammar.
It starts at a `#` character, and runs until the next end-of-line, or
the end of the grammar string, whichever is sooner. It is completely
ignored.

    >>> class DemoParser(BaseParser):
    ...     __grammar = """
    ...             # This is a comment.
    ...             an_a = 'a';
    ...         """
    >>> DemoParser.match('a')
    'a'

Atoms
=====

An atom is the most fundamental part of a parsing rule, performing some
kind of test on the next item in the sequence being parsed.

Strings
-------

- Looks like: a single quote (`'`), followed by non-newline,
  non-single-quote characters, followed by a single quote.
- Matches: if the next item of the sequence is exactly equal to the
  string, according to the rules of Python string equality.
- Value: the contents of the string itself.

Here, we define a parsing rule named `rule` that matches if the sequence
contains the single character '`a`':

    >>> class DemoParser(BaseParser):
    ...     __grammar = "an_a = 'a';"
    >>> DemoParser.match('a')
    'a'

Because the string atom matches a single letter 'a' and we gave it
a sequence (specifically, a string) containing a single letter 'a', it
matched and returned that single letter 'a'. If we give it a single
letter 'b' instead, it won't match:

    >>> DemoParser.match("b")
    Traceback (most recent call last):
        ...
    BacktrackException: 1:Expected 'a'

A string atom can contain backslash-escaped characters, but not all the
escape sequences supported by Python are supported by Omega. The
supported escape sequences are:

- `\'` represents a single-quote (As in Python, useful for putting
  single-quotes in a string)
- `\n` represents a newline character (since otherwise newlines cannot
  appear in strings)
- `\r` represents a carriage-return character
- `\t` represents a tab character.

It is possible for a string atom to contain multiple characters, but it
will only match the sequence if the next single item of the sequence is
a multi-character string. This is not possible if the sequence you are
parsing is a Python string, but it is if the sequence is, say, a Python
tuple:

    >>> class DemoParser(BaseParser):
    ...     __grammar = "an_abc = 'abc';"
    >>> DemoParser.match(('abc',))
    'abc'

Tokens
------

- Looks like: a double quote (`"`), followed by non-newline,
  non-double-quote characters, followed by a double quote.
- Matches: if the parsing rule `token` matches when invoked with the given
  string as a parameter.
- Value: the value returned by the `token` rule.

Many grammars involve fixed strings (keywords, operators, grouping symbols)
delimited in some standard way. Tokens are Omega's way of simplifying the
description of such items. If you write a string with double-quotes instead of
single quotes, it will be treated as an invocation of the `token` parsing rule,
with that string supplied as a parameter. That is, the following two rules are
exactly equivalent:

    example_a = "if" condition "then" statements+ "endif";
    example_b = token('if') condition token('then') statements+ token('endif');

In `BaseParser`, the `token` rule is defined as an alias for `seq`, but it's
common for parsers to override the default definition with something more
suitable for whatever it is they're parsing, such as implicitly skipping over
whitespace.

Invocations
-----------

- Looks like: an alphabetic character, followed by a sequence of
  alphabetic characters, digits, or underscores. It may be followed by
  an open bracket (`(`), some comma-delimited Python expressions, and
  a close bracket (`)`).
- Matches: if the named parsing rule matches.
- Value: the value returned by the named parsing rule.

This is the Omega equivalent of a Python function call; it invokes the
named parsing rule at the current position in the sequence. Here we
define a rule named `an_a` that matches if the sequence contains an
'`a`', and a rule named `two_as` that invokes the rule `an_a` twice:

    >>> class DemoParser(BaseParser):
    ...     __grammar = """
    ...             an_a = 'a';
    ...             two_as = an_a an_a;
    ...         """
    >>> DemoParser.match('aa')
    'a'

If you are invoking a parsing rule without parameters, you can't have
the brackets:

    >>> class DemoParser(BaseParser):
    ...     __grammar = """
    ...             an_a = 'a';
    ...             two_as = an_a() an_a();
    ...         """
    Traceback (most recent call last):
        ...
    UnrecoverableParseError: 37:Found unexpected stuff: expected EOF, found 'two_as = a'...

It's possible for a parsing rule to be defined with parameters; in that
case, it can also be invoked with parameters. Here we define a parsing
function with parameters, and invoke it from the Omega grammar:

    >>> class DemoParser(BaseParser):
    ...     __grammar = """
    ...             count :num :item = seq(num * (item,));
    ...             two_as = count(2, 'a');
    ...         """
    >>> DemoParser.match('aa')
    ('a', 'a')

When invoking a parsing rule with parameters, the contents of the
brackets can be almost any Python expression; see "Host Expressions"
near the top of this document for more information.

Groupings
---------

- Looks like: an open bracket (`(`), "alternatives" (see "Rules" below),
  followed by a close bracket (`)`).
- Matches: if the alternatives inside the brackets match.
- Value: the value returned by the grouped alternatives.

A grouping is a way to apply a single modifier or tag to multiple terms.
Consider the two rules in this parser:

    >>> class DemoParser(BaseParser):
    ...     __grammar = """
    ...             a_then_bs = 'a' 'b'+;
    ...             abs = ('a' 'b')+;
    ...         """
    >>> DemoParser.match('abb', 'a_then_bs')
    ['b', 'b']
    >>> DemoParser.match('abab', 'abs')
    ['b', 'b']

The rule `a_then_bs` matches a single '`a`' followed by one-or-more
'`b`'s (thanks to the Many modifier, which is attached to the `'b'`
atom). The rule `abs` matches one-or-more repetitions of the sequence
'`ab`' because the Many modifier is attached to the entire group.

Modifiers
=========

A modifier is an optional attachment to an atom that changes how that
atom is matched against the input sequence.

Positive Lookahead
------------------

- Looks like: an ampersand (`&`) followed by an atom.
- Matches: if the associated atom matches.
- Value: the value of the associated atom.

When the positive lookahead modifier is attached to an atom, Omega tests
whether the given atom matches the current position in the sequence, but
does not consume the matched items. This is useful if there is some
other parsing rule that accepts a number of variants, but you only want
to match some particular variant. For example:

    >>> class DemoParser(BaseParser):
    ...     __grammar = """
    ...             token_abc = ' '* 'a' 'b' 'c';
    ...             not_abc = '!' &'a' token_abc;
    ...         """

Here, `token_abc` is a rule that accepts zero-or-more spaces, followed
by '`abc`':

    >>> DemoParser.match('abc', 'token_abc')
    'c'
    >>> DemoParser.match('   abc', 'token_abc')
    'c'

Although `not_abc` calls `token_abc` to match the '`abc`' string, it
does not accept spaces in front of '`abc`':

    >>> DemoParser.match('!abc', 'not_abc')
    'c'
    >>> DemoParser.match('!   abc', 'not_abc')
    Traceback (most recent call last):
        ...
    BacktrackException: 2:Expected 'a'

This is because of the term `&'a'`, which requires that the next item in
the sequence be '`a`', but leaves it alone for the invocation of
`token_abc` to process.

Negative Lookahead
------------------

- Looks like: a tilde (`~`) followed by an atom.
- Matches: if the associated atom does not match.
- Value: the Python value `None`.

When the negative lookahead modifier is attached to an atom, Omega tests
that the atom does *not* match the current position in the sequence. For
example, here is a rule that matches a quoted string:

    >>> class DemoParser(BaseParser):
    ...     __grammar = r"""
    ...             quotedStr = '"' (~'"' anything)* '"';
    ...         """
    >>> DemoParser.match('"abc"')
    '"'

This rule matches a double-quote, followed by zero-or-more things that
aren't double-quotes, followed by another double-quote. Note that unlike
the Python regex syntax `"[^"]*"`, the "accept anything not explicitly in
this list" must be explicitly mentioned; the upside is that you can
match more subtle patterns than just "accept only these characters" or
"accept anything but these characters".

Optional
--------

- Looks like: an atom immediately followed by a question mark (`?`).
- Matches: always.
- Value: the value of the atom, if it matches. If the associated atom
  does not match, it has the Python value `None`.

As the name implies, the optional modifier makes an atom optional; if it
matches the current position in the sequence, it's used but otherwise
it's skipped over. For example:

    >>> class DemoParser(BaseParser):
    ...     __grammar = r"""
    ...             a_maybe_b = 'a' 'b'?;
    ...         """
    >>> DemoParser.match('ab')
    'b'
    >>> print DemoParser.match('a') # Python won't auto-print None.
    None

This rule matches '`ab`' if it can, but if the '`b`' is absent it can
still match '`a`'.

Any
---

- Looks like: an atom immediately followed by an asterisk (`*`).
- Matches: zero-or-more repetitions of the associated atom.
- Value: a (potentially empty) Python list containing the matched
  repetitions.

For example:

    >>> class DemoParser(BaseParser):
    ...     __grammar = r"""
    ...             a_maybe_bs = 'a' 'b'*;
    ...         """
    >>> DemoParser.match('a')
    []
    >>> DemoParser.match('ab')
    ['b']
    >>> DemoParser.match('abb')
    ['b', 'b']

Many
----

- Looks like: an atom immediately followed by a plus (`+`).
- Matches: one-or-more repetitions of the associated atom.
- Value: a Python list containing the matched repetitions.

For example:

    >>> class DemoParser(BaseParser):
    ...     __grammar = r"""
    ...             a_then_bs = 'a' 'b'+;
    ...         """
    >>> DemoParser.match('a')
    Traceback (most recent call last):
        ...
    BacktrackException: 1:Unexpected EOF
    >>> DemoParser.match('ab')
    ['b']
    >>> DemoParser.match('abb')
    ['b', 'b']

Terms
=====

"Term" is a generic category that includes atoms, modified atoms, and
other, more specialised things.

Semantic Actions
----------------

- Looks like: an exclamation mark (`!`), or an arrow (`->`) followed by
  a Host Expression.
- Matches: always.
- Value: the value obtained by evaluating the host expression.

When Omega reaches a semantic action term, it evaluates the given Python
expression, and the result is used as the value of the Semantic Action.
The contents of the semantic action's host expression can be almost any
Python expression; see "Host Expressions" near the top of this document
for more information.

While a semantic action on its own would be written with an exclamation
mark (`!`), a common idiom is to tag important terms in a rule, then put
a semantic action at the end that combines the various matched values
into a single value that summarises the entire rule (see Sequence
below). In that context, the arrow (`->`) is a more obvious depiction of
what's going on.

For example:

    >>> class DemoParser(BaseParser):
    ...     __grammar = r"""
    ...             an_a = 'a' !(3 + 5);
    ...         """
    >>> DemoParser.match('a')
    8

For an example with tagged terms, see Tagged Terms below.

Semantic Predicates
-------------------

- Looks like: a question mark (`?`) followed by a Host Expression.
- Matches: if the host expression is truthy.
- Value: the value obtained by evaluating the host expression.

When Omega reaches a semantic predicate term, it evaluates the given Python
expression. If the result is "truthy" the term is considered to match,
otherwise it has failed and backtracking commences. "Truthiness" in this
situation means exactly the same criteria Python uses when evaluating the
expression in an `if` or `while` statement; numerical zero, empty containers
and so forth are treated as false, while other values are treated as true.

Semantic predicates are useful for expressing conditions that are not
expressible, or very tedious, in pure Omega. For example, here's one way to
write a rule that matches decimal digits:

    >>> class DemoParser(BaseParser):
    ...     __grammar = """
    ...             digit = anything:x ?('0' <= x <= '9') -> (x);
    ...         """

First, the rule grabs an item from the sequence being parsed, then checks that
it's within the range of `0` to `9`. Lastly, we have a semantic predicate to
make sure that the rule returns the matched digit, rather than the boolean True
value returned by the semantic predicate.

    >>> DemoParser.match("7")
    '7'
    >>> DemoParser.match("a")
    Traceback (most recent call last):
        ...
    BacktrackException: 1:Predicate failed: ('0' <= x <= '9')

Tagged Terms
------------

- Looks like: an optional term followed by a colon (`:`) and a name.
- Matches: if the associated term matches.
- Value: the value of the associated term, or the next item in the sequence if
  no term was given.

A tagged term takes the value associated with a term and stores it under
the given name. They behave in much the same way as variable-assignments
in Python. Although a tagged term has a value, you cannot have multiple
tags on a single term, unless you wrap the tagged term in brackets.

Tagging a term has no effect on what it matches, but it makes the values
of individual terms available to semantic action, semantic predicate and
invocation terms. For example:

    >>> class DemoParser(BaseParser):
    ...     __grammar = r"""
    ...             match_only = 'a' 'b'* 'c';
    ...             sem_action = 'a':a 'b'*:bs 'c':c
    ...                 -> (a + "".join(bs) + c);
    ...         """

By default, a sequence's value is that of the final term, so our
`match_only` rule will always return the final '`c`' if it matches:

    >>> DemoParser.match('abbbc', 'match_only')
    'c'

In contrast, the final term of the `sem_action` rule is a semantic
action that stitches together all the tagged terms in the rule:

    >>> DemoParser.match('abbbc', 'sem_action')
    'abbbc'

Rules
=====

- Looks like: a name, followed by zero or more argument names (each is a colon
  (`:`) followed by a name), then an equals sign (`=`), "alternatives"
  (see below), and a semi-colon (`;`).
- Matches: if the alternatives match.
- Value: N/A.

A parsing rule is just a way of naming a particular group of terms, to
provide for re-use or just to help manage complexity of a large grammar.
It is exactly analogous to a Python function.

A parsing rule may accept arguments, whose values are available to semantic
actions and invocations just like tagged terms. Accordingly, their syntax
resembles tagged terms. Currently, Omega does not support testing parameters
against parsing rules, so each parameter definition must be a bare tag with no
associated term.

The body of a rule is a list of alternatives, each of which is
a sequence of terms.

Note that the `BaseParser` class provides an important class method named
`match`, so you should never create a parsing rule named `match` or else
you'll override it.

Sequence
--------

- Looks like: consecutive terms separated only by whitespace.
- Matches: if all the terms match in the given order.
- Value: the value associated with the final term.

A sequence is the fundamental way to combine individual terms to parse
more complicated structures. It's important to note that when a sequence
matches, the value it produces is the value of the final term; if your
final term is some kind of delimiter like a quote-mark or a closing
bracket, you'll want to use a Semantic Action term (see above) to
summarise all the terms of the sequence in some useful way.

    >>> class DemoParser(BaseParser):
    ...     __grammar = r"""
    ...             a_b_then_c = 'a' 'b' 'c';
    ...         """

This rule only matches if the input sequence contains `a`, `b` and `c`
in that exact order.

    >>> DemoParser.match('abc')
    'c'
    >>> DemoParser.match('ab')
    Traceback (most recent call last):
        ...
    BacktrackException: 2:Unexpected EOF
    >>> DemoParser.match('acb')
    Traceback (most recent call last):
        ...
    BacktrackException: 2:Expected 'b'

Alternatives
------------

- Looks like: one or more sequences separated by pipes (`|`). 
- Matches: if one of the contained sequences matches.
- Value: the value of the sequence that matched.

Alternatives are used when there is more than one possible sequence that
can match at the current position in the sequence. For example, in some
particular grammar a literal value might be a string or an integer; the
syntax for each is very different but both are permitted.

When Omega evaluates alternative sequences, it starts by saving the
current position, then trying the to match the first alternative. If it
matches, the current position is updated and Omega moves on. If it
doesn't match, the current position is reset to the saved position, and
it tries to match the next alternative, and so on until one of the
alternatives matches, or it runs out of alternatives. For example:

    >>> class DemoParser(BaseParser):
    ...     __grammar = r"""
    ...             a_or_b = 'a' | 'b';
    ...         """
    >>> DemoParser.match('a')
    'a'
    >>> DemoParser.match('b')
    'b'
    >>> DemoParser.match('ab')
    Traceback (most recent call last):
        ...
    UnrecoverableParseError: 1:Found unexpected stuff: expected EOF, found 'b'...

This parser matches both '`a`' and '`b`', but not '`ab`'.
