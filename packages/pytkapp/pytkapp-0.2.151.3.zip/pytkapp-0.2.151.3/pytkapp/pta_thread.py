#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" application thread object """

# pytkapp: application thread object
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
## import
###################################
import sys

import gettext
if __name__ == '__main__':
    if    sys.hexversion >= 0x03000000:
        gettext.install(__name__)
    else:
        gettext.install(__name__, unicode=True)
elif '_' not in __builtins__:
    _ = gettext.gettext

# fixme: uncomment this block to run script directly OR set pythonpath for your package
#if __name__ == '__main__':
    #import sys
    #import os.path
    #lv_file = __file__
    #while os.path.split(lv_file)[1] != '':
        #lv_file = os.path.split(lv_file)[0]
        #print('append %s'%lv_file)
        #sys.path.append(lv_file)

from pytkapp.pta_routines import novl

###################################
## constants
###################################
THREAD_YES = 'thread_yes'
THREAD_NO = 'thread_no'

###################################
## classes
###################################
class DummyThread():
    """ thread-like object """
    
    def __init__(self, group, **kw):
        """ init """
        
        self.group = group
        self.ident = -1
        self.name = kw.get('name', '???')
        self.target = novl(kw.get('target', None), self.do_pass)
        
    def get_ident(self):
        """ reutn ident """
        
        return self.ident
    
    def do_pass(self):
        """ do pass """
        
        pass
        
    def start(self):
        """ execute target """
        
        self.target()
        
    def getName(self):
        """ overloaded version """
        
        return self.get_name()
    
    def get_name(self):
        """ get name """
        
        return self.name
    
    def isAlive(self):       
        """ overloaded version """
        
        return self.is_alive()
    
    def is_alive(self):
        """ check alive state """
        
        return False
