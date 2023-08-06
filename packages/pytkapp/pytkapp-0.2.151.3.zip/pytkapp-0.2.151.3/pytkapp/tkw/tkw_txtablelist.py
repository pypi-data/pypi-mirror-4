#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" tablelist widget with scrolling and additional 
    controls (search, clear, unload, etc.)
"""

# pytkapp.tkw: tablelist widget with scrolling and additional controls
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
import itertools
import gettext
if __name__ == '__main__':
    if    sys.hexversion >= 0x03000000:
        gettext.install(__name__)
    else:
        gettext.install(__name__, unicode=True)
elif '_' not in __builtins__:
    _ = gettext.gettext     

if    sys.hexversion >= 0x03000000:
    from tkinter import Frame
    from tkinter.constants import N, S, W, E
else:
    from Tkinter import Frame
    from Tkconstants import N, S, W, E

# fixme: uncomment this block to run script directly OR set pythonpath for your package
#if __name__ == '__main__':
    #import sys
    #import os.path
    #lv_file = __file__
    #while os.path.split(lv_file)[1] != '':
        #lv_file = os.path.split(lv_file)[0]
        #print('append %s'%lv_file)
        #sys.path.append(lv_file)

from pytkapp.tkw.tkw_xtablelist import XTableList
from pytkapp.tkw.tkw_xtablelist import XTL_BF_HIDE, XTL_BF_SHOW
from pytkapp.tkw.tkw_routines import toolbar_button_generator, toolbar_separator_generator
import pytkapp.tkw.tkw_icons as tkw_icons

from pytkapp.pta_routines import tu

###################################
## globals
###################################  
XTL_BFG_TREE = 'tree'
gl_bfg = [XTL_BFG_TREE,]
          
gl_akw = ['allowtree',]

###################################
## routines
###################################  

###################################
## classes
###################################  
class TXTableList(XTableList):
    """ tree-XTableList """
    
    def __init__(self, parent, **kw):
        """ additional keywords:
              allowtree: True/False - show tree btns
        """        
        
        ld_kw = kw.copy()
                
        lb_allowtree = False
        
        for akw in gl_akw:
            if akw == 'allowtree':
                lb_allowtree = ld_kw.pop('allowtree', False)
                        
        XTableList.__init__(self, parent, **ld_kw)

        self.set_xtl_flag('allowtree', lb_allowtree)        
                
    def custom_bottom_subframe(self, pw_bframe, pv_r, pv_c):
        """ generate custom bottom subframe """
        
        lb_allowtree   = self.get_xtl_flag('allowtree')
        lb_allowresize = self.get_xtl_flag('allowresize')
        lb_allowexport = self.get_xtl_flag('allowexport')
        
        lv_c = pv_c
        
        if lb_allowtree:
            lw_bf = Frame(pw_bframe)
            
            item = toolbar_button_generator(lw_bf, 
                                            _('Collapse'), 
                                            tkw_icons.gv_icon_tree_collapseall, 
                                            lambda event=None, f=0: self.call_collapse(f),
                                            padx=2, pady=2)
            item.bind('<Control-Button-1>', lambda event=None, f=1: self.call_collapse(f))
            
            item = toolbar_button_generator(lw_bf, 
                                            _('Expand'), 
                                            tkw_icons.gv_icon_tree_expandall, 
                                            lambda event=None, f=0: self.call_expand(f),
                                            padx=2, pady=2)
            item.bind('<Control-Button-1>', lambda event=None, f=1: self.call_expand(f))
            
            if lb_allowresize or lb_allowexport:
                toolbar_separator_generator(lw_bf, ppadx=3, ppady=2)
                
            lw_bf.grid(row=pv_r, column=lv_c, sticky=N+E)
            self.set_xtl_bf(XTL_BFG_TREE, lw_bf)
            self.set_xtl_bfp(XTL_BFG_TREE, lv_c)
            lv_c += 1            
        
        return lv_c
    
    def manage_bottom_frame(self, pv_flag, pv_operation):
        """ hide/show bottom frame btn-groups """
        
        if pv_flag in gl_bfg:
            if pv_operation in (XTL_BF_HIDE, XTL_BF_SHOW) and self.get_xtl_flag('allow%s' % pv_flag):
                lw_frame = self.get_xtl_bf(pv_flag)
                if lw_frame is not None:
                    if pv_operation == XTL_BF_HIDE:
                        lw_frame.grid_forget()
                    else:
                        lw_frame.grid(row=0, column=self.get_xtl_bfp(pv_flag), sticky=N+E)
        else:
            XTableList.manage_bottom_frame(self, pv_flag, pv_operation)
                  
    def call_collapse(self, force=0):
        """ collapse selected row  or entire tree """
        
        lw_datawidget = self.get_datawidget()
        
        if force == 1:
            lw_datawidget.collapseall()
        else:
            lt_selection = self.curselection()
            if len(lt_selection) == 0:
                lw_datawidget.collapseall()
            else:
                for row_index in lt_selection:
                    lw_datawidget.collapse(row_index)
        
    def call_expand(self, force=0):
        """ expand selected row  or entire tree """
        
        lw_datawidget = self.get_datawidget()
        
        if force == 1:
            lw_datawidget.expandall()
        else:
            lt_selection = self.curselection()
            if len(lt_selection) == 0:
                lw_datawidget.expandall()
            else:
                for row_index in lt_selection:
                    lw_datawidget.expand(row_index)
        
    def filltree(self, pl_data, root_func, child_indx, parent_indx):
        """ generate tree from some list 
            pl_data - content
            root_func - function that applyed to row of pl_data and return True if row linked with root node
            child_indx - index of column with child id
            parent_indx - index of column with parent id
        """
        
        self.winfo_toplevel().update_idletasks()
                
        ll_roots = []
        ld_leafs = {}

        # get roots
        ll_roots = [i for i, x in enumerate(pl_data) if root_func(x)]
        
        # get leafs
        for i, data_row in enumerate(pl_data):
            ld_leafs.setdefault(data_row[parent_indx], []).append(i)
            
        for dkey in ld_leafs:
            ld_leafs[dkey].sort()
            
        # insert roots
        lw_tl = self.get_datawidget()
        
        try:     
            lw_tl.grid_forget()
                        
            # insert root
            lw_tl.insertchildlist("root", "end", tuple(map(pl_data.__getitem__, ll_roots)))
                    
            # its children...
            self.filltree_(ll_roots, ld_leafs, pl_data, child_indx, parent_indx)
        except:
            raise
        finally:
            lw_tl.grid(row=0, column=0, sticky=N+E+W+S)
    
    def filltree_(self, pl_level, pd_leafs, pl_data, child_indx, parent_indx):
        """ insert data into tree from prepared data
            pl_level - current level of tree (list of indexes)
            pd_leafs - dict for leafs
            pl_data - content
            child_indx - index of column with child id
            parent_indx - index of column with parent id
        """
        
        lw_tl = self.get_datawidget()
        
        ll_subs = []       
        ll_subss = []
        
        ll_chids = lw_tl.columncget(child_indx, '-text')        
        
        row_index = 0
        for row_data in map(pl_data.__getitem__, reversed(pl_level)):
            lv_ch = row_data[child_indx]
            try:
                ll_leafs = pd_leafs[lv_ch]
            except KeyError:
                pass
            else:
                presearch = False    
                for i in range(-1, -3, -1):
                    lv_tmpindx = row_index + i
                    if lv_tmpindx >= 0:
                        if ll_chids[lv_tmpindx] == lv_ch:                        
                            row_index = lv_tmpindx
                            presearch = True
                            break
                    else:
                        break
                if not presearch:
                    try:
                        row_index = ll_chids.index(lv_ch)
                    except ValueError:
                        row_index = ll_chids.index(tu(lv_ch))
                                    
                ll_subss.append(ll_leafs)
                try:
                    ll_leafs[1]
                except IndexError:
                    lw_tl.insertchild(row_index, "end", pl_data[ll_leafs[0]])
                else:
                    lw_tl.insertchildlist(row_index, "end", tuple(map(pl_data.__getitem__, ll_leafs)))
        
        if ll_subss:
            ll_subs = list(itertools.chain(*reversed(ll_subss)))
            
            self.filltree_(ll_subs, pd_leafs, pl_data, child_indx, parent_indx)
