#!/usr/bin/python
 #-
 # Copyright (c) 2013 Clint Banis (hereby known as "The Author")
 # All rights reserved.
 #
 # Redistribution and use in source and binary forms, with or without
 # modification, are permitted provided that the following conditions
 # are met:
 # 1. Redistributions of source code must retain the above copyright
 #    notice, this list of conditions and the following disclaimer.
 # 2. Redistributions in binary form must reproduce the above copyright
 #    notice, this list of conditions and the following disclaimer in the
 #    documentation and/or other materials provided with the distribution.
 # 3. All advertising materials mentioning features or use of this software
 #    must display the following acknowledgement:
 #        This product includes software developed by The Author, Clint Banis.
 # 4. The name of The Author may not be used to endorse or promote products
 #    derived from this software without specific prior written permission.
 #
 # THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS
 # ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
 # TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 # PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS
 # BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 # CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 # SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 # INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 # CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 # ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 # POSSIBILITY OF SUCH DAMAGE.
 #
"Display options for Pythonified rent file."

from pdb import set_trace as debug
from time import ctime

from constants import *
from scan import *

def toCString(n):
	i=n.find('\000')
	if i!=-1:
		return n[:i]
	return n

def prepstr(n, width=25):
	def prepstr(n, width=width):
		n=toCString(n)
		if len(n)>width:
			n=n[:width]
		return n

	return prepstr

class Item:
	def wearpos(wear):
		return wearPositions.get(wear, '#%d' % wear)
	wearpos=staticmethod(wearpos)

	def typename(type):
		return itemTypes.get(type, '#%d' % type)
	typename=staticmethod(typename)

	MemberNames=('vnum', 'name', 'longdescr', 'shortdescr', 'wear',
		'value1', 'value2', 'value3', 'value4', 'type',
		'extraflags', 'antiflags', 'wearflags',
		'weight', 'timer', 'bitvector',
		'affection1', 'affection2', 'affection3',
		'affection4', 'affection5', 'affection6')

	def __init__(self, item):
		filters=[None] +[toCString]*3 +[Item.wearpos] +[None]*4 +[Item.typename] +[None]*12

		for k, v, f in zip(Item.MemberNames, item, filters):
			if f:
				v=f(v)

			setattr(self, k, v)

	def __str__(self):
		def isLonger(a, b):
			b=len(b)
			if b>a:
				return b
			return a

		fmt='%%-%ds %%s' % (reduce(isLonger, Item.MemberNames, 0)+3)
		buf=[]

		for key in Item.MemberNames:
			v=getattr(self, key)
			if type(v) is str:
				v=toCString(v)
				if len(v)>40:
					v=v[:40]

			buf.append(fmt % ('%s:' % key, `v`))

		return ('\n' + getattr(self, 'indent', 0)*' ').join(buf)

class Rent:
	def __init__(self, path):
		rent=get_rent(path)
		self.rent=rent[0]
		self.items=[Item(item) for item in rent[1:]]

	def __iter__(self):
		return iter(self.items)

def list_item(item):
	"""
	   vnum,           keywords,       long-descr,   short-descr,  wearpos,
	   value 1,        value 2,        value 3,      value 4,      type,
	   extra flags,    anti flags,     wear flags,   weight,       timer,        bitvector
	   affection 1,    affection 2,    affection 3,  affection 4,  affection 5,  affection 6
	"""

	# Generator
	vnum=item[0]
	name=toCString(item[3])
	if len(name)>25:
		name=name[:25]

	wear=item[4]
	if wear != -1:
		wear-=1
	wear=wearPositions.get(wear, '#%d' % wear)

	type=item[9]
	type=itemTypes.get(type, '#%d' % type)

	values=[abs(v) for v in item[5:9]]
	values=tuple(values)

	fmt='    #[%5d] %-25s |%10s:%-10s| [%04x|%04x|%04x|%04x]'
	yield fmt % ((vnum, name, type, wear) + values)
	yield 'keywords : %r' % item[1]

def list_rent_info(rentinfo):
	# Generator
	r_time, r_code, r_perdiem, r_gold, r_acct, r_nitems = rentinfo[:6]

	r_time = ctime(r_time)
	r_code = rentCodes.get(r_code, '#%d' % r_code)

	yield ' at '.join([r_code, r_time])
	yield '[%ld/day, Gold: %ld, Acct: %ld] x %ld' % \
		  (r_perdiem, r_gold, r_acct, r_nitems)

def list_rent(rent):
	# Generator
	for ri in list_rent_info(rent[0]):
		yield ri

	for item in rent[1:]:
		for l in list_item(item):
			yield l

def NameOfFile(path):
	# Here's your chance to do basename and what not
	return path

def show_rent_file(filename):
	rent = get_rent(filename)
	show = list_rent(rent)

	print show.next(), '(%s)' % NameOfFile(filename)
	for l in show:
		print l

def parse_cmdln(argv = None):
	from optparse import OptionParser
	parser = OptionParser()
	parser.add_option('-d', '--debug', action = 'store_true')
	return parser.parse_args(argv)

def main(argv = None):
	(options, args) = parse_cmdln(argv)
	if options.debug:
		debug()

	for filename in args:
		show_rent_file(filename)

if __name__=='__main__':
	main()
