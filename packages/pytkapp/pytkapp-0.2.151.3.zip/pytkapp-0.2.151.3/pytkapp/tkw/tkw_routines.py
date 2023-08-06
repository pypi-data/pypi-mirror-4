#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" routines for additional tkinter widgets """

# pytkapp.tkw: routines for additional tkinter widgets
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
if    sys.hexversion >= 0x03000000:
    from tkinter import Toplevel, TclError, Frame, Toplevel, PhotoImage
    from tkinter.constants import N, S, W, E, LEFT, RIGHT, Y, NORMAL
    import tkinter.font as tkfont
    from tkinter.ttk import Style as ttkStyle    
    from tkinter.ttk import Separator as ttkSeparator
else:
    from Tkinter import Toplevel, TclError, Frame, Toplevel, PhotoImage
    from Tkconstants import N, S, W, E, LEFT, RIGHT, Y, NORMAL
    import tkFont as tkfont
    from ttk import Style as ttkStyle    
    from ttk import Separator as ttkSeparator

import os    

# fixme: uncomment this block to run script directly OR set pythonpath for your package
#if __name__ == '__main__':
    #import sys
    #import os.path
    #lv_file = __file__
    #while os.path.split(lv_file)[1] != '':
        #lv_file = os.path.split(lv_file)[0]
        #print('append %s'%lv_file)
        #sys.path.append(lv_file)

from pytkapp.pta_routines import get_estr, xprint, novl

from pytkapp.tkw.tkw_tooltippedbtn import ToolTippedBtn

###################################
## globals
###################################
READONLY = 'readonly'

###################################
## routines
###################################
def toolbar_button_generator( master, pv_tooltip, pv_logo, pf_command, **kw):
    """ add tooltipped button on some widget - use this for toolbar for example """
    
    if pv_logo == '':
        img = None
    else:
        img = PhotoImage(data=pv_logo)
        
    lw_btn = ToolTippedBtn(master, 
                           image=img, 
                           tooltip=pv_tooltip, 
                           text=kw.get('text', None),
                           state=kw.get('state', NORMAL), 
                           command=pf_command)
    lw_btn.pack(side=kw.get('side', LEFT), padx=kw.get('padx', 3), pady=kw.get('pady', 3))
    
    return lw_btn

def toolbar_lbutton_generator( master, pv_tooltip, pv_logo, pv_state, pf_command, ppadx=3, ppady=3):
    """ add tooltipped button on some widget - use this for toolbar for example """
    
    return toolbar_button_generator(master, pv_tooltip, pv_logo, pf_command, state=pv_state, side=LEFT, padx=ppadx, pady=ppady)
    
def toolbar_rbutton_generator( master, pv_tooltip, pv_logo, pv_state, pf_command, ppadx=3, ppady=3):
    """ add tooltipped button on some widget - use this for toolbar for example """
    
    return toolbar_button_generator(master, pv_tooltip, pv_logo, pf_command, state=pv_state, side=RIGHT, padx=ppadx, pady=ppady)
    
def toolbar_separator_generator(master, ppadx=5, ppady=3):
    """ add separator on some widget - use this for toolbar for example """
    
    lw_sep = ttkSeparator(master, orient='vertical')
    lw_sep.pack(side=LEFT, fill=Y, padx=ppadx, pady=ppady)
    
    return lw_sep
    
def tk_focus_get( widget ):
    """ some bug for tablelist """

    name = widget.tk.call('focus')
    if name == 'none' or not name:
        lw_focus = None
    else:
        if name.split('.')[-1] != 'body':
            lv_name = name
        else:
            lv_name = '.'.join(name.split('.')[:-1])

        lw_focus = widget._nametowidget(lv_name)

    return lw_focus

def clipboard_append(event):
    """ add text from called widget to clipboard """

    event.widget.winfo_toplevel().clipboard_clear()
    winfo_class = event.widget.winfo_class()
    if   winfo_class in ['Text','ScrolledText']:
        try:
            lv_frag = event.widget.get('sel.first','sel.last')
            if lv_frag == '':
                lv_frag = event.widget.get('1.0','end')
            event.widget.winfo_toplevel().clipboard_append(lv_frag)
        except TclError:
            lv_frag = event.widget.get('1.0','end')
            event.widget.winfo_toplevel().clipboard_append(lv_frag)
    elif winfo_class == 'Entry':
        event.widget.winfo_toplevel().clipboard_append(event.widget.get())

    return "break"

