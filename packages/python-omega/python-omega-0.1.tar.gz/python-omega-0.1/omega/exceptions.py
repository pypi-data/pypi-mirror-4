#!/usr/bin/python
"""
Exceptions that can be raised by Omega parser instances.
"""


class ParseError(Exception):
	"""
	Parent of all possible parsing problem.
	"""
	def __init__(self, sequence, pos, description):
		super(ParseError, self).__init__("%s:%s" % (pos, description))
		self.sequence = sequence
		self.pos = pos
		self.description = description


class UnrecoverableParseError(ParseError):
    """
    A parsing problem that can't be solved by back-tracking.
    """


class BacktrackException(ParseError):
    """
    A parsing problem that might be solved by back-tracking.
    """


