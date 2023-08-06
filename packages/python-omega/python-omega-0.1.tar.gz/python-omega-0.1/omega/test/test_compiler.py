#!/usr/bin/python
"""
Tests for the Omega compiler.

These are more integration tests than unit tests; the compiler itself produces
ASTs that are pretty much useless on their own; we don't really care what they
look like as long as they work, and that means involving _CoreGrammar and the
rest of the compiling infrastructure.
"""
import unittest
from omega.exceptions import ParseError
from omega.stdlib import BaseParser


# A unique object in the global namespace, so we can test that compiled Omega
# code uses the correct globals.
GLOBAL_VALUE = object()


class TestRuleParameters(unittest.TestCase):

	def test_invocation(self):
		class TestParser(BaseParser):
			# Define a Python-based parsing rule that takes a parameter.
			def addOne(self, number):
				return number + 1

			def addition(self, x, y):
				return x + y

			__grammar = """
					rule = addOne(5);
					rule2 = addOne(1, 2, 3);
					rule3 = addition(1, 2);
					rule4 = addition(1);
				"""

		# If we invoke the rule properly, we get the expected result.
		self.assertEqual(
				TestParser.match("", 'rule'),
				6,
			)

		# If we invoke the rule with too many arguments, we get the standard
		# Python too-many-arguments exception.
		self.assertRaises(TypeError,
				TestParser.match, "", 'rule2')

		# We can successfully invoke a rule with multiple arguments.
		self.assertEqual(
				TestParser.match("", 'rule3'),
				3,
			)
					
		# If we invoke the rule with too few arguments, we get the standard
		# Python too-few-arguments exception.
		self.assertRaises(TypeError,
				TestParser.match, "", 'rule4')

	def test_definition(self):
		class TestParser(BaseParser):
			__grammar = """
					addOne :x = !(x+1);
				"""

		tp = TestParser("")

		self.assertEqual(tp.addOne(2), 3)


class TestNamespaceLookups(unittest.TestCase):

	def test_globals(self):
		"""
		Compiled code can refer to global variables.
		"""
		class TestParser(BaseParser):
			__grammar = """
					rule = !(GLOBAL_VALUE);
				"""

		self.assertEqual(
				TestParser.match(""),
				GLOBAL_VALUE,
			)

	def test_locals(self):
		"""
		Compiled code can refer to variables local to the class.
		"""
		localValue = object()

		class TestParser(BaseParser):
			__grammar = """
					rule = !(localValue);
				"""

		self.assertEqual(
				TestParser.match(""),
				localValue,
			)

	# This function is expected to fail because Python doesn't actually make
	# intermediate namespaces between global() and locals() available to
	# introspection - they're added to locals() at compile-time when the
	# compiler notices the code referring to non-local variables. Because we
	# compile our own code divorced from the usual Python module-parsing, we
	# don't have access to the needed information, so we can't make this work.
	# See http://stackoverflow.com/questions/14158227/ for details.
	#
	# It's a pretty unlikely corner-case, though, so I think we can just ignore
	# it.
	@unittest.expectedFailure
	def test_nonlocals(self):
		"""
		Compiled code can refer to non-global, non-local variables.
		"""
		nonLocalValue = object()

		def newNamespace():
			class TestParser(BaseParser):
				__grammar = """
						rule = !(nonLocalValue);
					"""
			return TestParser.match("")

		self.assertEqual(
				newNamespace(),
				nonLocalValue,
			)


class TestTerms(unittest.TestCase):

	def test_semPredicate(self):
		class TestParser(BaseParser):
			__grammar = """
					succeeds = ?(True);
					fails = ?(False);
				"""

		self.assertEqual(TestParser.match("", 'succeeds'), True)
		self.assertRaises(ParseError, TestParser.match, "", 'fails')


if __name__ == "__main__":
	unittest.main()
