"""
The innermost code at the core of Omega. Not for public use.
"""
import functools
import ast
import types
import inspect
import collections
from omega.exceptions import BacktrackException, UnrecoverableParseError
from omega.compiler import OmegaCompiler


def _wrap_rule(rulefunc):
	"""
	Wrap the given rule function with boilerplate.

	Specifically, we want to wrap the rule-checking function so that it will:
		- automatically be memoized
		- handle pushing and popping the parser state.
	"""
	rulename = rulefunc.__name__
	@functools.wraps(rulefunc)
	def wrapper(self, *args):
		#print "Rule %s%r beginning at pos %d" % (rulename, args, self._position)
		packratKey = (self._makeState(), rulename, args)
		if packratKey in self._packratCache:
			item = self._packratCache[packratKey]
			if isinstance(item, self._backtrackException):
				raise item
			else:
				token, result = item
				self._setState(token)
				return result

		try:
			res = rulefunc(self, *args)
			self._packratCache[packratKey] = (self._makeState(), res)
			#print "Rule %s%r finished at pos %d: %r" % (rulename, args, self._position-1, res)
			return res

		except self._backtrackException, e:
			self._packratCache[packratKey] = e
			#print "Rule %s%r failed: %s" % (rulename, args, str(e))
			raise

	return wrapper


def _parse_if_needed(parser, name, bases, contents):
	"""
	Parse the Omega grammar in the given class, if any.

	Returns the parsed AST if there's a grammar to be compiled, otherwise
	None.
	"""
	grammarAttribName = "_%s__grammar" % (name,)

	if grammarAttribName not in contents:
		# This class does not define any rules with an Omega grammar.
		return False

	if parser is None:
		# We have a grammar to parse, but no parser to parse it with!
		raise RuntimeError("Class %s should set the '_parser' attribute "
				"to a valid parser for the grammar it defines."
				% (name,))

	omegaAST = parser.match(contents[grammarAttribName])

	# Let's do some basic sanity checks of the resulting grammar.
	assert omegaAST[0] == 'grammar', (
			"Expected an Omega grammar AST, not %r" % (omegaAST,)
		)
	assert len(omegaAST) > 1, (
			"Omega grammar AST must have at least one rule."
		)

	lastRuleName = None
	for rule in omegaAST[1:]:
		assert rule[0] == 'rule', (
				"Omega grammar AST must contain rules, not %r" % (rule,)
			)
		lastRuleName = rule[1]

	if "_start" in contents:
		# If this class defines a _start attribute, whatever it is, then we'll
		# keep it.
		pass
	else:
		# Otherwise, has _start been set to something other than None in any of
		# the base classes?
		for cls in bases:
			if getattr(cls, "_start", None) != None:
				break
		else:
			# Nothing has set _start so far, so let's default it to the
			# name of the last-defined rule.
			contents["_start"] = lastRuleName

	return omegaAST


def _compile_grammar(name, contents, namespace, omegaAST):
	"""
	Compile the given AST into the given class definition.
	"""
	compiler = OmegaCompiler()
	pythonAST = compiler.process("", omegaAST)
	ast.fix_missing_locations(pythonAST)
	code_obj = compile(pythonAST, "<string>", "single")

	exec code_obj in namespace, contents


