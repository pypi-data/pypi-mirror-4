#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" common routines ( Python 2.x ) """

# pytkapp.cpr: common routines ( Python 2.x )
#
# Copyright (c) 2013 Paul "Mid.Tier"
# Author e-mail: mid.tier@gmail.com

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

###################################
## constants
###################################
long_zero = 0L

unicode_type = unicode

gf_str_decode = str.decode

Others = StandardError

###################################
## routines
###################################
def compare( lhs_arg, rhs_arg ):
    return cmp( lhs_arg, rhs_arg )

def cmp_to_key(mycmp):
    """Convert a cmp= function into a key= function"""
    class K(object):
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
        def __hash__(self):
            raise TypeError('hash not implemented')
    return K

def to_long( num ):
    if num is None:
        return None
    else:
        try:
            return long(num)
        except ValueError:
            if getattr(num,'__class__',None) in (''.__class__, tu('').__class__) and num == '':
                return None
            else:
                raise

def recode_str2unicode( pv_str, p_enc='utf-8', p_mode='strict' ):
    if pv_str is None:
        return tu('')
    else:
        return gf_str_decode( pv_str, p_enc, p_mode )
    
def recode_str2unicode_( pv_str, p_enc='utf-8', p_mode='strict' ):
    """ only for non-None """
    
    return gf_str_decode( pv_str, p_enc, p_mode )
    
def tu( p_value, p_enc='utf-8' ):
    lv_value = p_value

    if lv_value is None:
        return ''

    if isinstance( lv_value, unicode ):
        return lv_value
    elif isinstance( lv_value, str):
        return unicode( lv_value, encoding=p_enc)
    else:
        return unicode( str(lv_value), encoding=p_enc)

def tu_( p_value, p_enc='utf-8' ):
    """ use for non-NONE and non-unicode """
    
    lv_value = p_value

    if isinstance( lv_value, str):
        return unicode( lv_value, encoding=p_enc)
    else:
        return unicode( str(lv_value), encoding=p_enc)
