Omega Tutorial
==============

This document will walk you through creating you first parser with Omega, and
show you how to do some of the most common tasks you might want to do with
a parser. It is not a comprehensive guide to everything you can do with Omega
(see the [[Library]] reference or the Python [[API]] guide for that), but it
should get you off to a good start.

This tutorial assumes that you are familiar with the Python language and that
you have Omega already installed, but does not assume any knowledge of parsing
theory. Familiarity with Python's regular expressions will also be pretty
handy.

What is a parser, anyway?
=========================

A parser is a program that takes a flat stream of bytes in some particular
format, and extracts the information that written there. For example, Python's
`configparser` module reads in a sequence of bytes in the "INI file" format,
and breaks them up into section headings, keys and values. Python's `csv`
module reads in a sequence of bytes in the CSV format, and breaks them up into
a grid of records and fields.

Python's standard library includes a number of handy parsers for a variety of
common formats like XML and JSON and CSV, but there's a lot of other
file-formats out there that Python doesn't handle out-of-the-box. Omega is
a toolkit for creating your own parsers for any format you can describe in the
Omega language.

My First Parser
===============

Here is the complete Python source code for a very, very simple format: files
that conform to this format must consist of exactly the single letter 'a', no
more or less. It's not a very useful file format, but let's see what it looks
like:

    >>> from omega import BaseParser
    >>> class MyFirstParser(BaseParser):
    ...     __grammar = """
    ...             format = 'a' ;
    ...         """

There's a number of things to notice about this code:

- We import the `BaseParser` class from the `omega` package. Every
  Omega-based parser must inherit from this class, as it contains the
  machinery for converting Omega format definitions into Python code.
- Our parser class has a class-variable named `__grammar` that defines the
  rules of this format. It's called "grammar" because, like the grammar of
  English or any other language, it describes what kinds of things can appear
  in which order, to create a sensible result. A byte-stream that breaks these
  rules might be a perfectly valid file in some other format, but not the
  format recognised by this parser.
- The grammar is written in a Python string. By convention we use
  a triple-quoted string because it means we don't have to worry about
  line-breaks or other whitespace issues.
- This grammar defines a single rule named `format`. The name isn't important
  in this example since there is only one rule, but in more complicated
  grammars it can be handy to have a short name you can use to refer to some
  particular grammar pattern.
- The `format` rule contains a single term: `'a'`. This means "expect the
  next item in the input stream to be 'a'".
- The `format` rule ends with a semi-colon. Unlike Python itself, Omega
  doesn't use indentation to figure out when a rule has ended, so you need to
  mark the end of each rule with ";".

Now we have a parser for this very simple format, what can we do with it?

The first thing we can do is test that it accepts the files we expect to
accept and rejects everything else. To match some particular input against
the grammar defined by a particular parser class, we use the class method
`match()` like this:

    >>> MyFirstParser.match('a')
    'a'

Note that when it parses the input, it returns some information about what it
saw. In a grammar this simple, it's not very interesting, so we'll ignore it
for now.

Because this grammar expects exactly a single 'a', we would expect it to
reject 'aa' or 'b'. When a parser gets an input that does not match its
grammar, it raises an exception that is a subclass of
`omega.ParseError`:

    >>> MyFirstParser.match('aa')
    Traceback (most recent call last):
        ...
    UnrecoverableParseError: 1:Found unexpected stuff: expected EOF, found 'a'...

The parser checks that there's no excess, trailing data in the input stream
after the bytes the grammar rules have matched. If there are, it raises this
exception.

    >>> MyFirstParser.match('b')
    Traceback (most recent call last):
        ...
    BacktrackException: 1:Expected 'a'

If the parser is given an input stream that does not match its grammar rules
at all, it raises this exception.

The distinction between `UnrecoverableParseError` and `BacktrackException` is
not very important unless you're writing a hybrid Omega/Python parser. If
you're just trying to catch exceptions raised by the `.match()` class method,
catch `ParseError`.

Recognising numbers
===================

Let's try writing a grammar to describe something slightly more sophisticated:
numbers. Python has a few kinds of numbers, with some sophisticated syntax for
the various types and varieties, but for now let's stick to the basics. In
English, we can define how to recognise a number as follows:

- a `digit` is one of the characters '0', '1', '2', '3', '4', '5', '6', '7',
  '8' or '9'.
- a `number` is a sequence of one-or-more `digit`s.

We can translate that description into an Omega parser like this:

    >>> class NumberRecogniser(BaseParser):
    ...     __grammar = r"""
    ...             digit = '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7'
    ...                 | '8' | '9' ;
    ...             number = digit+;
    ...         """

Our new `NumberRecogniser` class shows off a few more features of Omega:

