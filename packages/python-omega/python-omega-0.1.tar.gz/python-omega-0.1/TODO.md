Things to do:

- Rename things to match PEP8.
- Port to Python 3.x.
- Change the parser and compiler to leave parsing as late as possible.
    - Currently, we have our own parsing for strings (which we turn into string
      objects) and separate parsing for hostExpr strings. AST nodes like 'item'
      are expected to have proper Python objects, and AST nodes with hostExprs
      are supposed to have strings that we directly parse into Python AST
      nodes.
    - That means that we take an Omega string, parse it into a string object,
      for the Omega AST, then have to quote it back into a Python AST object to
      use it.
    - We should leave all literals as source strings in the Python AST, then
      just parse them to Python AST directly when we need them. That will make
      the compiler simpler, *and* we get the richer functionality of Python
      string syntax (extra escapes) at no extra cost.
    - This means Omega literals can be any Python literal we can write
      a recogniser for, pretty much.
- Fundamental builtin functions we want to implement.
    - foreign(cls, str)
        - instantiate the given grammar class with the current sequence
          and position, invoke the rule with the given name.
        - Update the API docs for `._setState()` to mention that this
          supported interface is usually a better idea than tinkering with
          state tuples directly.
        - We should probably share the packrat cache between both classes,
          so that if the foreign class happens to have a `foreign` call
          back into the original, we don't wind up re-parsing things. This
          means updating the constructor API docs.
        - Make sure that if we have called rule `foo` in this parser, then
          we call rule `foo` in a foreign parser, those two don't clobber
          each other in the packrat cache.
        - Update the API docs for `._backtrackException` to point out that
          if you change the value of that class property and you call
          `foreign()` or something else invokes you via `foreign()` then
          backtracking is likely to get very confused.
    - Make `backtrack(msg)` a standard parsing rule instead of just a Python
      API thing.
        - This would mean you could do things like `bindigit = '0' | '1'
          | backtrack("Expected a binary digit")` so you'd get a helpful error
          message rather than the generic "Expected '1'".
        - Obviously, this requires moving the details from the API docs to the
          Library docs.
- Standard library functions for text-parsing:
    - rules to match typical parsing tasks: upper, lower, alpha, digit,
      octdigit, hexdigit, alnum, space, spaces, eol.
    - redefine token as `token :t = spaces seq(t)`
    - Edit the Semantic Predicate docs to mention that using the text-parsing
      library is a much more sensible way to parse digits.
    - Edit `README.md` to make its example code take advantage of these rules.
- Standard library functions for sequence-processing:
    - rules for matching Python types, might as well name them after the
      Python types (int, str, dict, list, tuple, None, True, False)
- Standard library functions for binary parsing:
    - int8, int16, int32, int64, uint8, uint16, uint32, uint64, etc.
    - zstring
        - matches a null-terminated string.
    - block(n)
        - matches the next n bytes, whatever they are. Useful for
          fixed-size blocks, or for length-prefixed things (so you can say
          "int32:n block(n)")
        - You can do something similar without any special support (`block :n
          = ![self.anything() for i in range(n)]`) but it would be convenient
          for `block` to slice the sequence directly, instead of calling
          `anything` multiple times and building up a list.
    - We don't need special syntax to handle character-literals as distinct
      from 1-character string literals, even if we're using Python 3 semantics
      where indexing a bytestring gives you a value with a different type:
      we just define `token :t = seq(t.encode('latin1'))` and then we can say
      `"A"` to mean "the next byte in the sequence should have the value 65".
- Implement all these fancy Omega syntax features.
    - Iterable matching with `[]`: cast to tuple and iterate over that.
        - Update the "end" docs to mention that matching a sequence with
          `[]` also checks that the entire sequence is consumed, so "end"
          still isn't very useful.
    - The whole dispatch shebang: multiple rules with the same name, with
      different numbers of arguments, with parsing rules restricting the
      content of each argument, and with the dispatcher falling from one
      definition to the next until one can be found that matches.
        - Maybe this is overkill? Python gets along without it, maybe it
          would just confuse matters.
    - Integer literals in decimal, octal and hexadecimal.
    - Superclass calls: `^name` is compiled to `super(ClassName,
      self).name()`
    - regex-style repetition quantifiers in curly braces: `{2}`, `{,y}`,
      `{x,}`, `{x,y}` (but not `{,}`, since that would be identical to
      `*`).
        - Items inside curly braces should be hostExprs rather than
          literals, so that the count can be defined by some previous
          value read from the file.
    - Angle-brackets (`<>`) evaluate to the slice of the sequence matched
      by the enclosed terms, no matter what evaluating each term might
      produce. This means tokeniser-type rules can be written without
      `"".join(inner)` after every single one.
- Implement newer, fancier syntax:
    - The cut operator (`/`) which wraps a sequence and says "if any
      terms in this sequence fail to match, I will re-raise the
      BacktrackException as an UnrecoverableParseError".
        - Example usage might be "`'a' / 'b'`"; once `a` is matched, the
          lack of `b` becomes a fatal parse error.
        - This means that parse errors can become more friendly; if
          a group has a missing close-bracket, you'll get an error message
          about a broken group instead of back-tracking to try parsing it
          as an integer and getting a 'broken integer' error.
        - Since we know we won't be backtracking past a cut, we can also
          discard entries in the packrat cache for all positions before
          the current position in the sequence, which lowers our memory
          footprint.
        - There's a paper about automatically inserting the cut operator
          into PEG parsers, we should cite it and see if we can implement
          it as an optimization pass.
- Example parsers.
    - PDF parser?
    - JSON parser?
    - RIFF parser? (or some other moderately-complex binary format)
        - Maybe a PE or ELF parser?
        - Maybe ID3v2?
        - Minecraft's NBT format: http://www.minecraftwiki.net/wiki/NBT_Format
- Allow more flexible rule names via name-mangling.
    - leave most names alone.
    - any name that ends with an underscore, append another underscore.
    - any name that appears in a list of illegal names, append an underscore.
        - this list would be initialised with Python keywords, plus the class
          method 'match'.
        - Perhaps extensions to this list should be another property
          declared on parser classes?
- Optimizer
    - We want to combine things like character ranges and character
      sequences into regexes so they'll run faster.
- Compiler!
    - Add line/column information to the Omega parser and carry it across
      to the Python AST fed to the compiler.
- OMeta only memoizes rule-invocations with no parameters; rules with
  parameters don't get memoized.
    - kind of a shame, memoizing exactly() would probably be a win. Also
      any kind of regex-matcher.
    - If we do stop memoizing rules with parameters, we should update the
      "Python-based Parsing Rules" documentation to mention this
      restriction on parameter types has been removed.
