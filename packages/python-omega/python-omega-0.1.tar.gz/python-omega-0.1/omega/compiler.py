#!/usr/bin/python
"""
Tools for converting Omega parse trees into Python AST objects.
"""
import ast


def name(text):
	return ast.Name(text, ast.Load(), lineno=0, col_offset=0)


def arg(text):
	return ast.Name(text, ast.Param())


def attrib(obj, name):
	return ast.Attribute(obj, name, ast.Load(), lineno=0, col_offset=0)


def call(func, *args):
	return ast.Call(func, list(args), [], None, None, lineno=0, col_offset=0)


def encodeLiteral(value):
	if isinstance(value, str):
		return ast.Str(value)
	elif isinstance(value, int):
		return ast.Num(value)
	elif isinstance(value, list):
		return ast.List([encodeLiteral(x) for x in value], ast.Load())

	raise ValueError("Unknown argument %r" % (arg,))


def callWithLiterals(func, *rawArgs):
	return call(func, *[encodeLiteral(arg) for arg in rawArgs])


def assignment(name, value):
	return ast.Assign(
			[ast.Name(name, ast.Store(), lineno=0, col_offset=0)],
			value,
			lineno=0, col_offset=0,
		)


def tryExcept(tryBody, exceptBody, elseBody=None):
	if elseBody is None:
		elseBody = []
	return ast.TryExcept(
			tryBody,
			[
				ast.ExceptHandler(
					attrib(name("self"), "_backtrackException"),
					None, # no '...as e' clause
					exceptBody,
				),
			],
			elseBody,
			lineno=0,
			col_offset=0,
		)


def genIdents():
	"""
	Yield an infinite sequence of valid Python identifiers.
	"""
	start = 0
	while True:
		yield "_%d" % start
		start += 1