- A grammar can have multiple parsing rules. When you call the `.match()` class
  method without specifying which rule to start with, Omega will default to the
  last rule in grammar - in this case, `number`.
- Rules can have spaces in them, or even wrap across multiple lines, without
  breaking how they work.
- The `digit` rule contains a term for each digit, separated by the
  alternative operator (`|`). When matching a set of alternatives, Omega
  tries to match each one in turn against the current position in the
  input sequence.
- The `number` rule incorporates the `digit` rule just by naming it. When Omega
  reaches a reference to another parsing rule, it goes off and tests that rule
  against the current position in the input sequence, then resumes where it
  left off in the current rule.
- The `number` rule applies the "many" operator (`+`) to the `digit` rule.
  This works the same way that it does in regular expressions: the previous
  term must match against the input stream one or more consecutive times.

Let's try it out. Again, ignore the values returned by `.match()`, we're only
concerned with recognising numbers at this point. We can recognise small
numbers:

    >>> NumberRecogniser.match("0")
    ['0']
    >>> NumberRecogniser.match("1")
    ['1']

We can recognise big numbers:

    >>> NumberRecogniser.match("1234567890")
    ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

And we correctly reject things that aren't numbers:

    >>> NumberRecogniser.match("")
    Traceback (most recent call last):
        ...
    BacktrackException: 0:Unexpected EOF
    >>> NumberRecogniser.match("sasquatch")
    Traceback (most recent call last):
        ...
    BacktrackException: 1:Expected '9'

...however, this is a somewhat limiting definition of the word 'number'. For
example, 0.5 is definitely a number, yet our `NumberRecogniser` rejects it:

    >>> NumberRecogniser.match("0.5")
    Traceback (most recent call last):
        ...
    UnrecoverableParseError: 1:Found unexpected stuff: expected EOF, found '.5'...

So, let's replace our `NumberRecogniser` with one that supports numbers with
decimal places:

    >>> class NumberRecogniser(BaseParser):
    ...     __grammar = r"""
    ...             digit = '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7'
    ...                 | '8' | '9' ;
    ...             number = digit+ | digit+ '.' digit+ ;
    ...         """

Notice that we've added a new alternative (separated by the Alternative
operator, `|`) to the `number` rule. Now, a number can be one-or-more digits,
or it can be digits, followed by '.', followed by more digits. Let's try it
out!

Non-numbers still fail:

    >>> NumberRecogniser.match("sasquatch")
    Traceback (most recent call last):
        ...
    BacktrackException: 1:Expected '9'

Numbers with no decimal places still work:

    >>> NumberRecogniser.match("42")
    ['4', '2']

And now, numbers with decimal places...

    >>> NumberRecogniser.match("12.34")
    Traceback (most recent call last):
        ...
    UnrecoverableParseError: 2:Found unexpected stuff: expected EOF, found '.34'...

...still don't work. What gives?

The issue is the *order* of the alternatives in the `number` rule. When we try
to recognise "12.34" with our `NumberRecogniser`, Omega starts with the first
alternative, `digit+`, and matches that against the input. In this case, it
matches the first two characters, "12". Because it successfully matches the
first alternative, Omega doesn't consider that later alternatives might be
a better fit, it just accepts what it's found and moves on—in this case, since
`number` is the default parsing rule and it's found an acceptable candidate for
`number`, it considers its work done and goes off to double-check that there's
no extra data after the items it's successfully matched.

In order to fix this example, we need to switch the two alternatives around. In
general, when you have a set of alternatives in an Omega parsing rule, you need
to make sure that the more complex or specialised rules are at the front; more
specifically, you need to make sure that no alternative is a *prefix* of
a later alternative in the same rule. Notice that both alternatives in the
`number` rule start with `digit+`: the first alternative is identical to the
beginning of the second, which is to say it's a *prefix* of the second.

Here's our fixed `NumberRecogniser`, with the `number` alternatives the other
way around:

    >>> class NumberRecogniser(BaseParser):
    ...     __grammar = r"""
    ...             digit = '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7'
    ...                 | '8' | '9' ;
    ...             number = digit+ '.' digit+ | digit+ ;
    ...         """

...and now, it does indeed work as expected:

    >>> NumberRecogniser.match("sasquatch")
    Traceback (most recent call last):
        ...
    BacktrackException: 1:Expected '9'
    >>> NumberRecogniser.match("42")
    ['4', '2']
    >>> NumberRecogniser.match("12.34")
    ['3', '4']

Actually parsing numbers
========================

Being able to recognise whether a particular sequence of characters looks like
a number is useful, but perhaps not very practical: it would be much more
helpful to figure out *which* number a particular sequence represents. But
first, let's talk about the return value of the `.match()` class method.

