# Copyright (C) 2013 Julian Metzler
# See the LICENSE file for the full license.

def character_code_neighbor_sum(string, decode = False):
	"""
	Replaces the characters in the string with Unicode characters by adding the character codes of adjacent characters.
	"""
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

def backwards_interleave(string, decode = False):
	"""
	Interleaves the string with a backwards copy of itself. Decoding is the same process as encoding.
	"""
	result = u""
	length = len(string)
	remainder = divmod(length, 2)[1]
	forward = "".join([string[i] for i in range(0, length, 2)])
	backward = "".join([string[::-1][i] for i in range(remainder, length, 2)])
	if remainder:
		backward += " "
	result = u"".join([forward[i] + backward[i] for i in range(len(forward))])
	if remainder:
		result = result[:-1]
	return result

def character_code_timestamp_date(string, decode = False, fmt = "%d.%m.%Y %H:%M:%S"):
	"""
	Concatenates the character codes of the string and treats them like UNIX timestamps.
	"""
	from datetime import datetime
	from funencryptions.utils import chunks
	import time
	result = u""
	length = len(string)
	if decode:
		timestamps = [str(int(time.mktime(datetime.strptime(line, fmt).timetuple()) + 2147483648)) for line in string.splitlines()]
		codes = []
		for timestamp in timestamps:
			count = int(timestamp[0])
			codes += [int(chunk) for chunk in chunks(timestamp[1:], len(timestamp[1:]) / count)]
		result = u"".join([unichr(code) for code in codes])
	else:
		codes = [str(ord(char)) for char in string]
		i = 0
		while i < length:
			cat = []
			_tmp = codes[i]
			while len("".join(cat) + _tmp) < 9:
				cat.append(_tmp)
				cat = [entry.rjust(max([len(item) for item in cat]), "0") for entry in cat]
				if len("".join(cat)) > 9:
					while len("".join(cat)) > 9:
						cat.pop()
						i -= 1
					break
				i += 1
				if i >= length:
					break
				_tmp = codes[i]
			cat = str(len(cat)) + "".join(cat)
			result += time.strftime(fmt, time.localtime(-2147483648 + int(cat))) + "\n"
	return result