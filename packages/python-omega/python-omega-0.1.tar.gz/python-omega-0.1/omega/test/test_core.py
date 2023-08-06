#!/usr/bin/python
import unittest
from omega.exceptions import BacktrackException, UnrecoverableParseError
from omega import _core


class MockParser(object):

	@classmethod
	def match(cls, sequence):
		# A short and terribly hacky way to parse a ridiculous subset of Omega.
		rules = []
		for rule in sequence.split(";"):
			if not rule.strip():
				continue
			name, invocation = rule.split("=", 1)
			rules.append(
					('rule', name.strip(), (),
						('term', ('invocation', invocation.strip())))
				)

		return ['grammar'] + rules


class MockGrammar(_core.CoreGrammar):
	_parser = MockParser


class PythonDefinedParser(_core.CoreParser):
	"""
	A simple parser defined only in Python.
	"""
	_start = "an_a"

	def an_a(self):
		"""
		Matches exactly one 'a'.
		"""
		return self.seq('a')

	def some_bs(self):
		"""
		Matches zero or more 'b's.
		"""
		res = []

		while True:
			try:
				res.append(self.seq('b'))
			except self._backtrackException:
				break

		return "".join(res)


class TestCoreParser(unittest.TestCase):

	def test_makeState(self):
		"""
		CoreParser._makeState() returns an object representing parser state.
		"""
		sequence = "aaaa"
		parser = PythonDefinedParser(sequence)

		# Shuffle the state along a bit.
		parser.an_a()
		parser.an_a()

		self.assertEqual(
				parser._makeState(),
				(sequence, 2),
			)

	def test_setState(self):
		"""
		CoreParser._setState() restores parser state from a _makeState() blob.
		"""
		sequence = "aaaa"
		parser = PythonDefinedParser(sequence)

		# Shuffle the state along a bit.
		parser.an_a()
		self.assertEqual(parser._sequence, sequence)
		self.assertEqual(parser._position, 1)

		# Save state.
		cookie = parser._makeState()

		# Shuffle the state along a bit.
		parser.an_a()
		self.assertEqual(parser._sequence, sequence)
		self.assertEqual(parser._position, 2)

		# Restore state.
		parser._setState(cookie)

		# Should be back to the original state.
		self.assertEqual(parser._sequence, sequence)
		self.assertEqual(parser._position, 1)

	def test_match(self):
		"""
		CoreParser.match() picks a default rule and tests it consumes all input.
		"""
		# The default rule expects an 'a', so this should fail.
		self.assertRaises(BacktrackException,
				PythonDefinedParser.match, 'b')

		# The default rule consumes a single 'a', so trailing data should cause
		# it to complain.
		self.assertRaises(UnrecoverableParseError,
				PythonDefinedParser.match, 'aa')

		# If we give it the input it wants, it should be happy.
		self.assertEqual(
				PythonDefinedParser.match('a'),
				'a',
			)

	def test_parse_bogus_start_attribute(self):
		"""
		CoreParser.parse() complains if ._start points at a bogus value.
		"""
		class DummyParser(PythonDefinedParser):
			some_property = "sasquatch"

		# If ._start contains something that isn't the name of a class
		# property, it should raise ValueError.
		DummyParser._start = 42
		self.assertRaises(ValueError,
				DummyParser.match, 'a')

		# If .start contains the name of a non-callable property, it should
		# raise ValueError.
		DummyParser._start = "some_property"
		self.assertRaises(ValueError,
				DummyParser.match, 'a')

	def test_parse_specific_rule(self):
		"""
		CoreParser.parse() lets us specify which parsing rule to start with.
		"""
		sequence = "bbbb"

		# The default rule wants an 'a', so it won't parse this sequence.
		self.assertRaises(BacktrackException,
				PythonDefinedParser.match, sequence)

		# However, if we explicitly tell it we want to parse some 'b's, it
		# should be happy.
		self.assertEqual(
				PythonDefinedParser.match(sequence, "some_bs"),
				sequence,
			)

	def test_anything(self):
		"""
		CoreParser.anything() accepts any single item.
		"""
		self.assertEqual(
				PythonDefinedParser.match("a", "anything"),
				"a",
			)

		# anything() only accepts a single item.
		self.assertEqual(
				PythonDefinedParser("aaaa").anything(),
				"a",
			)

		# If anything() hits EOF, it raises an exception.
		self.assertRaises(BacktrackException,
				PythonDefinedParser.match, "", "anything")

	def test_seq(self):
		"""
		CoreParser.seq() tests each element of the passed sequence in turn.
		"""
		self.assertEqual(
				PythonDefinedParser("abc").seq("abc"),
				"abc",
			)

		# seq() only checks as many items as are in the sequence it's given.
		self.assertEqual(
				PythonDefinedParser("abcde").seq("abc"),
				"abc",
			)

		# seq() bails out if the given sequence is too long.
		self.assertRaises(BacktrackException,
				PythonDefinedParser("abc").seq, "abcde",
			)

		# seq() bails out if any element is wrong.
		self.assertRaises(BacktrackException,
				PythonDefinedParser("abc").seq, "abd",
			)

	def test_token(self):
		"""
		CoreParser.token() is just an alias for seq().
		"""
		self.assertEqual(
				PythonDefinedParser("abc").token("abc"),
				"abc",
			)

	def test_apply(self):
		"""
		CoreParser.apply() invokes the named parsing rule, maybe with args.
		"""
		# We can call a named parsing rule, without any arguments.
		self.assertEqual(
				PythonDefinedParser("bbb").apply("some_bs"),
				"bbb",
			)

		# We can call a named parsing rule, with arguments.
		self.assertEqual(
				PythonDefinedParser("abc").apply("seq", "abc"),
				"abc",
			)

		# We can call a rule that doesn't match.
		self.assertRaises(BacktrackException,
				PythonDefinedParser("abc").apply, "seq", "abd")

		# We can't call a rule that doesn't exist.
		self.assertRaises(AttributeError,
				PythonDefinedParser("abc").apply, "sasquatch")

		# We can't call a rule and give it the wrong number of arguments.
		self.assertRaises(TypeError,
				PythonDefinedParser("bbb").apply, "some_bs", "sasquatch")

	def test_parse_string(self):
		"""
		CoreParser accepts and understands byte strings.
		"""
		self.assertEqual(
				_core.CoreParser(b"a").anything(),
				b"a",
			)

	def test_parse_unicode(self):
		"""
		CoreParser accepts and understands unicode strings.
		"""
		self.assertEqual(
				_core.CoreParser(u"a").anything(),
				u"a",
			)

	def test_parse_tuple(self):
		"""
		CoreParser accepts and understands tuples.
		"""
		self.assertEqual(
				_core.CoreParser((1, 2, 3)).anything(),
				1,
			)

	def test_dont_parse_mutable_sequences(self):
		"""
		CoreParser requires an immutable sequence.
		"""
		self.assertRaises(TypeError, _core.CoreParser, [1, 2, 3])

	def test_dont_parse_non_sequence(self):
		"""
		CoreParser will not parse immutable non-sequences.
		"""
		self.assertRaises(TypeError, _core.CoreParser, frozenset([1, 2, 3]))


