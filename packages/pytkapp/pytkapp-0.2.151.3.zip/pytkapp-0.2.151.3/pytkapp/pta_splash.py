#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" application splash window, based on ActiveState recipe 576936 """

# pytkapp: application splash window
#
# Copyright (c) 2013 Paul "Mid.Tier"
# Author e-mail: mid.tier@gmail.com

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by# the Free Software Foundation, either version 3 of the License, or
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
    from tkinter import Toplevel, Label, PhotoImage, Frame
    from tkinter.constants import N, S, W, E, CENTER, RAISED, SUNKEN
    import tkinter.font as tkfont
else:
    from Tkinter import Toplevel, Label, PhotoImage, Frame
    from Tkconstants import N, S, W, E, CENTER, RAISED, SUNKEN
    import tkFont as tkfont

import time

from pytkapp.pta_routines import novl

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
class DummySplash:
    """ dummy class replacing app splash """
    
    def __init__(self, pw_root, **kw):
        """ init """
        
        self.__root = pw_root
        self.__kw = kw
        
    def __enter__(self):
        """ enter """
        
        pass
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """ exit """
        
        pass        

class BaseSplash:
    """ splash window, based on ActiveState recipe 576936 """
    
    def __init__(self, pw_root, **kw):
        """ init routines for splash
            kw may contain:
                wait: splash life time in seconds
                appicon: icon, showed in left side (in text format)
                appname: name
                appver:  version
                appurl: project url
                bg: splash background
                fg: splash foreground
                f1: font for app name
                f2: font for version, state and url
                bd1(2): border width for splash frame (1-window,2-inner frames)
                wrelief: tk const for window relief
                frelief: tk const for frame relief
        """

        # common
        self.__root = pw_root
        self.__wait = kw.get('wait', 3) + time.clock()
        self.__logo   = None        
        self.__window = None
                
        # content
        self.__appicon  = kw.get('appicon', None)
        self.__appname  = kw.get('appname', 'Demo')
        self.__appver   = kw.get('appver', '0.0.1.0')
        self.__appurl   = kw.get('appurl', None)
        
        # colors
        self.__bg   = kw.get('bg', 'blue')
        self.__fg   = kw.get('fg', 'white')
        
        # geometry & styles
        self.__bd1     = kw.get('bd1', 3)
        self.__bd2     = kw.get('bd2', 2)
        self.__wrelief = kw.get('relief', RAISED)
        self.__frelief = kw.get('relief', SUNKEN)
        
        # fonts
        if 'f1' not in kw:
            try:
                self.__f1 = tkfont.Font( family="times", size=12, weight="bold", slant="italic" )
            except:
                self.__f1 = tkfont.Font( family="arial", size=12, weight="bold", slant="italic" )
        else:
            self.__f1 = kw['f1']
            
        self.__f2 = kw.get( 'f2', tkfont.Font( family="arial", size=8, weight="normal" ) )

    def __enter__(self):
        """ enter """
        
        # Hide the root while it is built.
        self.__root.withdraw()
        # Create components of splash screen.
        window = Toplevel(self.__root, bd=self.__bd1, relief=self.__wrelief, background=self.__bg)
        window.withdraw()

        lv_splcol = 0

        # logo >>>
        if self.__appicon is not None:
            logo_frame = Frame(window, background=self.__bg, relief=self.__frelief, bd=self.__bd2)
            logo_image = PhotoImage( data=self.__appicon )
            lw_label = Label( logo_frame, image=logo_image, background=self.__bg)
            self.__logo = logo_image
            lw_label.grid( row=0, column=0, sticky=N+E+W+S, padx=0, pady=0 )
            logo_frame.rowconfigure( 0, weight = 1 )
            logo_frame.grid( column=lv_splcol, row=0, sticky=N+E+W+S, padx=1, pady=1 )
            lv_splcol += 1
        
        # text >>>
        lv_r = 0
        text_frame = Frame( window, background=self.__bg, relief=self.__frelief, bd=self.__bd2)
        lw_label = Label(text_frame,
                         text=self.__appname,
                         anchor=CENTER,
                         font=self.__f1, 
                         background=self.__bg,
                         fg = self.__fg)
        lw_label.grid( row=lv_r, column=0, sticky=N+E+W, padx=2, pady=1 )
        
        lv_r += 1 
        lv_text = self.__appver
            
        lw_label = Label(text_frame,
                         text=lv_text,
                         anchor=CENTER, 
                         font=self.__f2,
                         background=self.__bg,
                         fg = self.__fg)
        lw_label.grid( row=lv_r, column=0, sticky=N+E+W, padx=2, pady=1)
        
        if self.__appurl is not None:
            lv_r += 1
            lw_label = Label(text_frame,
                             text=self.__appurl,
                             anchor=CENTER,
                             font=self.__f2,
                             background=self.__bg,
                             fg = self.__fg)
            lw_label.grid( row=lv_r, column=0, sticky=E+W+S, padx=2, pady=1)

        text_frame.grid( column=lv_splcol, row=0, sticky=N+E+W+S, padx=1, pady=1)

        # Get the screen's width and height.
        scrW = window.winfo_screenwidth()
        scrH = window.winfo_screenheight()
        # Get the images's width and height.
        window.update_idletasks()
        splashW = window.winfo_reqwidth()
        splashH = window.winfo_reqheight()
        # Compute positioning for splash screen.
        Xpos = (scrW - splashW) // 2
        Ypos = (scrH - splashH) // 2
        # Configure the window showing the logo.
        window.overrideredirect(True)
        window.geometry(str(splashW)+"x"+str(splashH)+"+"+str(Xpos)+"+"+str(Ypos))
        window.deiconify()
        window.update()
        window.lift()
        window.grab_set()
        # Save the variables for later cleanup.
        self.__window = window

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ exit """
        
        # Ensure that required time has passed.
        now = time.clock()
        if now < self.__wait:
            time.sleep(self.__wait - now)
        # Free used resources in reverse order.
        del self.__logo
        self.__window.destroy()
        # Give control back to the root program.
        self.__root.update_idletasks()
