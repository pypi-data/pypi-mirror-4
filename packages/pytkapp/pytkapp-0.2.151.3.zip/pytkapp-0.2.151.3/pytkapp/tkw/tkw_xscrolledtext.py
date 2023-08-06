#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" text widget with scrolling and additional 
    controls (search, clear, unload, etc.)
"""

# pytkapp.tkw: text widget with scrolling and additional controls
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
import tempfile
import locale
import gettext
import codecs
import os
import subprocess
if __name__ == '__main__':
    if    sys.hexversion >= 0x03000000:
        gettext.install(__name__)
    else:
        gettext.install(__name__, unicode=True)
elif '_' not in __builtins__:
    _ = gettext.gettext

if    sys.hexversion >= 0x03000000:
    from tkinter import Text, Frame, Scrollbar, StringVar, Entry, TclError
    from tkinter.constants import N, S, W, E, NE
    from tkinter.constants import TOP, LEFT, RIGHT, X, END, YES, BOTH, HORIZONTAL, VERTICAL
    from tkinter.constants import NONE, CHAR, NORMAL, DISABLED
    import tkinter.filedialog as filedialog
    import tkinter.messagebox as messagebox
else:
    from Tkinter import Text, Frame, Scrollbar, StringVar, Entry, TclError
    from Tkconstants import N, S, W, E, NE
    from Tkconstants import TOP, LEFT, RIGHT, X, END, YES, BOTH, HORIZONTAL, VERTICAL
    from Tkconstants import NONE, CHAR, NORMAL, DISABLED
    import tkFileDialog as filedialog
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

from pytkapp.tkw.tkw_searchdialog import SearchDialog
from pytkapp.tkw.tkw_routines import make_widget_ro, READONLY, get_estr
from pytkapp.tkw.tkw_routines import toolbar_lbutton_generator
import pytkapp.tkw.tkw_icons as tkw_icons
from pytkapp.pta_routines import convert_fname, novl, get_currentfolder, xprint, gv_defenc

###################################
## constants
###################################
STRIP_MODE_ALL = 'all'
STRIP_MODE_LAST = 'last'

###################################
## classes
###################################
class XScrolledText(Frame):
    """ scrolledtext with additional functional
        contain widgets for clearing, unloading to file and searching
        kw:
           unloaddir/exportdir - folder for export text
           importdir - folder for import text
           defext - default extension for imported/exported files
           defwidth - default width
           defheight - default height
           presearchcmd - routine that fired before search dialog pop-up
           postsearchcmd - routine that fired after search dialog closed
           search - True/False - allow search
           clear - True/False - allow clear text
           unload/export_ - True/False - allow unload text
           import_ - True/False - allow import text
           print_ - True/False - allow print text
           wrap - if NONE then provide horizontal scrollbar for widget
           wstate - NORMAL/DISABLED/READONLY (default)
    """

    def __init__(self, master, **kw):
        """ init widget """

        Frame.__init__(self, master)

        # some attrs
        self.__exportdir = kw.get('exportdir', kw.get('unloaddir', get_currentfolder()))
        self.__importdir = kw.get('importdir', get_currentfolder())
        self.__defext    = kw.get('defext', 'txt')

        # widgets
        lw_mainframe = Frame(self)
        ld_kw = {}
        for kw_key in kw:
            if kw_key == 'defwidth':
                ld_kw['width'] = kw[kw_key]
            elif kw_key == 'defheight':
                ld_kw['height'] = kw[kw_key]
            elif kw_key in ['wstate', 'presearchcmd', 'postsearchcmd', 
                            'search', 'clear', 'import_', 'export_', 'unload', 'print_',
                            'unloaddir', 'exportdir', 'importdir', 'defext']:
                pass
            else:
                ld_kw[kw_key] = kw[kw_key]

        self.__datawidget = Text(lw_mainframe,
                                 **ld_kw)
        self.__datawidget.grid(column=0, row=0, sticky=N+E+W+S)

        lw_vsb = Scrollbar(lw_mainframe)
        lw_vsb.config(orient=VERTICAL, command=self.__datawidget.yview)
        lw_vsb.grid(column=1, row=0, sticky=N+S)
        self.__datawidget.config(yscrollcommand=lw_vsb.set)

        if ld_kw.get('wrap', CHAR) == NONE:
            lw_hsb = Scrollbar(lw_mainframe)
            lw_hsb.config(orient=HORIZONTAL, command=self.__datawidget.xview)
            lw_hsb.grid(column=0, row=1, sticky=E+N+W)
            self.__datawidget.config(xscrollcommand=lw_hsb.set)

        self.set_wstate(kw.get('wstate', READONLY))

        lw_mainframe.columnconfigure(0, weight=1)
        lw_mainframe.rowconfigure(0, weight=1)

        lw_mainframe.pack(side=TOP, expand=YES, fill=BOTH, padx=1, pady=1)

        # associate search dialog
        self.__lastsearch = None
        self.__presearchcmd = None
        self.__postsearchcmd = None
        if kw.get('search', False):
            self.__lastsearch = StringVar()
            self.__presearchcmd = kw.get('presearchcmd', None)
            self.__postsearchcmd = kw.get('postsearchcmd', None)
            self.__datawidget.bind('<Control-KeyPress-f>', self.call_seach_dialog)

        self.__udcf = Frame(self)
        self.__udcf.pack(side=LEFT, fill=X, padx=1, pady=1)

        self.__wcontrols = {}

        # create controls frame
        if kw.get('clear', False) or kw.get('import_', False) or kw.get('export_', False) or kw.get('unload', False) or kw.get('print_', False):
            lw_contolframe = Frame(self)

            if kw.get('clear', False):
                self.__wcontrols['clear_btn'] = toolbar_lbutton_generator(lw_contolframe, 
                                                                          _('Clear data'), 
                                                                          tkw_icons.gv_xscrolledtext_clear, 
                                                                          NORMAL, 
                                                                          self.call_clear_data, 
                                                                          2, 2)


            if kw.get('import_', False):
                self.__wcontrols['import_btn'] = toolbar_lbutton_generator(lw_contolframe, 
                                                                           _('Import data'), 
                                                                           tkw_icons.gv_xscrolledtext_import, 
                                                                           NORMAL, 
                                                                           self.call_import_data, 
                                                                           2, 2)
                
            if kw.get('unload', False) or kw.get('export_', False):
                lw_btn = toolbar_lbutton_generator(lw_contolframe, 
                                                   _('Export data'), 
                                                   tkw_icons.gv_xscrolledtext_export, 
                                                   NORMAL, 
                                                   self.call_export_data, 
                                                   2, 2)
                self.__wcontrols['unload_btn'] = lw_btn
                self.__wcontrols['export_btn'] = lw_btn

            if kw.get('print_', False):
                self.__wcontrols['print_btn'] = toolbar_lbutton_generator(lw_contolframe, _('Print data'), tkw_icons.gv_xscrolledtext_print, NORMAL, self.call_print_data, 2, 2)

            lw_contolframe.pack(side=RIGHT, anchor=NE, padx=1, pady=1)

    def get_wcontrols(self, wkey):
        """ return some controls """

        return self.__wcontrols.get(wkey, None)

    def get_udcf(self):
        """ return user-defined control frame """

        return self.__udcf

    def call_seach_dialog(self, event=None):
        """ call search dialog for widget """

        if self.__presearchcmd is not None:
            self.__presearchcmd()

        s = SearchDialog( self,
                          self.__datawidget,
                          lastsearch=self.__lastsearch,
                          postsearchcmd=self.__postsearchcmd)

        lv_index = s.get_firstindex()
        if lv_index is not None:
            self.__datawidget.see( lv_index )
            self.__datawidget.update_idletasks()

            return "break"

    def call_print_data(self, event=None):
        """ print some data """

        if messagebox.askokcancel(_('Confirm'), _('Print data ?'), parent=self):
            try:
                lf_temp = tempfile.NamedTemporaryFile(suffix='.tmp', delete=False)
                lv_txtdata = ''
                try:
                    lv_txtdata = self.__datawidget.get("sel.first","sel.last")
                    
                except TclError:
                    lv_txtdata = self.get_data()
                finally:
                    lf_temp.write(lv_txtdata.encode(gv_defenc))
                    lf_temp.close()
    
                # prepare temp file
                if sys.platform == 'win32':
                    subprocess.call(('notepad', '/p', '%s'%lf_temp.name))
                else:
                    subprocess.call(('lpr', '-p', lf_temp.name))
            except:
                lv_message = get_estr()
                print('Print error: %s' % lv_message)
            else:
                os.remove(lf_temp.name)
                
    def call_import_data(self, event=None):
        """ import data """

        lv_path = filedialog.askopenfilename(title=_('Import data'),
                                             filetypes = {"%s {.%s}" % (_('Data'), self.__defext):0,
                                                          "%s {.*}"  % (_('All')):1},
                                             initialdir=self.__importdir,
                                             parent=self
                                            )
        lv_path = convert_fname( lv_path )

        if novl(lv_path, '') != '':
            lv_path = os.path.realpath(lv_path)
            
            with codecs.open(lv_path, 'rb', encoding=locale.getpreferredencoding(), errors='replace') as lf_in:
                self.clear_data()
                lv_data = lf_in.read().replace('\r\n', '\n')
                self.insert_data(lv_data, True, '1.0')
                
                xprint(_('Import completed !'))

    def call_export_data(self, event=None):
        """ unload data """

        lv_unloadpath = filedialog.asksaveasfilename(title=_('Export data'),
                                                     filetypes = {"%s {.%s}"%(_('Data'), self.__defext):0},
                                                     initialdir=self.__exportdir,
                                                     parent=self,
                                                     defaultextension=self.__defext
                                                     )
        lv_unloadpath = convert_fname( lv_unloadpath )

        if novl(lv_unloadpath, '') != '':
            lv_unloadpath = os.path.realpath(lv_unloadpath.lower())
            
            if self.__defext.isalnum():
                if os.path.splitext(lv_unloadpath)[-1] != '.%s'%self.__defext:
                    lv_unloadpath += '.%s'%self.__defext

            if os.path.exists(os.path.split(lv_unloadpath)[0]):
                with codecs.open(lv_unloadpath, 'w', encoding=gv_defenc) as lf_out:
                    lf_out.write(self.get_data())
                    
                xprint(_('Data unloaded') )

    def get_data(self, startpos='1.0', endpos=END, strip_=None):
        """ return content of data widget """

        lv_data = self.__datawidget.get(startpos, endpos)
        
        if strip_ == STRIP_MODE_ALL:
            return lv_data.strip()
        elif strip_ == STRIP_MODE_LAST:
            try:
                return lv_data[:-1]
            except LookupError:
                return lv_data
        else:
            return lv_data

    def call_clear_data(self, event=None):
        """ clear log text """

        if messagebox.askokcancel(_('Confirm'), _('Clear data ?'), parent=self):
            self.clear_data()

    def clear_data(self):
        """ clear text """

        self.__datawidget.delete('1.0', END)

    def delete_data(self):
        """ clear text """

        self.__datawidget.delete('1.0', END)

    def insert_data(self, text, see_=False, position=END):
        """ insert text to data widget """

        self.__datawidget.insert(position, text)
        if see_:
            try:
                self.__datawidget.get("sel.first","sel.last")
            except:
                lb_sel = False
            else:
                lb_sel = True
                
            if not lb_sel:
                self.see_position(position)

    def get_datawidget(self):
        """ return datawidget """

        return self.__datawidget

    def set_wstate(self, pv_state=NORMAL):
        """ change state of widget: NORMAL/DISABLED/RO """

        lw_temp = Entry(self)
        lv_bg = lw_temp.cget('background')
        lv_fg = lw_temp.cget('foreground')
        lv_dbg = lw_temp.cget('disabledbackground')
        lv_dfg = lw_temp.cget('disabledforeground')
        lw_temp.destroy()

        if pv_state == NORMAL:
            self.__datawidget.configure(state=NORMAL, bg=lv_bg, fg=lv_fg, insertwidth=2, takefocus=1, insertofftime=300)
            self.__datawidget.unbind('<Any-KeyPress>')
        elif pv_state == DISABLED:
            self.__datawidget.configure(state=NORMAL, bg=lv_dbg, fg=lv_dfg, insertwidth=0, takefocus=0, insertofftime=0)
            make_widget_ro(self.__datawidget)
        elif pv_state == READONLY:
            self.__datawidget.configure(state=NORMAL, bg=lv_bg, fg=lv_fg, insertwidth=0, takefocus=1, insertofftime=0)
            make_widget_ro(self.__datawidget)

    def see_position(self, position=END):
        """ see specified position """

        try:
            self.__datawidget.see(position)
        except:
            pass
