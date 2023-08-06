#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" demo for additional tkinter widgets (tablelist-based) """

# pytkapp: demo for additional tkinter widgets (tablelist-based)
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
    from tkinter import Tk, Toplevel
    from tkinter.constants import N, E, W, S
    import tkinter.messagebox as messagebox
else:
    from Tkinter import Tk, Toplevel
    from Tkconstants import N, E, W, S
    import tkMessageBox as messagebox

# fixme: uncomment this block to run script directly OR set pythonpath for your package
#if __name__ == '__main__':
    #import sys
    #import os.path
    #lv_file = __file__
    #while os.path.split(lv_file)[1] != '':
        #lv_file = os.path.split(lv_file)[0]
        #print('append %s'%lv_file)
        #sys.path.append(lv_file)

from pytkapp.tkw.tkw_txtablelist import TXTableList
from pytkapp.tkw.tkw_extablelist import EXTableList
from pytkapp.tkw.tkw_extablelist import XTableList

from pytkapp.pta_routines import get_estr
from pytkapp.tkw.tkw_xtablelist import XTL_BF_HIDE, XTL_BF_SHOW, XTL_BFG_EXPORT, XTL_BFG_RESIZE
from pytkapp.tkw.tkw_routines import toolbar_button_generator
from pytkapp.tkw.tkw_extablelist import XTL_BFG_TLEDIT
from pytkapp.tkw.tkw_txtablelist import XTL_BFG_TREE

