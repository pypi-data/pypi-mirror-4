# Copyright (C) 2013 Julian Metzler
# See the LICENSE file for the full license.

"""
This file contains algorithms that convert strings to images and back. They return an image file object.
They do not take a 'decode' parameter since they will automatically decode if the source data in an image.
"""

from funencryptions.utils import int_to_rgb, rgb_to_int, chunks
from PIL import Image, ImageDraw
from tempfile import NamedTemporaryFile
import math

def character_code_color_bar(source, height = 1, segment_width = 1):
	"""
	Treats the string's characters' codes as hexadecimal color values and makes a colorful bar out of them.
	"""
	decode = type(source) is file
	result = None
	if decode:
		im = Image.open(source)
		pixels = im.load()
		width, height = im.size
		length = width / segment_width
		codes = []
		for i in range(length):
			codes.append(rgb_to_int(*pixels[i * segment_width, 0][:3]))
		result = u"".join([unichr(code) for code in codes])
	else:
		length = len(source)
		width = length * segment_width
		size = (width, height)
		im = Image.new('RGBA', size, (0, 0, 0, 0))
		draw = ImageDraw.Draw(im)
		codes = [ord(char) for char in source]
		for i in range(length):
			color = int_to_rgb(codes[i])
			draw.rectangle(((i * segment_width, 0), ((i + 1) * segment_width, height)), outline = color, fill = color)
		f = NamedTemporaryFile(suffix = ".png", delete = False)
		im.save(f, "PNG")
		f.flush()
		f.close()
		result = open(f.name, 'r')
	return result

def character_code_color_matrix(source, segments_per_row = None, max_width = None, segment_width = 1, segment_height = 1):
	"""
	Treats the string's characters' codes as hexadecimal color values and makes a colorful matrix out of them.
	"""
	decode = type(source) is file
	result = None
	if decode:
		im = Image.open(source)
		pixels = im.load()
		width, height = im.size
		rows = height / segment_height
		cols = width / segment_width
		codes = []
		for y in range(rows):
			codes.append([])
			for x in range(cols):
				if pixels[x * segment_width, y * segment_height][3] == 0:
					continue
				codes[y].append(rgb_to_int(*pixels[x * segment_width, y * segment_height][:3]))
		result = u"".join([u"".join([unichr(c) for c in code]) for code in codes])
	else:
		length = len(source)
		if segments_per_row:
			cols = segments_per_row
		elif max_width:
			cols = divmod(max_width, segment_width)[0]
		rows = int(math.ceil(length / float(cols)))
		width = cols * segment_width
		height = rows * segment_height
		size = (width, height)
		im = Image.new('RGBA', size, (0, 0, 0, 0))
		draw = ImageDraw.Draw(im)
		codes = [ord(char) for char in source]
		for y in range(rows):
			x = 0
			for code in codes[y * cols:(y + 1) * cols]:
				color = int_to_rgb(code)
				draw.rectangle(((x * segment_width, y * segment_height), ((x + 1) * segment_width - 1, (y + 1) * segment_height - 1)), outline = color, fill = color)
				x += 1
		f = NamedTemporaryFile(suffix = ".png", delete = False)
		im.save(f, "PNG")
		f.flush()
		f.close()
		result = open(f.name, 'r')
	return result