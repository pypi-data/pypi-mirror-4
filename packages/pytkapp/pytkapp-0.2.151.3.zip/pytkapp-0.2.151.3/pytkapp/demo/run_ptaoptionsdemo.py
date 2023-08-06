#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" demo for options object """

# pytkapp: container for app options
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
import time
import random
import gettext
if __name__ == '__main__':
    if    sys.hexversion >= 0x03000000:
        gettext.install(__name__)
    else:
        gettext.install(__name__, unicode=True)
elif '_' not in __builtins__:
    _ = gettext.gettext      
        
if    sys.hexversion >= 0x03000000:
    from tkinter import Tk, Frame, Button
    from tkinter.constants import TOP, BOTH, NORMAL, DISABLED, YES, NW
else:
    from Tkinter import Tk, Frame, Button
    from Tkconstants import TOP, BOTH, NORMAL, DISABLED, YES, NW
    
# fixme: uncomment this block to run script directly OR set pythonpath for your package
#if __name__ == '__main__':
    #import sys
    #import os.path
    #lv_file = __file__
    #while os.path.split(lv_file)[1] != '':
        #lv_file = os.path.split(lv_file)[0]
        #print('append %s'%lv_file)
        #sys.path.append(lv_file)
        
from pytkapp.pta_options import OptionsContainer

