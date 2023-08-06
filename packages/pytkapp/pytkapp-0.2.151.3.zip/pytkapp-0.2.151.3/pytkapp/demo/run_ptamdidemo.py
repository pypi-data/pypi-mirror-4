#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" demo for MDI app """

# pytkapp: demo for MDI app
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

import sys
import pytkapp.pta_appinfo as pytkapp_info
sys.modules['pytkapp_info'] = pytkapp_info

pytkapp_info.__appname__ = 'PyTkApp MDI Demo'
pytkapp_info.__appdesc__ = 'PyTkApp MDI Demo'

############################################################
## this object will catch sys.stdout, sys.stderr
############################################################
from pytkapp.pta_logger import get_greedlogger
go_greedlogger = get_greedlogger()

###################################
## import
###################################
import time
import threading

import gettext
if __name__ == '__main__':
    if    sys.hexversion >= 0x03000000:
        gettext.install(__name__)
    else:
        gettext.install(__name__, unicode=True)
elif '_' not in __builtins__:
    _ = gettext.gettext

if    sys.hexversion >= 0x03000000:
    from tkinter import Entry
    from tkinter import Label, LabelFrame, Frame, Button
    from tkinter.constants import YES, X, N, S, W, E, LEFT, DISABLED, NORMAL
    import tkinter.messagebox as messagebox
else:
    from Tkinter import Entry
    from Tkinter import Label, LabelFrame, Frame, Button
    from Tkconstants import YES, X, N, S, W, E, LEFT, DISABLED, NORMAL
    import tkMessageBox as messagebox

import pytkapp.pta_icons as pta_icons

from pytkapp.tkw.tkw_routines import make_widget_resizeable, READONLY
from pytkapp.tkw.tkw_xscrolledtext import XScrolledText

from pytkapp.dia.dia_selector import BaseSelector

from pytkapp.pta_child import BaseChild
from pytkapp.pta_app import BaseApp, APP_UI_MODE_MDI
from pytkapp.pta_routines import novl, get_estr, print_envdata

