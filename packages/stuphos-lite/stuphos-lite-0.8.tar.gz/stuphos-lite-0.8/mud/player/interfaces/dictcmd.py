#!/usr/local/bin/python
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
'Implements command searching with abbreviation management.  See CmdDict.'

# Override UserDict?
class CmdDict:
	'''
	Briefly, it encapsulates a command set dictionary that any command or
	abbreviation of a command will map to value.

	Insert control is provided for expressing abbreviated forms and those
	commands already present in the command set acceptable for overriding.

	And override is where one command abbreviation mapping is replaced with
	another according to the rules of insert[Overriding].

	'''

	# What method to use when using decorator assignment of functions.
	assignmentMethod = 'OverridingAll' # 'Overriding' # ''

	def __init__(self, c = None, assignment = None):
		# Forcing dict type:
		if c is None:
			c = self.c = dict()
		else:
			self.c = c

		self.__getitem__ = c.__getitem__
		self.__setitem__ = c.__setitem__

		# Decide assignment method.
		self.insertAssignment = getattr(self, 'insert' + (assignment or self.assignmentMethod))

	@staticmethod
	def abbreviations(*args):
		'''
		For each positional argument, generate a number of abbreviated
		forms, from longest to shorted, until the end 

		Each argument be either:
			- A 2-tuple:
			  ('command-name', end)
			  Where end is the ending index of the command name to stop abbreviations.

			- A string describing verb abbreviations (from lambda moo):
			  verb*name
			  The abbreviations are generated from the full name down to the asterisk.

			- A plain string.  All possible abbreviations will be generated down to
			  the first letter.  Useful for overriding the movement or violence commands.

		'''

		for m in args:
			if type(m) is tuple and len(m) == 2:
				# Only yield up to explicit column.
				m, end = m
				while len(m) >= end:
					yield m
					m = m[:-1]
			elif '*' in m:
				# Detect end column from 'verb*name' form.
				end = m.index('*') # -1 ?
				m = m.replace('*', '')
				while len(m) >= end:
					yield m
					m = m[:-1]
			else:
				# Use every possible abbreviation.
				while m:
					yield m
					m = m[:-1]

	def insert(self, m, a = None):
		'Insert abbreviations of command name into command set not overriding anything.'

		c = self.c
		a = a or m

		for x in self.abbreviations(m.lower()):
			# Overwrite not desired for any existing entries.
			if x not in c:
				c[x] = a

	def insertOverriding(self, m, a = None, *overriding):
		'''
		Insert only if command is either not already in command-set, or is part of overriding.

		Overriding arguments can be delivered as an abbreviation list:
		insertOverriding('the-*first-command', doCmd, *abbreviations('the-*second-command', 'the-*third-command))

		'''

		c = self.c
		a = a or m

		if overriding:
			s = set(self.abbreviations(overriding))

			for x in self.abbreviations(m.lower()):
				# Override all forms for those specified in trailing arguments.
				if x in s or x not in c:
					c[x] = a
		else:
			for x in self.abbreviations(m.lower()):
				# Reverse order invoking this function no overwrite worry.
				c[x] = a

	def insertOverridingAll(self, m, a = None):
		'Insert abbreviations of command name into command set overriding any and all.'

		c = self.c
		a = a or m

		for x in self.abbreviations(m.lower()):
			c[x] = a

	def lookup(self, cmd, default = None):
		'Looks for command name in the command set dictionary or returns a default value.'

		return self.c.get(cmd, default)

	def assign(self, *verbNames, **req):
		# Decorator for assignment, using free cell variable.
		assign = self.insertAssignment

		def invokeInsert(function):
			for form in verbNames:
				assign(str(form), function, **req)

			return function

		return invokeInsert

	@staticmethod
	def parse(cmd):
		'''Parses a MUD command considering non-alphanumeric first characters.
		Returns 2-tuple (command-name, argstr)'''

		cmd = cmd.lstrip()
		if not cmd:
			return (None, None)

		x = cmd[0]
		if not x.isalpha():
			return x, cmd[1:]

		x = cmd.find(' ')
		if x >= 0:
			return cmd[:x].lower(), cmd[x+1:]

		return cmd.lower(), None

	def remove(self, match):
		c = self.c
		for n in [n for (n, v) in c.iteritems() if v == match]: # v is match?
			del c[n]

	def removeByLookup(self, name):
		cmdfunc = self.lookup(name)
		if cmdfunc is not None:
			self.remove(cmdfunc)

# Testing
if __name__ == '__main__':
	from sys import stdin
	from consoleInteractive import *
	from Timing import Timing

	from pprint import pprint as pp
	from pdb import run, runcall

	cmds = CmdDict()

	@Timing('Multiple Command Load : %(SECONDS)d.%(MICRO)06d')
	def load(n, i = cmds.insertOverriding):
		for x in n:
			i(x)

	@Timing('Command Search : %(SECONDS)d.%(MICRO)06d')
	def lookup(n):
		n, argstr = cmds.parse(n)
		return cmds.lookup(n), argstr

	# Initial load.
	loadedCmds = list(input_cmdln())
	loadedCmds.reverse()

	for x in xrange(10):
		cmds.c = {}
		load(loadedCmds)

	def matchAll(x):
		buf = __import__('cStringIO').StringIO()
		for (k, v) in cmds.data().iteritems():
			if v.startswith(x):
				print>>buf, '%-20s' % k, ':', v
		page(buf.getvalue())

	for n in getline():
		if shellCommand(n, globals()):
			continue

		print lookup(n)
