# Copyright (C) 2013 Julian Metzler
# See the LICENSE file for the full license.

def character_code_neighbor_sum(string, decode = False):
	result = u""
	length = len(string)
	step = 1
	if decode:
		assert length >= 2
		first = string[-1]
		result += first
		for i in range(length):
			next = unichr(ord(string[i]) - ord(result[i]))
			result += next
		result = result[:len(result) - 2]
	else:
		for i in range(length):
			char = string[i]
			neighbor = string[i + step] if i < length - step else string[i - length + step]
			result += unichr(ord(char) + ord(neighbor))
		if length > 0:
			result += string[0]
	return result