###################################
## classes
###################################
class DemoChild( BaseChild ):
    """ child"""
    
    def __init__( self, pw_container, po_app, **kw ):
        """ init child """

        BaseChild.__init__(self, pw_container, po_app, **kw )
            
    def demo_change_title(self):
        """ demo """
        
        lw_entry = self.get_resource_item('entry')
        lv_value = lw_entry.get()
        
        if novl(lv_value,'').strip() != '':
            self.set_title(lv_value)
            self.get_parentapp().wmenu_configure_item( self.get_id(), 'rename', label=lv_value)
    
    def demo_call_subchild(self):
        """ demo """
        
        lw_entry = self.get_resource_item('entry')
        lv_value = lw_entry.get()
                
        if novl(lv_value,'').strip() != '':        
            self.call_subchild_add(lv_value, 'sub-child (%s)' % (lv_value), DemoSubChild)
    
    def demo_remove_help(self):
        """ demo """
        
        self.set_help([])
    
    def demo_add_help(self):
        """ demo """
        
        lw_log = self.get_resource_item('log')
        self.set_help(lw_log.get_data().split('\n'))
        
    def demo_call_process_start(self):
        """ demo """
        
        if messagebox.askokcancel(_('Confirm'), _('Start demo process ?')):
            self.process_start('Demo', self.demo_process)
            
    def demo_call_process_stop(self):
        """ demo """
        
        if messagebox.askokcancel(_('Confirm'), _('Stop demo process ?')):
            self.process_stop()
        
    def demo_process(self):
        """ demo """
        
        self.otms_logger( {'type':'LOG', 'data':'process: begin'} )
        
        lv_counter = 0
        if self.get_usethreads():
            lv_border = 200
        else:
            lv_border = 20
        
        while lv_counter < lv_border:
            lv_counter += 1
            
            if lv_counter % 10 == 0:
                self.otms_logger( {'type':'LOG', 'data':'process %s/%s' % (lv_counter, lv_border)} )

            if self.get_stop_event().is_set():
                self.otms_logger( {'type':'LOG', 'data':'process was broken on %s/%s' % (lv_counter, lv_border)} )
                break
            
            time.sleep(0.5) 
        
        self.otms_logger( {'type':'LOG', 'data':'process: end'} )
        
        # use this message to set thread = None
        self.otms_logger( {'type':'PROCESS_END', 'data':None} )
        
    def demo_selector(self, po_event=None):
        """ demo for selector """
        
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
        lo_dialog = BaseSelector(self.get_workspace(),
                                 **ld_params
                                )
        lv_result = lo_dialog.show(width=200, height=300, wal=True)
        if lv_result is None:
            self.child_showwarning('Variant was not selected !')
        else:
            self.child_showinfo('Variant: %s' % lv_result)

    def child_gui_reconf(self):
        """ reconf child gui controls """
        
        pass
        
        #if self.get_thread() is None:
            #lw_btn = self.get_resource_item('thstart_btn')
            #lw_btn.configure(state=NORMAL)
            #lw_btn = self.get_resource_item('thstop_btn')
            #lw_btn.configure(state=DISABLED)
        #else:
            #lw_btn = self.get_resource_item('thstart_btn')
            #lw_btn.configure(state=DISABLED)
            #lw_btn = self.get_resource_item('thstop_btn')
            #lw_btn.configure(state=NORMAL)

    def child_create_widgets(self):
        """ fill child workspace """

        # sample of child workspace >>>
        lw_workspace = self.get_workspace()

        lw_frame1 = Frame(lw_workspace)
        
        lw_label = Label(lw_frame1, text='Type some text here:')
        lw_label.grid(row=0, column=0, padx=2, pady=2)

        lw_entry = Entry(lw_frame1)
        lw_entry.grid(row=0, column=1, columnspan=3, padx=2, pady=2, sticky=N+E+W+S)
        self.set_resource_item('entry', lw_entry)
                
        lw_frame1.columnconfigure( 1, weight=1 )
        lw_frame1.grid(row=0, column=0, sticky=N+E+W+S)
                
        lw_frame2 = LabelFrame(lw_workspace, text='Common')
        
        b0 = Button(lw_frame2, text='Selector', command=self.demo_selector)
        b0.grid(row=0, column=0, padx=2, pady=2, sticky=N+E+W+S)
        
        b1 = Button(lw_frame2, text='Change title', command=self.demo_change_title)
        b1.grid(row=0, column=1, padx=2, pady=2, sticky=N+E+W+S)

        b2 = Button(lw_frame2, text='Call sub-child', command=self.demo_call_subchild)
        b2.grid(row=0, column=2, padx=2, pady=2, sticky=N+E+W+S)
                
        b3 = Button(lw_frame2, text='Remove help', command=self.demo_remove_help)
        b3.grid(row=0, column=3, padx=2, pady=2, sticky=N+E+W+S)

        b4 = Button(lw_frame2, text='Fill help from log', command=self.demo_add_help)
        b4.grid(row=0, column=4, padx=2, pady=2, sticky=N+E+W+S)
        
        lw_frame2.grid(row=1, column=0, sticky=N+E+W+S)
        
        lw_frame3 = LabelFrame(lw_workspace, text='Threads')
                
        b1 = Button(lw_frame3, text='Start process', command=self.demo_call_process_start)
        b1.grid(row=0, column=0, padx=2, pady=2, sticky=N+E+W+S)
        self.set_resource_item('thstart_btn', b1)
        self.thread_set_unsafe_item('thstart_btn', b1)
        
        b2 = Button(lw_frame3, text='Stop process', command=self.demo_call_process_stop)
        b2.grid(row=0, column=2, padx=2, pady=2, sticky=N+E+W+S)
        self.set_resource_item('thstop_btn', b2)
        self.thread_set_safe_item('thstop_btn', b2)
        
        lw_frame3.grid(row=2, column=0, sticky=N+E+W+S)

        lw_logframe = Frame(lw_workspace)
        lw_demowidget = XScrolledText(lw_logframe, 
                                      bg="white",
                                      defwidth=70, 
                                      defheight=5, 
                                      search=True,
                                      clear=True,
                                      unload=True,
                                      wstate=READONLY,
                                      presearchcmd=self.child_deactivate,
                                      postsearchcmd=self.child_activate)
        lw_demowidget.grid(row=0, column=0, sticky=N+E+W+S)
        make_widget_resizeable(lw_logframe)
        lw_logframe.grid(row=3, column=0, sticky=N+E+W+S)
        
        lw_workspace.rowconfigure(3, weight=1)
        lw_workspace.columnconfigure(0, weight=1)
                    
        self.set_resource_item('log', lw_demowidget)
        
        self.geom_propagate()
        
        self.otms_logger( {'type':'LOG', 'data':'I am alive !!!'} )
        
        self.family_gui_reconf()

    def options_postconf(self, po_options):
        """ options. routines that should be done after initial configuration """
        
        pass
    
    def child_gui_postinit(self):
        """ post-init routines for gui """
        
        pass
    
    def child_postinit(self):
        """ post init routines """
        
        pass

class DemoSubChild( BaseChild ):
    """ another variant of child """

    def __init__(self, pw_container, po_app, **kw):
        """ initialization of subchild """

        BaseChild.__init__(self, pw_container, po_app,
                           parentw=kw.get( 'parentw', None ),
                           childid=kw.get( 'childid', 'window' ),
                           title=kw.get( 'title', '' ),
                           mw=kw.get( 'mw', 250 ),
                           mh=kw.get( 'mh', 100 ),
                           icon=kw.get( 'icon', pta_icons.gv_subchild_header_icon ) )

    def child_create_widgets(self):
        """ fill child workspace """

        lw_entry = Entry( self.get_workspace(), width=40 )
        lw_entry.pack( side=LEFT, expand=YES, fill=X )
        
    def child_gui_reconf(self):
        """ reconf child gui controls """
        
        pass
    
    def options_postconf(self, po_options):
        """ options. routines that should be done after initial configuration """
        
        pass
    
    def child_gui_postinit(self):
        """ post-init routines for gui """
        
        pass
    
    def child_postinit(self):
        """ post init routines """
        
        pass    
    
