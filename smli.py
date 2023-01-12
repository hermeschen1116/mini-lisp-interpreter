import re
from functools import reduce
from typing import Any

import regex_spm


def parse(token_buffer: list) -> list:
	if len(token_buffer) == 0:
		raise SyntaxError('empty program')
	token: str = token_buffer.pop(0)
	if token == '(':
		parse_buffer: list = []
		while token_buffer[0] != ')':
			parse_buffer.append(parse(token_buffer))
		token_buffer.pop(0)
		return parse_buffer
	elif token == ')':
		raise SyntaxError('unpaired parenthesis')
	else:
		return validator(token)


def validator(token: str) -> Any:
	match token:
		case '+' | '-' | '*' | '/' | '%' | '>' | '<' | '=' | '&' | '|' | '!' | 'if' | 'define' | 'fun' | 'print-num' | 'print-bool' as symbol:
			return symbol
		case '#t' | '#f' as boolean:
			return True if boolean == '#t' else False
		case _ as other:
			match regex_spm.fullmatch_in(other):
				case r'0|\-?[1-9]\d*':
					return int(other)
				case r'[a-z]([a-z]|\d|\-)*':
					return other
				case _:
					raise SyntaxError('illegal word \'{}\''.format(other))


def interpreter(program: list) -> Any:
	variable_table: dict = {}
	for statement in program:
		match statement[0]:
			case 'define':
				statement.pop(0)
				define_statement(statement, variable_table)
			case 'print-num' | 'print-bool' as key_word:
				statement.pop(0)
				if key_word == 'print-num':
					print_num(statement, variable_table)
				else:
					print_boolean(statement, variable_table)
			case _:
				expression(statement, variable_table)


def define_statement(statement: list, variable_table: dict) -> None:
	if len(statement) != 2:
		raise SyntaxError('Need 2 parameters, but got {}'.format(len(statement)))
	variable_table[statement[0]] = expression(statement[1], variable_table)


def print_num(statement: list, variable_table: dict) -> None:
	if len(statement) != 1:
		raise SyntaxError('Need 1 parameters, but got {}'.format(len(statement)))
	exp: Any = expression(statement, variable_table)
	if type(exp) is not int:
		raise TypeError('Not a number')
	print(exp)


def print_boolean(statement: list, variable_table: dict) -> None:
	if len(statement) != 1:
		raise SyntaxError('Need 1 parameters, but got {}'.format(len(statement)))
	exp: Any = expression(statement, variable_table)
	if type(exp) is not bool:
		raise TypeError('Not a boolean')
	print('#t' if exp else '#f')


def expression(statement: Any, variable_table: dict):
	if type(statement) is bool or type(statement) is int:
		return statement
	if type(statement) is str and re.match(r'[a-z][a-z0-9\-]*', statement):
		try:
			return variable_table[statement]
		except KeyError:
			raise KeyError('Variable {} does not exist'.format(statement))
	if type(statement) is list and len(statement) == 0:
		raise SyntaxError('This expression is empty, just like you')
	if type(statement) is list and len(statement) == 1:
		try:
			return expression(statement[0], variable_table)
		except AttributeError:
			pass
	match statement[0]:
		case '+' | '-' | '*' | '/' | '%' | '>' | '<' | '=':
			return number_operation(statement, variable_table)
		case '&' | '|' | '!':
			return logical_operation(statement, variable_table)
		case 'if':
			try:
				return expression(statement[2], variable_table) if expression(statement[1], variable_table) else expression(statement[3], variable_table)
			except KeyError:
				raise SyntaxError('For a if-statement, need 3 expression, but only {} provided'.format(len(statement)))
		case 'fun':
			if len(statement[1]) == 0:
				if type(statement[2]) is not bool and type(statement[2]) is not int:
					raise SyntaxError('Function without parameters perform operation')
				return statement[2]
			return statement[1:]
		case _:
			if statement[0][0] == 'fun':
				fun_buffer: list = expression(statement.pop(0), variable_table)
				return function_call(fun_buffer, statement, variable_table)
			elif type(statement[0]) is str and re.match(r'[a-z][a-z0-9\-]*', statement[0]):
				try:
					return function_call(variable_table[statement.pop(0)], statement, variable_table)
				except KeyError:
					raise KeyError('Function {} does not exist'.format(statement[0]))
			else:
				raise SyntaxError("Invalid expression")


def number_operation(statement: list, variable_table: dict) -> int:
	if type(statement) is not list:
		raise SyntaxError('Need 2 or more parameters, got 1')
	operator = statement.pop(0)
	statement: list = [expression(s, variable_table) for s in statement]
	for s in statement:
		if type(s) is not int:
			raise TypeError('There a spy among us')
	num_parameter: int = len(statement)
	if operator == '+' or operator == '*' or operator == '=':
		if num_parameter < 2:
			raise SyntaxError('Need 2 or more parameters, got {}'.format(num_parameter))
		match operator:
			case '+':
				return sum(statement)
			case '*':
				return reduce((lambda x, y: x * y), statement)
			case '=':
				return reduce((lambda x, y: x == y), statement)
	if num_parameter != 2:
		raise SyntaxError('Need 2 parameters, got {}'.format(num_parameter))
	match operator:
		case '-':
			return statement[0] - statement[1]
		case '/':
			return statement[0] // statement[1]
		case '%':
			return statement[0] % statement[1]
		case '>':
			return statement[0] > statement[1]
		case '<':
			return statement[0] < statement[1]


def logical_operation(statement: list, variable_table: dict) -> int:
	operator = statement.pop(0)
	statement: list = [expression(s, variable_table) for s in statement]
	for s in statement:
		if type(s) is not bool:
			raise TypeError('There a spy among us')
	num_parameter: int = len(statement)
	if operator == '!':
		if num_parameter != 1:
			raise SyntaxError('Need only 1 parameters, got {}'.format(num_parameter))
		return not statement[0]
	if num_parameter < 2:
		raise SyntaxError('Need 2 parameters, got {}'.format(num_parameter))
	match operator:
		case '&':
			return reduce((lambda x, y: x and y), statement)
		case '|':
			return reduce((lambda x, y: x or y), statement)


def function_call(target_function: list, parameters: list, variable_table: dict):
	arg, exp = target_function
	if len(arg) != len(parameters):
		raise SyntaxError('Number of parameters is wrong')
	try:
		parameters: list = [expression(p, variable_table) for p in parameters]
	except KeyError:
		raise KeyError('Variable does not exist')
	arg: dict = dict(zip(arg, parameters))
	return expression(exp, arg)


program_buffer: str = ''

# get program content
while True:
	try:
		line_buffer: str = input().strip('\n').strip(' ')
		if line_buffer == '':
			continue
		program_buffer += line_buffer
		if line_buffer[-1] != '(' and line_buffer[-1] != ')':
			program_buffer += ' '
	except EOFError:
		break

# tokenize
tokens: list = program_buffer.replace('mod', '%').replace('and', '&').replace('or', '|').replace('not', '!').replace('(', ' ( ').replace(')',
                                                                                                                                         ' ) ').split()

# parse
parse_program: list = [parse(tokens)]
while len(tokens) != 0:
	parse_program.append(parse(tokens))
# interpreter
interpreter(parse_program)
