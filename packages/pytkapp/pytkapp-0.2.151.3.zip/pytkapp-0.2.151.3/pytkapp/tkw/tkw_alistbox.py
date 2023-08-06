#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" AListBox - widget based on ListBox with additional
    controls for adding/removing items
"""

# pytkapp.tkw: listbox with additional controls (add/remove)
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
    from tkinter import Frame, Listbox, Scrollbar, Entry
    from tkinter.constants import N, S, W, E
    from tkinter.constants import TOP, X, YES, BOTH, VERTICAL, LEFT
    from tkinter.constants import NORMAL, DISABLED
    from tkinter.ttk import Combobox as ttkCombobox
else:
    from Tkinter import Frame, Listbox, Scrollbar, Entry
    from Tkconstants import N, S, W, E
    from Tkconstants import TOP, X, YES, BOTH, VERTICAL, LEFT
    from Tkconstants import NORMAL, DISABLED
    from ttk import Combobox as ttkCombobox

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
from pytkapp.tkw.tkw_routines import toolbar_lbutton_generator, make_widget_ro
import pytkapp.tkw.tkw_icons as tkw_icons
  
###################################
## globals
###################################  
ALISTBOX_STYLE_ENTRY = 'entry'
ALISTBOX_STYLE_SENTRY = 'sentry'
ALISTBOX_STYLE_COMBO = 'combobox'
  
###################################
## classes
###################################  
class AListBox(Frame):
    """ listbox with additional controls to add, remove items """
    
    def __init__(self, parent, p_list, **kw):
        """ init widget """
        
        Frame.__init__(self, parent)

        self.__list = p_list
        self.__widgets = {}
        self.__style = ALISTBOX_STYLE_ENTRY
        
        lw_lframe = Frame( self )
        self.__listbox = Listbox(lw_lframe, activestyle="none")
        self.__listbox.grid(column=0, row=0, sticky=N+E+W+S, padx=2, pady=2)
        lw_sb = Scrollbar(lw_lframe)
        lw_sb.config(orient=VERTICAL, command=self.__listbox.yview)
        lw_sb.grid(column=1, row=0, sticky=N+S+E)
        self.__listbox.config(yscrollcommand=lw_sb.set)
        lw_lframe.columnconfigure(0, weight=1)
        lw_lframe.rowconfigure(0, weight=1)
        lw_lframe.pack(side=TOP, expand=YES, fill=BOTH)
        self.__listbox.bind('<Double-Button-1>', self.remove_item)
        self.__widgets['listbox'] = self.__listbox
        
        lw_cframe = Frame( self )
        lv_style = kw.get('style', ALISTBOX_STYLE_ENTRY)
        self.__style = lv_style
        lf_sentryfunc = None
        if lv_style == ALISTBOX_STYLE_ENTRY:
            self.__datawidget = Entry(lw_cframe)           
        elif lv_style == ALISTBOX_STYLE_SENTRY:
            self.__datawidget = Entry(lw_cframe)           
            make_widget_ro(self.__datawidget)
            lf_sentryfunc = kw.get('sentryfunc', None)
        elif lv_style == ALISTBOX_STYLE_COMBO:
            ll_combolist = kw.get('values', [])
            self.__datawidget = ttkCombobox(lw_cframe, state="readonly", values=ll_combolist )
            
        self.__datawidget.pack(side=LEFT, fill=X, expand=YES, padx=2, pady=2)
        self.__widgets['datawidget'] = self.__datawidget       
        
        if lf_sentryfunc and lv_style == ALISTBOX_STYLE_SENTRY:
            lw_btn = toolbar_lbutton_generator(lw_cframe, _("Search item"), tkw_icons.gv_alistbox_search, NORMAL, self.search_item, 2, 2)
            self.__widgets['sbtn'] = lw_btn

        lw_btn = toolbar_lbutton_generator(lw_cframe, _("Add item"), tkw_icons.gv_alistbox_add, NORMAL, self.add_item, 2, 2)
        self.__widgets['abtn'] = lw_btn
        
        lw_btn = toolbar_lbutton_generator(lw_cframe, _("Remove item"), tkw_icons.gv_alistbox_remove, NORMAL, self.remove_item, 2, 2)
        self.__widgets['dbtn'] = lw_btn
        
        self.__sentryfunc = lf_sentryfunc
        
        lw_cframe.pack(side=TOP, fill=X)
        
        for item in p_list[::-1]:
            self.__listbox.insert(0, item)
            
    def set_list(self, pv_value):
        """ external change """
        
        self.__list = pv_value
        self.__listbox.delete(0, "end")
        for item in pv_value[::-1]:
            self.__listbox.insert(0, item)        
            
    def get_datawidget(self):
        """ get datawidget """
        
        return self.__datawidget
            
    def get_listbox(self):
        """ get listbox """
        
        return self.__listbox
            
    def configure_listbox( self, **kw ):
        """ configure listbox itself """
        
        self.__listbox.configure( **kw )
        
    def search_item(self, event=None ):
        """ search item """
        
        lv_val = self.__sentryfunc(self.winfo_toplevel())
        self.__datawidget.delete('0', 'end')
        self.__datawidget.insert('0', lv_val)
        
    def add_item( self, p_data=None):
        """ add item to list """
        
        if p_data is None:
            lv_data = self.__datawidget.get()
        else:
            lv_data = p_data
            
        if novl(lv_data, '') != '':            
            self.__list.insert(0, lv_data)
            self.__listbox.insert(0, lv_data)
            
            self.event_generate('<FocusOut>')
        
    def remove_item( self, event=None ):
        """ remove item """
        if self.__listbox.cget('state') != DISABLED:
            lv_index = self.__listbox.curselection()

            if len(lv_index) > 0:
                self.__list.pop( int(lv_index[0]) )
                self.__listbox.delete(lv_index)
                
                self.event_generate('<FocusOut>')
        
    def get_selection( self ):
        """ get selection """
        
        return self.__listbox.curselection()
    
    def change_state( self, p_state=NORMAL ):      
        """ change widget state """
        
        self.__listbox.configure( state=p_state )
        if self.__style != ALISTBOX_STYLE_SENTRY:
            if p_state == NORMAL and self.__style != ALISTBOX_STYLE_ENTRY:
                self.__datawidget.configure( state="readonly" )
            else:
                self.__datawidget.configure( state=p_state )
        else:
            self.__widgets['sbtn'].configure( state=p_state )
            
        if 'abtn' in self.__widgets:
            self.__widgets['abtn'].configure( state=p_state )                    
        if 'dbtn' in self.__widgets:
            self.__widgets['dbtn'].configure( state=p_state )
        
    def get_list(self, event=None):        
        """ get associated list with values """
        
        return self.__list

    