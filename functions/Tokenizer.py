# number 0|-?[1-9]\d*
# id [a-z]([a-z]|\d|-)*
# bool #t|#f
# ( ) + - * / mod > < =
# and or not
# print-num print-bool
# define
# fun
# if
class Tokenizer:
	def __init__(self, lines: list):
		self.lines: list = lines


