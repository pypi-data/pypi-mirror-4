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
from scan import *
from show import *

from struct import pack

try:
	from md5 import new as MD5
	def checksum(x, MD5=__import__('md5').new):
		return MD5(str(x)).hexdigest()

except ImportError:
	checksum=lambda x:id(x)

def repack_item(item):
	#print `structfmt_obj_file_elem`, len(item), [type(v) for v in item]
	return pack(structfmt_obj_file_elem, *item)

# An EQ-Set is a (non-sorted) collection of items in their wear-positions
# as expressed in the final obj_file_elem parts of a rent-file.
#
# (A Rent-ID is sorted, specifically, and computed with a more appropriate
#  algorithm; see below.)
def repack_eqset(eqset):
	"Repack the EQ-Set into a buffer."
	return ''.join([repack_item(item) for item in eqset])

# This is mainly useful for re-writing the rentfile
def repack_rent(rent, result=[]):
	"""
	Reconstruct rent-file given the rent-tuple format:
		[(rent_info), (obj_file_elem) x N, ...]
	"""
	result  = [pack(structfmt_rent_info, *rent[0])]
	result += repack_eqset(rent[1:])

	return ''.join(result)

# A Rent-ID is meant to uniquely identify set of equipment,
# and is generally computed given 
#   - Sorted EQ-Set
#   - MD5 checksum the value of this written buffer
#   - Integrated secure (cryptographic) key
def compute_rentid(eqset):
	# Generate packed formats:
	eqset=map(repack_item, eqset)

	# Generate map for sorting, discarding old structures.  Checksums
	# are calculated for each blob used for sorting comparisons:
	eqset=zip(eqset, map(checksum, eqset))

	# Initial EQ-Set, and sort map is abandoned for a sorted set of
	# item buffers:
	eqset.sort(lambda x, y:cmp(x[1], y[1]))
	eqset=[item[0] for item in eqset]

	# Obtain packed buffer format (skipping repack_eqset).
	# Note that this is a sorted representation, and that's
	# where we get our identification properties from::
	eqset=''.join(eqset)

	# Calculate (checksum) Rent-ID from eqbuf:
	return checksum(eqset)

def apply_item_transform(items, proc, *args, **kwd):
	return [proc(i, *args, **kwd) for i in items]

def apply_rent_script(rent, info_proc=None, item_proc=None):
	items=rent[1:]
	rent=rent[0]

	if info_proc:
		rent=info_proc(rent)

	if item_proc:
		items=[list(i) for i in items]
		items=apply_item_transform(items, item_proc)
		items=filter(None, items)
		items=tuple([tuple(i) for i in items])

	return repack_rent((rent,) + items)

def NewDerivedFile(f):
	return f + '.out'

def path_applyscript(path, info_proc=None, item_proc=None, **kwd):
	# Keyword args: info_proc, item_proc, recursive_policy, NewDerivedFile
	locals().update(kwd)

	assert info_proc or item_proc, Error('No transformation..?')

	# XXX Test path for directory:

	outf=open(NewDerivedFile(path), 'w')
	outf.write(apply_rent_script(get_rent(path), info_proc, item_proc))
	outf.flush()
	outf.close()

