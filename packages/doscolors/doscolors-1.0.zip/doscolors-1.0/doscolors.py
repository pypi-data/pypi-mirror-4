from ctypes import *

# Inspired by and stolen from:
# http://www.burgaud.com/bring-colors-to-the-windows-console-with-python/
# Thanks, I had no idea on how to use structs in python for interop.
SHORT = c_short
WORD = c_ushort

class COORD(Structure):
	"""Defines the coordinates of a character cell in a console screen buffer. The origin of the coordinate system (0,0) is at the top, left cell of the buffer..
	See http://msdn.microsoft.com/en-us/library/windows/desktop/ms682119(v=vs.85).aspx
	Taken from http://www.burgaud.com/bring-colors-to-the-windows-console-with-python/"""
	_fields_ = [
	("X", SHORT),
	("Y", SHORT)]

class SMALL_RECT(Structure):
	"""Struct that defines the coordinates of the upper left and lower right corners of a rectangle.
	See http://msdn.microsoft.com/en-us/library/windows/desktop/ms686311(v=vs.85).aspx 
	Taken from http://www.burgaud.com/bring-colors-to-the-windows-console-with-python/"""
	_fields_ = [
	("Left", SHORT),
	("Top", SHORT),
	("Right", SHORT),
	("Bottom", SHORT)]

class CONSOLE_SCREEN_BUFFER_INFO(Structure):
	"""Struct that contains information about a console screen buffer. Important for us is that itcontains the colors of the console (wAttributes). Defined in wincon.h.
	See http://msdn.microsoft.com/en-us/library/windows/desktop/ms682093(v=vs.85).aspx.
	Taken from http://www.burgaud.com/bring-colors-to-the-windows-console-with-python/"""
	_fields_ = [
	("dwSize", COORD),
	("dwCursorPosition", COORD),
	("wAttributes", WORD),
	("srWindow", SMALL_RECT),
	("dwMaximumWindowSize", COORD)]

windll.Kernel32.GetStdHandle.restype = c_ulong
stdout_handle = windll.Kernel32.GetStdHandle(c_ulong(0xfffffff5))

def get_console_colors():
	'''Gets the colors of the console
		See http://msdn.microsoft.com/en-us/library/windows/desktop/ms683171(v=vs.85).aspx'''
	csbi = CONSOLE_SCREEN_BUFFER_INFO()
	windll.Kernel32.GetConsoleScreenBufferInfo(stdout_handle, byref(csbi))
	return csbi.wAttributes 

def set_console_colors(colors):
	'''Sets the colors of the console
		See http://msdn.microsoft.com/en-us/library/windows/desktop/ms686047(v=vs.85).aspx'''
	windll.Kernel32.SetConsoleTextAttribute(stdout_handle, colors)

def combine(foreground,background):
	'''Combines two colors to be used as wAttributes, eg. combine(red, blue). Background colors are just like foreground colors but at a different position. See http://msdn.microsoft.com/en-us/library/windows/desktop/ms686047(v=vs.85).aspx for further details.'''
	return foreground | (background << 4)

def current_color():
	'''Returns the current colors (wAttributes including foreground and background)'''
	return get_console_colors()

def current_background():
	'''Returns the current background color'''
	colors = get_console_colors()
	return background_from(colors)

def background_from(colors):
	'''Parses the background from wAttributes'''
	return colors & 0x0070

def foreground_from(colors):
	'''Parses the foreground from wAttributes'''
	return colors & 0x0007

def reset():
	'''Resets the color to the default_color. The default_color is initialized upon import. Use current_color() to update the default color.'''
	global default_color
	set_console_colors(default_color)

def make_default(color):
	global default_color
	default_color = color

def color(foreground, background):
	colors = combine(foreground, background)
	set_console_colors(colors)

def colored(foreground,background):
	def decorate(function):
		def wrap(*args, **kwargs):
			default = current_color()
			color(foreground, background)
			result = function(*args,**kwargs)
			set_console_colors(default)
			return result
		return wrap
	return decorate

def background(bgcolor):
	def decorate(function):
		def wrap(*args, **kwargs):
			default = current_color()
			fgcolor = foreground_from(default)
			color(fgcolor, bgcolor)
			result = function(*args,**kwargs)
			set_console_colors(default)
			return result
		return wrap
	return decorate

def foreground(fgcolor):
	def decorate(function):
		def wrap(*args, **kwargs):
			default = current_color()
			bg = background_from(default)
			color(fgcolor, bg)
			result = function(*args,**kwargs)
			set_console_colors(default)
			return result
		return wrap
	return decorate

b = 1
g = 2
r = 4
a = 8

class Colors(object):
	black = 0
	darkred = r
	darkgreen = g
	darkblue = b
	red 	= r|a
	green 	= g|a
	blue 	= b|a
	gray 	= r|g|b
	white 	= r|g|b | a
	ocre 	= r|g
	yellow 	= r|g 	| a
	purple 	= r|b
	pink 	= r|b   | a
	cyan 	= b|g
	lightcyan = b|g|a
	lightblue = lightcyan
	lime = green
	bordeaux = darkred
	navy = darkblue

default_color = current_color()

__all__ = ["background",
	"default_color",
	"color",
	"colored", 
	"Colors",
	"combine",
	"current_background",
	"current_color", 
	"foreground", 
	"make_default",
	"reset"]