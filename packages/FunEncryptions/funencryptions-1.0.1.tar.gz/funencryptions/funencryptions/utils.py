# Copyright (C) 2013 Julian Metzler
# See the LICENSE file for the full license.

from funencryptions import algorithms

def _dummy(string, decode = False):
	return string

def chain(string, functions, decode = False):
	"""
	Provides an easy way for applying multiple algorithms to a string without having to nest them in source code.
	"""
	functions = list(functions)
	for i in range(len(functions)):
		if type(functions[i]) in [str, unicode]:
			functions[i] = getattr(algorithms, functions[i], _dummy)
	if decode:
		functions.reverse()
	result = string[:]
	for fn in functions:
		result = fn(result, decode = decode)
	return result

def chunks(string, size):
	for i in range(0, len(string), size):
		yield string[i:i + size]