###################################
## routines
###################################   
def run_demo():
    """ main """
    
    root = Tk()
          
    # demo: extablelist
    try:
        lw_demotop = Toplevel(root)
        lw_demotop.title('(e)xtablelist demo')
        lv_coluns = 4
        lt_headers = ()
        for i in range(lv_coluns):
            lt_headers += ( 0, 'Column'+str(i), )
            
        lw_demowidget = EXTableList(lw_demotop,
                                    activestyle="none",
                                    background = "white",
                                    columns = lt_headers,
                                    selecttype="row",
                                    selectmode="extended", #single, browse, multiple, extended
                                    stretch = "all",
                                    stripebackground="gray90",
                                    height=15,
                                    width=0,
                                    # additional
                                    allowkeepsel=True,
                                    allowtledit=True,
                                    allowresize=True,
                                    allowexport=True,
                                    hscroll=True,
                                    vscroll=True
                                    )
        lw_demowidget.xcontent()
        
        lw_demowidget.columnconfigure(2, editable=True)
        lw_demowidget.columnconfigure(3, editable=True, editwindow='ttk::combobox')
        
        lw_udcf = lw_demowidget.get_udcf()
        
        toolbar_button_generator(lw_udcf, 
                                 _('hide Ed'), 
                                 '',  
                                 lambda e=None: lw_demowidget.manage_bottom_frame(XTL_BFG_TLEDIT, XTL_BF_HIDE),
                                 padx=2, pady=2)
        toolbar_button_generator(lw_udcf, 
                                 _('show Ed'), 
                                 '', 
                                 lambda e=None: lw_demowidget.manage_bottom_frame(XTL_BFG_TLEDIT, XTL_BF_SHOW),
                                 padx=2, pady=2)
        
        toolbar_button_generator(lw_udcf, 
                                 _('hide R'), 
                                 '', 
                                 lambda e=None: lw_demowidget.manage_bottom_frame(XTL_BFG_RESIZE, XTL_BF_HIDE),
                                 padx=2, pady=2)
        toolbar_button_generator(lw_udcf, 
                                 _('show R'), 
                                 '', 
                                 lambda e=None: lw_demowidget.manage_bottom_frame(XTL_BFG_RESIZE, XTL_BF_SHOW),
                                 padx=2, pady=2)
                
        toolbar_button_generator(lw_udcf, 
                                 _('hide E'), 
                                 '', 
                                 lambda e=None: lw_demowidget.manage_bottom_frame(XTL_BFG_EXPORT, XTL_BF_HIDE),
                                 padx=2, pady=2)
        toolbar_button_generator(lw_udcf, 
                                 _('show E'), 
                                 '', 
                                 lambda e=None: lw_demowidget.manage_bottom_frame(XTL_BFG_EXPORT, XTL_BF_SHOW),
                                 padx=2, pady=2)
        
        for i in range(15):
            lw_demowidget.insert("end", (i, 'text %s' % i, i+10, 'no'))
        
        def tledit_column3_estart_command(tbl, row, col, text, lf_ccom):
            """ demo method """
            
            lv_text = text
            
            lf_ccom('-values', ('yes', 'no',), )
            
            return lv_text
        
        setattr(lw_demowidget, 'tledit_column3_estart_command', tledit_column3_estart_command)
        
        def tledit_column3_eend_command(tbl, row, col, text, lf_ccom):
            """ demo method """
            
            lv_text = text
            if lv_text not in ('yes', 'no'):
                messagebox.showerror(_('Error'),
                                     _('Invalid argument'))
                lv_text = 'no'
                
            return lv_text
        
        setattr(lw_demowidget, 'tledit_column3_eend_command', tledit_column3_eend_command)
        
        lw_demowidget.grid(row=0, column=0, sticky=N+E+W+S)
        
        lw_demotop.columnconfigure(0, weight=1)
        lw_demotop.rowconfigure(0, weight=1)
    except:
        print('failed to create demo for "EXTableList":\n %s' % (get_estr()))
    
    # TXTableList
    try:
        lw_demotop = Toplevel(root)
        lw_demotop.title('(t)xtablelist demo')
        lv_coluns = 3
        lt_headers = ()
        for i in range(lv_coluns):
            lt_headers += ( 0, 'Column'+str(i), )
            
        lw_demowidget = TXTableList(lw_demotop,
                                    activestyle="none",
                                    background = "white",
                                    columns = lt_headers,
                                    selecttype="row",
                                    selectmode="extended", #single, browse, multiple, extended
                                    stretch = "all",
                                    stripebackground="gray90",
                                    height=15,
                                    width=0,
                                    # additional
                                    allowkeepsel=True,
                                    allowresize=True,
                                    allowtree=True,
                                    allowexport=True,
                                    hscroll=True,
                                    vscroll=True
                                    )
        lw_demowidget.xcontent()
        
        lw_udcf = lw_demowidget.get_udcf()
        
        toolbar_button_generator(lw_udcf, 
                                 _('hide R'), 
                                 '', 
                                 lambda e=None: lw_demowidget.manage_bottom_frame(XTL_BFG_RESIZE, XTL_BF_HIDE),
                                 padx=2, pady=2)
        toolbar_button_generator(lw_udcf, 
                                 _('show R'), 
                                 '', 
                                 lambda e=None: lw_demowidget.manage_bottom_frame(XTL_BFG_RESIZE, XTL_BF_SHOW),
                                 padx=2, pady=2)
        
        toolbar_button_generator(lw_udcf, 
                                 _('hide T'), 
                                 '', 
                                 lambda e=None: lw_demowidget.manage_bottom_frame(XTL_BFG_TREE, XTL_BF_HIDE),
                                 padx=2, pady=2)
        toolbar_button_generator(lw_udcf, 
                                 _('show T'), 
                                 '', 
                                 lambda e=None: lw_demowidget.manage_bottom_frame(XTL_BFG_TREE, XTL_BF_SHOW),
                                 padx=2, pady=2)
        
        toolbar_button_generator(lw_udcf, 
                                 _('hide E'), 
                                 '', 
                                 lambda e=None: lw_demowidget.manage_bottom_frame(XTL_BFG_EXPORT, XTL_BF_HIDE),
                                 padx=2, pady=2)
        toolbar_button_generator(lw_udcf, 
                                 _('show E'), 
                                 '', 
                                 lambda e=None: lw_demowidget.manage_bottom_frame(XTL_BFG_EXPORT, XTL_BF_SHOW),
                                 padx=2, pady=2)
        
        ll_data = []
        ll_data.append( ( 1, 'test1', 0) )
        ll_data.append( ( 2, 'test2', 0) )
        ll_data.append( ( 3, 'test3', 0) )
        ll_data.append( ( 4, 'test4', 0) )
        ll_data.append( ( 5, 'test1-1', 1) )
        ll_data.append( ( 6, 'test1-2', 1) )
        ll_data.append( ( 7, 'test3-1', 3) )
        ll_data.append( ( 8, 'test3-2', 3) )
        ll_data.append( ( 9, 'test3-3', 3) )
        ll_data.append( (10, 'test3-4', 3) )
        ll_data.append( (11, 'test3-2-1', 8) )
        ll_data.append( (12, 'test3-2-2', 8) )
        ll_data.append( (13, 'test3-2-3', 8) )
        
        lw_demowidget.configure(treecolumn=0)
        
        lw_demowidget.filltree(ll_data, lambda x: x[2]==0, 0, 2)
        
        lw_demowidget.grid(row=0, column=0, sticky=N+E+W+S)
        
        lw_demotop.columnconfigure(0, weight=1)
        lw_demotop.rowconfigure(0, weight=1)
    except:
        print('failed to create demo for "TXTableList":\n %s' % (get_estr()))
        
    # xtablelist
    try:
        lw_demotop = Toplevel(root)
        lw_demotop.title('xtablelist demo')
        lv_coluns = 4
        lt_headers = ()
        for i in range(lv_coluns):
            lt_headers += ( 0, 'Column'+str(i), )
            
        lw_demowidget = XTableList(lw_demotop,
                                   activestyle="none",
                                   background = "white",
                                   columns = lt_headers,
                                   selecttype="row",
                                   selectmode="extended", #single, browse, multiple, extended
                                   stretch = "all",
                                   stripebackground="gray90",
                                   height=15,
                                   width=0,
                                   # additional
                                   allowkeepsel=True,
                                   allowresize=True,
                                   allowexport=True,
                                   hscroll=True,
                                   vscroll=True
                                   )
        lw_demowidget.xcontent()        
        lw_udcf = lw_demowidget.get_udcf()
        
        toolbar_button_generator(lw_udcf, 
                                 _('hide R'), 
                                 '', 
                                 lambda e=None: lw_demowidget.manage_bottom_frame(XTL_BFG_RESIZE, XTL_BF_HIDE),
                                 padx=2, pady=2)
        toolbar_button_generator(lw_udcf, 
                                 _('show R'), 
                                 '', 
                                 lambda e=None: lw_demowidget.manage_bottom_frame(XTL_BFG_RESIZE, XTL_BF_SHOW),
                                 padx=2, pady=2)
                
        toolbar_button_generator(lw_udcf, 
                                 _('hide E'), 
                                 '', 
                                 lambda e=None: lw_demowidget.manage_bottom_frame(XTL_BFG_EXPORT, XTL_BF_HIDE),
                                 padx=2, pady=2)
        toolbar_button_generator(lw_udcf, 
                                 _('show E'), 
                                 '', 
                                 lambda e=None: lw_demowidget.manage_bottom_frame(XTL_BFG_EXPORT, XTL_BF_SHOW),
                                 padx=2, pady=2)
        
        for i in range(15):
            lw_demowidget.get_datawidget().insert("end", (i, 'text %s' % i, i+10, 'no'))
        
        lw_demowidget.grid(row=0, column=0, sticky=N+E+W+S)
        
        lw_demotop.columnconfigure(0, weight=1)
        lw_demotop.rowconfigure(0, weight=1)
    except:
        print('failed to create demo for "XTableList":\n %s' % (get_estr()))
            
    # show demos
    root.mainloop()

if __name__ == '__main__':    
    run_demo()
