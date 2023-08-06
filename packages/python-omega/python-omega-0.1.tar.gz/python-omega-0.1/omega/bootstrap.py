#!/usr/bin/python
"""
The tangled knot of base classes at the core of Omega.
"""
from omega._core import CoreGrammar, CoreParser


class BootstrapParser(CoreParser):
	"""
	A hand-coded parser for Omega parser definitions.

	This class only implements enough of the Omega language to parse the
	definition in the OmegaParser class. That definition is then compiled and
	used to parse every subsequent definition.
	"""

	_start = "grammar"

	def _op_qmark(self, rule, *args):
		token = self._makeState()
		try:
			return rule(*args)
		except self._backtrackException:
			self._setState(token)
			return None

	def _op_star(self, rule, *args):
		res = []

		while True:
			try:
				token = self._makeState()
				res.append(rule(*args))
			except self._backtrackException:
				self._setState(token)
				break
				
		return res

	def _op_plus(self, rule, *args):
		res = [rule(*args)]
		res.extend(self._op_star(rule, *args))
		return res

	def _op_alternative(self, *rules):
		for ruledef in rules[:-1]:
			rule, args = ruledef[0], ruledef[1:]
			try:
				token = self._makeState()
				return rule(*args)
			except self._backtrackException:
				self._setState(token)
				continue

		rule, args = rules[-1][0], rules[-1][1:]
		return rule(*args)

	def _op_lookahead(self, rule, *args):
		token = self._makeState()
		res = rule(*args)
		self._setState(token)
		return res

	def eol(self):
		def cr():
			self.seq("\r")
		def lf():
			self.seq("\n")
		def crlf():
			cr()
			lf()

		self._op_alternative(
				(crlf,),
				(cr,),
				(lf,),
			)

		return '\n'

	def comment(self):
		self.seq('#')

		def not_eol():
			item = self.anything()
			if item in "\r\n":
				self._backtrack("Didn't want an EOL, got %r" % (item,))
			return item

		self._op_star(not_eol)
		self._op_qmark(self.eol)

		return ''

	def spaces(self):
		def space():
			item = self.anything()
			if isinstance(item, basestring) and item.isspace():
				return " "
			else:
				self._backtrack("Got %r, expected whitespace" % (item,))

		def ignorable():
			self._op_alternative(
					(self.comment,),
					(space,),
					(self.eol,),
				)

		self._op_star(ignorable)
		return ' '

	def token(self, sequence):
		"""
		Skips whitespace and grabs a sequence of items.
		"""
		self.spaces()
		return self.seq(sequence)

	def uppercase(self):
		res = self.anything()
		if 'A' <= res <= 'Z':
			return res
		else:
			self._backtrack("Got %r, expected an uppercase letter." % (res,))

	def lowercase(self):
		res = self.anything()
		if 'a' <= res <= 'z':
			return res
		else:
			self._backtrack("Got %r, expected a lowercase letter." % (res,))

	def digit(self):
		res = self.anything()
		if '0' <= res <= '9':
			return res
		else:
			self._backtrack("Got %r, expected a digit." % (res,))

	def identStart(self):
		return self._op_alternative(
				(self.uppercase,),
				(self.lowercase,),
			)

	def identChar(self):
		def underscore():
			res = self.anything()
			if res == '_':
				return res
			else:
				self._backtrack("Got %r, expected '_'" % (res,))

		return self._op_alternative(
				(self.uppercase,),
				(self.lowercase,),
				(self.digit,),
				(underscore,),
			)

	def unquotedChar(self):
		res = self.anything()
		if res not in "'\\":
			return res
		else:
			self._backtrack("Got %r, expected anything but a backslash "
					"or apostrophe." % (res,))

	def quotedChar(self):
		res = self.anything()
		if res != '\\':
			self._backtrack("Got %r, expected a backslash." % (res,))

		res = self.anything()
		if res == '\'':
			return '\''
		elif res == '"':
			return '"'
		elif res == '\\':
			return '\\'
		elif res == 'r':
			return '\r'
		elif res == 'n':
			return '\n'
		elif res == 't':
			return '\t'
		else:
			self._backtrack("Got %r, expected a ', \\, r, n or t." % (res,))

	def stringContents(self):
		res = self._op_star(
				self._op_alternative,
				(self.unquotedChar,),
				(self.quotedChar,),
			)
		return "".join(res)

	def ident(self):
		self.spaces()
		start = self.identStart()
		rest = self._op_star(self.identChar)
		return start + "".join(rest)

	def hostExprString(self):
		def hostExprStringEscape():
			self.seq('\\')
			res = self.anything()
			return '\\' + res

		def unquotedChar(delim):
			res = self.anything()
			if res not in ('\\', '\n', '\r', delim):
				return res
			else:
				self._backtrack("Got %r, expected anything but a backslash, "
						"CR, LF, or %r" % (res, delim))

		def quotedString(delim):
			self.token(delim)
			res = self._op_star(
					self._op_alternative,
					(unquotedChar, delim),
					(hostExprStringEscape,),
				)
			self.seq(delim)
			return "%s%s%s" % (delim, "".join(res), delim)

		return self._op_alternative(
				(quotedString, "'"),
				(quotedString, '"'),
			)

	def hostExprContents(self):
		def hostExprChar():
			item = self.anything()
			if item in "()[]{}\"\'":
				self._backtrack("got %r" % (item,))
			else:
				return item

		def hostExprSpan():
			res = self._op_plus(hostExprChar)
			return "".join(res)

		return self._op_alternative(
				(self.hostExpr,),
				(hostExprSpan,),
			)

	def hostExprGroup(self):
		def genericGroup(start, end):
			self.token(start)
			inner = self._op_star(self.hostExprContents)
			self.token(end)
			return "%s%s%s" % (start, "".join(inner), end)

		return self._op_alternative(
				(genericGroup, '(', ')'),
				(genericGroup, '[', ']'),
				(genericGroup, '{', '}'),
			)

	def hostExpr(self):
		return self._op_alternative(
				(self.hostExprGroup,),
				(self.hostExprString,),
			)

	def hostExprItem(self):
		def hostExprItemChar():
			res = self.anything()
			if res not in "()[]{}\"',":
				return res
			else:
				self._backtrack("Got unwanted char %r" % (res,))

		def hostExprItemSpan():
			chars = self._op_plus(hostExprItemChar)
			return "".join(chars)

		def hostExprItemContent():
			return self._op_alternative(
					(self.hostExpr,),
					(hostExprItemSpan,),
				)

		self.spaces()
		inner = self._op_plus(hostExprItemContent)
		return "".join(inner)

	def hostExprList(self):
		def tailItem():
			self.token(',')
			return self.hostExprItem()

		first = self.hostExprItem()
		rest = self._op_star(tailItem)
		self._op_qmark(self.token, ',')
		return [first] + rest

	def atom(self):
		def quotedString():
			self.token("'")
			string = self.stringContents()
			self.seq("'")
			return ('item', string)

		def token():
			self._op_lookahead(self.token, '"')
			string = self.hostExprString()
			return ('invocation', 'token', string)

		def invocationWithArgs():
			name = self.ident()
			self.seq('(')
			args = self.hostExprList()
			self.token(')')
			return ('invocation', name) + tuple(args)

		def invocation():
			name = self.ident()
			return ("invocation", name)

		def bracketedAlternatives():
			self.token('(')
			inner = self.alternatives()
			self.token(')')
			return inner

		return self._op_alternative(
				(quotedString,),
				(token,),
				(invocationWithArgs,),
				(invocation,),
				(bracketedAlternatives,),
			)

	def quantified(self):
		def negativeLookAhead():
			self.token('~')
			inner = self.atom()
			return ('negLookahead', inner)

		def lookahead():
			self.token('&')
			inner = self.atom()
			return ('lookahead', inner)

		def atom_qmark():
			inner = self.atom()
			self.seq('?')
			return ('qmark', inner)

		def atom_star():
			inner = self.atom()
			self.seq('*')
			return ('star', inner)

		def atom_plus():
			inner = self.atom()
			self.seq('+')
			return ('plus', inner)

		return self._op_alternative(
				(negativeLookAhead,),
				(lookahead,),
				(atom_qmark,),
				(atom_star,),
				(atom_plus,),
				(self.atom,),
			)

	def semAction(self):
		self._op_alternative(
				(self.token, '!'),
				(self.token, '->'),
			)
		expr = self.hostExpr()
		return ('semAction', expr)

	def semPredicate(self):
		self.token("?")
		expr = self.hostExpr()
		return ('semPredicate', expr)

	def term(self):
		return self._op_alternative(
				(self.quantified,),
				(self.semAction,),
				(self.semPredicate,),
			)

	def taggedTerm(self):
		def anythingTag():
			self.spaces()
			self.seq(':')
			name = self.ident()
			return ('tagged', name, ('invocation', 'anything'))

		def somethingTag():
			inner = self.quantified()
			self.seq(':')
			name = self.ident()
			return ('tagged', name, inner)

		def untaggedTerm():
			inner = self.term()
			return ('term', inner)

		return self._op_alternative(
				(anythingTag,),
				(somethingTag,),
				(untaggedTerm,),
			)

	def sequence(self):
		inner = self._op_plus(self.taggedTerm)
		return ('seq',) + tuple(inner)

	def alternatives(self):
		def alternativeOptions():
			first = self.sequence()

			def alternativeOption():
				self.token("|")
				return self.sequence()

			rest = self._op_plus(alternativeOption)

			return ('alternatives', first) + tuple(rest)

		return self._op_alternative(
				(alternativeOptions,),
				(self.sequence,),
			)

	def ruleArgs(self):
		def arg():
			self.token(':')
			return self.ident()
		args = self._op_star(arg)
		return tuple(args)

	def rule(self):
		name = self.ident()
		args = self.ruleArgs()
		self.token('=')
		inner = self.alternatives()
		self.token(';')

		return ("rule", name, args, inner)

	def grammar(self):
		rules = self._op_plus(self.rule)
		self.spaces()
		return ('grammar',) + tuple(rules)