def dummy():
    """ dummy """
    
    pass

def make_widget_ro( widget):
    """ make widget read-only: accept only Ctrl-C, Ctrl-Ins """

    widget.bind('<Control-KeyPress-c>', clipboard_append)
    widget.bind('<Control-KeyPress-Insert>', clipboard_append)
    
    widget.bind('<Control-Home>', lambda x=1: dummy(), '+')
    widget.bind('<Home>', lambda x=1: dummy(), '+')
    widget.bind('<Control-End>', lambda x=1: dummy(), '+')
    widget.bind('<End>', lambda x=1: dummy(), '+')
    
    widget.bind('<Next>', lambda x=1: dummy(), '+')
    widget.bind('<Prior>', lambda x=1: dummy(), '+')
    
    for i in range(1, 13):
        widget.bind('<F%s>'%i, lambda x=1: dummy(), '+')
    
    widget.bind('<Any-KeyPress>',"break")

def bind_children( widget, event, command, add='+' ):
    """ bind command to all children of widget """

    for child in widget.__dict__['children'].values():
        bind_children(child, event, command, add)

    if hasattr(widget,'body_bind'):
        widget.body_bind(event, command, add)
    widget.bind(event, command, add)

def make_widget_resizeable( widget ):
    """make widget resizeable"""

    cols, rows = widget.grid_size()
    for i in range(0, cols):
        widget.columnconfigure( i, weight=1 )
    for i in range(0, rows):
        widget.rowconfigure( i, weight=1 )

def is_basechild_subwidget( pw_check ):
    """ check widget master - is it basechild ? """
    
    lw_master = getattr( pw_check, 'master', None )
    if lw_master is None or str(lw_master.__class__).split('.')[-1] in ['Tk','Toplevel']:
        return False
    else:
        if hasattr(lw_master, 'iamchild'):
            return True
        else:
            return is_basechild_subwidget( lw_master )
        
def get_parent_coords( pw_parent ):
    """ get coord of widget parent """

    if isinstance(pw_parent, Toplevel):
        return ( pw_parent.winfo_x(), pw_parent.winfo_y() )
    elif hasattr(pw_parent, 'iamchild') or is_basechild_subwidget( pw_parent ):
        return ( pw_parent.winfo_rootx(), pw_parent.winfo_rooty() )
    else:
        lw_parent = pw_parent.winfo_toplevel()
        return ( lw_parent.winfo_rootx(), lw_parent.winfo_rooty() )

    return (0, 0)

def assign_bitmap(pw_toplevel, pv_iconpath, pv_iconname, pb_default=True):
    """assign icon to toplevel widget"""
    
    try:
        ld_params = {}
        
        # gen bitmap name for different platforms
        if sys.platform.startswith('linux'):
            bname = '@'+os.path.join(pv_iconpath, pv_iconname+'.xbm')
        elif sys.platform == 'win32':
            bname = os.path.join(pv_iconpath, pv_iconname+'.ico')
            
            if pb_default:
                ld_params['default'] = bname
                
        ld_params['bitmap'] = bname
        
        # set bitmap to toplevel        
        pw_toplevel.iconbitmap(**ld_params)
        
    except:
        lv_message = 'failed to assign bitmap: %s' % (get_estr())
        xprint(lv_message)
        
