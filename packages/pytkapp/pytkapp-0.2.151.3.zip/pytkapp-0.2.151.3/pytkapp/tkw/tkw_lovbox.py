#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Lovbox - widget based on ttk.Combobox for 
    processing Combobox with separated values and labels
"""

# pytkapp.tkw: combobox with separated lists for values and labels
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
    from tkinter import Tk, StringVar, TclError, Button
    from tkinter.ttk import Combobox as ttkCombobox
    from tkinter.constants import DISABLED
else:
    from Tkinter import Tk, StringVar, TclError, Button
    from ttk import Combobox as ttkCombobox
    from Tkconstants import DISABLED

# fixme: uncomment this block to run script directly OR set pythonpath for your package
#if __name__ == '__main__':
    #import sys
    #import os.path
    #lv_file = __file__
    #while os.path.split(lv_file)[1] != '':
        #lv_file = os.path.split(lv_file)[0]
        #print('append %s'%lv_file)
        #sys.path.append(lv_file)
        
###################################
## globals
###################################         
LOV_READONLY = "readonly"
          
###################################
## classes
###################################  
class LovStringVar(StringVar):
    """ mod for string var """
    
    def __init__(self, master=None, value=None, name=None):
        """ init variable """
                
        self.__wlist = []
        
        StringVar.__init__(self, master=None, value=None, name=None)
        
    def set(self, value):
        """ set value for variable """
        
        StringVar.set(self, value)
        
        self.applyvar(value)
    
    def applyvar(self, value):
        """ apply var. value for widgets """
        
        for widget in self.__wlist:
            try:
                widget.set(value, True)
            except TclError:
                pass
        
    def regwidget(self, widget):
        """ add widget for int. list """
        
        if isinstance(widget, Lovbox):
            self.__wlist.append(widget)
        else:
            raise TypeError('widget with type "%s" cannot be registred with LovStringVar'%widget.__class__)
            
class Lovbox(ttkCombobox):
    """ modified version of combobox """
    
    def __init__(self, parent, **kw):
        """ init widget 
            kw: 
               labels - list of values in combobox       
               values - list of real values
        """
                
        self.__labels = kw.get('labels')
        self.__values = kw.get('values')
                        
        if len(self.__values) != len(self.__labels):
            raise KeyError('mismatch len of values and labels')
                
        lv_state = kw.get('state', LOV_READONLY)
        if lv_state not in (LOV_READONLY, DISABLED):
            raise KeyError('invalid state - should use "readonly" or "disabled"')
        
        lv_var = kw.get('variable', None)
        if lv_var is not None:
            if isinstance(lv_var, LovStringVar):
                self.__var_value = lv_var
                self.__var_value.regwidget(self)
            else:
                raise TypeError('only LovStringVar are acceptable')
        else:
            self.__var_value = None
            
        self.__var_label = StringVar()
        
        # create copy of kw
        ld_kw = {}
        for key in list(kw.keys()):
            if key not in ('textvariable', 'variable', 'values', 'labels', 'state'):
                ld_kw[key] = kw[key]
                
        ld_kw['values'] = self.__labels
        ld_kw['textvariable'] = self.__var_label
        ld_kw['state'] = lv_state
                
        ttkCombobox.__init__(self, parent, **ld_kw)
        self.bind('<<ComboboxSelected>>', self.on_select, '+')

        if self.__var_value.get():
            self.__var_value.set(self.__var_value.get())
        
    def on_select(self, po_event=None):
        """ process selection """
        
        lv_ind = self.__labels.index(self.__var_label.get())
        lv_value = self.__values[lv_ind]
        
        if self.__var_value is not None:
            self.__var_value.set(lv_value)
            
    def set(self, value, oneside=False):
        """ set value """
        
        if value == '':
            lv_label = ''
        else:
            lv_ind = self.__values.index(value)
            lv_label = self.__labels[lv_ind]
        
        ttkCombobox.set(self, lv_label)
        if not oneside:
            if self.__var_value is not None:
                self.__var_value.set(value)
        
    def get(self):
        """ get value """
        
        try:
            lv_ind = self.__labels.index(self.__var_label.get())
        except ValueError:
            return ''
        else:
            return self.__values[lv_ind]
    
    def get_value(self):
        """ get value """
        
        return self.get()
    
    def get_label(self):
        """ get label """
        
        return self.__var_label.get()
    
    def current(self, newindex=None):
        """ set new or get current """
        
        lv_res = ttkCombobox.current(self, newindex)
        if lv_res == -1:
            return lv_res
        elif newindex is None:
            return lv_res
        else:
            self.on_select()
            return lv_res

if __name__ == '__main__':
    root = Tk()
    
    
    ll_values = ['1', '2', '3', '4']
    ll_labels = ['a', 'b', 'c', 'd']
    
    var1 = StringVar()
    var2 = LovStringVar()    
      
    cbox = ttkCombobox(root,
                       textvariable=var1,
                       values=ll_values
                      ) 
    cbox.pack() 
    
    lbox = Lovbox(root,
                  variable=var2,
                  values=ll_values,
                  labels=ll_labels
                 )
    lbox.pack()
    
        
    def __rep():
        try:
            print('cbox: %s'%cbox.get())
        except:
            print('cbox:failed')
        try:
            print('lbox: %s'%lbox.get())
        except:
            print('lbox:failed')
            
    def __test1():
        var1.set(1)
        var2.set(2)
        
    def __test2():
        cbox.current(3)
        lbox.current(2)
        
    def __test3():
        var1.set('')
        var2.set('')
        
    lw_btn0 = Button(root, command=__rep, text='rep')
    lw_btn0.pack(fill="x")
    lw_btn1 = Button(root, command=__test1, text='test1')
    lw_btn1.pack(fill="x")
    lw_btn2 = Button(root, command=__test2, text='test2')
    lw_btn2.pack(fill="x")
    lw_btn3 = Button(root, command=__test3, text='test3')
    lw_btn3.pack(fill="x")
    
    root.mainloop()