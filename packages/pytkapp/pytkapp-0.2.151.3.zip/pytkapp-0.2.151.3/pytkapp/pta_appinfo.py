#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" information file for application base class """

# pytkapp: information file for application's base class
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

# versioning conventions
# major.minor.build.state
# state (0-alpha, 1-beta, 2-rc, 3-final)

__appid__          = 'pytkapp'
__appname__        = 'pytkapp'
__appdesc__        = 'Python package to develop a simple application (MDI/SDI) using tkinter library.'

__appmajor__       = 0
__appminor__       = 2
__appbuild__       = 151
__appstate__       = 3

__appurl__         = 'http://pypi.python.org/pypi/pytkapp'
__appmarker__      = ''
__appauthor__      = 'Paul "Mid.Tier"'
__appauthoremail__ = 'mid.tier@gmail.com'

def get_appid():
    return globals().get('__appid__', '???')

def get_appname():
    return globals().get('__appname__', '???')

def get_appmajor():
    return globals().get('__appmajor__', '???')

def get_appminor():
    return globals().get('__appminor__', '???')

def get_appbuild():
    return globals().get('__appbuild__', '???')

def get_appstate():
    return globals().get('__appstate__', '???')

def get_appstate_t():
    lv_state = get_appstate()
    if lv_state == 0:
        lv_state_t = 'alpha'
    elif lv_state == 1:
        lv_state_t = 'beta'
    elif lv_state == 2:
        lv_state_t = 'rc'
    else:
        lv_state_t = 'final'
        
    return lv_state_t

def get_appversion():
    lv_major = get_appmajor()
    lv_minor = get_appminor()
    lv_build = get_appbuild()
    lv_state = get_appstate()
    
    return '%s.%s.%s.%s' % (lv_major, lv_minor, lv_build, lv_state)

def get_appversion_t():
    lv_major   = get_appmajor()
    lv_minor   = get_appminor()
    lv_build   = get_appbuild()
    lv_state_t = get_appstate_t()
    
    return '%s.%s.%s (%s)' % (lv_major, lv_minor, lv_build, lv_state_t)

def get_appmarker():
    return globals().get('__appmarker__', '???')

def get_appurl():
    return globals().get('__appurl__', '???')
    
def get_appauthor():
    return globals().get('__appauthor__', '???')

def get_appauthoremail():
    return globals().get('__appauthoremail__', '???')

def get_appdesc():
    return globals().get('__appdesc__', '???')

def get_deftitle():
    lv_title = '%s v.%s' % (get_appname(), 
                            get_appversion_t()
                           )
    return lv_title

def cmp_version(pv_version):
    """compare current version with other
       return zero (if equal/exception) or first non-zero result (1-greater, 0-lower)
    """
    
    try:
        ll_check = [x for x in map(cmp, [int(x) for x in get_appversion().split('.')], 
                                    [int(x) for x in pv_version.split('.')]) 
                    if x != 0]
        if ll_check:
            lv_out = ll_check[0]
        else:
            lv_out = 0
    except:
        lv_out = 0
    finally:
        return lv_out
    