Every kind of pattern in an Omega parsing rule has a return value associated
with it (for complete details, the [[Language]] reference describes the value
each language-part returns). When we invoke the `number` rule like this:

    >>> NumberRecogniser.match("123")
    ['1', '2', '3']

...there's several levels of processing involved:

- The `.match()` method invokes the `number` rule, and returns the value that
  `number` returns.
- The `number` rule tries each of its alternatives, and returns the value from
  the alternative that matched.
- In this case, the alternative that matched was `digit+`, and the one-or-more
  operator (`+`) returns a list containing the one-or-more matches it found.
- The one-or-more operator was attached to an invocation of the `digit` rule,
  so the list will be a list of values returned by the `digit` rule.
- The `digit` rule tries each of its alternatives, and returns the value from
  the alternative that matched.
- Each alternative in the `digit` rule is a single character whose return value
  is the character itself.

So, the return value of `.match()` in our example above is a list (constructed
by the one-or-more operator) of digits (each returned by an alternative of the
`digit` rule) matched in our input sequence. Now, what about when we recognise
a number with decimal places?

    >>> NumberRecogniser.match("3.14159")
    ['1', '4', '1', '5', '9']

It's a similar story to before, except that instead of the `number` rule
returning the value of the `digit+` alternative, it returns the value of the
`digit+ '.' digit+` alternative. As you can see, when an alternative contains
a sequence of terms, only the value of the last term in that sequence is
returned: we get the list of digits after the '.', but not the '.' itself or
the list of digits before it.

This may sound limiting, but there's a way around it. Omega has a special kind
of term called a "semantic action", whose value is a Python expression that can
refer to values returned by previous parts of the sequence. Because
a sequence's value comes from its last term, a semantic action at the end of
a sequence lets you produce a value that sums up the entire thing.

Here's our `NumberRecogniser`, transformed into a `NumberParser` (note that we
import Python's `decimal` module here to represent our parsed numbers):

    >>> from decimal import Decimal
    >>> class NumberParser(BaseParser):
    ...     __grammar = r"""
    ...             digit = '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7'
    ...                 | '8' | '9' ;
    ...             number = digit+:int '.' digit+:frac
    ...                     -> (Decimal("".join(int) + '.' + "".join(frac)))
    ...                 | digit+:int -> (Decimal("".join(int)))
    ...                 ;
    ...         """

Several things have changed in the `number` rule:

- Some of the terms are followed by a colon (`:`) and a name, like `digit+:int`
  or `digit+:frac`. This is called a 'semantic tag', and it's like a variable
  assignment in Python; it stores the value returned by that term in a variable
  with the given name.
- At the end of each alternative in the `number` rule is the symbol `->`
  followed by a Python expression in brackets. This is the "semantic action"
  term. (The Python expression doesn't always have to appear in brackets,
  that's just the safest option; for details, see the "Host Expressions"
  section of the [[Language]] reference.)
- Notice that the "semantic action" expression can refer to both global
  variables (the `Decimal` class that was just imported) and local variables
  (semantic tags like `int` and `frac`).

The semantic action term doesn't affect what kinds of patterns the sequence
matches, it just affects the return value, so let's see it in action:

    >>> NumberParser.match("sasquatch")
    Traceback (most recent call last):
        ...
    BacktrackException: 1:Expected '9'
    >>> NumberParser.match("42")
    Decimal('42')
    >>> NumberParser.match("12.34")
    Decimal('12.34')

Success! We can now parse strings into numbers, with the help of Python's
`decimal` module. However, if you look at the Omega code, it seems there's
a common operation where we take one-or-more digits and join them into a single
string. If we factor that pattern out into a new parsing rule named
`digitSpan`, we get:

    >>> class NumberParser(BaseParser):
    ...     __grammar = r"""
    ...             digit = '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7'
    ...                 | '8' | '9' ;
    ...             digitSpan = digit+:ds -> ("".join(ds));
    ...
    ...             number =
    ...                 digitSpan:int '.' digitSpan:frac
    ...                     -> (Decimal(int + '.' + frac))
    ...                 | digitSpan:int
    ...                     -> (Decimal(int))
    ...                 ;
    ...         """

...which looks much tidier, but works the same way:

    >>> NumberParser.match("sasquatch")
    Traceback (most recent call last):
        ...
    BacktrackException: 1:Expected '9'
    >>> NumberParser.match("42")
    Decimal('42')
    >>> NumberParser.match("12.34")
    Decimal('12.34')

<!--
Other things to work into the tutorial:
- negative and positive lookahead
- brackets and grammar recursion
- defining and invoking rules with parameters
- comments
- double-quoted strings and the 'token' rule
-->
