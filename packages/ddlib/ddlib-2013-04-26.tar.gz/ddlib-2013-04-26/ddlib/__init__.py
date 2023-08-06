#-*- coding: utf-8 -*-

import sys
import random
import datetime





def log(s, level='', name=''):
	if name:
		level = ('%s\t%s' % (level, name)).strip()

	level = '\t%s'%level if level else ''

	print('%s%s\t%s' % (datetime.datetime.now(), level, s))
	sys.stdout.flush()


def log_debug(s):
	log(s, 'DEBUG')


def log_info(s):
	log(s, 'INFO')


def log_error(s):
	log(s, 'ERROR')






def gets(txt, begin, end=None):
	"""
		Gets some text between <begin> and <end> of <txt>.

		eg:
		>>> out = gets('This is sample text.', ' is ', ' text.')
		>>> print(out)
		'sample'

	"""
	out = None
	b = txt.find(begin)
	if b != -1:
		out = txt[b+len(begin):]
		if end:
			e = out.find(end)
			if e != -1:
				out = out[:e]

	return out





def random_string(dlugosc=10, dozwolone_znaki='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'):
	"""
		Generator losowych ciągłów znaków o wyznaczonej długości.
		Może zostać wykorzystany jako np: generator haseł.

		Arguments:
			dlugosc -- <int> długość wynikowego ciągu znaków
			dozwolone_znaki -- <str> ciąg znaków jakie zostaną użyte

		Return:
			<str> losowy ciag znaków o długości `dlugosc` stworzony ze znaków `dozwolone_znaki`

		Example:
			a = random_string(12)
			print(a)
	"""
	return ''.join(random.choice(dozwolone_znaki) for x in range(dlugosc))