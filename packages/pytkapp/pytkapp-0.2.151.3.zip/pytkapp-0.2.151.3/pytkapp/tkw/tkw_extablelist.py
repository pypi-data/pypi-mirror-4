#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" tablelist widget with scrolling and additional 
    controls (search, clear, unload, etc.)
"""

# pytkapp.tkw: tablelist widget with scrolling and additional controls
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
import itertools
import gettext
if __name__ == '__main__':
    if    sys.hexversion >= 0x03000000:
        gettext.install(__name__)
    else:
        gettext.install(__name__, unicode=True)
elif '_' not in __builtins__:
    _ = gettext.gettext     

if    sys.hexversion >= 0x03000000:
    from tkinter import Frame
    from tkinter.constants import N, E
    import tkinter.messagebox as messagebox
else:
    from Tkinter import Frame
    from Tkconstants import N, E
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

from pytkapp.tkw.tkw_xtablelist import XTableList
from pytkapp.tkw.tkw_xtablelist import XTL_BF_HIDE, XTL_BF_SHOW
from pytkapp.tkw.tkw_routines import toolbar_button_generator, toolbar_separator_generator
import pytkapp.tkw.tkw_icons as tkw_icons

from pytkapp.pta_routines import novl

###################################
## globals
###################################  
XTL_BFG_TLEDIT = 'tledit'
gl_bfg = [XTL_BFG_TLEDIT,]

gl_akw = ['allowtledit',]

###################################
## routines
###################################  

###################################
## classes
###################################  
class EXTableList(XTableList):
    """ editable XTablelist """
    
    def __init__(self, parent, **kw):
        """ additional keywords:
              allowtledit: True/False - interactive editing allowed                
        """
        
        ld_kw = kw.copy()
        
        lb_allowtledit = False
        
        for akw in gl_akw:
            if akw == 'allowtledit':
                lb_allowtledit = ld_kw.pop('allowtledit', False)
                        
        XTableList.__init__(self, parent, **ld_kw)

        self.set_xtl_flag('allowtledit', lb_allowtledit)
        
    def custom_bottom_subframe(self, pw_bframe, pv_r, pv_c):
        """ generate custom bottom subframe """
        
        lb_allowtledit = self.get_xtl_flag('allowtledit')
        lb_allowresize = self.get_xtl_flag('allowresize')
        lb_allowexport = self.get_xtl_flag('allowexport')
        
        lv_c = pv_c
        
        if lb_allowtledit:
            lv_datawidget = self.get_datawidget()
            lv_datawidget.configure(editstartcommand=self.__tledit_estart_command)
            lv_datawidget.configure(editendcommand=self.__tledit_eend_command)
            
            
            lw_bf = Frame(pw_bframe)
            
            toolbar_button_generator(lw_bf, 
                                     _('Add row'), 
                                     tkw_icons.gv_alistbox_add,
                                     self.call_tledit_add_row, 
                                     padx=2, pady=2)
            
            toolbar_button_generator(lw_bf, 
                                     _('Del row'), 
                                     tkw_icons.gv_alistbox_remove, 
                                     self.call_tledit_del_row, 
                                     padx=2, pady=2)
            
            if lb_allowresize or lb_allowexport:
                toolbar_separator_generator(lw_bf, ppadx=3, ppady=2)
                
            lw_bf.grid(row=pv_r, column=lv_c, sticky=N+E)
            self.set_xtl_bf(XTL_BFG_TLEDIT, lw_bf)
            self.set_xtl_bfp(XTL_BFG_TLEDIT, lv_c)
            lv_c += 1            
        
        return lv_c
    
    def manage_bottom_frame(self, pv_flag, pv_operation):
        """ hide/show bottom frame btn-groups """
        
        if pv_flag in gl_bfg:
            if pv_operation in (XTL_BF_HIDE, XTL_BF_SHOW) and self.get_xtl_flag('allow%s' % pv_flag):
                lw_frame = self.get_xtl_bf(pv_flag)
                if lw_frame is not None:
                    if pv_operation == XTL_BF_HIDE:
                        lw_frame.grid_forget()
                    else:
                        lw_frame.grid(row=0, column=self.get_xtl_bfp(pv_flag), sticky=N+E)
        else:
            XTableList.manage_bottom_frame(self, pv_flag, pv_operation)
            
    def __tledit_estart_command(self, tbl, row, col, text):
        """ edit start command """
        
        lv_wp = self.editwinpath()
        
        lv_name  = novl(str(self.columncget(col, '-name')), '').lower()
        lv_title = novl(str(self.columncget(col, '-title')), '').lower()
        
        lf_ccom = lambda *args: self.tk.call(lv_wp, "configure", *args)
                
        if hasattr(self, 'tledit_%s_estart_command' % lv_name):
            lv_text = getattr(self, 'tledit_%s_estart_command' % lv_name)(tbl, row, col, text, lf_ccom)
        elif hasattr(self, 'tledit_%s_estart_command' % lv_title):
            lv_text = getattr(self, 'tledit_%s_estart_command' % lv_title)(tbl, row, col, text, lf_ccom)
        else:
            lv_text = text
                
        return lv_text
    
    def __tledit_eend_command(self, tbl, row, col, text):
        """ edit end command """
        
        lv_wp = self.editwinpath()
        
        lv_name  = novl(str(self.columncget(col, '-name')), '').lower()
        lv_title = novl(str(self.columncget(col, '-title')), '').lower()
        
        lf_ccom = lambda *args: self.tk.call(lv_wp, "configure", *args)
        
        if hasattr(self, 'tledit_%s_eend_command' % lv_name):
            lv_text = getattr(self, 'tledit_%s_eend_command' % lv_name)(tbl, row, col, text, lf_ccom)
        elif hasattr(self, 'tledit_%s_eend_command' % lv_title):
            lv_text = getattr(self, 'tledit_%s_eend_command' % lv_title)(tbl, row, col, text, lf_ccom)                
        else:
            lv_text = text
                
        return lv_text
        
    def call_tledit_add_row(self, po_event=None):
        """ add row to tl """
        
        lv_table = self.get_datawidget()
        
        lt_ct = lv_table.cget('-columntitles')
        if isinstance(lt_ct, tuple) and len(lt_ct) > 0:            
            ll_data = list(itertools.repeat('', len(lt_ct)))
                                              
            if hasattr(self, 'tledit_get_def_row'):
                lt_data = tuple(self.tledit_get_def_row(ll_data))
            else:
                lt_data = tuple(ll_data)
            
            self.insert("end", lt_data)
            self.see("end")
        
    def call_tledit_del_row(self, po_event=None):
        """ del row from tl """
        
        lv_table = self.get_datawidget()
        
        lv_selection = lv_table.curselection()
        if len(lv_selection) == 1:        
            if messagebox.askokcancel(_('Confirm'),
                                      'Remove current row ?',
                                      parent=self.winfo_toplevel()):
                lv_table.delete(lv_selection[0])            
                self.on_get_selection()
    