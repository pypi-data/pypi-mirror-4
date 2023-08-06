"Convert rent file into Python."
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
from struct import calcsize, unpack

__all__=['scan_rentfile', 'get_rent']

MAX_OBJ_AFFECT=6
structfmt_obj_affected_type='2b'
structfmt_obj_file_elem    ='I128s256s128sh10il' + \
	(structfmt_obj_affected_type * MAX_OBJ_AFFECT)
structfmt_rent_info        ='14i'

structsz_obj_affected_type =calcsize(structfmt_obj_affected_type)
structsz_obj_file_elem     =calcsize(structfmt_obj_file_elem)
structsz_rent_info         =calcsize(structfmt_rent_info)

def checksize(size):
	size-=structsz_rent_info
	assert (size>=0) and not (size%structsz_obj_file_elem), \
		IOError('File not the right size!')

def scan_rentfile(path):
	# Generator
	rentfile=open(path).read() # XXX Read from file instead of slicing
	size=len(rentfile)

	checksize(size)

	yield unpack(structfmt_rent_info, rentfile[:structsz_rent_info])
	size-=structsz_rent_info

	while size>0: # >= structsz_obj_file_elem
		i=-size
		u=i+structsz_obj_file_elem

		if not u:
			objinfo=rentfile[i:]
		else:
			objinfo=rentfile[i:u]

		result=unpack(structfmt_obj_file_elem, objinfo)

		# Do some surgery on this value..
		# It comes in as a `long`, but the format is 'I'
		# (for unsigned int); struct.pack() doesn't do
		# this reverse coercion.
		result=list(result)
		result[0]=int(result[0])

		yield tuple(result)

		size-=structsz_obj_file_elem

def get_rent(path):
	"Assemble rent-object from scan_rentfile()"
	scan=scan_rentfile(path)
	rent=[scan.next()]

	for obj in scan:
		rent.append(obj)

	return rent

def cstring(s):
	i = s.find('\x00')
	if i < 0:
		return s

	return s[:i]

class Item:
	"""
	Represents this binary packed structure:
	---
	   obj_vnum item_number;

	   char name[128];
	   char description[256];
	   char short_description[128];
	   sh_int locate;
	   int	value[4];
	   int  item_type;
	   int /*bitvector_t*/	extra_flags;
	   int  anti_flags;
	   int  wear_flags;
	   int	weight;
	   int	timer;
	   long /*bitvector_t*/	bitvector;
	   struct obj_affected_type affected[MAX_OBJ_AFFECT];
	"""

	def __init__(self, rent):
		self.vnum     = rent[0]

		self.keywords = cstring(rent[1])
		self.desc     = cstring(rent[2])
		self.name     = cstring(rent[3])

		self.savedAt  = rent[4]
		self.values   = rent[5:9]

		self.itemType = rent[9]

		self.extra    = rent[10]
		self.anti     = rent[11]
		self.wear     = rent[12]

		self.weight   = rent[13]
		self.timer    = rent[14]
		self.bitv     = rent[15]

		self.affect   = rent[16:]

		# self.rent = rent

	def __repr__(self):
		return '<Item #%d (%s)>' % (self.vnum, self.name)

	pf = staticmethod(__import__('pprint').pformat)

	def __str__(self):
		return self.pf(self.__dict__)