class BootstrapGrammar(CoreGrammar):
	"""
	A Grammar metaclass that parses definitions with the BootstrapParser.
	"""
	_parser = BootstrapParser


class OmegaParser(CoreParser):
	"""
	A parser for the Omega parser-generator language, written in Omega.
	"""
	# We want our grammar to be parsed with the BootstrapParser.
	__metaclass__ = BootstrapGrammar

	__grammar = r"""
			eol = ('\r' '\n'? | '\n') -> '\n';
			comment = '#' (~('\r' | '\n') anything)* eol? -> '';
			spaces = (' ' | '\r' | '\n' | '\t' | comment)* -> ' ';
			token :t = spaces seq(t);
			uppercase = 'A' | 'B' | 'C' | 'D' | 'E' | 'F' | 'G' | 'H' | 'I'
					| 'J' | 'K' | 'L' | 'M' | 'N' | 'O' | 'P' | 'Q' | 'R' | 'S'
					| 'T' | 'U' | 'V' | 'W' | 'X' | 'Y' | 'Z' ;
			lowercase = 'a' | 'b' | 'c' | 'd' | 'e' | 'f' | 'g' | 'h' | 'i'
					| 'j' | 'k' | 'l' | 'm' | 'n' | 'o' | 'p' | 'q' | 'r' | 's'
					| 't' | 'u' | 'v' | 'w' | 'x' | 'y' | 'z' ;
			digit = '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' ;
			identStart = uppercase | lowercase ;
			identChar = uppercase | lowercase | digit | '_' ;
			unquotedChar = ~'\\' ~'\'' anything;
			quotedChar = '\\' (
					'\'' -> '\''
					| '"' -> '"'
					| '\\' -> '\\'
					| 'r' -> '\r'
					| 'n' -> '\n'
					| 't' -> '\t'
				);
			stringContents = (quotedChar | unquotedChar)*:chars
					-> ("".join(chars));
			ident = spaces identStart:start identChar*:rest
					-> (start + "".join(rest));

			hostExprStringEscape = '\\' anything:c -> ('\\' + c);
			hostExprString =
					# Single-quoted strings.
					"'" (
						(~'\\' ~'\'' ~'\n' ~'\r' anything)+:chars
							-> ("".join(chars))
						| hostExprStringEscape
					)*:spans "'"
						-> ('\'' + "".join(spans) + '\'')
					| # Double-quoted strings.
					"\"" (
						(~'\\' ~'"' ~'\n' ~'\r' anything)+:chars
							-> ("".join(chars))
						| hostExprStringEscape
					)*:spans "\""
						-> ('"' + "".join(spans) + '"')
					;
			hostExprContents = hostExpr
					| (
						~'(' ~')'
						~'[' ~']'
						~'{' ~'}'
						~'"' ~'\''
						anything
					)+:chars -> ("".join(chars))
					;
			hostExprGroup =
					"(" hostExprContents*:inner ")"
						-> ('(' + "".join(inner) + ')')
					| "[" hostExprContents*:inner "]"
						-> ('[' + "".join(inner) + ']')
					| "{" hostExprContents*:inner "}"
						-> ('{' + "".join(inner) + '}')
					;
			hostExpr = hostExprGroup | hostExprString;

			hostExprItemContent = hostExpr
					| (
						~'(' ~')' ~'[' ~']' ~'{' ~'}' ~'"' ~'\'' ~','
						anything
					)+:chars -> ("".join(chars))
					;
			hostExprItem =
					spaces hostExprItemContent+:inner
						-> ("".join(inner));
			hostExprList =
					hostExprItem:first ("," hostExprItem)*:rest (",")?
						-> ([first] + rest);

			atom = "'" stringContents:string "'" -> ('item', string)
					| spaces &'"' hostExprString:string
						-> ('invocation', 'token', string)
					| ident:name '(' hostExprList:args ")"
						-> (('invocation', name) + tuple(args))
					| ident:name -> ('invocation', name)
					| "(" alternatives:inner ")" -> (inner)
					;
			quantified = "~" atom:inner -> ('negLookahead', inner)
					| "&" atom:inner -> ('lookahead', inner)
					| atom:inner '?' -> ('qmark', inner)
					| atom:inner '*' -> ('star', inner)
					| atom:inner '+' -> ('plus', inner)
					| atom
					;
			semAction = ("!" | "->") hostExpr:e -> ('semAction', e);
			semPredicate = "?" hostExpr:e -> ('semPredicate', e);
			term = quantified | semAction | semPredicate;
			taggedTerm = ":" ident:name
						-> ('tagged', name, ('invocation', 'anything'))
					| term:inner ':' ident:name
						-> ('tagged', name, inner)
					| term:inner -> ('term', inner)
					;
			sequence = taggedTerm+:inner -> (('seq',) + tuple(inner));
			alternatives = sequence:first ("|" sequence)+:rest
						-> (('alternatives', first) + tuple(rest))
					| sequence
					;
			ruleArgs = (":" ident)*:args -> (tuple(args)) ;
			rule = ident:name ruleArgs:args "=" alternatives:inner ";"
						-> ('rule', name, args, inner);
			grammar = (rule)+:rules spaces -> (('grammar',) + tuple(rules));
		"""

