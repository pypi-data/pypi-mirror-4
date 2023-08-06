#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" application base class """

# pytkapp: application base class
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
import os
import webbrowser

if 'pytkapp_info' not in sys.modules:    
    import pytkapp.pta_appinfo as pytkapp_info
else:
    pytkapp_info = sys.modules['pytkapp_info']
    
print(pytkapp_info.get_deftitle())

import gettext
if __name__ == '__main__':
    if    sys.hexversion >= 0x03000000:
        gettext.install(__name__)
    else:
        gettext.install(__name__, unicode=True)
elif '_' not in __builtins__:
    _ = gettext.gettext

if    sys.hexversion >= 0x03000000:
    from tkinter import Tk, Menu, StringVar
    from tkinter import PhotoImage, PanedWindow
    from tkinter import Label, Frame, Entry, Menu, Button, Text
    from tkinter.constants import NW, N, S, W, E, YES, LEFT, CENTER, TOP, BOTTOM, BOTH, X, RAISED, SUNKEN, END, DISABLED, NORMAL, NONE
    from tkinter.constants import VERTICAL
    import tkinter.messagebox as messagebox
    
    from urllib.request import urlopen
else:
    from Tkinter import Tk, Menu, StringVar
    from Tkinter import PhotoImage, PanedWindow
    from Tkinter import Label, Frame, Entry, Menu, Button, Text
    from Tkconstants import NW, N, S, W, E, YES, LEFT, CENTER, TOP, BOTTOM, BOTH, X, RAISED, SUNKEN, END, DISABLED, NORMAL, NONE
    from Tkconstants import VERTICAL
    import tkMessageBox as messagebox
    
    from urllib2 import urlopen

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
from pytkapp.pta_options import OptionsContainer, OptionError, OPTIONS_UI_MODE_TK, OPTIONS_UI_MODE_NOTK
from pytkapp.pta_splash import BaseSplash, DummySplash
from pytkapp.pta_routines import get_estr, novl, xprint, DataClip, Others, open_file
from pytkapp.pta_child import BaseChild
from pytkapp.pta_constants import CHILD_ACTIVE, CHILD_DISABLED
from pytkapp.pta_constants import CHILD_UI_MODE_MDI
from pytkapp.pta_constants import LOG_WSTATE_HIDDEN, LOG_WSTATE_NORMAL
from pytkapp.pta_constants import MAGIC_W2L, MAGIC_H_RES, MAGIC_W_RES

from pytkapp.pta_constants import APP_MAX_CHILDREN, APP_MAX_SUBCHILDREN
from pytkapp.pta_constants import APP_UI_MODE_MDI, APP_UI_MODE_SDI
from pytkapp.pta_constants import APP_RECENTLIST_LEN

from pytkapp.tkw.tkw_routines import tk_focus_get, READONLY, bind_children
from pytkapp.tkw.tkw_routines import toplevel_footer, toplevel_header, get_deffonts_dict, apply_fonts2tk
from pytkapp.tkw.tkw_routines import assign_bitmap, toolbar_lbutton_generator, toolbar_separator_generator
from pytkapp.tkw.tkw_xscrolledtext import XScrolledText

