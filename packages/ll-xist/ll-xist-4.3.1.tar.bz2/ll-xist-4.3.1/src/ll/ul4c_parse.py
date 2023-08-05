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

from ply import parse

from ll import color, ul4c
from ll import ul4c_lex

class ExprParser(object):
	emptyerror = "expression required"
	start = "expr0"

	def __init__(self, input):
		self.input = input

	def compile(self, location):
		self.location = location
		if not location.code:
			raise ValueError(self.emptyerror)
		try:
			parser = yacc.yacc(module=self)
			return parser.parse(s. lexer=ul4c_lex.Lexer(self.info)))
		except Exception as exc:
			raise Error(location) from exc

	def makeconst(self, value):
		if value is None:
			return None_(self.location)
		elif value is True:
			return True_(self.location)
		elif value is False:
			return False_(self.location)
		elif isinstance(value, int):
			return Int(self.location, value)
		elif isinstance(value, float):
			return Float(self.location, value)
		elif isinstance(value, str):
			return Str(self.location, value)
		elif isinstance(value, color.Color):
			return Color(self.location, value)
		else:
			raise TypeError("can't convert {!r}".format(value))

	# To implement operator precedence, each expression rule has the precedence in its name. The highest precedence is 11 for atomic expressions.
	# Each expression can have only expressions as parts which have the some or a higher precedence with two exceptions:
	#    1. Expressions where there's no ambiguity, like the index for a getitem/getslice or function/method arguments;
	#    2. Brackets, which can be used to boost the precedence of an expression to the level of an atomic expression.

	def p_expr_none(self, p):
		"expr : NONE"
		p[0] = ul4c.LoadNone(self.location)

	def p_expr_true(self, p):
		"expr : TRUE"
		p[0] = ul4c.LoadTrue(self.location)

	def p_expr_false(self, p):
		"expr : FALSE"
		p[0] = ul4c.LoadFalse(self.location)

	def p_expr_int(self, p):
		"expr : INT"
		p[0] = ul4c.LoadInt(self.location, p[1].value)

	def p_expr_float(self, p):
		"expr : FLOAT"
		p[0] = ul4c.LoadFloat(self.location, p[1].value)

	def p_expr_str(self, p):
		"expr : STR"
		p[0] = ul4c.LoadStr(self.location, p[1].value)

	def p_expr_date(self, p):
		"expr : DATE"
		p[0] = ul4c.LoadDate(self.location, p[1].value)

	def p_expr_color(self, p):
		"expr : COLOR"
		p[0] = ul4c.LoadColor(self.location, p[1].value)

	def p_expr_id(self, p):
		"expr : ID"
		p[0] = ul4c.Var(self.location, p[1].value)

	def p_nestedname(self, p):
		"nestedname : ID"
		p[0] = p[1].value

	def p_nestedname1(self, p):
		"nestedname : LPAREN nestedname COMMA RPAREN"
		p[0] = (p[1],)

	def p_buildnestedname(self, p):
		"buildnestedname : LPAREN nestedname COMMA nestedname"
		p[0] = (p[1], p[3])

	def p_addnestedname(self, p):
		"buildnestedname : buildnestedname COMMA nestedname"
		p[0] = p[1] + (p[3],)

	def p_finishnestedname0(self, p):
		"nestedname : buildnestedname RPAREN"
		p[0] = p[1]

	def p_finishnestedname1(self, buildname, _0, _1):
		"nestedname : buildnestedname COMMA RPAREN"
		p[0] = p[1]

	def p_expr_emptylist(self, p):
		"expr : LBRACK RBRACK"
		p[0] = ul4c.List(self.location)

	def p_expr_buildlist(self, p):
		"buildlist : LBRACK expr"
		p[0] = ul4c.List(self.location, p[1])

	def p_expr_addlist(self, list, _0, expr):
		"buildlist ::= buildlist COMMA expr"
		p[1].items.append(p[2])
		p[0] = p[1]

	@spark.production('expr11 ::= buildlist ]')
	def expr_finishlist(self, list, _0):
		return list

	@spark.production('expr11 ::= buildlist , ]')
	def expr_finishlist1(self, list, _0, _1):
		return list

	@spark.production('expr11 ::= [ expr0 for nestedname in expr0 ]')
	def expr_listcomp0(self, _0, item, _1, varname, _2, container, _3):
		return ListComp(self.location, item, varname, container)

	@spark.production('expr11 ::= [ expr0 for nestedname in expr0 if expr0 ]')
	def expr_listcomp1(self, _0, item, _1, varname, _2, container, _3, condition, _4):
		return ListComp(self.location, item, varname, container, condition)

	@spark.production('expr11 ::= { }')
	def expr_emptydict(self, _0, _1):
		return Dict(self.location)

	@spark.production('builddict ::= { expr0 : expr0')
	def expr_builddict(self, _0, exprkey, _1, exprvalue):
		return Dict(self.location, (exprkey, exprvalue))

	@spark.production('builddict ::= { ** expr0')
	def expr_builddictupdate(self, _0, _1, expr):
		return Dict(self.location, (expr,))

	@spark.production('builddict ::= builddict , expr0 : expr0')
	def expr_adddict(self, dict, _0, exprkey, _1, exprvalue):
		dict.items.append((exprkey, exprvalue))
		return dict

	@spark.production('builddict ::= builddict , ** expr0')
	def expr_updatedict(self, dict, _0, _1, expr):
		dict.items.append((expr,))
		return dict

	@spark.production('expr11 ::= builddict }')
	def expr_finishdict(self, dict, _0):
		return dict

	@spark.production('expr11 ::= builddict , }')
	def expr_finishdict1(self, dict, _0, _1):
		return dict

	@spark.production('expr11 ::= { expr0 : expr0 for nestedname in expr0 }')
	def expr_dictcomp0(self, _0, key, _1, value, _2, varname, _3, container, _4):
		return DictComp(self.location, key, value, varname, container)

	@spark.production('expr11 ::= { expr0 : expr0 for nestedname in expr0 if expr0 }')
	def expr_dictcomp1(self, _0, key, _1, value, _2, varname, _3, container, _4, condition, _5):
		return DictComp(self.location, key, value, varname, container, condition)

	@spark.production('expr11 ::= ( expr0 for nestedname in expr0 )')
	def expr_genexp0(self, _0, item, _1, varname, _2, container, _3):
		return GenExpr(self.location, item, varname, container)

	@spark.production('expr11 ::= ( expr0 for nestedname in expr0 if expr0 )')
	def expr_genexp1(self, _0, item, _1, varname, _2, container, _3, condition, _4):
		return GenExpr(self.location, item, varname, container, condition)

	@spark.production('exprarg ::= expr0')
	def expr_arg(self, expr):
		return expr

	@spark.production('exprarg ::= expr0 for nestedname in expr0')
	def expr_arg_genexp0(self, item, _0, varname, _1, container):
		return GenExpr(self.location, item, varname, container)

	@spark.production('exprarg ::= expr0 for nestedname in expr0 if expr0')
	def expr_arg_genexp1(self, item, _0, varname, _1, container, _2, condition):
		return GenExpr(self.location, item, varname, container, condition)

	@spark.production('expr11 ::= ( expr0 )')
	def expr_bracket(self, _0, expr, _1):
		return expr

	@spark.production('expr10 ::= var ( )')
	def expr_callfunc0(self, var, _0, _1):
		return CallFunc(self.location, var.name)

	@spark.production('buildfunccall ::= var ( exprarg')
	def expr_buildcallfunc(self, var, _0, arg):
		return CallFunc(self.location, var.name, arg)

	@spark.production('buildfunccall ::= buildfunccall , exprarg')
	def expr_addcallfunc(self, funccall, _0, arg):
		funccall.args.append(arg)
		return funccall

	@spark.production('expr10 ::= buildfunccall )')
	def expr_finishcallfunc0(self, funccall, _0):
		return funccall

	@spark.production('expr10 ::= buildfunccall , )')
	def expr_finishcallfunc1(self, funccall, _0, _1):
		return funccall

	@spark.production('expr9 ::= expr9 . var')
	def expr_getattr(self, expr, _0, var):
		return GetAttr(self.location, expr, var.name)

	@spark.production('expr9 ::= expr9 . var ( )')
	def expr_callmeth0(self, expr, _0, var, _1, _2):
		return CallMeth(self.location, var.name, expr)

	@spark.production('expr9 ::= expr9 . var ( exprarg )')
	def expr_callmeth1(self, expr, _0, var, _1, arg1, _2):
		return CallMeth(self.location, var.name, expr, arg1)

	@spark.production('expr9 ::= expr9 . var ( exprarg , exprarg )')
	def expr_callmeth2(self, expr, _0, var, _1, arg1, _2, arg2, _3):
		return CallMeth(self.location, var.name, expr, arg1, arg2)

	@spark.production('expr9 ::= expr9 . var ( exprarg , exprarg , exprarg )')
	def expr_callmeth3(self, expr, _0, var, _1, arg1, _2, arg2, _3, arg3, _4):
		return CallMeth(self.location, var.name, expr, arg1, arg2, arg3)

	@spark.production('callmethkw ::= expr9 . var ( var = exprarg')
	def methkw_startname(self, expr, _0, methname, _1, argname, _2, argvalue):
		return CallMethKeywords(self.location, methname.name, expr, (argname.name, argvalue))

	@spark.production('callmethkw ::= expr9 . var ( ** exprarg')
	def methkw_startdict(self, expr, _0, methname, _1, _2, argvalue):
		return CallMethKeywords(self.location, methname.name, expr, (argvalue,))

	@spark.production('callmethkw ::= callmethkw , var = exprarg')
	def methkw_buildname(self, call, _0, argname, _1, argvalue):
		call.args.append((argname.name, argvalue))
		return call

	@spark.production('callmethkw ::= callmethkw , ** exprarg')
	def methkw_builddict(self, call, _0, _1, argvalue):
		call.args.append((argvalue,))
		return call

	@spark.production('expr9 ::= callmethkw )')
	def methkw_finish(self, call, _0):
		return call

	@spark.production('expr9 ::= expr9 [ expr0 ]')
	def expr_getitem(self, expr, _0, key, _1):
		if isinstance(expr, Const) and isinstance(key, Const): # Constant folding
			return self.makeconst(expr.value[key.value])
		return GetItem(self.location, expr, key)

	@spark.production('expr8 ::= expr8 [ expr0 : expr0 ]')
	def expr_getslice12(self, expr, _0, index1, _1, index2, _2):
		if isinstance(expr, Const) and isinstance(index1, Const) and isinstance(index2, Const): # Constant folding
			return self.makeconst(expr.value[index1.value:index2.value])
		return GetSlice(self.location, expr, index1, index2)

	@spark.production('expr8 ::= expr8 [ expr0 : ]')
	def expr_getslice1(self, expr, _0, index1, _1, _2):
		if isinstance(expr, Const) and isinstance(index1, Const): # Constant folding
			return self.makeconst(expr.value[index1.value:])
		return GetSlice(self.location, expr, index1, None)

	@spark.production('expr8 ::= expr8 [ : expr0 ]')
	def expr_getslice2(self, expr, _0, _1, index2, _2):
		if isinstance(expr, Const) and isinstance(index2, Const): # Constant folding
			return self.makeconst(expr.value[:index2.value])
		return GetSlice(self.location, expr, None, index2)

	@spark.production('expr8 ::= expr8 [ : ]')
	def expr_getslice(self, expr, _0, _1, _2):
		if isinstance(expr, Const): # Constant folding
			return self.makeconst(expr.value[:])
		return GetSlice(self.location, expr, None, None)

	@spark.production('expr7 ::= - expr7')
	def expr_neg(self, _0, expr):
		if isinstance(expr, Const): # Constant folding
			return self.makeconst(-expr.value)
		return Neg(self.location, expr)

	@spark.production('expr6 ::= expr6 * expr6')
	def expr_mul(self, obj1, _0, obj2):
		if isinstance(obj1, Const) and isinstance(obj2, Const): # Constant folding
			return self.makeconst(obj1.value * obj2.value)
		return Mul(self.location, obj1, obj2)

	@spark.production('expr6 ::= expr6 // expr6')
	def expr_floordiv(self, obj1, _0, obj2):
		if isinstance(obj1, Const) and isinstance(obj2, Const): # Constant folding
			return self.makeconst(obj1.value // obj2.value)
		return FloorDiv(self.location, obj1, obj2)

	@spark.production('expr6 ::= expr6 / expr6')
	def expr_truediv(self, obj1, _0, obj2):
		if isinstance(obj1, Const) and isinstance(obj2, Const): # Constant folding
			return self.makeconst(obj1.value / obj2.value)
		return TrueDiv(self.location, obj1, obj2)

	@spark.production('expr6 ::= expr6 % expr6')
	def expr_mod(self, obj1, _0, obj2):
		if isinstance(obj1, Const) and isinstance(obj2, Const): # Constant folding
			return self.makeconst(obj1.value % obj2.value)
		return Mod(self.location, obj1, obj2)

	@spark.production('expr5 ::= expr5 + expr5')
	def expr_add(self, obj1, _0, obj2):
		if isinstance(obj1, Const) and isinstance(obj2, Const): # Constant folding
			return self.makeconst(obj1.value + obj2.value)
		return Add(self.location, obj1, obj2)

	@spark.production('expr5 ::= expr5 - expr5')
	def expr_sub(self, obj1, _0, obj2):
		if isinstance(obj1, Const) and isinstance(obj2, Const): # Constant folding
			return self.makeconst(obj1.value - obj2.value)
		return Sub(self.location, obj1, obj2)

	@spark.production('expr4 ::= expr4 == expr4')
	def expr_eq(self, obj1, _0, obj2):
		if isinstance(obj1, Const) and isinstance(obj2, Const): # Constant folding
			return self.makeconst(obj1.value == obj2.value)
		return EQ(self.location, obj1, obj2)

	@spark.production('expr4 ::= expr4 != expr4')
	def expr_ne(self, obj1, _0, obj2):
		if isinstance(obj1, Const) and isinstance(obj2, Const): # Constant folding
			return self.makeconst(obj1.value != obj2.value)
		return NE(self.location, obj1, obj2)

	@spark.production('expr4 ::= expr4 < expr4')
	def expr_lt(self, obj1, _0, obj2):
		if isinstance(obj1, Const) and isinstance(obj2, Const): # Constant folding
			return self.makeconst(obj1.value < obj2.value)
		return LT(self.location, obj1, obj2)

	@spark.production('expr4 ::= expr4 <= expr4')
	def expr_le(self, obj1, _0, obj2):
		if isinstance(obj1, Const) and isinstance(obj2, Const): # Constant folding
			return self.makeconst(obj1.value <= obj2.value)
		return LE(self.location, obj1, obj2)

	@spark.production('expr4 ::= expr4 > expr4')
	def expr_gt(self, obj1, _0, obj2):
		if isinstance(obj1, Const) and isinstance(obj2, Const): # Constant folding
			return self.makeconst(obj1.value > obj2.value)
		return GT(self.location, obj1, obj2)

	@spark.production('expr4 ::= expr4 >= expr4')
	def expr_ge(self, obj1, _0, obj2):
		if isinstance(obj1, Const) and isinstance(obj2, Const): # Constant folding
			return self.makeconst(obj1.value >= obj2.value)
		return GE(self.location, obj1, obj2)

	@spark.production('expr3 ::= expr3 in expr3')
	def expr_contains(self, obj, _0, container):
		if isinstance(obj, Const) and isinstance(container, Const): # Constant folding
			return self.makeconst(obj.value in container.value)
		return Contains(self.location, obj, container)

	@spark.production('expr3 ::= expr3 not in expr3')
	def expr_notcontains(self, obj, _0, _1, container):
		if isinstance(obj, Const) and isinstance(container, Const): # Constant folding
			return self.makeconst(obj.value not in container.value)
		return NotContains(self.location, obj, container)

	@spark.production('expr2 ::= not expr2')
	def expr_not(self, _0, expr):
		if isinstance(expr, Const): # Constant folding
			return self.makeconst(not expr.value)
		return Not(self.location, expr)

	@spark.production('expr1 ::= expr1 and expr1')
	def expr_and(self, obj1, _0, obj2):
		if isinstance(obj1, Const) and isinstance(obj2, Const): # Constant folding
			return self.makeconst(obj1.value and obj2.value)
		return And(self.location, obj1, obj2)

	@spark.production('expr0 ::= expr0 or expr0')
	def expr_or(self, obj1, _0, obj2):
		if isinstance(obj1, Const) and isinstance(obj2, Const): # Constant folding
			return self.makeconst(obj1.value or obj2.value)
		return Or(self.location, obj1, obj2)

	# These rules make operators of different precedences interoperable, by allowing an expression to "drop" its precedence.
	@spark.production('expr10 ::= expr11')
	@spark.production('expr9 ::= expr10')
	@spark.production('expr8 ::= expr9')
	@spark.production('expr7 ::= expr8')
	@spark.production('expr6 ::= expr7')
	@spark.production('expr5 ::= expr6')
	@spark.production('expr4 ::= expr5')
	@spark.production('expr3 ::= expr4')
	@spark.production('expr2 ::= expr3')
	@spark.production('expr1 ::= expr2')
	@spark.production('expr0 ::= expr1')
	def expr_dropprecedence(self, expr):
		return expr


class ForParser(ExprParser):
	emptyerror = "loop expression required"
	start = "for"

	@spark.production('for ::= nestedname in expr0')
	def for_(self, name, _0, cont):
		return For(self.location, name, cont)


class StmtParser(ExprParser):
	emptyerror = "statement required"
	start = "stmt"

	@spark.production('stmt ::= nestedname = expr0')
	def stmt_assign(self, name, _0, value):
		return StoreVar(self.location, name, value)

	@spark.production('stmt ::= var += expr0')
	def stmt_iadd(self, var, _0, value):
		return AddVar(self.location, var.name, value)

	@spark.production('stmt ::= var -= expr0')
	def stmt_isub(self, var, _0, value):
		return SubVar(self.location, var.name, value)

	@spark.production('stmt ::= var *= expr0')
	def stmt_imul(self, var, _0, value):
		return MulVar(self.location, var.name, value)

	@spark.production('stmt ::= var /= expr0')
	def stmt_itruediv(self, var, _0, value):
		return TrueDivVar(self.location, var.name, value)

	@spark.production('stmt ::= var //= expr0')
	def stmt_ifloordiv(self, var, _0, value):
		return FloorDivVar(self.location, var.name, value)

	@spark.production('stmt ::= var %= expr0')
	def stmt_imod(self, var, _0, value):
		return ModVar(self.location, var.name, value)

	@spark.production('stmt ::= del var')
	def stmt_del(self, _0, var):
		return DelVar(self.location, var.name)
