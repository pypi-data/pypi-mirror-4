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

def int_to_rgb(integer):
	assert integer <= 0xFFFFFF
	assert integer >= 0x000000
	hexa = hex(integer)[2:].rjust(6, "0")
	r, g, b = [int(chunk, 16) for chunk in chunks(hexa, 2)]
	return r, g, b

def rgb_to_int(r, g, b):
	assert r >= 0
	assert r <= 255
	assert g >= 0
	assert g <= 255
	assert b >= 0
	assert b <= 255
	hexa = hex(r)[2:] + hex(g)[2:] + hex(b)[2:]
	integer = int(hexa, 16)
	return integer