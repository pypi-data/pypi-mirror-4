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
from __future__ import with_statement
from contextlib import contextmanager
from types import GeneratorType as generator

def withAs(ctx):
	with ctx as f:
		return f

@contextmanager
def instdict(inst):
	'Create a context variable access out of the variable dictionary.'
	yield inst.__dict__

class Environment(object):
	from new import instance

	class Options:
		from pprint import pformat as pf
		pf = staticmethod(pf)

		def __repr__(self):
			return '<Environment.Options %s>' % self.pf(self.__dict__)

	def __init__(self, avatar, attr = ('env', 'e'), **options):
		self.avatar = avatar

		self.__options = options = dict(options)
		self.options = self.o = self.instance(self.Options, options)

		if type(attr) in (list, tuple, generator):
			for a in attr:
				setattr(avatar, a, self)

		elif type(attr) is str:
			setattr(avatar, attr, self)

	def __getattr__(self, name):
		return self.avatar.find(name, **self.__options)

	def __repr__(self):
		return '<Environment lookup %r>' % self.avatar.find

	def presearch(self, *args):
		'Presearch the environment.'
		return dict((k, getattr(self, k)) for k in args)

	@contextmanager
	def __context__(self):
		'''
		with mobile.e as e:
			print e.fido, e.wyrm, e.zifnab

		with instdict(mobile.e.presearch(*args)) as p:
			print p # The presearched dictionary result.

		'''
		yield self

ment = Environment