class CoreGrammar(type):
	"""
	Metaclass that fills out a Parser class.
	"""
	_parser = None

	def __new__(mcls, name, bases, contents):
		"""
		Build a functioning parser from the definition in the given class.
		"""
		#print "Creating class %r" % (name,)

		# If there's a class variable named '__grammar', compile it into new
		# rule methods.
		omegaAST = _parse_if_needed(mcls._parser, name, bases, contents)
		if omegaAST:
			#from pprint import pprint
			#pprint(omegaAST)

			# We want any variable references in the compiled source-code to
			# use the namespace where this class was defined, not where it's
			# being compiled (in the same way that a Python method defined in
			# a class uses the namespace where the class is defined). For that,
			# we need to use.. *cough* stack introspection. :(
			namespace = {}
			callerFrame = inspect.currentframe(1)
			if callerFrame is not None:
				try:
					namespace.update(callerFrame.f_globals)
					namespace.update(callerFrame.f_locals)
				finally:
					del callerFrame

			_compile_grammar(name, contents, namespace, omegaAST)

		# Decorate all our newly-defined parsing rules with memoization magic.
		for attrName in contents:
			# We only want to wrap actual functions.
			if not isinstance(contents[attrName], types.FunctionType):
				continue

			# We only want to wrap publically-accessible rules.
			if attrName.startswith("_"):
				continue

			contents[attrName] = _wrap_rule(contents[attrName])

		return type.__new__(mcls, name, bases, contents)

	def match(cls, sequence, ruleName=None):
		"""
		Instantiate this parser class and use it to parse the given sequence.

		If ruleName is supplied, the parsing rule with that name will be
		applied to the sequence. If not supplied, or set to None, the rule
		named in the class's _start attribute will be used.
		"""
		#print "Trying to parse %r with %r" % (sequence, cls)
		parser = cls(sequence)

		if ruleName is None:
			ruleName = parser._start

		if not isinstance(ruleName, str):
			raise ValueError("Tried to start parsing with parser %s rule %r, "
					"but that doesn't look like the name of a parsing rule."
					% (cls, ruleName))

		rule = getattr(parser, ruleName)

		if not callable(rule):
			raise ValueError("Tried to start parsing with parser %s rule %r, "
					"but that name refers to %r, not a parsing rule."
					% (cls, ruleName, rule))

		res = rule()

		if parser._sequence != sequence:
			raise RuntimeError("whoa, parser derailed!")
		if parser._position < len(sequence):
			pos = parser._position
			raise UnrecoverableParseError(sequence, pos,
					"Found unexpected stuff: expected EOF, found %r..."
					% (sequence[pos:pos+10],)
				)

		return res


class CoreParser(object):
	"""
	Base class that supplies most of the Omega 'standard library'.
	"""
	__metaclass__ = CoreGrammar

	# Used to store the name of the top-level parsing rule. If a parser class
	# defines its parser rules with a __grammar definition, this will be
	# automatically set to the last-defined parsing rule. If a parser class is
	# pure-Python, it will need to set this manually.
	_start = None

	# This is the exception that will be raised by ._backtrack() and which
	# should be caught by code that wants to implement backtracking behaviour.
	_backtrackException = BacktrackException

	def __init__(self, sequence, position=0):
		# We only work with sequences, so let's give a helpful error message
		# now, instead of an explosion deep in generated code at some
		# unspecified future time.
		if not isinstance(sequence, collections.Sequence):
			raise TypeError("Omega only parses immutable sequences, not %r"
					% (type(sequence),))

		# We also require that the sequence be immutable, so we can use it as
		# part of a dictionary key. This will throw TypeError if the sequence,
		# or any nested item of the sequence is mutable.
		hash(sequence)

		self._sequence = sequence
		self._position = position
		self._packratCache = {}

	def _makeState(self):
		"""
		Return a token representing the parser state.
		"""
		return (self._sequence, self._position)

	def _setState(self, token):
		"""
		Set the parser state to the one described by the given token.
		"""
		self._sequence, self._position = token

	def _backtrack(self, message):
		raise self._backtrackException(self._sequence, self._position, message)

	def anything(self):
		"""
		Grabs the next item from the sequence, whatever it is.
		"""
		if self._position >= len(self._sequence):
			# We've run off the end.
			self._backtrack("Unexpected EOF")

		res = self._sequence[self._position]
		self._position += 1
		return res

	def seq(self, target):
		"""
		Tests that each element of target matches the sequence in turn.
		"""
		for expected in target:
			actual = self.anything()
			if actual != expected:
				self._backtrack("Got %r, expected %r" % (actual, expected))

		return target

	token = seq

	def apply(self, name, *args):
		"""
		Invokes the named parsing rule, optionally with arguments.
		"""
		func = getattr(self, name)
		return func(*args)