def toplevel_header( pw_parent, **kw):
    """ create toplevel widget with specified attrs 
        kw keys:
            title - toplevel title
            destroycmd - action on close toplevel
            logopath - path for logo
            logoname - logo name
            noframe - dont create child frame in toplevel
            nowait - dont use transient
    """

    lw_toplevel = Toplevel( pw_parent )
    lw_toplevel.withdraw()    
    
    lw_toplevel.bind('<Alt-Prior>', lambda x=1, p=pw_parent: lw_toplevel.geometry('%sx%s+%s+%s' % (int(p.winfo_screenwidth()*0.75), 
                                                                                                   int(p.winfo_screenheight()*0.75), 
                                                                                                   get_parent_coords(p)[0]+50,
                                                                                                   get_parent_coords(p)[1]+50)))
    lw_toplevel.bind('<Alt-Next>', lambda x=1, t=lw_toplevel, p=pw_parent: lw_toplevel.geometry('%sx%s+%s+%s' % (t.winfo_reqwidth(), 
                                                                                                                 t.winfo_reqheight(), 
                                                                                                                 get_parent_coords(p)[0]+50,
                                                                                                                 get_parent_coords(p)[1]+50)))
    
    pw_parent.update_idletasks()

    lw_toplevel.title(kw.get('title',''))
    destroycmd = novl(kw.get('destroycmd', None), lw_toplevel.destroy)
    lw_toplevel.protocol("WM_DELETE_WINDOW", destroycmd)

    lv_logo = kw.get('logoname', None)
    lv_path = kw.get('logopath', os.getcwd() )
    if lv_logo is not None:
        assign_bitmap(lw_toplevel, lv_path, lv_logo, False)

    if not kw.get('nowait', False):
        lw_toplevel.transient( pw_parent )        

    if kw.get('noframe', False):
        lw_topframe = None
    else:
        lw_topframe = Frame(lw_toplevel)
        make_widget_resizeable(lw_toplevel)
        lw_topframe.grid(sticky=N+E+W+S)

    return (lw_toplevel, lw_topframe)

def toplevel_footer(pw_self, pw_parent, **kw):
    """ Restore top page on window after widgets generation
        pw_self: dialog toplevel
        pw_parent: widget - parent of dialog (possible not toplevel)
        kw keys:
            nowait - True/False make toplevel indenpendent
            wres_allowed - True/False - is self width resizable ?
            hres_allowed - True/False - is self height resizable ?
            min_width - min width for self toplevel
            min_height - min height for self toplevel
            focusto - set focus in spec.widget when toplevel appear
            skipbackfocus - dont change focus to parent widget after close
    """

    lw_focusto = kw.get('focusto', None)
    
    pw_self.update_idletasks() 
    
    ws_x, ws_y = get_parent_coords( pw_parent )
    ws_x += 50
    ws_y += 50
    
    lv_reqwidth  = pw_self.winfo_reqwidth()
    lv_reqheight = pw_self.winfo_reqheight()
    
    lv_minwidth  = novl(kw.get('min_width', None), lv_reqwidth)
    lv_minheight = novl(kw.get('min_height', None), lv_reqheight)

    lv_width  = max(lv_minwidth, lv_reqwidth)
    lv_height = max(lv_minheight, lv_reqheight)
    
    pw_self.geometry(str(lv_width)+"x"+str(lv_height)+"+"+str(ws_x)+"+"+str(ws_y))
    pw_self.resizable(width = kw.get('wres_allowed', False), height = kw.get('hres_allowed', False))

    pw_self.minsize(min(lv_minwidth, lv_reqwidth), min(lv_minheight, lv_reqheight))

    lw_grabbed = pw_parent.grab_current()
    
    pw_self.deiconify()
    pw_self.lift()
    pw_self.grab_set()
    
    if lw_focusto is not None:
        lw_focusto.focus_set()
    else:
        pw_self.focus_set()

    if not kw.get('nowait', False):
        pw_self.bind('<Activate>', pw_self.update_idletasks(), '+')
        pw_parent.wait_window( pw_self )
    
    if not kw.get('skipbackfocus', False):
        try:
            pw_parent.focus() 
            if lw_grabbed is not None and kw.get('dograb', True):
                lw_grabbed.grab_set()
        except:
            lv_message = 'failed to change focus from toplevel footer: %s' % get_estr()
            xprint( lv_message )

