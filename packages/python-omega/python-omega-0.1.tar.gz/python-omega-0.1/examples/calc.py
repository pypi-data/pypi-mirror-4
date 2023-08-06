#!/usr/bin/python
"""
calc - a basic four function calculator

A demonstration of the Omega parsing library.
"""
import unittest
import decimal
from omega import BaseParser


class ArithmeticParser(BaseParser):
	"""
	A parser for arithmetic expressions.
	"""

	__grammar = r"""
			# Some basic definitions for recognising tokens in the input
			# stream.
			space = ' ' | '\r' | '\n' | '\t' ;
			spaces = space*;
			token :t = spaces seq(t);
			digit = '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' ;
			digitSpan = digit+:ds -> ("".join(ds));

			# We only deal with floats here, for simplicity.
			number =
					# The most complex definition goes firs
					spaces digitSpan:int '.' digitSpan:frac
						-> (decimal.Decimal(int + '.' + frac))
					| spaces '.' digitSpan:ds -> (decimal.Decimal('0.' + ds))
					| spaces digitSpan:ds '.'? -> (decimal.Decimal(ds))
					;

			# To get the operator precedence correct, we must define terms from
			# the innermost outward, because the leaves of the parse tree are
			# evaluated first.

			term =
					# A term can be some other term with a preceding unary
					# minus. Because this is a recursive definition, a term can
					# have any number of preceding unary minus signs, just like
					# in Python.
					"-" term:n -> (-1 * n)

					# A term can be an ordinary number.
					| number

					# A term can be some other expression in brackets.
					| "(" summation:inner ")" -> (inner)

					;

			# A product is two terms multiplied or divided (or
			# a modulus... 'modulated'?). So that we can have a chain of things
			# multiplied or divided, we'll make this a recursive rule.
			product = term:a "*" product:b -> (a * b)
				| term:a "/" product:b -> (a / b)
				| term:a "%" product:b -> (a % b)
				| term
				;

			# A summation is two products added or subtracted from each other.
			# So that we can have a chain of things added or subtracted, we'll
			# make this a recursive rule.
			summation = product:a "+" summation:b -> (a + b)
					| product:a "-" summation:b -> (a - b)
					# As the base case of this recursion, a summation can just
					# be a product.
					| product
					;

		"""


class ArithmeticParserTestCase(unittest.TestCase):

	def test_number_parsing(self):
		"""
		ArithmeticParser parses numbers.
		"""
		self.assertEqual(
				ArithmeticParser.match("  12"), decimal.Decimal("12.0"))

		self.assertEqual(
				ArithmeticParser.match("   .12"), decimal.Decimal("0.12"))

		self.assertEqual(
				ArithmeticParser.match("  12."), decimal.Decimal("12.0"))

		self.assertEqual(
				ArithmeticParser.match("    12.34"), decimal.Decimal("12.34"))

	def test_unary_minus(self):
		"""
		ArithmeticParser understands unary minus.
		"""
		self.assertEqual(
				ArithmeticParser.match("  -   12.34"),
				decimal.Decimal("-12.34"),
			)

		self.assertEqual(
				ArithmeticParser.match("---12.34"),
				decimal.Decimal("-12.34"),
			)

	def test_summation(self):
		"""
		ArithmeticParser can add and subtract.
		"""
		self.assertEqual(ArithmeticParser.match("1 + 1"), 2)
		self.assertEqual(ArithmeticParser.match("3 - 1"), 2)

		# Test chaining too.
		self.assertEqual(ArithmeticParser.match("1 + 2 + 3"), 6)

	def test_product(self):
		"""
		ArithmeticParser can multiply and divide.
		"""
		self.assertEqual(ArithmeticParser.match("2 * 3"), 6)
		self.assertEqual(ArithmeticParser.match("8 / 4"), 2)
		self.assertEqual(ArithmeticParser.match("9 % 4"), 1)

		# Test chaining too.
		self.assertEqual(ArithmeticParser.match("2 * 2 * 2"), 8)

	def test_brackets(self):
		"""
		ArithmeticParser handles expressions in brackets.
		"""
		self.assertEqual(ArithmeticParser.match("(2 + 3) * (1 + 2)"), 15)

	def test_precedence(self):
		"""
		ArithmeticParser gets operator precedence correct.
		"""
		# Make sure we're not just processing the first operator first.
		self.assertEqual(ArithmeticParser.match("2 + 3 * 4"), 14)

		# Make sure we're not just processing the last operator first.
		self.assertEqual(ArithmeticParser.match("2 * 3 + 4"), 10)


if __name__ == "__main__":
	unittest.main()
