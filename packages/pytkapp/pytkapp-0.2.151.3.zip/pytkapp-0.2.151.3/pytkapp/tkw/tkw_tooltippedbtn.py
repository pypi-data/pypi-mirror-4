#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" button with the pop-up tooltip """

# pytkapp.tkw: button with the pop-up tooltip
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

if sys.hexversion >= 0x03000000:
    from tkinter import Toplevel, Button, StringVar, Message
    #from tkinter.ttk import Button as ttkButton
else:
    from Tkinter import Toplevel, Button, StringVar, Message
    #from ttk import Button as ttkButton

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
## classes
###################################
class ToolTippedBtn( Button ):
    """ button with some tooltip """

    def __init__( self, master, **kw ):
        """ init widget """

        self.av_state = 0
        self.hide_afid = None
        self.show_afid = None
        ld_kw = kw.copy()
        
        self.__img = None
        
        self.av_tooltip = kw.get('tooltip', '')
        self.aw_showdelay = kw.get('showdelay', 1)
        self.aw_hidedelay = kw.get('hidedelay', 10)

        if 'tooltip' in kw:
            del ld_kw['tooltip']
        if 'showdelay' in kw:
            del ld_kw['showdelay']
        if 'hidedelay' in kw:
            del ld_kw['hidedelay']
            
        if ld_kw.get('image', None) is None:
            if ld_kw.get('text', None) is None:
                ld_kw['text'] = self.av_tooltip
            else:
                ld_kw['text'] = ld_kw.get('text', '')

        Button.__init__(self, master, **ld_kw)
        
        self.__img = ld_kw.get('image', None)
        
        if 'command' in ld_kw:
            self.bind('<Return>', ld_kw['command'])

        self.aw_tooltip_toplevel = Toplevel( master,
                                             bg='black',
                                             padx=1,
                                             pady=1)
        self.aw_tooltip_toplevel.withdraw()
        self.aw_tooltip_toplevel.overrideredirect( True )

        self.av_tooltipvar = StringVar()
        self.av_tooltipvar.set(self.av_tooltip)

        self.aw_tooltip = Message( self.aw_tooltip_toplevel,
                                   bg="#ffffcc",
                                   aspect=1000,
                                   textvariable=self.av_tooltipvar)
        self.aw_tooltip.pack()

        self.bind( '<Enter>', self.init_tooltip, "+" )
        self.bind( '<Leave>', self.hide_tooltip, "+" )

    def init_tooltip( self, event=None ):
        """ check parent activities """

        self.av_state = 1
        self.show_afid = self.after( int( self.aw_showdelay * 1000 ), self.show_tooltip )

    def show_tooltip( self, event=None ):
        """ show tooltip """

        self.av_state = 2
        self.show_afid = None
        # get self position & height
        lv_x = self.winfo_rootx()
        lv_y = self.winfo_rooty()
        lv_height = self.winfo_height()

        # calc coords
        lv_lx = (self.winfo_rootx() + self.aw_tooltip.winfo_width() + 5)
        if lv_lx < self.winfo_screenwidth() - 5:
            lv_x += 5
        else:
            lv_x += self.winfo_screenwidth() - lv_lx

        lv_ly = (self.winfo_rooty() + self.winfo_height() + self.aw_tooltip.winfo_height() + 5)
        if lv_ly < self.winfo_screenheight() - 5:
            lv_y += lv_height + 5
        else:
            lv_y += -(self.aw_tooltip.winfo_height() + 5)

        self.aw_tooltip_toplevel.wm_geometry( "+%d+%d" % ( lv_x, lv_y ) )

        self.aw_tooltip_toplevel.deiconify()
        self.hide_afid = self.after( int( self.aw_hidedelay * 1000 ), self.hide_tooltip )

    def hide_tooltip( self, event=None ):
        """ hide tooltip """

        if self.show_afid is not None:
            self.after_cancel( self.show_afid )
            self.show_afid = None
        if self.hide_afid is not None:
            self.after_cancel( self.hide_afid )
            self.hide_afid = None
        self.av_state = 0
        self.aw_tooltip_toplevel.withdraw()

    def configure( self, **kw ):
        """ configure widget """

        ld_kw = kw.copy()

        if 'tooltip' in kw:
            self.av_tooltip = kw.get('tooltip', '')
            self.av_tooltipvar.set(self.av_tooltip)
            del ld_kw['tooltip']
        if 'showdelay' in kw:
            self.aw_showdelay = kw.get('showdelay', 1)
            del ld_kw['showdelay']
        if 'hidedelay' in kw:
            self.aw_hidedelay = kw.get('hidedelay', 10)
            del ld_kw['hidedelay']

        Button.configure(self, **ld_kw)

        if 'image' in ld_kw:
            self.__img = ld_kw.get('image', None)
            
        if 'command' in ld_kw:
            self.bind('<Return>', ld_kw['command'])            