def get_deffonts_dict( pv_basic_size=8 ):
    """ create dict with default fonts """
    
    ld_fonts = {}
    lt_fams = tkfont.families()
    
    # default fonts
    if 'Courier' in lt_fams:
        ld_fonts['basic'] = tkfont.Font(family="Courier", size=pv_basic_size, weight=tkfont.NORMAL)
    elif 'FreeSerif' in lt_fams:
        ld_fonts['basic'] = tkfont.Font(family="FreeSerif", size=pv_basic_size, weight=tkfont.NORMAL)
    elif 'OpenSymbol' in lt_fams:
        ld_fonts['basic'] = tkfont.Font(family="OpenSymbol", size=pv_basic_size, weight=tkfont.NORMAL)
    elif 'Symbol' in lt_fams:
        ld_fonts['basic'] = tkfont.Font(family="Symbol", size=pv_basic_size, weight=tkfont.NORMAL)
    else:
        ld_fonts['basic'] = tkfont.Font(family="System", size=pv_basic_size, weight=tkfont.NORMAL)

    # fonts for label and menus    
    if   'Arial' in lt_fams:
        ld_fonts['label'] = tkfont.Font(family="Arial", size=pv_basic_size, weight=tkfont.NORMAL)
    elif 'Sans' in lt_fams:
        ld_fonts['label'] = tkfont.Font(family="Sans", size=pv_basic_size, weight=tkfont.NORMAL)
    elif 'Serif' in lt_fams:
        ld_fonts['label'] = tkfont.Font(family="Serif", size=pv_basic_size, weight=tkfont.NORMAL)
    elif 'FreeSerif' in lt_fams:
        ld_fonts['label'] = tkfont.Font(family="FreeSerif", size=pv_basic_size, weight=tkfont.NORMAL)
    elif 'OpenSymbol' in lt_fams:
        ld_fonts['label'] = tkfont.Font(family="OpenSymbol", size=pv_basic_size, weight=tkfont.NORMAL)
    elif 'Symbol' in lt_fams:
        ld_fonts['label'] = tkfont.Font(family="Symbol", size=pv_basic_size, weight=tkfont.NORMAL)
    else:
        ld_fonts['label'] = tkfont.Font(family="System", size=pv_basic_size, weight=tkfont.NORMAL)
    
    # fonts for logos    
    if 'Times' in lt_fams:
        ld_fonts['biglogolabel'] = tkfont.Font(family="Times", size=pv_basic_size+2, weight=tkfont.BOLD)
        ld_fonts['logolabel'] = tkfont.Font(family="Times", size=pv_basic_size, weight=tkfont.NORMAL)
    elif 'Times New Roman' in lt_fams:
        ld_fonts['biglogolabel'] = tkfont.Font(family="Times New Roman",   size=pv_basic_size+2, weight=tkfont.BOLD)
        ld_fonts['logolabel'] = tkfont.Font(family="Times New Roman",   size=pv_basic_size, weight=tkfont.NORMAL)
    elif 'FreeSerif' in lt_fams:
        ld_fonts['biglogolabel'] = tkfont.Font(family="FreeSerif",   size=pv_basic_size+2, weight=tkfont.BOLD)
        ld_fonts['logolabel'] = tkfont.Font(family="FreeSerif",   size=pv_basic_size, weight=tkfont.NORMAL)
    else:
        ld_fonts['biglogolabel'] = ld_fonts['label']
        ld_fonts['logolabel'] = ld_fonts['label']
            
    return ld_fonts

def apply_fonts2tk( pw_root, pd_fonts=None ):
    """ set fonts for widgets """
    
    if pd_fonts is None:
        ld_fonts = get_deffonts_dict()        
    else:
        ld_fonts = pd_fonts    
    
    s = ttkStyle()
    s.configure('.', font=ld_fonts['label'])

    pw_root.option_add('*font',    ld_fonts['basic'], priority=20)
    
    pw_root.option_add('*Button*font',       ld_fonts['basic'], priority=20)
    pw_root.option_add('*Entry*font',        ld_fonts['basic'], priority=20)
    pw_root.option_add('*Text*font',         ld_fonts['basic'], priority=20)
    pw_root.option_add('*ScrolledText*font', ld_fonts['basic'], priority=20)
    pw_root.option_add('*Listbox*font',      ld_fonts['basic'], priority=20)
    pw_root.option_add('*Spinbox*font',      ld_fonts['basic'], priority=20)
    pw_root.option_add('*Checkbutton*font',  ld_fonts['basic'], priority=20)    
    
    pw_root.option_add('*TCombobox*font',         ld_fonts['basic'], priority=20)
    pw_root.option_add('*TCombobox*Listbox*font', ld_fonts['basic'], priority=20)

    pw_root.option_add('*Label*font',        ld_fonts['label'], priority=20)
    pw_root.option_add('*Menu*font',         ld_fonts['label'], priority=20)
    