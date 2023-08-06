#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" demo for additional tkinter widgets (basic) """

# pytkapp: demo for additional tkinter widgets (basic)
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

if    sys.hexversion >= 0x03000000:
    from tkinter import Tk, Toplevel, Button
    from tkinter.constants import NORMAL, NONE, X, TOP, LEFT, BOTH, YES
else:
    from Tkinter import Tk, Toplevel, Button
    from Tkconstants import NORMAL, NONE, X, TOP, LEFT, BOTH, YES

# fixme: uncomment this block to run script directly OR set pythonpath for your package
#if __name__ == '__main__':
    #import sys
    #import os.path
    #lv_file = __file__
    #while os.path.split(lv_file)[1] != '':
        #lv_file = os.path.split(lv_file)[0]
        #print('append %s'%lv_file)
        #sys.path.append(lv_file)

import pytkapp.pta_icons as pta_icons
from pytkapp.pta_routines import get_estr

from pytkapp.tkw.tkw_routines import READONLY

from pytkapp.dia.dia_xmessage import XMessage, XMESSAGE_STYLE_WARNING
from pytkapp.dia.dia_selector import BaseSelector

###################################
## routines
###################################
def call_demoxmessage(root):
    """demo for xmessage"""
    
    try:
        XMessage(root, 
                 style=XMESSAGE_STYLE_WARNING,
                 title='DEMO',
                 message='Sample',
                 tab=True,
                 tabh=('col1', 'col2', 'col3',),
                 tabr=(('1','1','1','1',), ('2','2','2','2',), ('3','3','3','3','3',),),
                 tabc={(1,None,):{'bg':'red'},(2,2,):{'bg':'green'}})  
    except:
        print('failed to create demo for "xmessage":\n %s' % (get_estr()))
        
def call_demoselector(root):
    """demo for selector"""
    
    try:           
        ld_params = {}
            
        ll_variants = []
    
                            # text, tooltip, icon, value
        ll_variants.append( ('File', 'Process one file', pta_icons.gv_options_openfile, '<file>',) )
        ll_variants.append( ('Folder', 'Process folder', pta_icons.gv_options_openfolder, '<folder>',) )
    
        ll_variants.append( ('<separator>', ))
    
        ll_variants.append( ('Dummy1', None, pta_icons.gv_options_openfolder, '<dummy1>',) )
        ll_variants.append( ('Dummy2', None, None, '<dummy2>',) )
        ll_variants.append( ('Dummy3', None, None, None,) )
        
        ld_params['variants'] = ll_variants
        ld_params['title'] = 'Select variant'
        ld_params['detail'] = 'Some details here'
        lo_dialog = BaseSelector(root,
                                 **ld_params
                                )
        lv_result = lo_dialog.show(width=200, height=300, wal=True)
        if lv_result is None:
            print('Variant was not selected !')
        else:
            print('Variant: %s' % lv_result)        
    except:
        print('failed to create demo for "selector":\n %s' % (get_estr()))
    
def run_demo():
    """ main """
    
    root = Tk()
         
    # demo: xmessage
    b = Button(root, text="Show XMessage demo", command=lambda e=None: call_demoxmessage(root))
    b.pack(side=TOP, fill=X, padx=2, pady=2)
    
    # demo: selector
    b = Button(root, text="Show Selector demo", command=lambda e=None: call_demoselector(root))
    b.pack(side=TOP, fill=X, padx=2, pady=2)
                    
    # show demos
    root.mainloop()

if __name__ == '__main__':    
    run_demo()
