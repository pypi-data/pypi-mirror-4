#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" MListBox - widget based on ListBox with additional
    controls for moving items in list
"""

# pytkapp.tkw: listbox with additional controls (moving)
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
    from tkinter import Frame, Listbox, Scrollbar, StringVar
    from tkinter.constants import N, S, W, E
    from tkinter.constants import END, VERTICAL, EXTENDED, NORMAL
    import tkinter.messagebox as messagebox
else:
    from Tkinter import Frame, Listbox, Scrollbar, StringVar
    from Tkconstants import N, S, W, E
    from Tkconstants import END, VERTICAL, EXTENDED, NORMAL
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

from pytkapp.tkw.tkw_routines import toolbar_lbutton_generator
import pytkapp.tkw.tkw_icons as tkw_icons
  
###################################
## classes
################################### 
class MListBox(Frame):
    """ the listbox with an additional controls to reposition items """
    
    def __init__(self, parent, p_list, **kw):
        """ init widget """
        
        Frame.__init__(self, parent)

        self.__listvar = StringVar()
        self.__list = []

        lb_selectallbtn = False
        if 'selectallbtn' in kw:
            lb_selectallbtn = kw['selectallbtn']
            del kw['selectallbtn']
            
        self.__listbox = Listbox(self, **kw)
        self.__listbox.grid(column=0, row=0, sticky=N+E+W+S, padx=2, pady=2)
        sb = Scrollbar(self)
        sb.config(orient=VERTICAL, command=self.__listbox.yview)
        sb.grid(row=0, column=1, sticky=N+S+E)
        self.__listbox.config(yscrollcommand=sb.set)
        
        self.__listbox.configure( listvariable=self.__listvar, activestyle="none", selectmode=EXTENDED )
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # control frame
        lw_cframe = Frame(self)
        
        lw_btn = toolbar_lbutton_generator(lw_cframe, _("Up"), tkw_icons.gv_mlistbox_moveup, NORMAL, self.call_move_up, 2, 2)
        
        lw_btn = toolbar_lbutton_generator(lw_cframe, _("Down"), tkw_icons.gv_mlistbox_movedown, NORMAL, self.call_move_down, 2, 2)

        if lb_selectallbtn:
            lw_btn = toolbar_lbutton_generator(lw_cframe, _("Select all"), tkw_icons.gv_mlistbox_selectall, NORMAL, self.call_select_all, 2, 2)
            
        lw_btn = toolbar_lbutton_generator(lw_cframe, _("Reset"), tkw_icons.gv_mlistbox_reset, NORMAL, self.call_reset, 2, 2)
        
        lw_cframe.grid( row=1, column=0, columnspan=2, sticky=N+E+W+S )
        
        self.ab_reordereed = False
        # append initial data
        for item in p_list:
            self.__listbox.insert("end", item)
        
        self.__list = p_list
        self.__dlist = p_list[:]
   
    def get_selection( self ):
        """ get listbox selection """
        
        return self.__listbox.curselection()
    
    def call_select_all( self ):
        """ select all items """
        
        self.__listbox.selection_set( 0, "end" )   
        
    def configure_listbox( self, **kw ):
        """ configure listbox itself """
        
        self.__listbox.configure( **kw )        
    
    def call_move_up(self, event=None):
        """ move item up """
        
        sel = self.__listbox.curselection()
        if len(sel) == 1:
            lv_index = int(sel[0])
            lv_newindex = lv_index - 1 
            if lv_newindex >= 0:
                lv_value = self.__listbox.get( lv_index )
                # del record
                self.__listbox.delete( lv_index )
                # insert record
                self.__listbox.insert( lv_newindex, lv_value )
                # select record
                self.__listbox.selection_set( lv_newindex )            
                
                self.change_list()
                self.ab_reordereed = True
                self.event_generate('<FocusOut>')
        else:
            self.__listbox.selection_clear(0, END)
            messagebox.showwarning(_('Caution'), 
                                   _('You need select one record !'),
                                   parent=self.winfo_toplevel())
    
    def call_move_down(self, event=None):
        """ move item down """
        
        sel = self.__listbox.curselection()
        if len(sel) == 1:
            lv_index = int(sel[0])
            lv_newindex = lv_index + 1
            if lv_newindex < self.__listbox.size():
                lv_value = self.__listbox.get( lv_index )
                # del record
                self.__listbox.delete( lv_index )
                # insert record
                self.__listbox.insert( lv_newindex, lv_value )
                # select record
                self.__listbox.selection_set( lv_newindex )  
                
                self.change_list()
                self.ab_reordereed = True
                self.event_generate('<FocusOut>')
        else:
            self.__listbox.selection_clear(0, END)
            messagebox.showwarning(_('Caution'), 
                                   _('You need select one record !'),
                                   parent=self.winfo_toplevel())
            
    def change_list(self):
        """ change internal list """
        
        for i in range(len(self.__list)):
            self.__list.pop(0)
        for list_data in self.get_list():
            self.__list.append(list_data)
    
    def call_reset(self, event=None):
        """ restore items positions """
        
        self.__listbox.selection_clear(0, END)
        self.__listbox.delete(0, END)
        for item in self.__dlist:
            self.__listbox.insert("end", item)
            
        self.change_list()
        self.ab_reordereed = False
        
    def set_list(self, pv_value):
        """ external change """
        
        self.__list = pv_value
        self.__dlist = pv_value[:]
        self.__listbox.delete(0, "end")
        for item in pv_value[::-1]:
            self.__listbox.insert(0, item)          
    
    def get_list(self, event=None):
        """ get widget items as list """
        
        ll_out = []
        for i in range(self.__listbox.size()):
            ll_out.append(self.__listbox.get( i ))
                          
        return ll_out
   
    def get_listbox(self):
        """ get listbox """
        
        return self.__listbox   
    
    def get_datawidget(self):
        """ get datawidget """
        
        return self.__listbox    