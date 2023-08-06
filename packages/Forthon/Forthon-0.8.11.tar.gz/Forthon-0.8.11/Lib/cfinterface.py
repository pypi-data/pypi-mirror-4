# Created by David P. Grote, March 6, 1998
# $Id: cfinterface.py,v 1.17 2011/05/16 18:55:26 grote Exp $

# Routines which allows c functions to be callable by fortran
import sys
import re
import struct

from Forthon_options import options,args

# Set default values of inputs
machine = options.machine
f90 = options.f90
realsize = options.realsize
underscoring = options.underscoring
twounderscores = options.twounderscores

#----------------------------------------------------------------------------
# Set size of fortran integers and logicals, which is the same size as a
# C long integer. This is always either 4 or 8.
intsize = '%d'%struct.calcsize('l')
isz = 'kind=%s'%intsize

#----------------------------------------------------------------------------
# Set the size of floating point numbers
fpsize = 'kind=%s'%realsize

#----------------------------------------------------------------------------
# Creates a function which converts a C name into a Fortran name

if machine in ['hp-uxB','aix4','aix5','win32','MAC']:
  def fname(n):
    return n.lower()
elif machine in ['linux2','linux3','darwin','SOL','sunos5','AXP','osf1V4','DOS','cygwin']:
  if underscoring:
    if twounderscores:
      def fname(n):
        m = re.search('_',n)
        if m == None: return n.lower()+'_'
        else:         return n.lower()+'__'
    else:
      def fname(n):
        return n.lower()+'_'
  else:
    def fname(n):
      return n.lower()
elif machine in ['T3E','sn67112','C90','J90','SGI','irix646']:
  def fname(n):
    return n.upper()
else:
  raise ValueError('Machine %s not supported'%machine)

#----------------------------------------------------------------------------
# Creates a function which returns the Fortran name of an object

if not f90:
  def fnameofobj(f):
    return fname(f.name)
else:
  def fnameofobj(f):
    return fname(f.name)
# if machine in ['hp-uxB','linux2','linux3', \
#                'SOL','sunos5','AXP','osf1V4','DOS','MAC']:
#   def fnameofobj(f):
#     return f.name+'_in_'+f.group
# elif machine in ['T3E','sn67112','C90','J90']:
#   def fnameofobj(f):
#     return f.name.upper()+'_in_'+f.group.upper()
# elif machine in ['SGI','irix646']:
#   def fnameofobj(f):
#     return f.name.upper()+'.in.'+f.group.upper()
# elif machine in ['aix4']:
#   def fnameofobj(f):
#     return '__'+f.group+'_MOD_'+f.name
# else:
#   raise ValueError('Machine %s not supported'%machine)

#----------------------------------------------------------------------------
# Sets up C macros which are used to take the place of the length
# of a string passed from Fortran to C.

if machine in ['hp-uxB','linux2','linux3','darwin','SOL','sunos5','DOS','aix4','aix5','win32','cygwin']:
  charlen_at_end = 1
  forthonf2c = """
#define FSTRING char*
#define SL1 ,int sl1
#define SL2 ,int sl2
#define SL3 ,int sl3
#define SL4 ,int sl4
#define SL5 ,int sl5
#define FSTRLEN1(S) sl1
#define FSTRLEN2(S) sl2
#define FSTRLEN3(S) sl3
#define FSTRLEN4(S) sl4
#define FSTRLEN5(S) sl5
#define FSTRPTR(S) S
#define FSETSTRING(S,P,L) S = P
#define FSETSTRLEN1(S,L) sl1 = L
#define FSETSTRLEN2(S,L) sl2 = L
#define FSETSTRLEN3(S,L) sl3 = L
#define FSETSTRLEN4(S,L) sl4 = L
#define FSETSTRLEN5(S,L) sl5 = L
"""

elif machine in ['T3E','sn67112','SGI','irix646']:
  charlen_at_end = 0
  forthonf2c = """
typedef struct {char* ptr;int len;} fstring;
#define FSTRING fstring
#define SL1 
#define SL2 
#define SL3 
#define SL4 
#define SL5 
#define FSTRLEN1(S) S.len
#define FSTRLEN2(S) S.len
#define FSTRLEN3(S) S.len
#define FSTRLEN4(S) S.len
#define FSTRLEN5(S) S.len
#define FSTRPTR(S) S.ptr
#define FSETSTRING(S,P,L) {S.ptr = P;S.len = L;}
"""

elif machine in ['C90','J90']:
  charlen_at_end = 0
  forthonf2c = """
#include <fortran.h>
#define FSTRING _fcd
#define SL1 
#define SL2 
#define SL3 
#define SL4 
#define SL5 
#define FSTRLEN1(S) _fcdlen(S)
#define FSTRLEN2(S) _fcdlen(S)
#define FSTRLEN3(S) _fcdlen(S)
#define FSTRLEN4(S) _fcdlen(S)
#define FSTRLEN5(S) _fcdlen(S)
#define FSTRPTR(S) _fcdtocp(S)
#define FSETSTRING(S,P,L) S = _cptofcd(P,L);
"""

elif machine in ['MAC']:
  charlen_at_end = 0
  forthonf2c = """
#define FSTRING char*
#define SL1 
#define SL2 
#define SL3 
#define SL4 
#define SL5 
#define FSTRLEN1(S) sl1
#define FSTRLEN2(S) sl2
#define FSTRLEN3(S) sl3
#define FSTRLEN4(S) sl4
#define FSTRLEN5(S) sl5
#define FSTRPTR(S) S
#define FSETSTRING(S,P,L) S = P
#define FSETSTRLEN1(S,L) sl1 = L
#define FSETSTRLEN2(S,L) sl2 = L
#define FSETSTRLEN3(S,L) sl3 = L
#define FSETSTRLEN4(S,L) sl4 = L
#define FSETSTRLEN5(S,L) sl5 = L
"""

else:
  raise ValueError('Machine %s not supported'%machine)

# --- Create the forthonf2c.h file
ff = open('forthonf2c.h','w')
ff.write(forthonf2c)
ff.close()


