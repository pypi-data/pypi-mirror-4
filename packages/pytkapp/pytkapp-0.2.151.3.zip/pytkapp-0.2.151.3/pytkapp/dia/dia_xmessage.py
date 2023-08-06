#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" common dialogs - message with tabular details """

# pytkapp: common dialogs - message with tabular details
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
import gettext
if __name__ == '__main__':
    if    sys.hexversion >= 0x03000000:
        gettext.install(__name__)
    else:
        gettext.install(__name__, unicode=True)
elif '_' not in __builtins__:
    _ = gettext.gettext
    
if    sys.hexversion >= 0x03000000:
    from tkinter import Tk, PhotoImage, Frame, Label
    from tkinter.constants import NONE, NW, N, E, W, S, TOP, BOTH, YES, RAISED
else:
    from Tkinter import Tk, PhotoImage, Frame, Label
    from Tkconstants import NONE, NW, N, E, W, S, TOP, BOTH, YES, RAISED

# pytkapp
from pytkapp.pta_dialog import BaseDialog
from pytkapp.tkw.tkw_routines import toplevel_footer, toplevel_header, make_widget_resizeable
from pytkapp.tkw.tkw_xscrolledtext import XScrolledText, READONLY
from pytkapp.tkw.tkw_txtablelist import TXTableList
import pytkapp.tkw.tkw_icons as tkw_icons

###################################
## globals
###################################
XMESSAGE_STYLE_ERROR   = 'error'
XMESSAGE_STYLE_WARNING = 'warning'
XMESSAGE_STYLE_INFO    = 'info'

XMESSAGE_STYLES = (XMESSAGE_STYLE_ERROR, XMESSAGE_STYLE_WARNING, XMESSAGE_STYLE_INFO)

###################################
## routines
###################################

###################################
## classes
###################################      
class XMessage(BaseDialog):
    """message box with tabular details """
    
    def __init__(self, pw_parent, **kw):
        """ init routines 
        kw:
        style - error/warning/info
        title - title of dialog
        message - some message
        tabh - list of tab headers
        tabr - list of rows as tuples
        tabc - conf.dict for tab 
               keys (index, None) or index affected on row
               keys (index, index) affected on cell
        """
        
        lv_nbc = kw.get('nobackconfirm', True)
        kw['nobackconfirm'] = lv_nbc
      
        BaseDialog.__init__(self, pw_parent, **kw)
        
        lv_style = kw.get('style', XMESSAGE_STYLE_INFO)
        if lv_style not in XMESSAGE_STYLES:
            lv_style = XMESSAGE_STYLE_INFO
            
        if lv_style == XMESSAGE_STYLE_ERROR:
            lv_imagedata = tkw_icons.gv_icon_dialog_error
        elif lv_style == XMESSAGE_STYLE_WARNING:
            lv_imagedata = tkw_icons.gv_icon_dialog_warning
        else:
            lv_imagedata = tkw_icons.gv_icon_dialog_information
            
        lv_title = kw.get('title', _('Message'))
        lv_message = kw.get('message', '')
        
        if kw.get('tab', None):
            lv_tab = 1
            ll_tabh = list(kw.get('tabh', [])[:])
            ll_tabr = list(kw.get('tabr', [])[:])
            ld_tabc = kw.get('tabc', {}).copy()
            
            # align cells len
            lv_cells = max([len(tr) for tr in ll_tabr])
            if lv_cells > len(ll_tabh):
                for cell_indx in range(len(ll_tabh), lv_cells):
                    ll_tabh.append(_('Column %s') % cell_indx)
        else:
            lv_tab = None
            
        lw_toplevel, lw_topframe = toplevel_header(self.get_parent(),
                                                   title=lv_title,
                                                   path=self.get_kwlogopath(),
                                                   logo=self.get_kwlogoname(),
                                                   destroycmd=self.call_back
                                                  )   
        self.set_toplevel(lw_toplevel)
        
        # main >>>
        lw_main = Frame(lw_topframe)
        
        lw_image = PhotoImage(data=lv_imagedata)
        lw_label = Label(lw_main, image=lw_image, relief=RAISED, bd=1)
        lw_label.grid(row=0, column=0, sticky=NW, padx=2, pady=2)      
        
        lw_text = XScrolledText(lw_main, 
                                wrap=NONE,
                                takefocus=0,
                                defheight=5,
                                exportdir=kw.get('exportdir', os.getcwd()),
                                export_=True,
                                print_=True,
                                wstate=READONLY)
        lw_text.insert_data(lv_message)
        lw_text.grid(row=0, column=1, sticky=N+E+W+S, padx=2, pady=2)      

        if lv_tab:
            lt_headers = ()
            for i in ll_tabh:
                lt_headers += ( 0, i, )
                
            lw_tab = TXTableList(lw_main,
                                 activestyle="none",
                                 background = "white",
                                 columns = lt_headers,
                                 selecttype="row",
                                 selectmode="browse", #single, browse, multiple, extended
                                 stretch = "all",
                                 stripebackground="gray90",
                                 height=max(len(ll_tabr), 5),
                                 width=0,
                                 # additional
                                 exportdir=kw.get('exportdir', os.getcwd()),
                                 allowexport=True,
                                 allowresize=True,
                                 hscroll=True,
                                 vscroll=True
                                 )
            lw_tab.xcontent()
            lw_tab.grid(row=1, column=1, sticky=N+E+W+S, padx=2, pady=2)
            
            # insert data
            for data in ll_tabr:
                lw_tab.insert("end", data)
                
            # recond data
            for confkey in ld_tabc:
                lv_row = None
                lv_cell = None
                if len(confkey) == 2:
                    lv_row, lv_cell = confkey
                else:
                    lv_row = confkey
                    lv_cell = None
                    
                try:
                    if lv_cell:
                        lw_tab.cellconfigure('%s,%s' % (lv_row, lv_cell,), ld_tabc[confkey])
                    else:
                        lw_tab.rowconfigure(lv_row, ld_tabc[confkey])
                except:
                    pass
        
        lw_main.columnconfigure(1, weight=1)
        
        lw_main.pack(side=TOP, fill=BOTH, expand=YES, padx=2, pady=2)
                
        ## controls >>>
        #lw_cframe = Frame(lw_topframe, relief=RAISED, bd=2)
        
        #img = PhotoImage(data=pta_icons.gv_app_action_back)
        #lw_backbtn = ToolTippedBtn(lw_cframe, image=img, tooltip=_('Back'), command=self.call_back)
        #lw_backbtn.pack(side=RIGHT, anchor=NE, padx=2, pady=2)

        #lw_cframe.pack(side=TOP, fill=X)
          
        make_widget_resizeable(lw_toplevel)
        lw_toplevel.update_idletasks()
        
        toplevel_footer(lw_toplevel, 
                        self.get_parent(),
                        min_width=max(lw_toplevel.winfo_reqwidth(), kw.get('width',150)),
                        min_height=max(lw_toplevel.winfo_reqheight(), kw.get('height',100)),
                        hres_allowed=kw.get('hal',False),
                        wres_allowed=kw.get('wal',False)
                        )
