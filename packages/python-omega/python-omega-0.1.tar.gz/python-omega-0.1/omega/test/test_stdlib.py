#!/usr/bin/python
import unittest
from omega import stdlib
from omega.exceptions import ParseError


class TestBaseParser(unittest.TestCase):

	def test_end(self):
		"""
		end detects the end of the stream.
		"""
		# If we're not at the end of the stream, fail.
		self.assertRaises(ParseError, stdlib.BaseParser("a").end)

		# Make a new parser with a non-empty stream.
		bp = stdlib.BaseParser("a")

		# Empty the stream.
		bp.anything()

		# Now we're at the end.
		self.assertEqual(bp.end(), None)

	def test_empty(self):
		"""
		empty consumes nothing.
		"""
		bp = stdlib.BaseParser("a")

		# We can call empty as much as we like...
		self.assertEqual(bp.empty(), '')
		self.assertEqual(bp.empty(), '')
		self.assertEqual(bp.empty(), '')

		# ...it still hasn't consumed any of the stream.
		self.assertEqual(bp.anything(), 'a')

	def test_exactly(self):
		"""
		exactly matches if the next item equals the given item.
		"""
		# exactly detects a non-match
		self.assertRaises(ParseError, stdlib.BaseParser(("abc",)).exactly, 'a')

		# exactly detects a match.
		self.assertEqual(stdlib.BaseParser(("abc",)).exactly('abc'), 'abc')

		# exactly consumes only one item, even if it's given a sequence and
		# following items would continue the match.
		self.assertRaises(ParseError, stdlib.BaseParser("abc").exactly, 'abc')


if __name__ == "__main__":
	unittest.main()