class OmegaCompiler(object):

	# This is structured very much like an Omega parser object, but doesn't
	# actually use the Omega dispatch machinery. This is because the Omega
	# dispatch machinery needs to be compiled in order to do anything useful,
	# so that would be a circular dependency.
	#
	# We could get around that by having a "bootstrap compiler" that generated
	# the code for the real compiler, like we have a bootstrap parser and
	# a real parser, but the bootstrap parser is trivial, and the compiler is
	# not, and it'd be a shame to duplicate all this code.

	def __init__(self):
		self._identifiers = genIdents()

	def _buildParserStateTools(self):
		# Return some handy pre-fab statements that will save parser state to
		# and restore parser state from a new variable.
		stateVar = self._identifiers.next()

		saveStateStmt = assignment(stateVar,
				call(attrib(name("self"), "_makeState"))
			)
		restoreStateStmt = ast.Expr(
				call(attrib(name("self"), "_setState"), name(stateVar)),
				lineno=0,
				col_offset=0,
			)

		return saveStateStmt, restoreStateStmt

	def process(self, identifier, node):
		nodeName, nodeArgs = node[0], node[1:]
		handler = getattr(self, nodeName)
		return handler(identifier, *nodeArgs)

	def item(self, identifier, expected):
		return self.invocation(identifier, "anything") + [
				ast.If(
					ast.Compare(
						name(identifier),
						[ast.NotEq()],
						[encodeLiteral(expected)],
					),
					[
						ast.Expr(callWithLiterals(
							attrib(name("self"), "_backtrack"),
							"Expected %r" % (expected,)
						)),
					],
					[], # else:
				)
			]

	def invocation(self, identifier, ruleName, *rawArgs):
		argsAST = [
				ast.parse(expr, '<string>', 'eval').body
				for expr in rawArgs
			]

		return [
				assignment(
					identifier,
					call(
						attrib(name("self"), ruleName),
						*argsAST
					),
				),
			]

	def negLookahead(self, identifier, node):
		# We need a way to save and restore parser state.
		saveStateStmt, restoreStateStmt = self._buildParserStateTools()

		return [
				saveStateStmt,
				tryExcept(
					self.process(identifier, node),
					[
						# Got an exception, as expected.
						restoreStateStmt,
						assignment(identifier, name("None")),
					],
					[
						# No exception occurred! Raise the alarm!
						ast.Expr(callWithLiterals(
							attrib(name("self"), "_backtrack"),
							"Matched a rule that shouldn't match."
						)),
					],
				)
			]

	def lookahead(self, identifier, node):
		# We need a way to save and restore parser state.
		saveStateStmt, restoreStateStmt = self._buildParserStateTools()

		return [
				saveStateStmt,
				] + self.process(identifier, node) + [
				restoreStateStmt,
			]

	def star(self, identifier, node):
		# We need a way to save and restore parser state.
		saveStateStmt, restoreStateStmt = self._buildParserStateTools()

		# We need an item variable to store each item, before we append it to
		# the accumulator.
		itemName = self._identifiers.next()

		return [
				assignment(identifier, encodeLiteral([])),
				ast.While(name("True"),
					[
						saveStateStmt,
						tryExcept(
							self.process(itemName, node)
							+ [ast.Expr(call(
								attrib(name(identifier), "append"),
								name(itemName),
							))],
							[
								restoreStateStmt,
								ast.Break(),
							]
						)
					],
					[], # else clause
				),
			]

	def plus(self, identifier, node):
		# We need a way to save and restore parser state.
		saveStateStmt, restoreStateStmt = self._buildParserStateTools()

		# We need an item variable to store each item, before we append it to
		# the accumulator.
		itemName = self._identifiers.next()

		return self.process(itemName, node) + [
				assignment(identifier, encodeLiteral([])),
				ast.Expr(call(
					attrib(name(identifier), "append"), name(itemName),
				)),
				ast.While(name("True"),
					[
						saveStateStmt,
						tryExcept(
							self.process(itemName, node)
							+ [ast.Expr(call(
								attrib(name(identifier), "append"),
								name(itemName),
							))],
							[
								restoreStateStmt,
								ast.Break(),
							]
						)
					],
					[], # else clause
				),
			]

	def qmark(self, identifier, node):
		# We need a way to save and restore parser state.
		saveStateStmt, restoreStateStmt = self._buildParserStateTools()

		return [
				saveStateStmt,
				tryExcept(
					self.process(identifier, node),
					[
						restoreStateStmt,
						assignment(identifier, name("None")),
					],
				),
			]

	def term(self, identifier, node):
		return self.process(identifier, node)

	def tagged(self, _, identifier, node):
		return self.process(identifier, node)

	def seq(self, identifier, *nodes):
		res = []
		for node in nodes:
			res.extend(self.process(identifier, node))
		return res

	def alternatives(self, identifier, *nodes):
		# We need to save the parser state before we start and reset it before
		# each attempt, so let's make a variable to store that state in.
		saveStateStmt, restoreStateStmt = self._buildParserStateTools()

		# This is kind of a complicated construction. Given alternatives alt1,
		# alt2 and alt3, we're trying to contstruct something like this:
		#
		# 	saveStateStmt()
		# 	while True:
		# 		try:
		# 			res = alt1()
		# 			break
		# 		except BacktrackException:
		# 			restoreStateStmt()
		#
		# 		try:
		# 			res = alt2()
		# 			break
		# 		except BacktrackException:
		# 			restoreStateStmt()
		#
		# 		res = alt3()
		# 		break
		#
		# This way, we should be able to try each alternative in turn, and
		# a failure in the last alternative will still cause proper
		# backtracking. The "while True" combined with a bunch of break
		# statements is a nasty way to emulate goto in Python.

		nodes, tail = nodes[:-1], nodes[-1]
		return [
				saveStateStmt,
				ast.While(
					name("True"),
					[
						tryExcept(
							self.process(identifier, n) + [ast.Break()],
							[restoreStateStmt],
						)
						for n in nodes
					] + self.process(identifier, tail)
						+ [ast.Break()],
					[], # else:
				),
			]

	def semAction(self, identifier, expr):
		# Parse the given expr into an AST we can attach to the AST we're
		# building.
		exprAST = ast.parse(expr, '<string>', 'eval').body
		return [assignment(identifier, exprAST)]

	def semPredicate(self, identifier, expr):
		# Parse the given expr into an AST we can attach to the AST we're
		# building.
		exprAST = ast.parse(expr, '<string>', 'eval').body
		return [
				assignment(identifier, exprAST),
				ast.If(
					ast.UnaryOp(ast.Not(), name(identifier)),
					[
						ast.Expr(callWithLiterals(
							attrib(name("self"), "_backtrack"),
							"Predicate failed: %s" % (expr,)
						)),
					],
					[], # else:
				)
			]

	def rule(self, _, ruleName, argNames, node):
		# We want to add the implicit self parameter to the beginning of the
		# arguments list.
		arguments = ast.arguments(
				[arg('self')] + [arg(x) for x in argNames],
				None, None, [],
			)

		# We need a way to allocate local variable names in this function.
		self._identifiers = genIdents()

		# We need a result variable to store the result of this function.
		resName = self._identifiers.next()

		# Build all the statements in this function.
		statements = self.process(resName, node)

		# The last statement returns the result.
		statements.append(
				ast.Return(name(resName))
			)

		return [ast.FunctionDef(ruleName, arguments, statements, [])]

	def grammar(self, _, *rules):
		statements = []
		for rule in rules:
			statements.extend(self.process("", rule))
		return ast.Interactive(statements)

