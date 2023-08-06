#!/usr/bin/python
"""
Classes and helper functions for implementing Omega-based parsers.
"""
from omega import _core
from omega import bootstrap

class OmegaGrammar(_core.CoreGrammar):
	_parser = bootstrap.OmegaParser


class BaseParser(_core.CoreParser):
	# This class's parser definitions should be parsed as Omega source code.
	__metaclass__ = OmegaGrammar

	# Prevent any of our standard library functions from being picked as the
	# default parsing rule.
	_start = None

	__grammar = """
			# All the rules we can helpfully implement directly in Omega.
			end = ~anything ;
			empty = -> '' ;
			exactly :item = seq((item,)) -> (item) ;
		"""
