# -*- coding: utf-8 -*-

## Copyright 2009-2012 by LivingLogic AG, Bayreuth/Germany
## Copyright 2009-2012 by Walter Dörwald
##
## All Rights Reserved
##
## See ll/__init__.py for the license


"""
:mod:`ll.ul4c` provides templating for XML/HTML as well as any other text-based
format. A template defines placeholders for data output and basic logic (like
loops and conditional blocks), that define how the final rendered output will
look.

:mod:`ll.ul4c` compiles a template to an internal format, which makes it
possible to implement template renderers in multiple programming languages.
"""


__docformat__ = "reStructuredText"

import re, ast

from ply import lex

from ll import color, ul4c

# Regular expression used for splitting dates in isoformat
datesplitter = re.compile("[-T:.]")


class LexicalError(Exception):
	def __init__(self, token):
		self.token = token

	def __str__(self):
		return "Illegal token {!r} at position {}".format(self.token.value, self.token.lexpos)


class UnterminatedStringError(Exception):
	"""
	Exception that is raised by the parser when a string constant is not
	terminated.
	"""
	def __str__(self):
		return "Unterminated string"


class Lexer(object):
	def __init__(self, input):
		self.lexer = lex.lex(module=self)
		self.lexer.input(input)

	def token(self):
		token = self.lexer.token()
		if token is None and lexer.lexstate != "INITIAL":
			raise UnterminatedStringError()
		return token

	states = (
		("STR1", "exclusive"), # '-quoted string
		("STR2", "exclusive"), # "-quoted string
	)

	# List of token names
	tokens = (
		"LPAREN",
		"RPAREN",
		"LBRACK",
		"RBRACK",
		"LBRACE",
		"RBRACE",
		"DOT",
		"COMMA",
		"EQEQ",
		"EXCLEQ",
		"LEEQ",
		"LE",
		"GREQ",
		"GR",
		"EQ",
		"PLUSEQ",
		"MINUSEQ",
		"ASTEQ",
		"SLASHSLASHEQ",
		"SLASHEQ",
		"PERCEQ",
		"PERC",
		"COLON",
		"PLUS",
		"MINUS",
		"ASTAST",
		"AST",
		"SLASHSLASH",
		"SLASH",
		"COLOR8",
		"COLOR6",
		"COLOR4",
		"COLOR3",
		"DATE",
		"ID",
		"INT",
		"STR",
		"FLOAT"
	)

	# Reserved keywords
	reserved = {"for", "if", "in", "not", "or", "and", "del", "None", "True", "False"}

	tokens += tuple(keyword.upper() for keyword in reserved)

	# Regular expression rules for simple tokens
	t_LPAREN       = "\\("
	t_RPAREN       = "\\)"
	t_LBRACK       = "\\["
	t_RBRACK       = "\\]"
	t_LBRACE       = "\\{"
	t_RBRACE       = "\\}"
	t_DOT          = "\\."
	t_COMMA        = ","
	t_EQEQ         = "=="
	t_EXCLEQ       = "\\!="
	t_LEEQ         = "<="
	t_LE           = "<"
	t_GREQ         = ">="
	t_GR           = ">"
	t_EQ           = "="
	t_PLUSEQ       = "\\+="
	t_MINUSEQ      = "\\-="
	t_ASTEQ        = "\\*="
	t_SLASHSLASHEQ = "//="
	t_SLASHEQ      = "/="
	t_PERCEQ       = "%="
	t_PERC         = "%"
	t_COLON        = ":"
	t_PLUS         = "\\+"
	t_MINUS        = "-"
	t_ASTAST       = "\\*\\*"
	t_AST          = "\\*"
	t_SLASHSLASH   = "//"
	t_SLASH        = "/"

	@lex.TOKEN("\\#[0-9a-fA-F]{8}")
	def t_COLOR8(self, t):
		t.value = color.Color(int(t.value[1:3], 16), int(t.value[3:5], 16), int(t.value[5:7], 16), int(t.value[7:9], 16))
		return t

	@lex.TOKEN("\\#[0-9a-fA-F]{6}")
	def t_COLOR6(self, t):
		t.value = color.Color(int(t.value[1:3], 16), int(t.value[3:5], 16), int(t.value[5:7], 16))
		return t

	@lex.TOKEN("\\#[0-9a-fA-F]{4}")
	def t_COLOR4(self, t):
		t.value = color.Color(17*int(t.value[1], 16), 17*int(t.value[2], 16), 17*int(t.value[3], 16), 17*int(t.value[4], 16))
		return t

	@lex.TOKEN("\\#[0-9a-fA-F]{3}")
	def t_COLOR3(self, t):
		t.value = color.Color(17*int(t.value[1], 16), 17*int(t.value[2], 16), 17*int(t.value[3], 16))
		return t

	@lex.TOKEN("@\\(\\d{4}-\\d{2}-\\d{2}(T(\\d{2}:\\d{2}(:\\d{2}(\\.\\d{6})?)?)?)?\\)")
	def t_DATE(self, t):
		t.value = datetime.datetime(*map(int, [_f for _f in datesplitter.split(t.value[2:-1]) if _f]))
		return t

	@lex.TOKEN("None")
	def t_NONE(self, t):
		t.value = LoadNone(None)
		return t

	@lex.TOKEN("True")
	def t_TRUE(self, t):
		t.value = LoadTrue(None)
		return t

	@lex.TOKEN("False")
	def t_FALSE(self, t):
		t.value = LoadFalse(None)
		return t

	@lex.TOKEN("[a-zA-Z_][\\w]*")
	def t_ID(self, t):
		if t.value in self.reserved: # Check for reserved words
			t.type = t.value.upper()
		return t

	# We don't have negative numbers, this is handled by constant folding in the AST for unary minus
	@lex.TOKEN("\\d+\\.\\d*([eE][+-]?\\d+)?|\\d+(\\.\\d*)?[eE][+-]?\\d+")
	def t_FLOAT(self, t):
		t.value = float(t.value)
		return t

	@lex.TOKEN("0[xX][\\da-fA-F]+|0[oO][0-7]|0[bB][01]|\\d+")
	def t_INT(self, t):
		t.value = int(t.value, 0)
		return t

	@lex.TOKEN("'")
	def t_BEGINSTR1(self, t):
		t.lexer.collectstr = []
		t.lexer.string_start = t.lexer.lexpos
		t.lexer.begin("STR1")

	@lex.TOKEN('"')
	def t_BEGINSTR2(self, t):
		t.lexer.collectstr = []
		t.lexer.string_start = t.lexer.lexpos
		t.lexer.begin("STR2")

	@lex.TOKEN("\\\\\\\\")
	def t_STR1_ESCAPEDBACKSLASH(self, t):
		t.lexer.collectstr.append("\\")
	t_STR2_ESCAPEDBACKSLASH = t_STR1_ESCAPEDBACKSLASH

	@lex.TOKEN("\\\\'")
	def t_STR1_ESCAPEDAPOS(self, t):
		t.lexer.collectstr.append("'")
	t_STR2_ESCAPEDAPOS = t_STR1_ESCAPEDAPOS

	@lex.TOKEN('\\\\"')
	def t_STR2_ESCAPEDQUOT(self, t):
		t.lexer.collectstr.append('"')
	t_STR2_ESCAPEDQUOT = t_STR1_ESCAPEDQUOT

	@lex.TOKEN("\\\\a")
	def t_STR1_ESCAPEDBELL(self, t):
		t.lexer.collectstr.append("\a")
	t_STR2_ESCAPEDBELL = t_STR1_ESCAPEDBELL

	@lex.TOKEN("\\\\b")
	def t_STR1_ESCAPEDBACKSPACE(self, t):
		t.lexer.collectstr.append("\b")
	t_STR2_ESCAPEDBACKSPACE = t_STR1_ESCAPEDBACKSPACE

	@lex.TOKEN("\\\\f")
	def t_STR1_ESCAPEDFORMFEED(self, t):
		t.lexer.collectstr.append("\f")
	t_STR2_ESCAPEDFORMFEED = t_STR1_ESCAPEDFORMFEED

	@lex.TOKEN("\\\\n")
	def t_STR1_ESCAPEDLINEFEED(self, t):
		t.lexer.collectstr.append("\n")
	t_STR2_ESCAPEDLINEFEED = t_STR1_ESCAPEDLINEFEED

	@lex.TOKEN("\\\\r")
	def t_STR1_ESCAPEDCARRIAGERETURN(self, t):
		t.lexer.collectstr.append("\r")
	t_STR2_ESCAPEDCARRIAGERETURN = t_STR1_ESCAPEDCARRIAGERETURN

	@lex.TOKEN("\\\\t")
	def t_STR1_ESCAPEDTAB(self, t):
		t.lexer.collectstr.append("\t")
	t_STR2_ESCAPEDTAB = t_STR1_ESCAPEDTAB

	@lex.TOKEN("\\\\v")
	def t_STR1_ESCAPEDVERTICALTAB(self, t):
		t.lexer.collectstr.append("\v")
	t_STR2_ESCAPEDVERTICALTAB = t_STR1_ESCAPEDVERTICALTAB

	@lex.TOKEN("\\\\e")
	def t_STR1_ESCAPEDESCAPE(self, t):
		t.lexer.collectstr.append("\x1b")
	t_STR2_ESCAPEDESCAPE = t_STR1_ESCAPEDESCAPE

	@lex.TOKEN("\\\\x[0-9a-fA-F]{2}")
	def t_STR1_ESCAPED8BITCHAR(self, t):
		t.lexer.collectstr.append(chr(int(t.value[2:], 16)))
	t_STR2_ESCAPED8BITCHAR = t_STR1_ESCAPED8BITCHAR

	@lex.TOKEN("\\\\u[0-9a-fA-F]{4}")
	def t_STR1_ESCAPED16BITCHAR(self, t):
		t.lexer.collectstr.append(chr(int(t.value[2:], 16)))
	t_STR2_ESCAPED16BITCHAR = t_STR1_ESCAPED16BITCHAR

	@lex.TOKEN("'")
	def t_STR1_ENDSTR1(self, t):
		t.type = "STR"
		t.value = "".join(t.lexer.collectstr)
		t.lexpos = t.lexer.string_start
		t.lexer.collectstr = None
		t.lexer.begin("INITIAL")
		return t

	@lex.TOKEN('"')
	def t_STR2_ENDSTR2(self, t):
		t.type = "STR"
		t.value = "".join(t.lexer.collectstr)
		t.lexpos = t.lexer.string_start
		t.lexer.collectstr = None
		t.lexer.begin("INITIAL")
		return t

	# Must be after the token for the string end
	@lex.TOKEN(".|\\n")
	def t_STR1_TEXT(self, t):
		t.lexer.collectstr.append(t.value)
	t_STR2_TEXT = t_STR1_TEXT

	# A string containing ignored characters (spaces, tabs, and linefeeds)
	t_INITIAL_ignore = '\r\n \t'

	# Don't ignore anything in string constants
	t_STR1_ignore = t_STR2_ignore = ""

	# Error handling rule
	def t_error(self, t):
		raise LexicalError(t)
	t_STR1_error = t_STR2_error = t_error