# Classes of transformation applied by 
class Apply:
	def FileScript(path):
		code=open(path).read()
		code=compile(code, path, 'exec')

		def ProcessItemWithScript(item, code=code):
			ns={'item':item}
			exec code in ns
			return ns.get('item', item)

		return ProcessItemWithScript
	FileScript=staticmethod(FileScript)

	def ForAll(item):
		return True
	ForAll=staticmethod(ForAll)

	def ForNone(item):
		return False
	ForNone=staticmethod(ForNone)

	class IndexCheck:
		def __init__(self, index, acptbl=None):
			self.index=index
			self.acceptable=acptbl

		def IsAcceptable(self, item):
			val=item[self.index]
			actbl=self.actbl

			if type(actbl) in (list, tuple):
				return val in actbl

			elif callable(actbl):
				return actbl(val)

			return val == actbl

		__call__=IsAcceptable

	class Condition:
		def __init__(self, condition, procedure):
			self.cond=condition
			self.proc=procedure

		def TransformUnderCondition(self, item):
			if self.cond(item):
				item=self.proc(item)

			return item

		__call__=TransformUnderCondition

	# class CookedConditions(Condition):
	#	def __init__(*args):
	#		Condition.__init__(*args)
	#	def CheckUnderCookedConditions(self, item):
	#		...
	#		return Condition.TransformUnderCondition(self, item)
	#	__call__=CheckUnderCookedConditions

	class Aggregate:
		"""
		VR_NDX=0 # Virtual Number Index
		WP_NDX=4 # Wear-positional index

		vnums=range(*input(' ZBottom, ZTop? '))

		a_aggr=Apply.Aggregate()
		a_acpt=Apply.Condition(IndexCheck(VR_NDX, vnums), a_aggr)

		def PutIntoInventory(item):
			item=list(item)
			item[WP_NDX]=0

			return tuple(item)

		a_aggr.add(PutIntoInventory)
		# a_aggr.add()

		apply_objfile_script('ada.objs', item_proc=a_acpt)
		"""
		def __init__(self, sequence=[], *args, **kwd):
			self.sequence=sequence or []
			self.args=args
			self.kwd=kwd

		def ExecuteSequence(self, item):
			for s in self.sequence:
				if not item:
					break

				item=s(item, *self.args, **self.kwd)

			return item
		__call__=ExecuteSequence

		def addToSequence(self, proc):
			if type(proc) in (list, tuple):
				for p in proc:
					self.addToSequence(p)

			elif callable(proc):
				self.sequence.append(proc)

			# Method-Chaining:
			# return self
		add=__iadd__=addToSequence

def path_applymodule(path, module, *args, **kwd):
	"""
	Load module as: module, path-name, file, single-function
	Load rent file from: path

	Build item transformation application with: module
	Call path_applyscript with: path, transformation application
	"""
	locals().update(kwd)

	# XXX Move this module building into an Application routine!!

	tp=type(module)
	if tp is __import__('types').ModuleType:
		module=module.__dict__.values()

	elif tp is str:
		modpath=module
		module=open(module)

	elif tp is file:
		modpath=module.name

	elif callable(module):
		module=[module]

	if type(module) is file:
		ns={'__file__':modpath}
		exec compile(module.read(), modpath, 'exec') in ns

		# XXX pname ..??
		pname='process_item'
		isProcessItem=lambda f, pn=pname:f.func_code.co_name == pn
		module=[v for v in ns.values() if isProcessItem(v)]

	assert type(module) is list

	from types import FunctionType as function
	module=filter(lambda f:type(f) is function, module)

	return path_applyscript(path, item_proc=Apply.Aggregate(module), **kwd)

def transform_interface(path):
	args=[]
	kwd={}

	# XXX Use a menu to inquire: module path-name/object, args/kwd environment
	module=input(' Module? ')

	return path_applymodule(path, module, *args, **kwd)

def edit_transformation(path, names=('transform', 'transform_item', 'process', 'process_item')):
	from nano import edit as nano

	ns={}
	code=nano()
	code=compile(code, 'fast', 'exec')
	exec code in ns

	from types import FunctionType as function
	module=[]
	kwd={}

	for k, v in ns.iteritems():
		if type(v) is function and v.func_code.co_name in names:
			module.append(v)

		else:
			kwd[k]=v

	return path_applymodule(path, module, **kwd)
edittrans=edit_transformation

def fast_transformation(path, script=None):
	assert script
	return path_applymodule(path, Apply.FileScript(script))
fasttrans=fast_transformation

def show_rentid(path):
	"Compute Rent-ID given rent-file path name."
	rent=get_rent(path)
	eqset=rent[1:]

	rentid=compute_rentid(eqset)

	print path, ':', rentid
	for line in list_rent_info(rent[0]):
		print '    ', line

if __name__=='__main__':
	config={}
	proc=[show_rentid]

	for a in __import__('sys').argv[1:]:
		op=a[0]
		if op in '-=+':
			parts=a[1:].split(':')
			name=parts[0]
			parts=parts[1:]

			if name in ('t', 'proc', 'procedure'):
				proc=[eval(p) for p in parts]

			elif op == '=':
				config[name]=[eval(p) for p in parts]

			else:
				config[name]=':'.join(parts)

		else:
			for p in proc:
				p(a, **config)