###################################
## classes
###################################
class BaseApp():
    """ base application class """

    def __init__(self, p_root, **kw):
        
        self.__initkw = kw
        # app ui mode
        self.__uimode = kw.get('uimode', APP_UI_MODE_MDI)        
        
        if p_root is None:
            self.__root = Tk()
            self.__root.withdraw()
        else:
            if '__root' not in dir(self):
                self.__root = p_root
                
        self.__splashdata = None
        ld_splashdata = kw.get('splashdata', None)
        if ld_splashdata is None:
            lc_splash = DummySplash
            ld_splashdata = {}
        else:
            lc_splash = ld_splashdata.get('customflash', BaseSplash)
            
        with lc_splash(self.__root, **ld_splashdata):
            
            # prepare internal structures
            self.__deffonts = None
            self.__lasth = None
            self.__lastc = None
            
            # attrs >>>
            lv_minwidth = kw.get( 'minwidth', MAGIC_H_RES )
            lv_minheight = kw.get( 'minheight', MAGIC_W_RES )
    
            self.__active_child = None
            
            self.__idsclip = DataClip(5, None)
            
            self.__av_numerator = 0
    
            self.__sb_stringvar1 = StringVar()
            self.__sb_stringvar2 = StringVar()
            self.__sb_stringvar3 = StringVar()
    
            self.__ad_gui_ess_items = {}
            self.__ad_gui_std_items = {}
            self.__ad_resources = {}
    
            self.__al_children = []
            self.__ad_children = {}
            self.__ad_id2label = {}
            self.__ad_images = {}
    
            self.__menu = None
            self.__toolbar = None
            self.__desktop = None
            self.__workspace = None
            
            self.__useapplog = kw.get('useapplog', False)
            self.__logspace = None
            self.__logwidget = None
            self.__logwstate = LOG_WSTATE_NORMAL            
            self.__statusbar = None
            
            self.__usethreads = kw.get('usethreads', False)
            
            self.__splashdata = ld_splashdata

            # about >>>
            self.__aboutlist = kw.get('aboutlist', [])
            if not isinstance(self.__aboutlist, list):
                self.__aboutlist = []
            
            # options >>>
            ll_optionsdata = kw.get('optionsdata', None)
            ll_rulesdata = kw.get('rulesdata', None)
            
            if self.__uimode in [APP_UI_MODE_MDI, APP_UI_MODE_SDI]:
                lv_optmode = OPTIONS_UI_MODE_TK
            else:
                lv_optmode = OPTIONS_UI_MODE_NOTK                
            self.__options = OptionsContainer(lv_optmode)
            
            if ll_optionsdata is not None:
                try:
                    self.options_initconf(self.__options, ll_optionsdata, ll_rulesdata, regonly=True)
                except OptionError as x:
                    lv_outmessage = x.message
                    xprint(lv_outmessage)
                    sys.exit(2)    
                   
            if lv_optmode != OPTIONS_UI_MODE_NOTK:
                # expand options with styles and colors
                try:
                    lw_tempe = Entry()
                    lw_tempm = Menu()
                    lw_tempb = Button()
                    lw_tempt = Text()
                    
                    lv_hbg_a    = lw_tempt.cget('selectbackground')
                    lv_hfg_a    = lw_tempt.cget('selectforeground')
                    #lv_hbg_a    = lw_tempm.cget('activebackground')
                    #lv_hfg_a    = lw_tempm.cget('activeforeground')
                    lv_hbg_ina  = lw_tempe.cget('disabledbackground')
                    lv_hfg_ina  = lw_tempe.cget('disabledforeground')
                    lv_hbbg_a   = lw_tempb.cget('activebackground')
                    lv_hbbg_ina = lw_tempb.cget('background')
                    
                    lw_tempe.destroy()
                    lw_tempm.destroy()
                    lw_tempb.destroy()
                    lw_tempt.destroy()
        
                    ll_styleoptions = []
                    ll_styleoptions.append( {'name':'sys.child.header.bg.active', 'type':'str', 'default':lv_hbg_a,
                                             'reset':1, 'export':0, 'wstyle':'Entry',
                                             'min':None, 'max':None, 'step':None, 'cdata':None,
                                             'group':None, 'desc':'' } )
                    ll_styleoptions.append( {'name':'sys.child.header.fg.active', 'type':'str', 'default':lv_hfg_a,
                                             'reset':1, 'export':0, 'wstyle':'Entry',
                                             'min':None, 'max':None, 'step':None, 'cdata':None,
                                             'group':None, 'desc':'' } )
                    ll_styleoptions.append( {'name':'sys.child.header.bg.inactive', 'type':'str', 'default':lv_hbg_ina,
                                             'reset':1, 'export':0, 'wstyle':'Entry',
                                             'min':None, 'max':None, 'step':None, 'cdata':None,
                                             'group':None, 'desc':'' } )
                    ll_styleoptions.append( {'name':'sys.child.header.fg.inactive', 'type':'str', 'default':lv_hfg_ina,
                                             'reset':1, 'export':0, 'wstyle':'Entry',
                                             'min':None, 'max':None, 'step':None, 'cdata':None,
                                             'group':None, 'desc':'' } )
                    ll_styleoptions.append( {'name':'sys.child.hbutton.bg.active', 'type':'str', 'default':lv_hbbg_a,
                                             'reset':1, 'export':0, 'wstyle':'Entry',
                                             'min':None, 'max':None, 'step':None, 'cdata':None,
                                             'group':None, 'desc':'' } )
                    ll_styleoptions.append( {'name':'sys.child.hbutton.bg.inactive', 'type':'str', 'default':lv_hbbg_ina,
                                             'reset':1, 'export':0, 'wstyle':'Entry',
                                             'min':None, 'max':None, 'step':None, 'cdata':None,
                                             'group':None, 'desc':'' } )
                    self.options_initconf(self.__options, ll_styleoptions, [])
                except Others:
                    lv_outmessage = get_estr()
                    xprint(lv_outmessage)
                    sys.exit(2)                
                    
            # widgets >>>
            self.app_gui_initconf()            
            
            self.app_create_widgets(**kw)            
    
            # geometry >>>
            self.__toolbar.pack( side = TOP, fill = X )
            self.__desktop.pack( side = TOP, expand=YES, fill=BOTH )
            self.__statusbar.pack( side = BOTTOM, fill=X )
    
            self.__root.update_idletasks()
            ws_x = self.__root.winfo_rootx()+50
            ws_y = self.__root.winfo_rooty()+50
            lv_width  = max(self.__root.winfo_reqwidth(), lv_minwidth)
            lv_height = max(self.__root.winfo_reqheight(), lv_minheight)
            self.__root.geometry(str(lv_width)+"x"+str(lv_height)+"+"+str(ws_x)+"+"+str(ws_y))
            self.__root.minsize(lv_width, lv_height)
    
            self.__root.protocol("WM_DELETE_WINDOW", self.call_app_close)
            self.__root.resizable(True, True)
            
            self.app_postinit()
            
    def app_create_widgets(self, **kw):
        """ create widgets """
        
        self.app_create_menu()
        self.app_create_toolbar()
        self.app_create_desktop(kw.get('useapplog', False))
        self.app_create_statusbar()        
            
    def app_postinit(self):
        """ post init routines - use it for SDI app (see demo) """
        
        raise NotImplementedError
            
    def get_uimode(self):
        """ return ui mode """
        
        return self.__uimode
    
    def app_generate_title(self):
        """ generate string for app title and return it """
        
        return pytkapp_info.get_deftitle()
                
    def get_deffonts(self):
        """ return fonts dict """
        
        return self.__deffonts
    
    def set_deffonts(self, pd_fonts):
        """ set deffonts """
        
        self.__deffonts = pd_fonts
        
    def get_root(self):
        """ return app root """
        
        return self.__root
        
    def get_usethreads(self):
        """ return value of usethreads flag """
        
        return self.__usethreads
    
    def get_useapplog(self):
        """ return value of useapplog flag """
        
        return self.__useapplog 
    
    def get_options(self):
        """ return options object """
        
        return self.__options
    
    def options_sync(self, option_key):
        """ call sync for spec. option """
        
        if self.__options is not None:
            self.__options.sync_(option_key)
    
    def options_get_value(self, option_key, pv_readthss=False, p_copy=False):
        """ get value of spec. option """
        
        if self.__options is not None:
            return self.__options.get_value(option_key, pv_readthss, p_copy)
        else:
            return None
        
    def options_set_value(self, option_key, option_value, pb_chdef=False, pb_writethss=False):
        """ set value for spec. option """
        
        if self.__options is not None:
            return self.__options.set_value(option_key, option_value, pb_chdef, pb_writethss)
        else:
            return None
            
    def options_append_value(self, option_key, option_value):
        """ append value to option-list """
        
        if self.__options is not None:
            return self.__options.append_value(option_key, option_value)
        else:
            return None 
    
    def options_initconf(self, po_options, pl_options, pl_rules, **kw):
        """ fill options and rules """
        
        # options itself >>>
        for optiondata in pl_options:
            po_options.register_option( optiondata['name'],
                                        optiondata['type'],
                                        optiondata['default'],
                                        reset=optiondata.get('reset',1),
                                        export=optiondata.get('export',0),
                                        desc=optiondata.get('desc','???'),
                                        wstyle=optiondata.get('wstyle',None),
                                        minv=optiondata.get('min',0),
                                        maxv=optiondata.get('max',1),
                                        stepv=optiondata.get('step',None),
                                        cdata=optiondata.get('cdata',None),
                                        group=optiondata.get('group',None)
                                      ) 
            
        # rules - if exists >>>
        if pl_rules is not None:
            for ruledata in pl_rules:
                po_options.register_rule( *ruledata )
                
        if not kw.get('regonly', False):
            # reset options >>>
            po_options.reset(force=1)
            
            self.options_postconf(po_options)
        
    def options_postconf(self, po_options):
        """ options. routines that should be done after initial configuration """
        
        pass
        
    def get_al_children( self, pv_index=None ):
        """ return children or copy of al_children list """
        
        try:
            return self.__al_children[pv_index]
        except IndexError:
            return self.__al_children[:]
    
    def get_ad_children_keys( self ):
        """ get keys of ad_children """
        
        return list( self.__ad_children.keys() )
    
    def get_ad_children( self, pv_childid ):
        """ get children from ad_children """
        
        return self.__ad_children.get( pv_childid, None )
    
    def get_resource_item( self, pv_name ):
        """ get some ctrl item """

        return self.__ad_resources.get( pv_name, None )

    def set_resource_item( self, pv_name, pv_value ):
        """ set some ctrl item """

        self.__ad_resources[ pv_name ] = pv_value

    def get_gui_std_keys( self ):
        """ return list with std gui keys """

        return list( self.__ad_gui_std_items.keys() )

    def get_gui_std_item( self, pv_name ):
        """ return item for gui items """

        return self.__ad_gui_std_items.get( pv_name, None )

    def set_gui_std_item( self, pv_name, pw_item ):
        """ set std gui items """

        self.__ad_gui_std_items[ pv_name ] = pw_item

    def get_gui_ess_keys( self ):
        """ return list with ess gui keys """

        return list( self.__ad_gui_ess_items.keys() )

    def get_gui_ess_item( self, pv_name ):
        """ return item for gui items """

        return self.__ad_gui_ess_items.get( pv_name, None )

    def set_gui_ess_item( self, pv_name, pw_item ):
        """ set std gui items """

        self.__ad_gui_ess_items[ pv_name ] = pw_item

    def get_menu( self ):
        """ get menu widget """

        return self.__menu

    def get_toolbar( self ):
        """ get toolbar widget """

        return self.__toolbar

    def get_workspace( self ):
        """ get workspace frame """

        return self.__workspace

    def get_logspace( self ):
        """ get log item """

        return self.__logspace
    
    def get_logwidget( self ):
        """ return log widget """
        
        return self.__logwidget

    def get_statusbar( self ):
        """ get statusbar widget """

        return self.__statusbar

    def set_sb_stringvar( self, pv_index, pv_text ):
        """ set StringVar that displayed in status bar (index in 1,2,3) """

        if   pv_index == 1:
            self.__sb_stringvar1.set( pv_text )
        elif pv_index == 2:
            self.__sb_stringvar2.set( pv_text )
        elif pv_index == 3:
            self.__sb_stringvar3.set( pv_text )
            
    def call_app_children_close(self):
        """ call to close all children """
        
        if self.app_askokcancel(_("Close all opened children ?")):
            self.app_children_close()
            
    def app_children_close(self):
        """ close all opened children and stop their threads """
        
        for wid in self.__al_children[:]:
            self.app_child_close(wid)  
            
        self.__active_child = None
        self.app_focus2child_set( None, 'app_children_close' )        

    def app_close( self ):
        """ close entire app """

        self.app_children_close()
        self.__root.quit()
        self.__root.destroy()

    def call_app_close(self):
        """ call close app """

        lw_focus = tk_focus_get( self.__root )
        if lw_focus is None or self.__root == lw_focus.winfo_toplevel():
            if self.app_askokcancel(_("Do you really want to quit ?")):
                self.app_close()

    def app_create_menu(self):
        """ create top-level menu """
        self.__menu = Menu(self.__root, relief=RAISED)
        self.__root.config(menu=self.__menu)

        self.menu_initconf()

    def menu_add_command(self, p_menu, p_name, p_command, p_state=NORMAL):
        """ add command into app menu """

        ld_menu_draft = self.__ad_resources['menu_draft']

        if p_name in ld_menu_draft:

            lv_image = ld_menu_draft[p_name].get('image', None)

            p_menu.add_command( label=ld_menu_draft[p_name]['label'], command=p_command, state=p_state )
            if lv_image is not None:
                try:
                    img = PhotoImage( data=lv_image )
                except Others:
                    img = None
                if img is not None:
                    p_menu.entryconfigure(END, compound=LEFT, image=img)
                    self.__ad_images[p_name] = img

    def menu_create_wmenu(self):
        """ create default menu for window management """

        if self.__menu is not None:
            lw_menu = Menu(self.__menu, tearoff=0)
            self.__ad_resources['wmenu'] = lw_menu

            self.__menu.add_cascade(label=self.__ad_resources['menu_draft']['wmenu']['label'], menu=lw_menu)
            self.menu_add_command(lw_menu, 'maximize', self.call_app_activechild_maximize, DISABLED )
            self.menu_add_command(lw_menu, 'restore', self.call_app_activechild_restore, DISABLED )
            lw_menu.add_separator()
            self.menu_add_command(lw_menu, 'cascade', self.call_app_children_cascade, DISABLED )
            self.menu_add_command(lw_menu, 'tile', self.call_app_children_tile, DISABLED )

    def menu_create_amenu(self):
        """ create default about menu """
        
        if self.__menu is not None:
            lw_menu = Menu(self.__menu, tearoff=0)
            self.__ad_resources['amenu'] = lw_menu
            self.__menu.add_cascade(label=self.__ad_resources['menu_draft']['amenu']['label'], menu=lw_menu)
            
            if novl(pytkapp_info.get_appmarker(), '') != '':
                self.menu_add_command(lw_menu, 'cupd_menu', self.call_amenu_check_forupd )        

            if len(self.__aboutlist) > 0:
                self.menu_add_command(lw_menu, 'about_menu', self.call_amenu_about_window )        
                
    def menu_create_omenu(self):
        """ create default menu for options """
        
        if self.__menu is not None:
            lw_menu = Menu(self.__menu, tearoff=0)
            self.__ad_resources['omenu'] = lw_menu
            
            self.__menu.add_cascade(label=self.__ad_resources['menu_draft']['omenu']['label'], menu=lw_menu)
            self.menu_add_command(lw_menu, 'pref_options', self.call_options_window )

    def optwindow_post_optnotebook(self, pw_toplevel, pw_frame, pd_widgets):
        """ process additional conf. for options widgets on opt.window """
        
        pass
    
    def optwindow_post_window(self):
        """ process here some routines that necessary after changing some opt.."""
        
        self.__options.fill_thss()        
        
    def get_logos_data(self, pv_key=None):
        """ return tuple as (path,file),
           path - folder with icons
           file - filename of icon 
           they will use for toplevels
        """
        
        return (None, None)
    
    def get_recentlen(self):
        """get len of recent list specifief for console or app"""
        
        lv_recentlen = self.options_get_value('sys_recentlen')
            
        return novl(lv_recentlen, APP_RECENTLIST_LEN)
    
    def get_classname(self):
        """get class name"""
        
        return str(self.__class__).split('.')[-1]
    
    def optwindow_prepare_optopts(self):
        """ return dict with options attrs for displaing """
        
        ld_optopts = {}       
        
        return ld_optopts
    
    def optwindow_prepare_excluded_groups(self):
        """ return list of groups that we want to hide"""
        
        ll_exlist = ['<unassigned>']
        
        return ll_exlist
    
    def optwindow_prepare_excluded_options(self):
        """ return list of options that we want to hide"""
        
        ll_exlist = []
        
        return ll_exlist
    
    def call_amenu_check_forupd(self, event=None):
        """ check for updates """
        
        self.app_activechild_state_set(CHILD_DISABLED)
        try:
            # get data
            lv_url = novl(pytkapp_info.get_appurl(), '')
            
            lf_web = urlopen(pytkapp_info.get_appmarker())            
            lv_data = lf_web.read()
                        
            lv_check = pytkapp_info.cmp_version(lv_data)
            
            if lv_check >= 0:                
                lv_title   = _('No updates found !')
                lv_message = _('You have latest version of the application')
                lv_detail  = ''

                messagebox.showinfo(lv_title, 
                                    lv_message
                                   )
            else:
                lv_title   = _('Update found !')                
                lv_detail  = _('Current version: %s') % pytkapp_info.get_appversion() + '\n' + \
                             _('Available version: %s') % lv_data

                if lv_url != '':
                    lv_message = _('Visit project site ?')
                    if self.app_askokcancel(lv_message, 
                                            title=lv_title, 
                                            detail=lv_detail,
                                           ):
                        webbrowser.open(lv_url)                    
                else:
                    lv_message = _('Please visit project site')
                    messagebox.showinfo(lv_title, 
                                        lv_message, 
                                        detail=lv_detail,
                                       )                    
        except Others:
            lv_message = 'failed to check updates: %s' % (get_estr())
            xprint(lv_message)
           
        self.app_activechild_state_set(CHILD_ACTIVE)
        
        # use this if you bind routine to some widgets
        return "break"       
    
    def call_amenu_about_window(self, event=None):
        """ show app about info """
        
        self.app_activechild_state_set(CHILD_DISABLED)
        try:
            lt_logos = self.get_logos_data()
            
            lw_toplevel, lw_frame = toplevel_header( self.__root,
                                                     title=_('About'),
                                                     logopath=lt_logos[0],
                                                     logoname=lt_logos[1]
                                                   )
            
            ld_splashdata = novl(self.get_splashdata(), {})
            if isinstance(ld_splashdata, dict) and len(ld_splashdata.keys()) > 0:
                lw_headerframe = Frame(lw_frame)
            
                lv_bg = ld_splashdata.get('bg', 'gray')
                lv_fg = ld_splashdata.get('fg', 'black')
                
                ld_fonts = get_deffonts_dict()
                
                if ld_splashdata.get('appicon', None) is not None:
                    lw_logoframe = Frame(lw_headerframe, background=lv_bg)
                    lv_img = PhotoImage(data=ld_splashdata['appicon'])
                    lw_icon = Label(lw_logoframe, image=lv_img, background=lv_bg)
                    lw_icon.img = lv_img
                    lw_icon.grid(row=0, column=0, sticky=N+E+W+S, padx=0, pady=0)                    
                    lw_logoframe.rowconfigure( 0, weight = 1 )
                    lw_logoframe.grid(column=0, row=0, sticky=N+E+W+S, padx=1, pady=1)
                    if ld_splashdata.get('appurl', None) is not None:
                        lw_logoframe.configure(cursor="hand2")
                        lw_icon.bind('<ButtonPress-1>', lambda x=1: webbrowser.open(ld_splashdata['appurl']))
                        lw_logoframe.bind('<ButtonPress-1>', lambda x=1: webbrowser.open(ld_splashdata['appurl']))
                
                lw_textframe = Frame( lw_headerframe, background=lv_bg )
                l = Label(lw_textframe,
                          text=ld_splashdata.get('appname','???'),
                          anchor=CENTER,
                          font=ld_splashdata.get('f1', ld_fonts['biglogolabel']),
                          background=lv_bg,
                          fg=lv_fg)
                l.grid(row=0, column=0, sticky=N+E+W, padx=2, pady=0)
        
                l = Label(lw_textframe,
                          text='%s' % (ld_splashdata.get('appver','???'),),
                          anchor=CENTER, 
                          font=ld_splashdata.get('f2', ld_fonts['biglogolabel']),
                          background=lv_bg,
                          fg=lv_fg)
                l.grid(row=1, column=0, sticky=N+E+W, padx=2, pady=0)
                
                if ld_splashdata.get('appurl', None) is not None:
                    lw_textframe.configure(cursor="hand2")
                    l = Label(lw_textframe,
                              text=ld_splashdata['appurl'],
                              anchor=CENTER,
                              font=ld_splashdata.get('f2', ld_fonts['biglogolabel']),
                              background=lv_bg,
                              fg=lv_fg)
                    l.grid(row=2, column=0, sticky=N+E+W, padx=2, pady=0)
                    lw_textframe.bind('<ButtonPress-1>', lambda x=1: webbrowser.open(ld_splashdata['appurl']))
                    bind_children(lw_textframe, '<ButtonPress-1>', lambda x=1: webbrowser.open(ld_splashdata['appurl']))
                    
                lw_textframe.columnconfigure( 0, weight=1 )
                lw_textframe.grid(column=1, row=0, sticky=N+E+W+S, padx=1, pady=1)
                
                lw_headerframe.columnconfigure( 1, weight=1 )                
                lw_headerframe.pack(side=TOP, fill=X)
            
            lw_text = XScrolledText(lw_frame, 
                                    bg="white",
                                    defwidth=50, 
                                    defheight=10, 
                                    search=True,
                                    wrap=NONE,
                                    wstate=READONLY)
            for about_line in self.__aboutlist:
                lw_text.insert_data( about_line.rstrip()+'\n' )
                
            lw_text.pack(side=TOP, fill=BOTH, expand=YES)
            
            toplevel_footer(lw_toplevel, self.__root)
        except Others:
            lv_message = 'failed to call about window: %s' % (get_estr())
            xprint(lv_message)
           
        self.app_activechild_state_set(CHILD_ACTIVE)
        
        # use this if you bind routine to some widgets
        return "break"       
    
    def get_aboutlist(self):
        """ return about content """
        
        return self.__aboutlist
    
    def get_splashdata(self):
        """ return splashdata """
        
        return self.__splashdata

    def call_options_window(self, event=None):
        """ show app options as Notebook widget """
        
        self.app_activechild_state_set(CHILD_DISABLED)
        try:
            ld_optopts  = self.optwindow_prepare_optopts()
            ll_exgroups = self.optwindow_prepare_excluded_groups()
            ll_exopts   = self.optwindow_prepare_excluded_options()
            
            lt_logos = self.get_logos_data()
            
            lw_toplevel, lw_frame = toplevel_header( self.__root,
                                                     title=_('Options'),
                                                     logopath=lt_logos[0],
                                                     logoname=lt_logos[1]
                                                   )
            
            ld_items = self.__options.show_optnotebook( lw_frame,
                                                        ld_optopts,
                                                        excluded_groups=ll_exgroups,
                                                        excluded_options=ll_exopts
                                                      )
            
            self.__options.force_rules()
            
            lw_toplevel.protocol("WM_DELETE_WINDOW", lambda w=lw_toplevel: self.__options.notice_of_the_eviction(w, True))
            
            self.optwindow_post_optnotebook(lw_toplevel, lw_frame, ld_items)
            
            toplevel_footer(lw_toplevel, self.__root, min_width=50, min_height=50)        
        except Others:
            lv_message = 'failed to call options window: %s' % (get_estr())
            xprint(lv_message)
           
        self.optwindow_post_window()
        self.app_activechild_state_set(CHILD_ACTIVE)
        
        # use this if you bind routine to some widgets
        return "break"
    
    def get_defoptnames(self):
        """ return default path and name from options file """
        
        return (os.getcwd(), 'default.opt')
    
    def call_options_export(self, pw_parent=None, pt_names=None):
        """ call to export options """
        
        if self.app_askokcancel(_('Export options ?'), parent=pw_parent):
            try:
                if pt_names is None:
                    lt_names = self.get_defoptnames()
                else:
                    lt_names = pt_names
                    
                # save             
                lv_res = self.options_export(lt_names[0], lt_names[1], makebak=True)
                if lv_res is not None:
                    lv_message = 'export error: %s' % (lv_res)
                    xprint(lv_message)
                else:
                    messagebox.showinfo(_('Info'), _('Options exported !'), parent=pw_parent)
            except Others:
                lv_message = 'failed to export options: %s' % (get_estr())
                xprint(lv_message)
                
    def options_export(self, filepath, filename, **kw):
        """ try to call option's export """
        
        if self.__options is not None:
            return self.__options.export_( filepath, filename, **kw)
        else:
            return None
        
    def call_options_import(self, pw_parent=None, pt_names=None, pb_force=False):
        """ call to import options """
        
        if pb_force or self.app_askokcancel(_('Import options ?'), parent=pw_parent):
            try:
                if pt_names is None:
                    lt_names = self.get_defoptnames()
                else:
                    lt_names = pt_names
                    
                # save             
                lv_res = self.options_import(lt_names[0], lt_names[1])
                
                if lv_res == '-1':
                    lv_message = 'options is not been exported yet'
                    xprint(lv_message)  
                elif lv_res is not None:
                    lv_message = 'import error: %s' % (lv_res)
                    xprint(lv_message)          
                else:
                    if not pb_force:
                        messagebox.showinfo(_('Info'), _('Options imported !'), parent=pw_parent)
                    else:
                        lv_message = 'options was imported !'
                        xprint(lv_message)                      
            except Others:
                lv_message = 'failed to import options: %s' % (get_estr())
                xprint(lv_message)
                
    def options_import(self, filepath, filename, **kw):
        """ try to call option's import """
        
        if self.__options is not None:
            return self.__options.import_( filepath, filename, **kw)
        else:
            return None                
                
    def call_options_reset(self, pw_parent=None):
        """ call to reset options """
        
        if self.app_askokcancel(_('Reset options ?'), parent=pw_parent):
            self.__options.reset()
        
    def wmenu_reconf_controls( self, pv_state=NORMAL ):
        """ reconfigure window controls - menu, toolbar """

        # menu
        lw_wmenu = self.__ad_resources['wmenu']
        for i in range( 6 ):
            if i == 5:
                if pv_state == NORMAL:
                    lw_wmenu.add_separator()
                else:
                    lw_wmenu.delete( i )
            else:
                if lw_wmenu.type( i ) != 'separator':
                    lw_wmenu.entryconfigure( i, state=pv_state )

        # toolbar
        for wname in [ 'wtoolbar_del', 'wtoolbar_cascade', 'wtoolbar_tile', 'wtoolbar_closeall']:
            lw_wtoolbar_item = self.get_gui_std_item( wname )
            if lw_wtoolbar_item is not None:
                lw_wtoolbar_item.configure( state = pv_state )

    def wmenu_configure_item( self, pv_wid, pv_action, **kw ):
        """ configure item in default window menu """

        lw_wmenu = self.__ad_resources['wmenu']
        lv_wlen = lw_wmenu.index(END)+1
        lv_windex = None
        
        # get current label
        lv_label = self.__ad_id2label.get(pv_wid, None)
        if lv_label is not None:
            for lv_index in range(5, lv_wlen):
                if lw_wmenu.type(lv_index) != 'separator':
                    lv_wlabel = lw_wmenu.entrycget(lv_index,'label')
                    if lv_wlabel == lv_label:
                        lv_windex = lv_index
                        break
                    
        if pv_action in ('add', 'addsingle', 'rename'):        
            lv_newlabel = '%s %s' % (pv_wid, kw.get('label',''))
            lv_newlabel = lv_newlabel.strip()
        else:
            lv_newlabel = ''
                    
        if lv_windex is not None:
            if pv_action == 'delete':
                lw_wmenu.delete( lv_windex )
            elif pv_action == 'recommand':
                lw_wmenu.entryconfigure( lv_windex,
                                         command = lambda wid=pv_wid:self.app_focus2child_set(wid, 'menu'))
            elif pv_action == 'rename':
                lw_wmenu.entryconfigure( lv_windex,
                                         label = lv_newlabel)
                self.set_id2label(pv_wid, lv_newlabel)
            elif pv_action == 'add_sub':
                lv_wid    = kw.get('wid','')
                lv_wlabel = kw.get('label','')

                lw_submenupath = lw_wmenu.entrycget( lv_windex, 'menu' )
                lw_submenu = lw_wmenu.children[ lw_submenupath.split('.')[-1] ]

                if lw_submenu.index(END) == 0:
                    lw_submenu.add_separator()

                lw_submenu.add_command( label = lv_wlabel,
                                        command = lambda ch_id=lv_wid:self.app_focus2child_set(ch_id,'submenu'))
                
                self.set_id2label(lv_wid, lv_newlabel)                
            elif pv_action == 'del_sub':
                lv_wid    = kw.get('wid','')

                lw_submenupath = lw_wmenu.entrycget( lv_windex, 'menu' )
                lw_submenu = lw_wmenu.children[ lw_submenupath.split('.')[-1] ]

                # loop at submenu - search id
                lv_sublabel = self.__ad_id2label[ lv_wid ]
                for lv_index in range(lw_submenu.index(END)+1):
                    if lw_submenu.type(lv_index) != 'separator':
                        lv_submlabel = lw_submenu.entrycget(lv_index,'label')
                        if lv_submlabel == lv_sublabel:
                            lw_submenu.delete( lv_index )
                            break
                if lw_submenu.index(END) == 1:
                    lw_submenu.delete( END )                    
        elif pv_action == 'add':
            lv_wmainlabel = kw.get('wmainlabel', _('Main window'))

            lw_submenu = Menu(lw_wmenu, tearoff=0)

            lw_submenu.add_command(label = lv_wmainlabel,
                                   command = lambda ch_id=pv_wid:self.app_focus2child_set(ch_id,'menu'))

            lw_wmenu.add_cascade(label = lv_newlabel,
                                 menu = lw_submenu)
            self.set_id2label(pv_wid, lv_newlabel)
        elif pv_action == 'addsingle':
            lw_wmenu.add_command(label = lv_newlabel,
                                 command = lambda ch_id=pv_wid:self.app_focus2child_set(ch_id,'menu'))
            self.set_id2label(pv_wid, lv_newlabel)

    def app_create_toolbar(self):
        """ create app toolbar """

        self.__toolbar = Frame(self.__root, relief=RAISED, bd=2)
        self.toolbar_initconf()
        
    def toolbar_create_lbtns(self, **kw):
        """ create default log-related buttons """
        
        ld_toolbar_draft = self.get_resource_item('toolbar_draft')
        
        lw_frame = Frame( self.get_toolbar(), padx=2, pady=2 )
        self.set_gui_std_item( 'ltoolbar_frame', lw_frame )        
                
        item = toolbar_lbutton_generator(lw_frame, ld_toolbar_draft['tooglelog_btn']['label'], pta_icons.gv_app_toolbar_toogle_logpane, NORMAL, self.app_reconf_logpane)
        item.configure(relief=SUNKEN)
        self.set_gui_std_item( 'ltb_tooglelog_btn', item )        
        
        toolbar_separator_generator(lw_frame)
        
        lw_frame.pack(side=LEFT)
        
    def toolbar_create_wbtns(self, **kw):
        """ create default toolbar buttons """

        ld_toolbar_draft = self.get_resource_item('toolbar_draft')

        lw_frame = Frame( self.get_toolbar(), padx=2, pady=2 )
        self.set_gui_std_item( 'wtoolbar_frame', lw_frame )

        if kw.get('add', True):
            # add window
            item = toolbar_lbutton_generator(lw_frame, ld_toolbar_draft['add_btn']['label'], pta_icons.gv_app_toolbar_add, NORMAL, lambda x=1: self.call_app_child_add(self.get_default_child_class()))
            self.set_gui_std_item( 'wtoolbar_add', item )

        if kw.get('close', True):
            # close window
            item = toolbar_lbutton_generator(lw_frame, ld_toolbar_draft['close_btn']['label'], pta_icons.gv_app_toolbar_close, DISABLED, self.call_app_activechild_close)
            self.set_gui_std_item( 'wtoolbar_del', item )

        if kw.get('cascade', True):
            # cascade window
            item = toolbar_lbutton_generator(lw_frame, ld_toolbar_draft['cascade_btn']['label'], pta_icons.gv_app_toolbar_cascade, DISABLED, self.call_app_children_cascade)
            self.set_gui_std_item( 'wtoolbar_cascade', item )
            
        if kw.get('tile', True):
            # tile window
            item = toolbar_lbutton_generator(lw_frame, ld_toolbar_draft['tile_btn']['label'], pta_icons.gv_app_toolbar_tile, DISABLED, self.call_app_children_tile)
            self.set_gui_std_item( 'wtoolbar_tile', item )

        if kw.get('closeall', True):
            # close all window
            item = toolbar_lbutton_generator(lw_frame, ld_toolbar_draft['closeall_btn']['label'], pta_icons.gv_app_toolbar_closeall, DISABLED, self.call_app_children_close)
            self.set_gui_std_item( 'wtoolbar_closeall', item )

        lw_frame.pack(side=LEFT)

    def app_create_logspace(self):
        """ create log space """

        self.__logspace = Frame(self.__desktop, relief=RAISED, bd=1)
        
        lw_label = Label(self.__logspace, text=_('Log'))
        lw_label.pack(side=TOP, anchor=NW)
        
        if self.__options:
            lv_logpath = self.options_get_value('app:log')        
        else:
            lv_logpath = os.getcwd()
        lv_logpath = novl(lv_logpath, os.getcwd())
            
        self.__logwidget = XScrolledText(self.__logspace, 
                                         unloaddir=lv_logpath,
                                         wrap=NONE,
                                         takefocus=0,
                                         defheight=5, 
                                         search=True,
                                         clear=True,
                                         unload=True,
                                         print_=True,
                                         wstate=READONLY)
        self.__logwidget.pack(side=BOTTOM, expand=YES, fill=BOTH)

    def app_create_workspace(self):
        """ create main workspace """

        self.__workspace = Frame(self.__desktop, takefocus=1, bg="dark gray", relief=SUNKEN)
        
    def app_create_desktop(self, addlog=False):
        """ create gui desktop """
        
        self.__desktop = PanedWindow(self.__root, 
                                     bd=1, 
                                     sashwidth=4,
                                     relief=SUNKEN, 
                                     orient=VERTICAL,
                                     opaqueresize=False)
        
        lv_minheight = self.__initkw.get('minheight', MAGIC_H_RES)
        lv_wprc = MAGIC_W2L
                
        self.app_create_workspace()
        
        self.__lasth = int(lv_minheight*lv_wprc)
        self.__lastc = lv_wprc
        
        self.__desktop.add(self.__workspace, minsize=int(lv_minheight*lv_wprc), sticky=N+E+W+S)
        self.__desktop.bind('<Configure>', lambda x=1: self.__on_reconf_desktop())
        
        if addlog:
            self.app_create_logspace()
            self.__desktop.add(self.__logspace, minsize=min(int(lv_minheight*(1.0-lv_wprc)), 150), sticky=N+E+W+S)
                        
    def __on_reconf_desktop(self, po_event=None):
        """ reconf desktop """
        
        lv_minheight = self.__initkw.get('minheight', MAGIC_H_RES)
        lv_wprc = MAGIC_W2L + (1.0 - MAGIC_W2L) / ( 1.0*self.__root.winfo_height() / self.__lasth)  * 0.25
        
        self.__lasth = self.__root.winfo_height()
        self.__lastc = lv_wprc

        self.__desktop.paneconfig(self.__workspace, minsize=int(max(self.__root.winfo_height(), lv_minheight)*lv_wprc))
        
    def app_reconf_logpane(self, po_event=None):
        """ toogle logpane """
        
        lv_minheight = self.__initkw.get('minheight', MAGIC_H_RES)
        lv_wprc = novl(self.__lastc, MAGIC_W2L)
        
        lw_btn = self.get_gui_std_item('ltb_tooglelog_btn')

        if self.__logwstate == LOG_WSTATE_HIDDEN:
            self.__desktop.add(self.__logspace, minsize=min(int(lv_minheight*(1.0-lv_wprc)), 150), sticky=N+E+W+S)
            self.__logwstate = LOG_WSTATE_NORMAL
            
            lw_btn.configure(relief=SUNKEN, tooltip=_('Hide log pane'))
        else:
            self.__desktop.forget(self.__logspace)
            self.__logwstate = LOG_WSTATE_HIDDEN
            lw_btn.configure(relief=RAISED, tooltip=_('Show log pane'))
            
        self.app_on_logpane_reconf(self.__logwstate)
            
    def app_on_logpane_reconf(self, pv_state):
        """ process some routines after toogle """
        
        pass
                               
    def app_create_statusbar(self):
        """ create status bar and associated variables """

        self.__statusbar = Frame(self.__root, relief=RAISED, bd=2)

        self.set_sb_stringvar( 1, '')
        self.set_sb_stringvar( 2, '')
        self.set_sb_stringvar( 3, '')

        lw_label = Label(self.__statusbar, textvariable=self.__sb_stringvar1)
        lw_label.pack(side=LEFT)
        self.set_gui_std_item( 'l1', lw_label )

        lw_label = Label(self.__statusbar, textvariable=self.__sb_stringvar2)
        lw_label.pack(side=LEFT)
        self.set_gui_std_item( 'l2', lw_label )

        lw_label = Label(self.__statusbar, textvariable=self.__sb_stringvar3)
        lw_label.pack(side=LEFT)
        self.set_gui_std_item( 'l3', lw_label )

    def call_app_activechild_maximize(self, event=None):
        """ max active child """

        self.app_activechild_maximize()
        
    def app_activechild_maximize(self):
        """ max active child """
        
        if self.__active_child is not None:
            self.__active_child.call_geom_maximize()

    def call_app_activechild_restore(self, event=None):
        """ restore active child size """
        
        self.app_activechild_restore()
        
    def app_activechild_restore(self):
        """ restore active child size """

        if self.__active_child is not None:
            self.__active_child.call_geom_restore()
        
    def app_activechild_toogle(self):
        """ toogle active child size """

        if self.__active_child is not None:
            self.__active_child.geom_toggle()

    def call_app_children_cascade(self, event=None):
        """ place children in cascade """
        
        self.app_children_cascade()
        
    def app_children_cascade(self):
        """ place children in cascade """

        try:
            if self.__active_child is not None:
                children_len = len(self.__al_children)
                if children_len > 0:
                    v_maxw_w = -1
                    v_maxw_h = -1
    
                    # restore all children
                    for i in range( children_len-1, -1, -1 ):
                        child_id = self.__al_children[i]
                        self.__ad_children[child_id].geom_restore()
    
                        lv_currw_w = self.__ad_children[child_id].winfo_width()
                        lv_currw_h = self.__ad_children[child_id].winfo_height()
                        if lv_currw_w > v_maxw_w:
                            v_maxw_w = lv_currw_w
                        if lv_currw_h > v_maxw_h:
                            v_maxw_h = lv_currw_h
    
                    if children_len > 1:
                        v_divisor = (children_len-1)
                    else:
                        v_divisor = 1
    
                    v_xstep = max((self.__workspace.winfo_width()-v_maxw_w-1 ) / v_divisor, 1)
                    v_ystep = max((self.__workspace.winfo_height()-v_maxw_h-1 ) / v_divisor, 1)
    
                    v_topid = self.__active_child.get_id()
    
                    # prepare list in order: child1 sub1 sub2 child2
                    ll_clist = []
                    for child_id in self.__al_children:
                        lw_child = self.__ad_children[ child_id ]
                        if lw_child.get_parentwidget() is None:
                            ll_clist.append( child_id )
                            ll_clist += lw_child.get_subchildren_ids()
    
                    for i in range( children_len-1, -1, -1 ):
                        child_id = ll_clist[i]
                        lv_x = 1 + v_xstep * i
                        lv_y = 1 + v_ystep * i
                        if child_id != v_topid:
                            self.__ad_children[child_id].lower()
                        self.__ad_children[child_id].place( x = lv_x, y = lv_y )
    
                    self.__active_child.lift()
        except:
            lv_message = get_estr()
            self.app_showerror(lv_message)                    
                
    def call_app_children_tile(self, event=None):
        """ place children as tile """
        
        self.app_children_tile()                
                
    def app_children_tile(self):
        """ place children in cascade """

        try:
            if self.__active_child is not None:
                children_len = len(self.__al_children)
                
                if children_len > 0:
                    lv_cols = max(int(round(children_len ** 0.6)),1)
                    lv_rows = int(round(children_len / lv_cols))
                    if children_len % lv_cols > 0:
                        lv_rows += 1
                    
                    lv_cols = int(lv_cols)
                    lv_rows = int(lv_rows)
                            
                    v_maxw_w = -1
                    v_maxw_h = -1
    
                    # restore all children
                    for i in range( children_len-1, -1, -1 ):
                        child_id = self.__al_children[i]
                        self.__ad_children[child_id].geom_restore()
    
                        lv_currw_w = self.__ad_children[child_id].winfo_width()
                        lv_currw_h = self.__ad_children[child_id].winfo_height()
                        if lv_currw_w > v_maxw_w:
                            v_maxw_w = lv_currw_w
                        if lv_currw_h > v_maxw_h:
                            v_maxw_h = lv_currw_h
                            
                    self.__workspace.update_idletasks()
                                        
                    if lv_cols > 1:
                        v_xstep = max((self.__workspace.winfo_width()-v_maxw_w-1) / (lv_cols-1), 1)
                    else:
                        v_xstep = max((self.__workspace.winfo_width()-v_maxw_w-1) / 1, 1)
                    if lv_rows > 1:    
                        v_ystep = max((self.__workspace.winfo_height()-v_maxw_h-1) / (lv_rows-1), 1)
                    else:
                        v_ystep = max((self.__workspace.winfo_height()-v_maxw_h-1) / 1, 1)
                                            
                    v_topid = self.__active_child.get_id()
                    
                    # prepare list in order: child1 sub1 sub2 child2
                    ll_clist = []
                    for child_id in self.__al_children:
                        lw_child = self.__ad_children[ child_id ]
                        if lw_child.get_parentwidget() is None:
                            ll_clist.append( child_id )
                            ll_clist += lw_child.get_subchildren_ids()                
    
                    lv_childpos = 0
                    for tile_row in range(lv_rows):
                        for tile_col in range(lv_cols):
                            
                            child_id = ll_clist[lv_childpos]
                            lv_x = 1 + v_xstep * tile_col
                            lv_y = 1 + v_ystep * tile_row
                            if child_id != v_topid:
                                self.__ad_children[child_id].lift()
                            self.__ad_children[child_id].place( x = lv_x, y = lv_y )                        
    
                            lv_childpos += 1
                            if lv_childpos >= children_len:
                                break                 
                        if lv_childpos >= children_len:
                            break                 
    
                    self.__active_child.lift()
        except:
            lv_message = get_estr()
            self.app_showerror(lv_message)

    def wmenu_generate_label(self, window_id, class_, window_nick=''):
        """ generate label for label in window menu """

        lv_nick = window_nick
        if novl(lv_nick, '') == '':
            lv_nick = '(empty)'
            
        lv_text = '%s' % (lv_nick)

        return lv_text
        
    def get_maxchildren(self):
        """ return max number of allowed children """
        
        if self.__options is not None:
            lv_value = self.__options.get_value('sys_maxchildren')
        else:
            lv_value = None
            
        return novl(lv_value, APP_MAX_CHILDREN)
    
    def get_maxsubchildren(self):
        """ return max number of allowed sub-children """
        
        if self.__options is not None:
            lv_value = self.__options.get_value('sys_maxsubchildren')
        else:
            lv_value = None
            
        return novl(lv_value, APP_MAX_SUBCHILDREN)

    def call_app_child_add(self, class_=None):
        """ call new child addition """
        
        lw_child = None
        
        if len(self.__al_children) >= self.get_maxchildren():
            messagebox.showwarning(_('Warning'), _('Maximum number of children !'))
        elif class_ is None:
            messagebox.showwarning(_('Warning'), _('Child class is missed !'))
        elif not issubclass(class_, BaseChild):
            messagebox.showwarning(_('Warning'), _('Child class must subclassed from BaseChild !'))
        else:
            lw_child = self.app_child_add(class_)
            if lw_child is not None:
                if self.__active_child is not None:
                    lv_wstate = self.__active_child.get_wstate()
                    lv_x = novl(self.__active_child.winfo_x(), 0) + 25
                    lv_y = novl(self.__active_child.winfo_y(), 0) + 25
                else:
                    lv_wstate = 0
                    lv_x = 1
                    lv_y = 1
                                    
                lw_child.place(x=lv_x, y=lv_y)
                self.app_focus2child_set(lw_child.get_id(), 'ins')
                
                if lv_wstate == 1:
                    self.__active_child.geom_maximize()
            else:
                messagebox.showwarning(_('Warning'), _('Child creation was failed !'))
                    
        return lw_child

    def app_child_add( self, class_ ):
        """ create child and configure window menu """

        lw_child = None

        child_id = '[%s]' % self.__av_numerator
        self.__av_numerator += 1

        if len( self.__al_children ) == 0 and self.__uimode == APP_UI_MODE_MDI:
            self.wmenu_reconf_controls( NORMAL )

        lw_child = self.app_child_generator( child_id, class_ )

        if lw_child is not None:
            if self.__uimode == APP_UI_MODE_MDI:
                lw_child.child_reconf_close_btn( lambda wid=child_id: self.call_app_child_close(wid) )
    
            self.__ad_children[child_id] = lw_child
            self.__al_children.append(child_id)
    
            lv_label = self.wmenu_generate_label(child_id, class_, '')
            self.app_focus2child_bind(lw_child, child_id)
    
            if self.__uimode == APP_UI_MODE_MDI:
                self.wmenu_configure_item( child_id, 'add', label=lv_label )
        else:
            if len( self.__al_children ) == 0 and self.__uimode == APP_UI_MODE_MDI:
                self.wmenu_reconf_controls( DISABLED )            

        return lw_child

    def app_child_generator(self, child_id, class_):
        """ create instance of class_ object and fill it ui """

        lw_child = class_( self.get_workspace(), self, 
                           childid=child_id, 
                           title=child_id, 
                           helptext=['Demo'],
                           uimode = self.get_default_child_uimode())
        lw_child.child_gui_init()

        return lw_child

    def app_subchild_allowed(self, po_parent, pv_children):
        """ return True/False - can po_parent create another child ? """
        
        return pv_children+1 <= self.get_maxsubchildren()
    
    def get_default_child_uimode(self):
        """ return preffered mode of child's ui """
        
        return CHILD_UI_MODE_MDI
    
    def get_default_subchild_uimode(self):
        """ return default mode of subchild's ui """
        
        return CHILD_UI_MODE_MDI
    
    def get_default_child_class(self):
        """ get default child class """
        
        raise NotImplementedError
    
    def app_subchild_add( self, pv_id, pv_name, po_parent, class_ ):
        """ add some sub child """

        lw_child = class_( self.__workspace, self,
                           parentw = po_parent,
                           childid = pv_id,
                           title = pv_name,
                           uimode = self.get_default_subchild_uimode())
        lw_child.child_gui_init()

        if self.__uimode == APP_UI_MODE_MDI:
            # recommand close btn
            lw_child.child_reconf_close_btn( lambda wid=pv_id: self.call_app_child_close(wid) )

        self.__ad_children[pv_id] = lw_child
        self.__al_children.append(pv_id)

        if self.__uimode == APP_UI_MODE_MDI:        
            # configure wmenu
            self.wmenu_configure_item( po_parent.get_id(), 'add_sub', wid=pv_id, label=pv_name )

        return lw_child

    def set_id2label( self, lv_id, lv_label ):
        """ keep id -> label for window menu """

        self.__ad_id2label[lv_id] = lv_label
        
    def app_children_maximize(self, child):
        """ maximize all children and make one top """
        
        for child_item in list(self.__ad_children.values()):
            if child_item != child:
                child_item.geom_maximize()
        child.geom_maximize()
        
    def app_children_restore(self, child):
        """ restore all children and make one top """
        
        for child_item in list(self.__ad_children.values()):
            if child_item != child:
                child_item.geom_restore()
        child.geom_restore()          

    def app_focus2child_bind(self, child, child_id):
        """ default binding on child activation """

        lf_c = lambda event, chid = child_id: self.app_focus2child_set(chid, 'b-1', event)
        child.xbind_add('<Button-1>', lf_c)

    def app_child_close(self, p_windowid):
        """ close child """

        lw_child = self.__ad_children.get(p_windowid, None)

        if lw_child is not None:
            # stop any threads
            if issubclass(lw_child.__class__, BaseChild):
                if lw_child.thread_inuse():
                    lw_child.process_stop()
            
            lw_parent = lw_child.get_parentwidget()
            
            if lw_parent is None:
                if self.__uimode == APP_UI_MODE_MDI:
                    # configure menu
                    self.wmenu_configure_item( p_windowid, 'delete' )

                # close all children
                for subs_id in lw_child.get_subchildren_ids():
                    self.app_child_close( subs_id )

                # destroy child
                lw_child.child_close()
            else:
                if self.__uimode == APP_UI_MODE_MDI:
                    # configure menu
                    self.wmenu_configure_item( lw_parent.get_id(), 'del_sub', wid=p_windowid )

                lw_parent.subchild_close( p_windowid )

            # clear internal data
            del self.__ad_children[p_windowid]
            del self.__al_children[self.__al_children.index(p_windowid)]
            
            if self.__uimode == APP_UI_MODE_MDI:
                del self.__ad_id2label[p_windowid]
    
                if len( self.__al_children ) == 0:
                    self.wmenu_reconf_controls( DISABLED )

    def call_app_child_close(self, p_windowid):
        """ call close child """

        lv_topwid = None
        lw_parent = None
        if self.__active_child is not None:
            lv_topwid = self.__active_child.get_id()
            lw_parent = self.__active_child.get_parentwidget()

        self.app_child_close( p_windowid )

        if lv_topwid == p_windowid:
            self.__active_child = None

            if lw_parent is None:
                self.app_focus2child_set( None, 'close' )
            else:
                self.app_focus2child_set( lw_parent.get_id(), 'ch2parent' )

    def call_app_activechild_close(self, event=None):
        """ call active child deletion """

        if self.__active_child is not None:
            child_id = self.__active_child.get_id()
            self.app_child_close( child_id )
            
            self.__active_child = None
            self.app_focus2child_set( None, 'closetop' )

    def app_focus2child_set(self, pv_windowid, pv_dtext='', po_event=None):
        """ routine for changing focus between children """

        lv_towdw = None
        try:
            if self.__active_child is not None:
                self.__idsclip.push(self.__active_child.get_id())
            
            if pv_windowid is not None:
                lv_towdw = self.__ad_children[pv_windowid]
            elif len(self.__al_children) > 0:
                lv_towdw = None
                
                lv_id = 'x'
                while lv_towdw is None and lv_id is not None:
                    lv_id = self.__idsclip.pop()
                    if lv_id is not None:
                        try:
                            lv_towdw = self.__ad_children[lv_id]
                        except:
                            lv_towdw = None
                        
                if lv_towdw is None:
                    lv_towdw = self.__ad_children[self.__al_children[0]]
            else:
                lv_towdw = None

            if lv_towdw is not None:
                lv_oldtop = None
                if self.__active_child != lv_towdw:
                    lv_oldtop = self.__active_child
                    if lv_oldtop is not None:
                        lv_oldtop.child_deactivate()
                    else:
                        lv_oldtop = None

                if lv_towdw is not None and lv_towdw.get_state() != CHILD_ACTIVE:
                    lv_towdw.child_activate( lv_oldtop )

            self.__active_child = lv_towdw

        except Others:
            lv_message = 'failed to look at child [%s]: %s'% ( pv_dtext, get_estr() )
            xprint(lv_message)
        else:
            self.app_gui_reconf()
            
    def app_reconf_title(self, **kw):
        """ reconf app title """
        
        lw_root = self.get_root()
        lw_root.title(self.app_generate_title())

    def app_reconf_menu(self, **kw):
        """ reconf state of menu items """
        
        pass

    def app_reconf_toolbar(self, **kw):
        """ reconf state of toolbar controls """
        
        pass
    
    def app_add_recentrep(self, pv_reppath):
        """add report in the recent-rep list"""
        
        # get without copy !
        ll_recentlist = self.options_get_value('app:recentreplist', False, False)
        
        if ll_recentlist is not None:
            # process data            
            lv_recentlen = self.get_recentlen()
            
            # check data in list
            try:
                ll_recentlist.pop(ll_recentlist.index(pv_reppath))
            except ValueError:
                pass
            
            ll_recentlist.insert(0, pv_reppath)
            
            # strip recent list
            ll_recentlist = ll_recentlist[:lv_recentlen]
            
            self.options_set_value('app:recentreplist', ll_recentlist)            
            
            self.menu_create_rrlist()
            
    def menu_create_rrlist(self, pl_rrlist=None):
        """ generate recent rep-list"""
            
        if pl_rrlist is None:
            # get without copy !
            ll_recentlist = self.options_get_value('app:recentreplist', False, False)
        else:
            ll_recentlist = pl_rrlist
        
        if ll_recentlist is not None:            
            # regenerate menu 
            lw_rrlist = self.get_resource_item('recentreplist')
            if lw_rrlist:
                lw_rrlist.delete(0, END)
    
                for rritem in ll_recentlist:
                    lv_label = os.path.splitext(os.path.split(rritem)[1])[0]
                    lw_rrlist.add_command( label=lv_label, 
                                           command=lambda p=rritem: open_file( p ) )
        
    def app_reconf_statusbar(self, **kw):
        """ reconf statusbar """
        
        lv_sb1 = ''
        lv_sb2 = ''
        lv_sb3 = ''        
            
        if self.__active_child is not None:
            lv_sb1, lv_sb2, lv_sb3 = self.__active_child.get_description()
            
        self.set_sb_stringvar(1, lv_sb1)
        self.set_sb_stringvar(2, lv_sb2)
        self.set_sb_stringvar(3, lv_sb3)
            
    def app_gui_reconf(self, **kw):
        """ common reconf routines """
                
        if kw.get('title', True):
            self.app_reconf_title(**kw)
        if kw.get('menu', True):
            self.app_reconf_menu(**kw)
        if kw.get('toolbar', True):
            self.app_reconf_toolbar(**kw)
        if kw.get('statusbar', True):
            self.app_reconf_statusbar(**kw)
            
    def app_gui_initconf(self):
        """ initial routines for title, fonts and bitmaps """
        
        lw_root = self.get_root()
        
        self.app_reconf_title()
        
        self.set_deffonts(get_deffonts_dict(8))
        apply_fonts2tk( lw_root, self.get_deffonts() )
        
        lv_path, lv_logo = self.get_logos_data()
        if lv_logo is not None:
            assign_bitmap(lw_root, lv_path, lv_logo)              
                
    def toolbar_create_draft(self):
        """ prepare control data of toolbar items """

        ld_draft = {}
        self.set_resource_item('toolbar_draft', ld_draft) 

        ld_draft['add_btn']      = {'label':_("Add"),       'type':'button'}
        ld_draft['close_btn']    = {'label':_("Close"),     'type':'button'}
        ld_draft['cascade_btn']  = {'label':_("Cascade"),   'type':'button'}
        ld_draft['tile_btn']     = {'label':_("Tile"),      'type':'button'}
        ld_draft['closeall_btn'] = {'label':_("Close all"), 'type':'button'}
        
        ld_draft['tooglelog_btn'] = {'label':_("Hide log pane"), 'type':'button'}

    def toolbar_initconf(self):
        """ toolbar filling """

        self.toolbar_create_draft()

        if self.get_useapplog():
            self.toolbar_create_lbtns()

        if self.get_uimode() == APP_UI_MODE_MDI:
            self.toolbar_create_wbtns()
            
    def menu_create_draft(self):
        """ prepare control data of menu items """

        # fill menu draft
        self.__ad_resources['menu_draft'] = {}

        self.__ad_resources['menu_draft']['omenu']         = {'label':_("Preferences"),   'type':'header'}
        self.__ad_resources['menu_draft']['pref_options']  = {'label':_("Options"), 'type':'control', 'image':pta_icons.gv_app_options }

        self.__ad_resources['menu_draft']['wmenu'] = {'label':_("Window"),   'type':'header'}
        self.__ad_resources['menu_draft']['maximize']    = {'label':_("Maximize"), 'type':'control', 'image':pta_icons.gv_app_toolbar_maximize_child }
        self.__ad_resources['menu_draft']['restore']     = {'label':_("Restore"),  'type':'control', 'image':pta_icons.gv_app_toolbar_restore_child }
        self.__ad_resources['menu_draft']['cascade']     = {'label':_("Cascade"),  'type':'control', 'image':pta_icons.gv_app_toolbar_cascade }
        self.__ad_resources['menu_draft']['tile']        = {'label':_("Tile"),     'type':'control', 'image':pta_icons.gv_app_toolbar_tile }

        self.__ad_resources['menu_draft']['amenu']      = {'label':_("?"),       'type':'header'}
        self.__ad_resources['menu_draft']['cupd_menu']  = {'label':_("Check for updates"), 'type':'control'}
        self.__ad_resources['menu_draft']['about_menu'] = {'label':_("About"),             'type':'control'}
        
    def menu_need_amenu(self):
        """ check about content """
        
        if len(self.__aboutlist) > 0 or novl(pytkapp_info.get_appmarker(), '') != '':
            return True
        else:
            return False

    def menu_initconf(self):
        """ initial conf. routins """

        # create menu draft >>>
        self.menu_create_draft()
        
        # create options menu >>>        
        if self.__options is not None:
            self.menu_create_omenu()
        
        # create windows menu >>>
        if self.__uimode == APP_UI_MODE_MDI:
            self.menu_create_wmenu()
        
        if self.menu_need_amenu():
            self.menu_create_amenu()
        
    def get_active_child( self ):
        """ return active child """
        
        return self.__active_child
        
    def get_active_child_id( self ):
        """ return id of active child """
        
        if self.__active_child is not None:
            return self.__active_child.get_id()
        else:
            return None
    
    def app_activechild_state_set( self, pv_state=CHILD_ACTIVE ):
        """ change state of active child """
        
        if self.__active_child is not None:
            if pv_state == CHILD_ACTIVE:
                self.__active_child.child_activate()
            elif pv_state == CHILD_DISABLED:
                self.__active_child.child_deactivate()
                
    def app_message(self, pv_type, pv_message, **kw):
        """ show some message """
        
        lv_silence = kw.get('silence', False)
        if lv_silence not in (True, False):
            lv_silence = False
            
        lv_detail = kw.get('detail', None)
        lw_parent = kw.get('parent', None)
        
        ld_kw = {}
        if lv_detail is not None:
            ld_kw['detail'] = lv_detail
        ld_kw['parent'] = novl(lw_parent, self.get_root())        
        
        if pv_type == 'warning':
            lv_header = '[warning]'
            lf_func = messagebox.showwarning
        elif pv_type == 'error':
            lv_header = '[error]'
            lf_func = messagebox.showerror
        else:
            lv_header = '[info]'
            lf_func = messagebox.showinfo
        
        print('%s: %s' % (lv_header, pv_message))
        if lv_detail is not None:
            print('detail:\n%s'%lv_detail)
        if not lv_silence:
            lf_func(lv_header, pv_message, **ld_kw)            
                
    def app_showwarning(self, pv_message, **kw):
        """ show some warning """
        
        self.app_message('warning', pv_message, **kw)
                               
    def app_showerror(self, pv_message, **kw):
        """ show some error """
        
        self.app_message('error', pv_message, **kw)
                               
    def app_showinfo(self, pv_message, **kw):
        """ show some info """
        
        self.app_message('info', pv_message, **kw)                

    def app_ask(self, pv_type, pv_message, **kw):
        """ask... from messagebox"""
        
        if pv_type == 'okcancel':
            lf_subprogram = messagebox.askokcancel
        elif pv_type == 'yesno':
            lf_subprogram = messagebox.askyesno
        elif pv_type == 'yesnocancel':
            lf_subprogram = messagebox.askyesnocancel
        else:
            lf_subprogram = messagebox.askokcancel
            
        ld_kw = kw.copy()
        if 'title' in ld_kw:
            lv_title = _(ld_kw.pop('title'))
        else:
            lv_title = _('Confirm')
            
        return lf_subprogram(lv_title, 
                             pv_message,
                             **ld_kw)
        
    def app_askokcancel(self, pv_message, **kw):
        """ask ok/cancel"""
        
        return self.app_ask('okcancel', pv_message, **kw)
        
    def app_askyesno(self, pv_message, **kw):
        """ask yes/no"""
        
        return self.app_ask('yesno', pv_message, **kw)
                
    def app_askyesnocancel(self, pv_message, **kw):
        """ask yes/no/cancel"""
        
        return self.app_ask('yesnocancel', pv_message, **kw)
                
    def app_c2c_interaction(self, **kw):
        """ process interaction between children """
        
        pass
   
    def run(self):
        """ run application """

        try:
            self.__root.deiconify()
            self.__root.mainloop()
        except SystemExit as x:
            if repr(x.code) != '0':
                xprint( 'SystemExit: %s'%get_estr() )
        except Others:
            xprint( _( 'Run: %s'%get_estr() ) )