class DemoApp( BaseApp ):
    """ demo application"""

    def __init__(self, p_root, **kw):
        """ init app """
        
        BaseApp.__init__(self, p_root, **kw)
        
        lw_log = self.get_logwidget()
        if lw_log is not None:
            go_greedlogger.add_outmethod( threading.current_thread().ident,
                                          lambda message: lw_log.insert_data(message,True)
                                        )
        else:
            go_greedlogger.add_outmethod( threading.current_thread().ident, 'print' )
            
    def app_generate_title(self):
        """ generate string for app title and return it """
        
        return pytkapp_info.get_deftitle()
            
    def app_postinit(self):
        """ post init routines """
        
        pass
    
    def get_default_child_class(self):
        """ get default child class """
        
        return DemoChild
                        
    def options_postconf(self, po_options):
        """ options. routines that should be done after initial configuration """
        
        pass     
    
    def app_reconf_menu(self, **kw):
        """ reconf state of menu items """
        
        pass     

    def app_reconf_toolbar(self, **kw):
        """ reconf state of toolbar controls """
        
        pass 

###################################
## routines
###################################      
def run_demo():
    """ main """
    
    print_envdata()    
    
    ### splash
    # prepare parameters for application's splash window 
    ld_splash = {}
    ld_splash['appname']  = pytkapp_info.get_appname()
    ld_splash['appver']   = '%s' % (pytkapp_info.get_appversion_t(),)
    ld_splash['appurl']   = pytkapp_info.get_appurl()
    ld_splash['bg']  = 'white'
    ld_splash['fg']  = 'black'    
    ld_splash['bd1'] = 1
    ld_splash['bd2'] = 1

    # OR use splashdata=None (OR call app without splashdata keyword)
    #ld_splash = None
    
    ### options
    # prepare options for application
    ll_options = []
    ll_options.append( {'name':'sys_maxchildren',
                        'type':'int',
                        'default':10,
                        'reset':1,
                        'export':0,
                        'wstyle':'Spinbox',
                        'min':1,
                        'max':20,
                        'step':1,
                        'cdata':None,
                        'group':_('System'),
                        'desc':_('maximum number of children')
                        } )
    ll_options.append( {'name':'sys_maxsubchildren',
                        'type':'int',
                        'default':3,
                        'reset':1,
                        'export':0,                                     
                        'wstyle':'Spinbox',
                        'min':1,
                        'max':5,
                        'step':1,
                        'cdata':None,
                        'group':_('System'),
                        'desc':_('maximum number of sub-children')
                        } )
        
    # OR use optionsdata=None (OR call app without optionsdata keyword)
    #ll_options = None
    
    # if you use options - than you can specify rules
    ll_rulesdata = []
    ll_rulesdata.append( ('sys_maxchildren',  # when for option
                          'value>', # it value will be more than
                          10, # 20
                          'sys_maxsubchildren', # then this options
                          'value', # will be setted to
                          5
                          ) )
    ll_rulesdata.append( ('sys_maxchildren',  # when for option
                          'value<=', # it value will be less (or equal) than
                          10, # 20
                          'sys_maxsubchildren', # then this options
                          'value', # will be setted to
                          3
                          ) )
        
    # OR use rulesdata=None (OR call app without rulesdata keyword)
    #ld_rulesdata = None
    
    ### threads
    # set usethreads = True to call routines from child in threads
    lb_usethreads = True
    
    # OR set usetgreads=False (OR dont use usethreads keyword)
    #lb_usethreads = False
    
    ### log
    # set useapplog to True and app will contain Xscrolledtext as log
    lb_useapplog = True    
    # OR set it to False (OR dont use it)
    #lb_useapplog = False
    
    ### about info
    # set aboutlist - app will be display about menu
    ll_aboutlist = []
    ll_aboutlist.append('Here is a sample of about text')
    ll_aboutlist.append('another line...')
    
    # OR set ll_aboutlist=None (OR dont use aboutlist keyword)
    #ll_aboutlist=None
    
    try:
        print('Init application...')
        lo_app = DemoApp( None, 
                          uimode=APP_UI_MODE_MDI,                      
                          splashdata=ld_splash, 
                          optionsdata=ll_options,
                          rulesdata=ll_rulesdata,
                          usethreads=lb_usethreads,
                          aboutlist=ll_aboutlist,
                          useapplog=lb_useapplog,
                          minwidth=640, 
                          minheight=480 )
        
        print('Run application...')
        lo_app.run()
    except:
        print('run-time error:%s'%(get_estr()))

if __name__ == '__main__':
    run_demo()
