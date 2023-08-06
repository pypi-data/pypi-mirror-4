#!/usr/bin/python
import unittest
from omega import bootstrap
from omega.exceptions import ParseError


class OmegaParserTestMixin(object):
	"""
	Tests for anything that parses the Omega language.
	"""

	def _parse(self, sequence, ruleName=None):
		raise NotImplementedError()

	def test_eol(self):
		# A newline is an EOL marker.
		self.assertEqual(self._parse("\n", 'eol'), "\n")

		# A carriage return is an EOL marker (on classic MacOS).
		self.assertEqual(self._parse("\r", 'eol'), "\n")

		# A carriage return/newline combo is a single EOL marker.
		self.assertEqual(self._parse("\r\n", 'eol'), "\n")

		# Other whitespace characters don't match.
		self.assertRaises(ParseError, self._parse, " ", 'eol')
		self.assertRaises(ParseError, self._parse, "\t", 'eol')

	def test_comment(self):
		# A comment is anything from a '#' to the end of the line.
		self.assertEqual(self._parse("#sasquatch %@#$%@#$#\n", 'comment'), '')

		# Other EOL types are also accepted.
		self.assertEqual(self._parse("#abc\r", 'comment'), '')
		self.assertEqual(self._parse("#abc\r\n", 'comment'), '')

		# If there's no trailing newline, everything up to the end of the
		# sequence is enclosed.
		self.assertEqual(self._parse("#abc", 'comment'), '')

		# An empty comment is just fine.
		self.assertEqual(self._parse("#", 'comment'), '')

		# Anything that doesn't start with "#" is rejected.
		self.assertRaises(ParseError, self._parse, "a", 'comment')

	def test_spaces(self):
		# A single space is parsed as a space.
		self.assertEqual(self._parse(" ", 'spaces'), " ")

		# A sequence of spaces is parsed as a space.
		self.assertEqual(self._parse("    ", 'spaces'), " ")

		# Other whitespaces characters are parsed as a space.
		self.assertEqual(self._parse("\r\n\t", 'spaces'), " ")

		# A comment counts as a whitespace character.
		self.assertEqual(self._parse("\n#abc\n\n", 'spaces'), " ")

		# An empty string is parsed as a space.
		self.assertEqual(self._parse("", 'spaces'), " ")

		# Anything that's not a space doesn't match.
		self.assertRaises(ParseError, self._parse, "a", 'spaces')

	def test_hostExprGroup(self):
		# A hostExprGroup is any consists of any kind of grouping symbols,
		# wrapped around any content at all.
		self.assertEqual(self._parse("(abc)", 'hostExprGroup'), "(abc)")
		self.assertEqual(self._parse("[abc]", 'hostExprGroup'), "[abc]")
		self.assertEqual(self._parse("{abc}", 'hostExprGroup'), "{abc}")

		self.assertEqual(self._parse("(abc\n + def, ghi)", 'hostExprGroup'),
				"(abc\n + def, ghi)")

		# We require grouping characters to be matched.
		self.assertRaises(ParseError,
				self._parse, "(abc", 'hostExprGroup')
		self.assertRaises(ParseError,
				self._parse, "(abc(", 'hostExprGroup')
		self.assertRaises(ParseError,
				self._parse, "(abc()", 'hostExprGroup')
		self.assertRaises(ParseError,
				self._parse, "[abc)", 'hostExprGroup')
		self.assertRaises(ParseError,
				self._parse, "(abc]", 'hostExprGroup')

		# We are not tricked by grouping characters inside strings.
		self.assertEqual(self._parse("(abc')')", 'hostExprGroup'), "(abc')')")

	def test_hostExprString(self):
		# A hostExprString can be a single quoted string, with escaped quotes.
		self.assertEqual(self._parse(r"'ab'", 'hostExprString'), r"'ab'")
		self.assertEqual(self._parse(r"'\''", 'hostExprString'), r"'\''")

		# Any backslash-escaped character is passed straight through.
		self.assertEqual(self._parse(r"'\a'", 'hostExprString'), r"'\a'")
		self.assertEqual(self._parse(r"'\\'", 'hostExprString'), r"'\\'")

		# A string cannot end with a backslash.
		self.assertRaises(ParseError,
				self._parse, r"'a\'", 'hostExprString')

		# A single-quoted string can have escaped double quotes, although you
		# don't have to escape double-quotes.
		self.assertEqual(self._parse("'\\\"'", 'hostExprString'), "'\\\"'")
		self.assertEqual(self._parse("'\"'", 'hostExprString'), "'\"'")

		# Single-quoted strings cannot contain line-breaks.
		self.assertRaises(ParseError,
				self._parse, "'a\nb'", 'hostExprString')

		# Likewise for double-quoted strings.
		self.assertEqual(self._parse(r'"ab"', 'hostExprString'), r'"ab"')
		self.assertEqual(self._parse(r'"\""', 'hostExprString'), r'"\""')
		self.assertEqual(self._parse(r'"\a"', 'hostExprString'), r'"\a"')
		self.assertEqual(self._parse(r'"\\"', 'hostExprString'), r'"\\"')
		self.assertEqual(self._parse('"\\\'"', 'hostExprString'), '"\\\'"')
		self.assertEqual(self._parse('"\'"', 'hostExprString'), '"\'"')
		self.assertRaises(ParseError,
				self._parse, '"a\nb"', 'hostExprString')

	def test_hostExpr(self):
		self.assertEqual(self._parse("(abc)", 'hostExpr'), "(abc)")
		self.assertEqual(self._parse("(abc + def)", 'hostExpr'), "(abc + def)")
		self.assertEqual(self._parse("(abc())", 'hostExpr'), "(abc())")
		self.assertEqual(self._parse("[abc]", 'hostExpr'), "[abc]")
		self.assertEqual(self._parse("{a:b}", 'hostExpr'), "{a:b}")
		self.assertEqual(self._parse("'abc'", 'hostExpr'), "'abc'")
		self.assertEqual(self._parse("\"abc\"", 'hostExpr'), "\"abc\"")

		self.assertEqual(self._parse("(abc(\n))", 'hostExpr'), "(abc(\n))")
		self.assertEqual(self._parse("'abc\\'def'", 'hostExpr'), "'abc\\'def'")
		self.assertEqual(self._parse("\"abc\\\"def\"", 'hostExpr'),
				"\"abc\\\"def\"")
		self.assertEqual(self._parse("'('", 'hostExpr'), "'('")
		self.assertEqual(self._parse("(abc(')'))", 'hostExpr'), "(abc(')'))")
		self.assertEqual(self._parse("(a(b\n+ c))", 'hostExpr'), "(a(b\n+ c))")


		# We skip over leading whitespace.
		self.assertEqual(self._parse("    ()", 'hostExpr'), "()")

		# We must start and finish with brackets.
		self.assertRaises(ParseError,
				self._parse, "  abc)", 'hostExpr')
		self.assertRaises(ParseError,
				self._parse, "(abc", 'hostExpr')

		# We can put whatever the hell we like in between the brackets.
		self.assertEqual(self._parse("(a!b/c+d)", 'hostExpr'), "(a!b/c+d)")

		# We can even nest brackets however we like.
		self.assertEqual(
				self._parse("(foo() + bar(()))", 'hostExpr'),
				"(foo() + bar(()))",
			)

	def test_hostExprItem(self):
		# A hostExprItem is a single item in a list - pretty much anything up
		# to the next comma (except that commas can appear inside grouping
		# character or strings).
		self.assertEqual(self._parse("abc", 'hostExprItem'), "abc")
		self.assertEqual(self._parse("abc + def", 'hostExprItem'), "abc + def")
		self.assertEqual(self._parse("abc\rdef", 'hostExprItem'), "abc\rdef")
		self.assertEqual(self._parse("abc\ndef", 'hostExprItem'), "abc\ndef")
		self.assertEqual(self._parse("abc()", 'hostExprItem'), "abc()")
		self.assertEqual(self._parse("abc[0]", 'hostExprItem'), "abc[0]")
		self.assertEqual(self._parse("abc + {}", 'hostExprItem'), "abc + {}")
		self.assertEqual(self._parse("'abc'", 'hostExprItem'), "'abc'")
		self.assertEqual(self._parse('"abc"', 'hostExprItem'), '"abc"')

		# We skip leading whitespace.
		self.assertEqual(self._parse("   abc", 'hostExprItem'), "abc")

		# Pure whitespace is not an acceptable item.
		self.assertRaises(ParseError,
				self._parse, "   ", 'hostExprItem')

		# We don't handle commas.
		self.assertRaises(ParseError,
				self._parse, "abc,def", 'hostExprItem')

		# We do handle commas inside groups.
		self.assertEqual(self._parse("abc(1,2)", 'hostExprItem'), "abc(1,2)")

		# We do handle commas inside strings.
		self.assertEqual(self._parse("','", 'hostExprItem'), "','")

	def test_hostExprList(self):
		# A hostExprList is a comma-delimited list of items.
		self.assertEqual(
				self._parse("abc, def", 'hostExprList'),
				["abc", "def"],
			)

		# A single item is fine.
		self.assertEqual(self._parse("abc", 'hostExprList'), ["abc"])

		# An empty list is not fine (if you want to invoke a rule with no
		# arguments, just mention it without brackets at all.
		self.assertRaises(ParseError,
				self._parse, "", 'hostExprList')

		# A trailing comma is fine.
		self.assertEqual(
				self._parse("abc, def,", 'hostExprList'),
				["abc", "def"],
			)

		# Commas within a grouping are fine.
		self.assertEqual(self._parse("(a,b,c)", 'hostExprList'), ["(a,b,c)"])

		# Commas within a string item are fine.
		self.assertEqual(self._parse("','", 'hostExprList'), ["','"])

	def test_ident(self):
		# An identifier must start with an upper-case or lower-case letter.
		self.assertEqual(self._parse("A", 'ident'), "A")
		self.assertEqual(self._parse("b", 'ident'), "b")
		self.assertRaises(ParseError, self._parse, "_", 'ident')
		self.assertRaises(ParseError, self._parse, "1", 'ident')
		self.assertRaises(ParseError, self._parse, " ", 'ident')

		# After the first character, however, you can use any number of
		# letters, digits, or underscores.
		self.assertEqual(self._parse("Q1337_a", 'ident'), "Q1337_a")

		# You still can't use spaces, though.
		self.assertRaises(ParseError,
				self._parse, "hello world", 'ident')

		# Whitespace in front of an identifier is skipped.
		self.assertEqual(self._parse("    tanuki", 'ident'), "tanuki")

	def test_atom_string(self):
		# A string is compiled as an 'item' match.
		self.assertEqual(self._parse("'hello'", 'atom'),
				('item', "hello"))

		# We skip over initial whitespace.
		self.assertEqual(self._parse("     'hello'", 'atom'),
				('item', "hello"))

		# An empty string is OK.
		self.assertEqual(self._parse("''", 'atom'),
				('item', ""))

		# You can't put single quotes into a string directly.
		self.assertRaises(ParseError,
				self._parse, "'''", 'atom')

		# You can put single quotes in if you escape them.
		self.assertEqual(self._parse(r"'\''", 'atom'),
				('item', "'"))

		# You can use other backslash-escapes too.
		self.assertEqual(self._parse(r"'\r\n\t\\'", 'atom'),
				('item', "\r\n\t\\"))

	def test_atom_token(self):
		# A double-quoted string is compiled as an invocation of 'token'. Note
		# that because the compiler assumes invocations come from hostExprs, it
		# will try to parse the parameter to 'token', so the parameter must be
		# escaped like a Python string.
		self.assertEqual(self._parse('"hello"', 'atom'),
				('invocation', 'token', '"hello"'))

		# We skip over initial whitespace.
		self.assertEqual(self._parse('     "hello"', 'atom'),
				('invocation', 'token', '"hello"'))

		# An empty token is OK.
		self.assertEqual(self._parse('""', 'atom'),
				('invocation', 'token', '""'))

		# You can't put double quotes into a token directly.
		self.assertRaises(ParseError, self._parse, '"""', 'atom')

		# You can put double quotes in if you escape them.
		self.assertEqual(self._parse(r'"\""', 'atom'),
				('invocation', 'token', r'"\""'))

		# You can use other backslash-escapes too.
		self.assertEqual(self._parse(r'"\r\n\t\\"', 'atom'),
				('invocation', 'token', r'"\r\n\t\\"'))

	def test_atom_invocation(self):
		# Any random identifier gets parsed as an invocation of a rule with
		# that name.
		self.assertEqual(self._parse("foo", 'atom'), ('invocation', 'foo'))

		# An identifier followed by hostExprs in brackets means the rule will
		# be invoked with arguments.
		self.assertEqual(self._parse("foo('a', 2)", 'atom'),
				('invocation', 'foo', "'a'", '2'))

	def test_atom_bracketed(self):
		# If we hit some brackets, we jump back to the top of the expression
		# hierarchy and can put any crazy expression we desire.
		self.assertEqual(self._parse("(foo)", 'atom'),
				('seq', ('term', ('invocation', 'foo'))))

		# We skip over whitespace before the brackets.
		self.assertEqual(self._parse("    (foo    )", 'atom'),
				('seq', ('term', ('invocation', 'foo'))))

		# If we don't hit a closing bracket, that's a Problem.
		self.assertRaises(ParseError, self._parse, "(foo", 'atom')

	def test_quantified_negative_lookahead(self):
		# If we hit '~', we wrap the following in a negative lookahead.
		self.assertEqual(self._parse("~foo", 'quantified'),
				('negLookahead', ('invocation', 'foo')))

		# We skip over whitespace before the '~'.
		self.assertEqual(self._parse("     ~foo", 'quantified'),
				('negLookahead', ('invocation', 'foo')))

		# We don't allow quantifiers to be stacked.
		self.assertRaises(ParseError,
				self._parse, "~~foo", 'quantified')

	def test_quantified_lookahead(self):
		# If we hit '&' we wrap the following in a lookahead.
		self.assertEqual(self._parse("&foo", 'quantified'),
				('lookahead', ('invocation', 'foo')))

		# We skip over whitespace before the '&'
		self.assertEqual(self._parse("     &foo", 'quantified'),
				('lookahead', ('invocation', 'foo')))

		# We don't allow quantifiers to be stacked.
		self.assertRaises(ParseError,
				self._parse, "&&foo", 'quantified')

	def test_quantified_atoms(self):
		for quantifier, name in [('?', 'qmark'), ('*', 'star'), ('+', 'plus')]:
			# We don't allow space between the atom and the quantifier.
			self.assertRaises(ParseError,
					self._parse, "foo " + quantifier, 'quantified')

			# We don't allow quantifiers to be stacked.
			self.assertRaises(ParseError,
					self._parse, "foo" + quantifier + "?", 'quantified')

			# A quantifier is parsed as just another wrapper.
			self.assertEqual(
					self._parse("foo" + quantifier, 'quantified'),
					(name, ('invocation', 'foo')),
				)

	def test_unquantified_atoms(self):
		# Without a quantifier, the 'quantified' rule just passes straight
		# through to the atom rule.
		self.assertEqual(
				self._parse("foo", 'quantified'),
				('invocation', 'foo'),
			)

	def test_semAction(self):
		# When we hit an exclamation mark, the next thing in brackets is
		# a semantic action.
		self.assertEqual(
				self._parse("!(True)", 'semAction'),
				('semAction', '(True)'),
			)

		# We allow whitespace around the '!'.
		self.assertEqual(
				self._parse("   !   (True)", 'semAction'),
				('semAction', '(True)'),
			)

		# We allow '->' as an alternative for '!.
		self.assertEqual(
				self._parse("->(True)", 'semAction'),
				('semAction', '(True)'),
			)
		self.assertEqual(
				self._parse("   ->   (True)", 'semAction'),
				('semAction', '(True)'),
			)

		# We don't allow whitespace between '-' and '>'.
		self.assertRaises(ParseError,
				self._parse, '-   >(True)', 'semAction')

	def test_semPredicate(self):
		# When we hit a question mark, the next thing in brackets is a semantic
		# predicate.
		self.assertEqual(
				self._parse("?(True)", 'semPredicate'),
				('semPredicate', '(True)'),
			)

		# We allow whitespace around the '?'.
		self.assertEqual(
				self._parse("   ?   (True)", 'semPredicate'),
				('semPredicate', '(True)'),
			)

	def test_term(self):
		# A term can be a quantified atom.
		self.assertEqual(
				self._parse('foo*', 'term'),
				('star', ('invocation', 'foo')),
			)

		# A term can be a semantic action.
		self.assertEqual(
				self._parse('!(True)', 'term'),
				('semAction', '(True)'),
			)

		# A term can be a semantic predicate.
		self.assertEqual(
				self._parse('?(True)', 'term'),
				('semPredicate', '(True)'),
			)

	def test_tagged_term(self):
		# A semantic tag unattached to an atom is implicitly attached to an
		# invocation of 'anything'.
		self.assertEqual(
				self._parse(":x", 'taggedTerm'),
				('tagged', 'x', ('invocation', 'anything')),
			)

		# We allow whitespace before the colon.
		self.assertEqual(
				self._parse("    :x", 'taggedTerm'),
				('tagged', 'x', ('invocation', 'anything')),
			)

		# We accept whitespace between the colon and the tag.
		self.assertEqual(
				self._parse(": x", 'taggedTerm'),
				('tagged', 'x', ('invocation', 'anything')),
			)

		# A semantic tag is wrapped around the atom it comes after.
		self.assertEqual(
				self._parse("foo:x", 'taggedTerm'),
				('tagged', 'x', ('invocation', 'foo')),
			)

		# We don't tolerate any whitespace between the atom and the tag.
		self.assertRaises(ParseError,
				self._parse, "foo :x", 'taggedTerm')

		# We accept whitespace between the colon and the tag.
		self.assertEqual(
				self._parse("foo: x", 'taggedTerm'),
				('tagged', 'x', ('invocation', 'foo')),
			)

		# We can tag quantified atoms too.
		self.assertEqual(
				self._parse("foo?:y", 'taggedTerm'),
				('tagged', 'y', ('qmark', ('invocation', 'foo'))),
			)

		# A tagged term without a tag is just a term.
		self.assertEqual(
				self._parse("foo", 'taggedTerm'),
				('term', ('invocation', 'foo')),
			)

	def test_sequence(self):
		# One term can be a sequence.
		self.assertEqual(
				self._parse("foo", 'sequence'),
				('seq',
					('term', ('invocation', 'foo')),
				),
			)

		# Multiple terms can be a sequence.
		self.assertEqual(
				self._parse("foo bar baz", 'sequence'),
				('seq',
					('term', ('invocation', 'foo')),
					('term', ('invocation', 'bar')),
					('term', ('invocation', 'baz')),
				),
			)

		# You need at least one item to make a sequence.
		self.assertRaises(ParseError,
				self._parse, "    ", 'sequence')

	def test_alternative_options(self):
		# We can have alternative sequences separated by pipes.
		self.assertEqual(
				self._parse("foo|bar", 'alternatives'),
				('alternatives',
					('seq', ('term', ('invocation', 'foo'))),
					('seq', ('term', ('invocation', 'bar'))),
				),
			)

		# We can even have more than two alternatives.
		self.assertEqual(
				self._parse("foo|bar|baz", 'alternatives'),
				('alternatives',
					('seq', ('term', ('invocation', 'foo'))),
					('seq', ('term', ('invocation', 'bar'))),
					('seq', ('term', ('invocation', 'baz'))),
				),
			)

		# We can have spaces around the pipe symbols.
		self.assertEqual(
				self._parse("foo | bar | baz", 'alternatives'),
				('alternatives',
					('seq', ('term', ('invocation', 'foo'))),
					('seq', ('term', ('invocation', 'bar'))),
					('seq', ('term', ('invocation', 'baz'))),
				),
			)

		# Each pipe-delimited alternative can be a sequence of expressions.
		self.assertEqual(
				self._parse("foo bar | baz qux", 'alternatives'),
				('alternatives',
					('seq',
						('term', ('invocation', 'foo')),
						('term', ('invocation', 'bar')),
					),
					('seq',
						('term', ('invocation', 'baz')),
						('term', ('invocation', 'qux')),
					),
				),
			)

	def test_single_alternative(self):
		# If there's only a single alternative, it's returned undecorated.
		self.assertEqual(
				self._parse("foo", 'alternatives'),
				('seq', ('term', ('invocation', 'foo'))),
			)

	def test_rule(self):
		# A rule is a name, an equal sign, an expression, then a semicolon.
		self.assertEqual(
				self._parse("foo = bar ;", 'rule'),
				('rule', 'foo', (), ('seq', ('term', ('invocation', 'bar')))),
			)

		# A rule can have named parameters defined.
		self.assertEqual(
				self._parse("foo :x :y :abc = bar ;", 'rule'),
				('rule', 'foo',
					('x', 'y', 'abc'),
					('seq', ('term', ('invocation', 'bar')))
				),
			)

		# We don't actually need any of that whitespace.
		self.assertEqual(
				self._parse("foo=bar;", 'rule'),
				('rule', 'foo', (), ('seq', ('term', ('invocation', 'bar')))),
			)

		# We do need at least one expression to match.
		self.assertRaises(ParseError,
				self._parse, "foo = ;", 'rule')

		# We can have alternatives and all crazy stuff in there.
		self.assertEqual(
				self._parse("foo = bar | baz:x qux:y -> (x + y);", 'rule'),
				('rule', 'foo', (),
					('alternatives',
						('seq', ('term', ('invocation', 'bar'))),
						('seq',
							('tagged', 'x', ('invocation', 'baz')),
							('tagged', 'y', ('invocation', 'qux')),
							('term', ('semAction', '(x + y)')),
						),
					),
				),
			)

	def test_grammar(self):
		# A grammar cannot be empty.
		self.assertRaises(ParseError, self._parse, '', 'grammar')

		# A grammar can have one rule.
		self.assertEqual(
				self._parse('foo = bar;'),
				('grammar',
					('rule', 'foo', (),
						('seq', ('term', ('invocation', 'bar'))))),
			)

		# A grammar can have multiple rules.
		self.assertEqual(
				self._parse('foo = bar; baz = qux;'),
				('grammar',
					('rule', 'foo', (),
						('seq', ('term', ('invocation', 'bar')))),
					('rule', 'baz', (),
						('seq', ('term', ('invocation', 'qux')))),
				),
			)

		# A grammar can have trailing space.
		self.assertEqual(
				self._parse('foo = bar;   '),
				('grammar',
					('rule', 'foo', (),
						('seq', ('term', ('invocation', 'bar'))))),
			)


class TestBootstrapParser(OmegaParserTestMixin, unittest.TestCase):
	"""
	Run the BootstrapParser through the OmegaParserTestMixin tests.
	"""

	def _parse(self, sequence, ruleName=None):
		return bootstrap.BootstrapParser.match(sequence, ruleName)


class TestOmegaParser(OmegaParserTestMixin, unittest.TestCase):
	"""
	Run OmegaParser through the OmegaParserTestMixin tests.
	"""

	def _parse(self, sequence, ruleName=None):
		return bootstrap.OmegaParser.match(sequence, ruleName)


if __name__ == "__main__":
	unittest.main()