class TestCoreGrammar(unittest.TestCase):

	def test_no_grammar_no_start_name(self):
		"""
		With no grammar and no custom _start, _start defaults to None.
		"""
		class TestingParser(_core.CoreParser):
			__metaclass__ = MockGrammar

		self.assertEqual(TestingParser._start, None)

	def test_no_grammar_custom_start_name(self):
		"""
		With no grammar, a custom _start is left alone.
		"""
		class TestingParser(_core.CoreParser):
			__metaclass__ = MockGrammar
			_start = "sasquatch"

		self.assertEqual(TestingParser._start, "sasquatch")

	def test_custom_grammar_no_start_name(self):
		"""
		With a custom grammar and no custom _start, default to the last rule.
		"""
		class TestingParser(_core.CoreParser):
			__metaclass__ = MockGrammar
			__grammar = "myrule = anything ;"

		self.assertEqual(TestingParser._start, "myrule")

	def test_custom_grammar_custom_start_name(self):
		"""
		With a custom grammar, a custom _start is left alone.
		"""
		class TestingParser(_core.CoreParser):
			__metaclass__ = MockGrammar
			__grammar = "myrule = anything;"
			_start = "anotherrule"

			def anotherrule(self):
				pass

		self.assertEqual(TestingParser._start, "anotherrule")

	def test_custom_grammar_reset_start_name(self):
		"""
		With a custom grammar, _start can be explicitly reset to None.
		"""
		class TestingParser(_core.CoreParser):
			__metaclass__ = MockGrammar
			__grammar = "myrule = anything"
			_start = None

		self.assertEqual(TestingParser._start, None)

	def test_inherited_rules_custom_grammar_no_start_name(self):
		"""
		Inheriting from a parser and adding rules, the original _start stays.
		"""
		class TestingParser1(_core.CoreParser):
			__metaclass__ = MockGrammar
			__grammar = "firstrule = anything;"

		class TestingParser2(TestingParser1):
			__grammar = "secondrule = anything;"

		# Although TestingParser1 defines some new rules from the __grammar
		# attribute, the _start property isn't updated.
		self.assertEqual(TestingParser2._start, "firstrule")

	def test_inherited_reset_start_name(self):
		"""
		Inheriting from a parser that resets _start, default to the last rule.
		"""
		class TestingParser1(_core.CoreParser):
			__metaclass__ = MockGrammar
			__grammar = "firstrule = anything;"
			_start = None

		class TestingParser2(TestingParser1):
			__grammar = "secondrule = anything;"

		# TestingParser1 reset _start to None, but TestingParser2._start should
		# default to the last rule defined.
		self.assertEqual(TestingParser2._start, "secondrule")




if __name__ == "__main__":
	unittest.main()