###################################
## routines
###################################      
def run_demo():
    """ main """
    
    root = Tk()
    root.title('options demo')
    
    rf = Frame( root )
    
    # produce samples for options
    lo_options = OptionsContainer()
    
    # generate samples by groups
    ll_options = []
    ###simples:        name, type, default, reset, export, desc, wstyle, min, max, step, cdata, group
    ll_options.append(('entry',       'str', '', 1, 1, 'entry', 'Entry', None, None, None, None, 'Simples'))
    ll_options.append(('pwdentry',    'str', '', 1, 1, 'password', 'PWDEntry', None, None, None, None, 'Simples'))
    ll_options.append(('spinbox',     'int', 0, 1, 1, 'spinbox', 'Spinbox', 0, 10, 1, None, 'Simples'))
    ll_options.append(('checkbutton', 'int', 0, 1, 1, 'checkbutton', 'Checkbutton', 0, 1, None, None, 'Simples'))
    ll_options.append(('combobox',    'str', 'test1', 1, 1, 'combobox', 'Combobox', None, None, None, ['test1', 'test2', 'test3', 'test4', 'test5'], 'Simples'))
    ll_options.append(('xcombobox',   'str', 'test1', 1, 1, 'xcombobox', 'xCombobox', None, None, None, {'test1':'long desc for test-1', 
                                                                                                         'test2':'long desc for test-2', 
                                                                                                         'test3':'long desc for test-3'}, 'Simples'))
    ll_options.append(('lovbox',    'str', 'test1', 1, 1, 'lovbox', 'Lovbox', None, None, None, {'values':['test1', 'test2', 'test3', 'test4', 'test5'], 
                                                                                                 'labels':['test1-label', 'test2-label', 'test3-label', 'test4-label', 'test5-label']}, 'Simples'))

    ###dialoged entries:name, type, default, reset, export, desc, wstyle, min, max, step, cdata, group
    ll_options.append(('folder',       'str', '', 1, 1, 'folder', 'FolderEntry', None, None, None, None, 'Dialoged entries'))
    ll_options.append(('file',         'str', '', 1, 1, 'file', 'FileEntry', None, None, None, None, 'Dialoged entries'))
    ll_options.append(('date',        'date', '', 1, 1, 'date', 'DateEntry', None, None, None, 'dd.mm.yyyy', 'Dialoged entries'))
    
    ###AListBox:       name, type, default, reset, export, desc, wstyle, min, max, step, cdata, group
    ll_options.append(('alistbox1', 'list', ['test1', 'test2', 'test3', 'test4', 'test5'], 1, 1, 'alistbox with entry',  'AListBox', None, None, None, '' , 'AListBox'))
    ll_options.append(('alistbox2', 'list', ['test1', 'test2', 'test3', 'test4', 'test5'], 1, 1, 'alistbox with combo',  'AListBox', None, None, None, ['test1', 'test2', 'test3', 'test4', 'test5'] , 'AListBox'))
    ll_options.append(('alistbox3', 'list', ['test1', 'test2', 'test3', 'test4', 'test5'], 1, 1, 'alistbox with search', 'AListBox', None, None, None, lambda ui: 'test%s' % random.randint(10, 1000), 'AListBox'))

    ###MListBox:       name, type, default, reset, export, desc, wstyle, min, max, step, cdata, group
    ll_options.append(('mlistbox1', 'list', ['test1', 'test2', 'test3', 'test4', 'test5'], 1, 1, 'moveable listbox',  'MListBox', None, None, None, '' , 'MListBox'))
    
    ###rulezzz:        name, type, default, reset, export, desc, wstyle, min, max, step, cdata, group
    ll_options.append(('e-item1', 'str', '', 1, 1, 'e-item1\ntype "cb0"/"cb1" to change state of "cb-item1"', 'Entry', None, None, None, None, 'Rulezzz'))
    ll_options.append(('e-item2', 'str', '', 1, 1, 'e-item2\n', 'Entry', None, None, None, None, 'Rulezzz'))
    ll_options.append(('e-item3', 'str', '', 1, 1, 'e-item3\n', 'Entry', None, None, None, None, 'Rulezzz'))

    ll_options.append(('cb-item1', 'int',  0, 1, 1, 'cb-item1\ncheck to enable "e-item2"\ndisable for enabling "sb-item1"', 'Checkbutton', 0, 1, None, None, 'Rulezzz'))
    
    ll_options.append(('sb-item1', 'int', 0, 1, 1, 'sb-item1\nchange value >=3/<3 for "e-item3"', 'Spinbox', 0, 10, 1, None, 'Rulezzz'))

    ll_options.append(('d-item1', 'date', '', 1, 1, 'change value for "e-item4"', 'DateEntry', None, None, None, 'dd.mm.yyyy', 'Rulezzz'))
    ll_options.append(('e-item4',  'str', '', 1, 1, 'e-item4', 'Entry', None, None, None, None, 'Rulezzz'))

       
    # configure gui paraneters
    ld_optopts = {}
    ld_optopts['folder']    = {'title':True, 'ro':True, 'twoline':False}
    ld_optopts['file']      = {'title':True, 'ro':True, 'twoline':False}
    ld_optopts['e-item4']   = {'title':True, 'ro':True}
    ld_optopts['date']      = {'title':True, 'width':10}
    ld_optopts['lovbox']    = {'titlse':True, 'width':10}
    ld_optopts['alistbox1'] = {'title':True, 'pheight':5, 'twoline':False}
    ld_optopts['alistbox2'] = {'title':True, 'pheight':5, 'twoline':False}
    ld_optopts['alistbox3'] = {'title':True, 'pheight':5, 'twoline':False}
    ld_optopts['mlistbox1'] = {'title':True, 'pheight':5, 'twoline':False}

    for optdata in ll_options:
        lo_options.register_option(optdata[0], 
                                   optdata[1], 
                                   optdata[2], 
                                   reset=optdata[3], 
                                   export=optdata[4],
                                   desc=_(optdata[5]),
                                   wstyle=optdata[6],
                                   minv=optdata[7],
                                   maxv=optdata[8],
                                   stepv=optdata[9],
                                   cdata=optdata[10],
                                   group=optdata[11])
        
        if optdata[6] in ('Listbox', 'AListBox', 'MListBox',):
            lo_options.set_value(optdata[0], optdata[2][:])
    
    # rules
    lo_options.register_rule('e-item1', 'value', 'cb1', 'cb-item1', 'state', NORMAL)
    lo_options.register_rule('e-item1', 'value', 'cb0', 'cb-item1', 'state', DISABLED)   
    
    lo_options.register_rule('cb-item1', 'state', NORMAL, 'sb-item1', 'state', DISABLED)
    lo_options.register_rule('cb-item1', 'state', DISABLED, 'sb-item1', 'state', NORMAL)
    
    lo_options.register_rule('cb-item1', 'value', 1, 'e-item2', 'state', NORMAL)
    lo_options.register_rule('cb-item1', 'value', 0, 'e-item2', 'state', DISABLED)
    
    lo_options.register_rule('sb-item1', 'value>=', 3, 'e-item3', 'value', 'xxx')
    lo_options.register_rule('sb-item1', 'value<', 3, 'e-item3', 'value', 'yyy')    
    
    lo_options.register_rule('d-item1', 'value>', time.strftime("%d.%m.%Y", time.localtime(time.time())), 'e-item4', 'value', 'Date in future')
    lo_options.register_rule('d-item1', 'value', time.strftime("%d.%m.%Y", time.localtime(time.time())), 'e-item4', 'value', 'This is today')
    lo_options.register_rule('d-item1', 'value<', time.strftime("%d.%m.%Y", time.localtime(time.time())), 'e-item4', 'value', 'This is past')
    
    lo_options.show_optnotebook(rf, ld_optopts)    
        
    # reset all options to fill def.values
    lo_options.reset(1)
    lo_options.fill_thss()
        
    lo_options.force_rules()
           
    rf.pack( side=TOP, fill=BOTH, expand=YES )

    b = Button( root, text='Reset options', command = lambda x=1: lo_options.reset(1))
    b.pack( side=TOP, anchor=NW )
    
    root.protocol("WM_DELETE_WINDOW", lambda r=root: lo_options.notice_of_the_eviction(r, True))
   
    root.update_idletasks()
    root.minsize(root.winfo_reqwidth(), root.winfo_reqheight())
    
    root.mainloop()    
    
if __name__ == '__main__':
    run_demo()
