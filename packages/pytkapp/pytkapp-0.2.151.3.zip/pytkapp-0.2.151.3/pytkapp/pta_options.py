#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" container for app options """

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
import os
import pickle
import zlib
import calendar
import locale
import gettext
if __name__ == '__main__':
    if    sys.hexversion >= 0x03000000:
        gettext.install(__name__)
    else:
        gettext.install(__name__, unicode=True)
elif '_' not in __builtins__:
    _ = gettext.gettext      
        
if    sys.hexversion >= 0x03000000:
    from tkinter import Tk, Toplevel, Scrollbar, Frame, Button, LabelFrame, PhotoImage, StringVar, IntVar, Label, Entry, Spinbox, Checkbutton, Listbox
    from tkinter.constants import N, W, E, S, NW, TOP, YES, VERTICAL, BOTH, NORMAL, DISABLED
    from tkinter.constants import GROOVE, SUNKEN
    import tkinter.messagebox as messagebox
    import tkinter.filedialog as filedialog
    from tkinter.ttk import Combobox, Notebook
else:
    from Tkinter import Tk, Toplevel, Scrollbar, Frame, Button, LabelFrame, PhotoImage, StringVar, IntVar, Label, Entry, Spinbox, Checkbutton, Listbox
    from Tkconstants import N, W, E, S, NW, TOP, YES, VERTICAL, BOTH, NORMAL, DISABLED
    from Tkconstants import GROOVE, SUNKEN
    import tkMessageBox as messagebox
    import tkFileDialog as filedialog
    from ttk import Combobox, Notebook
    
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

from pytkapp.pta_routines import novl, get_estr, xprint, tu, get_translated_dvalue, LList

from pytkapp.tkw.tkw_routines import make_widget_ro

from pytkapp.tkw.tkw_alistbox import AListBox, ALISTBOX_STYLE_COMBO, ALISTBOX_STYLE_SENTRY
from pytkapp.tkw.tkw_mlistbox import MListBox
from pytkapp.tkw.ttkcalendar import validate_date, show_calendar, ALLOWED_DATE_FORMATS, DATETIME_MAP
from pytkapp.tkw.tkw_lovbox import Lovbox, LovStringVar

###################################
## constants
###################################
OPTIONS_UI_MODE_TK = 'tk'
OPTIONS_UI_MODE_NOTK = 'notk'

DEFAULT_WRAP_LENGTH = 200
ALLOWED_OPTION_STYLES = ['None',
                         'Entry',
                         'PWDEntry',
                         'Spinbox',
                         'Checkbutton',
                         'Combobox', 
                         'xCombobox',
                         'Lovbox',
                         'AListBox',
                         'MListBox',
                         'FolderEntry',
                         'FileEntry',
                         'DateEntry']
ALLOWED_OPTION_FLAGS1 = ['value', 'state', 'value>', 'value>=', 'value<', 'value<=']
ALLOWED_OPTION_FLAGS2 = ['value', 'state', 'message']

###################################
## classes
###################################
class OptionError(Exception):
    def __init__(self, message):
        self.message = message

class OptionsContainer():
    """ storing and manipulating user-defined options """
    
    def __init__(self, pv_uimode=OPTIONS_UI_MODE_TK, superoptions=None):
        """ init object 
            uimode: 'tk'/'notk' - in case of tk we store option values in vars
            superoptions: options object of the parent, if we cant find key in self - see in super
        """
        
        self.__uimode = pv_uimode
        self.__superoptions = superoptions
        
        # options itself
        self.__options = {}
        
        # thread safe storage
        self.__thss = {}
        
        # options rule - allow change state or value linked options, see demo
        self.__rules = {}
        
        # store list of option tabs and its content
        self.__groupslist = []
        self.__groupsdata = {}
        
        # store widgets associated with options when they showed as widget
        # 'key':[widget1, widget2, widget3, ...]
        self.__optwidgets = {}
        
        self.__prevopt = {}
        
        self.__oll = {}
        
    def get_uimode(self):
        """ return uimode """
        
        return self.__uimode
    
    def get_superoptions(self):
        """ return superoptions """
        
        return self.__superoptions
    
    def has_option(self, option_key):
        """ check present option_key in options """
        
        return option_key in self.__options
        
    def has_rules(self, pv_key):
        """ if option with key has some rules than return True """

        return pv_key in self.__rules
    
    def register_option(self, option_key, p_datatype, p_default, **kw):
        """ register option """

        if self.has_option(option_key):
            lv_message = _('Option [%s]: already exists')%(option_key)
            raise OptionError( lv_message )
        
        # parse kw
        lv_wstyle = novl(kw.get('wstyle', None), 'Entry')
        lv_minv   = kw.get('minv', None)
        lv_maxv   = kw.get('maxv', None)
        lv_stepv  = kw.get('stepv', None)
        lv_cdata  = kw.get('cdata', None)
        lv_desc   = kw.get('desc', '???')
        lv_reset  = kw.get('reset', 1)
        lv_export = kw.get('export', 0)
        lv_rerun  = kw.get('rerun', 0)
        lv_group  = novl(kw.get('group', None),'<unassigned>')
                                
        # check parameters
        if lv_wstyle not in ALLOWED_OPTION_STYLES:
            lv_message = _('Option [%s]: unknown style for widget [%s]')%(option_key, lv_wstyle)
            raise OptionError( lv_message )
        
        # check style against datatype
        if lv_wstyle in ['Spinbox','Checkbutton'] and p_datatype != 'int':
            lv_message = _('Option [%s]: datatype [%s] can not be used with widgets style [%s]')%(option_key, p_datatype, lv_wstyle)
            raise OptionError( lv_message )
        
        if lv_wstyle in ['Listbox', 'AListBox', 'MListBox'] and p_datatype != 'list':
            lv_message = _('Option [%s]: datatype [%s] can not be used with widgets style [%s]')%(option_key, p_datatype, lv_wstyle)
            raise OptionError( lv_message )
        
        if lv_wstyle == 'Spinbox':
            if lv_minv is None:
                lv_message = _('Option [%s]: min. value must be defined') % (option_key)
                raise OptionError( lv_message )
            if lv_maxv is None:
                lv_message = _('Option [%s]: max. value must be defined') % (option_key)
                raise OptionError( lv_message )
            if lv_stepv is None:
                lv_message = _('Option [%s]: step value must be defined') % (option_key)
                raise OptionError( lv_message )
        
        if lv_wstyle not in ['Combobox', 'xCombobox'] and p_datatype == 'int':
            # check min,max,step
            if lv_minv is not None and not isinstance(lv_minv, int):
                lv_message = _('Option [%s]: min. datatype must be [%s]') % (option_key, p_datatype)
                raise OptionError(lv_message)
            if lv_maxv is not None and not isinstance(lv_maxv, int):
                lv_message = _('Option [%s]: max. datatype must be [%s]') % (option_key, p_datatype)
                raise OptionError(lv_message)
            if lv_stepv is not None and not isinstance(lv_stepv, int):
                lv_message = _('Option [%s]: step datatype must be [%s]') % (option_key, p_datatype)
                raise OptionError(lv_message)

        if lv_wstyle == 'PWDEntry' and p_datatype != 'str':
            lv_message = _('Option [%s]: datatype [%s] can not be used with widgets style [%s]') % (option_key, p_datatype, lv_wstyle)
            raise OptionError( lv_message )
        
        if lv_wstyle == 'Lovbox':
            if p_datatype != 'str':
                lv_message = _('Option [%s]: datatype [%s] can not be used with widgets style [%s]') % (option_key, p_datatype, lv_wstyle)
                raise OptionError( lv_message )
            elif lv_cdata is None:
                lv_message = _('Option [%s]: missed control-data') % (option_key)
                raise OptionError( lv_message )                
            elif not isinstance(lv_cdata, dict) or len(lv_cdata.keys()) != 2:
                lv_message = _('Option [%s]: invalid control-data') % (option_key)
                raise OptionError( lv_message )                
            elif len(list(lv_cdata.values())[0]) != len(list(lv_cdata.values())[1]):
                lv_message = _('Option [%s]: invalid control-data') % (option_key)
                raise OptionError( lv_message )                

        if lv_wstyle == 'DateEntry':
            if p_datatype != 'date':
                lv_message = _('Option [%s]: datatype [%s] can not be used with widgets style [%s]') % (option_key, p_datatype, lv_wstyle)
                raise OptionError( lv_message )
            elif lv_cdata is None:
                lv_message = _('Option [%s]: missed date format') % (option_key)
                raise OptionError( lv_message )
            elif lv_cdata not in ALLOWED_DATE_FORMATS:
                lv_message = _('Option [%s]: invalid date format') % (option_key)
                raise OptionError( lv_message )            
        
        # create storage
        if   p_datatype == 'int':
            if self.__uimode == OPTIONS_UI_MODE_TK:
                storage = IntVar()
            else:
                storage = None
        elif p_datatype == 'str':
            if self.__uimode == OPTIONS_UI_MODE_TK:
                if lv_wstyle != 'Lovbox':
                    storage = StringVar()
                else:
                    storage = LovStringVar()
            else:
                storage = None
        elif p_datatype == 'date':
            if self.__uimode == OPTIONS_UI_MODE_TK:
                storage = StringVar()
            else:
                storage = None            
        elif p_datatype == 'dict':
            storage = {}
        elif p_datatype == 'list':
            storage = []
        else:
            lv_message = _('Option [%s]: unrecognised datatype [%s]') % (option_key, p_datatype)
            raise OptionError(lv_message)

        if p_datatype == 'dict':
            if not isinstance(p_default, dict):
                lv_message = _('Option [%s]: incorrect default value [%s] for datatype [%s]') % (option_key, p_default, p_datatype)
                raise OptionError(lv_message)
            else:
                lv_default = p_default.copy()
        elif p_datatype == 'list':
            if not isinstance(p_default, list):
                lv_message = _('Option [%s]: incorrect default value [%s] for datatype [%s]') % (option_key, p_default, p_datatype)
                raise OptionError(lv_message)                
            else:
                lv_default = p_default[:]
        else:
            lv_default = p_default
            
        # reg option
        self.__options[option_key] = {'datatype':p_datatype,
                                      'default':lv_default,
                                      'storage':storage,
                                      'desc':lv_desc,
                                      'wstyle':lv_wstyle,
                                      'minv':lv_minv,
                                      'maxv':lv_maxv,
                                      'stepv':lv_stepv,
                                      'cdata':lv_cdata,
                                      'reset':lv_reset,
                                      'export':lv_export,
                                      'rerun':lv_rerun,
                                      'group':lv_group}
        
        self.__thss[option_key] = None
        
        self.__optwidgets[option_key] = []
        
        if lv_group not in self.__groupsdata:
            self.__groupslist.append( lv_group  )
            self.__groupsdata[lv_group] = []
        self.__groupsdata[lv_group].append(option_key)

    def clear_thss(self):
        """ clear thss values """
        
        for thss_key in self.__thss:
            self.__thss[thss_key] = None        
    
    def register_rule( self, pv_key1, pv_flag1, pv_condition1, pv_key2, pv_flag2, pv_condition2 ):
        """ add rule for some options 
            note: both options must be registered early
        """
        
        if not self.has_option(pv_key1):
            lv_message = _('Option [%s]: doesnt exists')%pv_key1
            raise OptionError( lv_message )
        if not self.has_option(pv_key2) and pv_key2 is not None:
            lv_message = _('Option [%s]: doesnt exists')%pv_key2
            raise OptionError( lv_message )
        if pv_key1 == pv_key2:
            lv_message = _('You cannot specify rule for same option')
            raise OptionError( lv_message )

        # check flags
        if pv_flag1 not in ALLOWED_OPTION_FLAGS1:
            lv_message = _('Option [%s]: unknown flag %s')%(pv_key1, pv_flag1)
            raise OptionError( lv_message )        
        if pv_flag2 not in ALLOWED_OPTION_FLAGS2:
            lv_message = _('Option [%s]: unknown flag %s')%(pv_key2, pv_flag2)
            raise OptionError( lv_message )
        
        # check values
        if pv_flag1 == 'state':
            if pv_condition1 not in [NORMAL, DISABLED,'readonly']:
                lv_message = _('Option [%s]: invalid condition flag->value: %s->%s')%(pv_key1, pv_flag1, pv_condition1)
                raise OptionError( lv_message )
        if pv_flag2 == 'state':
            if pv_condition2 not in [NORMAL, DISABLED,'readonly']:
                lv_message = _('Option [%s]: invalid condition flag->value: %s->%s')%(pv_key2, pv_flag2, pv_condition2)
                raise OptionError( lv_message )
        
        # check duplicates
        if pv_key1 in self.__rules:
            for rule in self.__rules[pv_key1]:
                f1 = rule['flag1']
                c1 = rule['cond1']
                k2 = rule['key2']
                f2 = rule['flag2']
                c2 = rule['cond2']
                
                if k2 == pv_key2 and f2 == pv_flag2 and f1 == pv_flag1 and c1 == pv_condition1:
                    lv_message = _('Option [%s]: there is exists similar rule: on %s=%s set %s: %s=%s')%(pv_key1, f1, c1, k2, f2, c2)
                    raise OptionError( lv_message )
                
        # check cycle
        if self.is_cycled( pv_key2, pv_key1, pv_flag1, [] ):
            lv_message = _('Option [%s]: for %s - cycle detected')%(pv_key1, pv_key2)
            raise OptionError( lv_message )
        
        # save rule
        if pv_key1 not in self.__rules:
            self.__rules[pv_key1] = []
        self.__rules[pv_key1].append({'flag1':pv_flag1, 
                                       'cond1':pv_condition1, 
                                       'key2':pv_key2, 
                                       'flag2':pv_flag2, 
                                       'cond2':pv_condition2})
        
    def is_cycled(self, pv_key, pv_checkedkey, pv_flag, pl_checklist):
        """ check cycles in rule """
        
        if pv_key in self.__rules:
            for rule in self.__rules[pv_key]:
                if rule not in pl_checklist:
                    k2 = rule['key2']
                    f2 = rule['flag2']
                    if k2 is not None and k2 == pv_checkedkey and f2 == pv_flag:
                        return True
                    elif k2 != pv_checkedkey:
                        ll_checklist = pl_checklist[:]
                        ll_checklist.append(rule)
                        if self.is_cycled( k2, pv_checkedkey, pv_flag, ll_checklist ):
                            return True
        return False
    
    def update_gui_labels(self):
        """ update additional widget attr for displayed options """
        
        for option_key in self.__options:
            if self.get_optionparam(option_key,'wstyle') == 'xCombobox':
                for optwidget in self.__optwidgets.get(option_key, []):
                    optwidget[0].update_label(None)
        
    def notice_of_the_eviction( self, pw_home, pb_destroyit=False ):
        """ remove option widgets that displayed on pw_home widget """
        
        if isinstance( pw_home, (Tk, Frame, LabelFrame, Toplevel, Notebook) ):
            for child in pw_home.__dict__['children'].values():
                if isinstance( child, (Frame, LabelFrame, Toplevel, Notebook) ):
                    self.notice_of_the_eviction( child )
                    
            lv_path = pw_home._w
            
            for key in self.__optwidgets:
                ll_guis = self.__optwidgets[key]
                ll_len = len(ll_guis)
                    
                for i in range(ll_len-1, -1, -1):
                    lw_item = ll_guis[i][0]
                    if lw_item is None or lw_item.winfo_parent() == lv_path:
                        del ll_guis[i]    
                        
                        if lw_item in self.__oll:
                            del self.__oll[lw_item]
                            
        if pb_destroyit:
            pw_home.destroy()
            
    def force_rules( self ):
        """ apply all rules """
        
        for key in self.__rules:
            if key in self.__optwidgets:
                self.apply_rules( key )

    def apply_rules( self, pv_key, pv_event=None ):
        """ apply rule for specified option """
        
        if pv_event is None:
            lw_item = self.__optwidgets[pv_key][-1][0]
        else:
            lw_item = pv_event.widget
        
        lv_vcond1 = self.get_value( pv_key )
        if self.get_optionparam(pv_key, 'wstyle') == 'DateEntry':
            if novl(lv_vcond1,'') != '':
                try:
                    lv_vcond1 = validate_date(lv_vcond1, self.get_optionparam(pv_key, 'cdata'))
                except ValueError:
                    lv_vcond1 = None
            else:
                lv_vcond1 = None            
                
        lv_state = str(lw_item.cget('state'))
                
        for rule in self.__rules.get(pv_key, []):
            
            lb_applyed = None
            
            lv_key2 = rule['key2']            
            lv_rule_cond1 = rule['cond1']
            if self.get_optionparam(pv_key, 'wstyle') == 'DateEntry':
                if novl(lv_rule_cond1,'') != '':
                    try:
                        lv_rule_cond1 = validate_date(lv_rule_cond1, self.get_optionparam(pv_key, 'cdata'))                
                    except ValueError:
                        lv_rule_cond1 = None
                else:
                    lv_rule_cond1 = None
            
            if (
                lv_vcond1 is not None and lv_rule_cond1 is not None and\
               (
                  (rule['flag1'] == 'value>=' and lv_vcond1 >= lv_rule_cond1 )\
               or (rule['flag1'] == 'value>' and lv_vcond1 > lv_rule_cond1 )\
               or (rule['flag1'] == 'value' and lv_vcond1 == lv_rule_cond1)\
               or (rule['flag1'] == 'value<' and lv_vcond1 < lv_rule_cond1 )\
               or (rule['flag1'] == 'value<=' and lv_vcond1 <= lv_rule_cond1 )\
               ))\
               or (rule['flag1'] == 'state' and lv_rule_cond1 == lv_state):
                lb_applyed = False
                if rule['flag2'] == 'value':
                    lv_vcond2 = rule['cond2']
                    if self.get_value(lv_key2) != lv_vcond2:
                        self.set_value(lv_key2, lv_vcond2)
                        lb_applyed = True
                elif rule['flag2'] == 'message':
                    lv_vcond2 = rule['cond2']
                    messagebox.showinfo(_('Info'), lv_vcond2)
                    lb_applyed = True
                elif rule['flag2'] == 'state':
                    lv_scond2 = rule['cond2']
                    for items_set in self.__optwidgets[lv_key2]:                        
                        lw_titem = items_set[0]
                        if self.__options[lv_key2]['wstyle'] in ['FolderEntry', 'FileEntry', 'DateEntry']:
                            items_set[0].configure( state=lv_scond2 ) # entry
                            items_set[1].configure( state=lv_scond2 ) # button
                        elif isinstance(lw_titem, AListBox) or isinstance(lw_item, MListBox):
                            lw_titem.change_state( lv_scond2 )                            
                        else:
                            lw_titem.configure( state=lv_scond2 )      
                    lb_applyed = True
                    
                #if lb_applyed:
                    #print('applyed rule [%s]->[%s]' % (pv_key, lv_key2))
                            
                # check rules for changed key
                self.apply_rules( lv_key2 )
                        
    def overawe_widget( self, pw_item, pv_key, pv_mode='rule' ):
        """ bind widget with rules """
        
        if pv_mode == 'audit':
            lf_c = lambda event = None, w = pw_item, k = pv_key: self.audit_widget( w, k )
        elif pv_mode == 'validate':
            lf_c = lambda event = None, w = pw_item, k = pv_key: self.validate_item( w, k )
        else:
            lf_c = lambda event = None, k = pv_key: self.apply_rules( k, event )
        
        if pw_item not in self.__oll:
            self.__oll[pw_item] = LList()
        lf_ll = self.__oll[pw_item]
        lf_ll.addl(lf_c)
        
        pw_item.bind('<Tab>', lf_ll, '+')
        pw_item.bind('<Return>', lf_ll, '+')
        pw_item.bind('<Escape>', lf_ll, '+')
        if issubclass( pw_item.__class__, Combobox ):
            pw_item.bind('<<ComboboxSelected>>', lf_ll, '+')
        elif isinstance( pw_item, Checkbutton ):
            pw_item.configure( command = lf_ll )
        elif isinstance( pw_item, Spinbox ):
            pw_item.configure( command = lf_ll )
            pw_item.bind('<FocusOut>', lf_ll, '+')
        elif isinstance( pw_item, AListBox ):
            pw_item.bind('<FocusOut>', lf_ll, '+')
        elif isinstance( pw_item, MListBox ):
            pw_item.bind('<FocusOut>', lf_ll, '+')
        else:
            pw_item.bind('<FocusOut>', lf_ll, '+')

    def audit_widget( self, pw_item, pv_key):
        """ audit widget changes """
        
        if isinstance(pw_item, AListBox):
            lw_item = pw_item.get_listbox()
        if isinstance(pw_item, MListBox):
            lw_item = pw_item.get_listbox()
        elif issubclass( pw_item.__class__, Combobox ):
            lw_item = pw_item
        else:
            lw_item = pw_item
        
        if self.is_defaulted(pv_key):
            # fixme: remove print !!!
            #print('%s has default value !' % pv_key)
            
            lv_oldcursor = ''
            
            if lw_item.cget('cursor') != lv_oldcursor:            
                lw_item.configure(cursor=lv_oldcursor)
        else:
            # fixme: remove print !!!
            #print('%s has non default value !' % pv_key)

            if lw_item.cget('cursor') != 'hand2':
                lw_item.configure(cursor='hand2')
            
        return "break"
    
    def translate_desc(self):
        """ translate desc of options """
        
        for option_key in self.__options:
            option_desc = self.__options[option_key]['desc']
            self.__options[option_key]['desc'] = _(option_desc)
    
    def diff( self, other, pl_skiplist=None, p_all=False, p_exists=True ):
        """generate list of diff. for options in both objects"""     
        
        ll_out = []
        
        if pl_skiplist is None:
            ll_skiplist = []
        else:
            ll_skiplist = pl_skiplist[:]
        
        for item in list(self.__options.keys()):
            opt = self.__options[item]
            
            if (opt['export'] == 1 or p_all) and item not in ll_skiplist:
                if other.has_option(item):
                    if self.get_value( item ) != other.get_value( item ):
                        ll_out.append( item )
                else:
                    if not p_exists:
                        ll_out.append( item )
            
        return ll_out
            
    def accept_value( self, option_key, value ):
        """ accept value for options """
        
        lv_out = 'OK'
        
        if self.has_option(option_key):
            lv_option = self.__options[option_key]            
            lv_datatype = lv_option['datatype']
            if lv_option['wstyle'] in ['Spinbox','Checkbutton']:
                try:
                    lv_value = int(value)
                except:
                    lv_value = None
                if isinstance(lv_value, int):
                    if lv_option['minv'] is not None and lv_value < lv_option['minv']:
                        lv_out = _('The value less than allowed [%s]')%(str(lv_option['minv']))
                    if lv_option['maxv'] is not None and lv_value > lv_option['maxv']:
                        lv_out = _('The value more than allowed [%s]')%(str(lv_option['maxv']))
                else:
                    lv_out = _('Invalid datatype')
            elif lv_option['wstyle'] in ['Combobox','xCombobox']:
                lv_value = value
                if lv_datatype == 'int':
                    try:
                        lv_value = int(value)
                    except:
                        pass                
                if lv_value not in lv_option['cdata']:
                    lv_out = _('Inadmissible value')
            elif lv_option['wstyle'] == 'DateEntry':
                if novl(value, '') == '':
                    lb_result = True
                else:
                    lb_result = False
                    try:
                        if validate_date(value, lv_option['cdata']) is None:
                            lb_result = False
                        else:
                            lb_result = True
                    except ValueError:
                        lb_result = False
                        
                if not lb_result:
                    lv_out = _('Invalid value/format')
        else:
            lv_out = _('Unknown option')
            
        return lv_out
                
    def get_report(self):
        """report contains as list"""
        
        ll_report = []

        lv_header = '-'*10+_(' Current options ')+'-'*10
        ll_report.append(lv_header)
        
        ll_opt = list(self.__options.keys())
        ll_opt.sort()
        for option_key in ll_opt:
            lv_option = self.__options[option_key]   
            option_value = self.get_value(option_key)
                                      
            if   lv_option['wstyle'] == 'Checkbutton':
                if option_value == lv_option['minv']:
                    option_value = '( )'
                else:
                    option_value = '(X)'
            elif lv_option['wstyle'] == 'xCombobox':
                option_value = '%s -> %s' % (tu(option_value),  tu(lv_option['cdata'][option_value]))
            
            lv_coded_key = tu(option_key)
            lv_coded_val = tu(option_value)
            
            ll_report.append(lv_coded_key + ': ' + lv_coded_val)

        ll_report.append(' ')
        return ll_report            
        
    def reset(self, force=0):
        """reset options to default values"""
        
        for option_key in self.__options:
            lv_defvalue = self.__options[option_key]['default']
            lv_datatype = self.__options[option_key]['datatype']
            
            if force == 1 or self.__options[option_key]['reset'] == 1:
                if lv_datatype == 'list':
                    lv_value = lv_defvalue[:]
                elif lv_datatype == 'dict':
                    lv_value = lv_defvalue.copy()
                else:
                    lv_value = lv_defvalue
            
                if not self.set_value(option_key, lv_value):
                    lv_message = 'cannot reset option [%s]' % (option_key)
                    xprint(lv_message)
                
        self.update_gui_labels()

    def set_value(self, option_key, option_value, pb_chdef=False, pb_writethss=False):
        """set specified option to value"""
        
        result = False        
        try:
            if self.has_option(option_key):
                ld_option = self.__options[option_key]
                
                if ld_option['datatype'] == 'int':
                    lv_value = int(option_value)
                elif ld_option['datatype'] == 'str':                    
                    lv_value = option_value
                elif ld_option['datatype'] == 'date':                    
                    lv_value = option_value
                elif ld_option['datatype'] == 'list':
                    if isinstance(option_value, list):
                        lv_value = option_value
                    else:
                        raise TypeError
                elif ld_option['datatype'] == 'dict':
                    if isinstance(option_value, dict):
                        lv_value = option_value
                    else:
                        raise TypeError
                else:
                    raise TypeError
                
                if self.__uimode == OPTIONS_UI_MODE_TK and self.__options[option_key]['datatype'] not in ['dict','list']:
                    self.__options[option_key]['storage'].set(lv_value)
                    result = True
                else:
                    self.__options[option_key]['storage'] = lv_value
                    result = True
                    
                if pb_chdef:
                    self.__options[option_key]['default'] = lv_value
                    
                if pb_writethss:
                    self.__thss[option_key] = lv_value
                    
                # complex. widgets
                lv_wstyle = self.__options[option_key]['wstyle']
                for wdata in self.__optwidgets[option_key]:
                    witem = wdata[0]
                    try:
                        if lv_wstyle in ('AListBox', 'MListBox',):
                            witem.set_list(lv_value)
                    except:
                        witem = None
                
                    if witem is not None:
                        self.audit_widget(witem, option_key)
        except:
            result = False
            
        return result

    def append_value(self, option_key, option_value):
        """ append value to option-list """
        
        result = False
        
        try:
            lv_option = self.get_option(option_key)
            if lv_option is not None and lv_option['storage'] == 'list':            
                lv_option['storage'].append(option_value)
                result = True
        except:
            result = False
            
        return result

    def get_option(self, option_key):
        """get option"""
        
        return self.__options.get(option_key, None)
    
    def get_optionparam(self, option_key, option_param):
        """ get some parameter of option """
        
        lv_out = None
        
        lv_option = self.get_option(option_key)
        
        if lv_option is not None:
            lv_out = lv_option.get(option_param, None)
        else:
            lv_out = None
            
        return lv_out
    
    def set_optionparam(self, option_key, option_param, param_value):
        """ set some parameter of option """
        
        lv_option = self.get_option(option_key)
        
        if lv_option is not None:
            if option_param in lv_option:
                if option_param == 'cdata':
                    lv_option[option_param] = param_value

    def get_value(self, option_key, pv_readthss=False, p_copy=False):
        """get option value"""
        
        result = None
        if self.has_option(option_key):
            if not pv_readthss:
                if self.__uimode == OPTIONS_UI_MODE_TK and self.__options[option_key]['datatype'] not in ['dict','list']:
                    result = self.__options[option_key]['storage'].get()
                else:
                    result = self.__options[option_key]['storage']
            else:
                result = self.__thss[option_key]
                
            # return copy of dict/list
            if p_copy:
                if self.__options[option_key]['datatype'] == 'list':
                    result = novl(result, [])[:]
                elif self.__options[option_key]['datatype'] == 'dict':
                    result = novl(result, {}).copy()
                
        elif self.__superoptions is not None:
            result = self.__superoptions.get_value(option_key, pv_readthss)
                
        return result

    def get_defvalue(self, option_key):
        """get option default value"""
        
        result = None
        if self.has_option(option_key):
            result = self.__options[option_key]['default']
                
            # return copy of dict/list
            if self.__options[option_key]['datatype'] == 'list':
                result = novl(result, [])[:]
            elif self.__options[option_key]['datatype'] == 'dict':
                result = novl(result, {}).copy()
                
        elif self.__superoptions is not None:
            result = self.__superoptions.get_defvalue(option_key)
                
        return result
    
    def get_datatype(self, option_key):
        """get option datatype"""
        
        result = None
        if self.has_option(option_key):
            result = self.__options[option_key]['datatype']                
        elif self.__superoptions is not None:
            result = self.__superoptions.get_datatype(option_key)
                
        return result
    
    def get_wstyle(self, option_key):
        """get option wstyle"""
        
        result = None
        if self.has_option(option_key):
            result = self.__options[option_key]['wstyle']                
        elif self.__superoptions is not None:
            result = self.__superoptions.get_wstyle(option_key)
                
        return result
    
    def is_defaulted(self, pv_key):
        """is value eq. to default ?"""
        
        lv_res = True
        
        try:
            lv_datatype = self.get_datatype(pv_key)
            if lv_datatype in ('list', 'dict',):
                lv_value = self.get_value(pv_key, False, True)
            else:
                lv_value = self.get_value(pv_key, False)
                
            lv_dvalue = self.get_defvalue(pv_key)
            
            if lv_datatype == 'list':
                if len(lv_value) != len(lv_dvalue):
                    lv_res = False
                else:
                    for vindx, vval in enumerate(lv_value):
                        if vval != lv_dvalue[vindx]:
                            lv_res = False
                            break
            elif lv_datatype == 'dict':
                if len(list(lv_value.keys())) != len(list(lv_dvalue.keys())):
                    lv_res = False
                else:
                    for vkey, vval in lv_value.items():
                        if vkey not in lv_dvalue or \
                           lv_dvalue[vkey] != vval:
                            lv_res = False
                            break
            else:
                lv_res = True if lv_value == lv_dvalue else False
            
        except:
            lv_message = 'check [%s]: %s' % (pv_key, get_estr())
            xprint(lv_message)
        
        return lv_res
    
    def fill_thss(self):
        """ fill thread safe storage as usual dict: option_key: option_value """
        
        for option_key in self.__options:
            option_value = self.get_value(option_key)
            self.__thss[option_key] = option_value
    
    def refresh_widget(self, p_widget, option_key):
        """ refresh content of the associated widget """
        
        if self.__uimode == OPTIONS_UI_MODE_TK:
            if self.has_option(option_key):
                lv_message = 'failed to refresh unknown option: [%s]' % (option_key)
                xprint(lv_message)
            else:
                ld_option = self.__options[option_key]
                
                if isinstance( p_widget, Listbox ):
                    p_widget.delete(0,"end")
                    for item in ld_option['storage']:
                        p_widget.insert("end", item)
                
                p_widget.update_idletasks()
            
    def show(self, master, option_key, pr, pc, title=True, **args ):
        """ show option as widget """
        
        lt_items = ()

        if self.__uimode != OPTIONS_UI_MODE_TK:
            return None
            
        if not self.has_option(option_key):
            lv_message = 'failed to show unknown option: [%s]' % (option_key)
            xprint(lv_message)
        else:
            lv_option = self.__options[option_key]            
            
            # parse args
            lv_wraplength  = args.get('wraplength', DEFAULT_WRAP_LENGTH)
            lv_width       = args.get('width', 5)
            lv_descwidth   = args.get('descwidth', 30)
            lv_activestyle = args.get('activestyle', "none")
            lv_ro          = args.get('ro', False)
            lv_twoline     = args.get('twoline', False)
            if lv_ro:
                lv_state = DISABLED
            else:
                lv_state = NORMAL
                
            # produce widgets            
            if lv_option['wstyle'] == 'Spinbox':
                if title:
                    l = Label( master, 
                               text=lv_option['desc'], 
                               justify='left', 
                               wraplength=lv_wraplength)
                    l.grid(row=pr, column=pc, sticky=W)
                    
                if lv_ro:
                    lv_state = "readonly"                    

                s = Spinbox( master, 
                             from_= lv_option['minv'], 
                             to_ = lv_option['maxv'], 
                             increment=lv_option['stepv'], 
                             width=lv_width, 
                             justify='center',
                             state=lv_state,
                             textvariable = lv_option['storage'] )
                s.grid(row=pr, column=pc+1, sticky=E, padx=2, pady=1)
                lt_items = (s,)
            elif lv_option['wstyle'] in ['FolderEntry', 'FileEntry', 'DateEntry']:                
                if lv_twoline or not title:
                    lv_cspan = 2
                else:
                    lv_cspan = 1    
                    
                if title:
                    l = Label( master, 
                               text=lv_option['desc'],
                               justify='left',
                               wraplength=lv_wraplength)
                    l.grid(row=pr, column=pc, sticky=NW, columnspan=lv_cspan)
                
                # make new frame
                lo_frame = Frame( master )
                
                e = Entry( lo_frame, 
                           width=lv_width, 
                           justify='left', 
                           textvariable = lv_option['storage'] )
                e.grid(row=0, column=0, padx=2, pady=2, sticky=N+E+W+S)
                
                if lv_ro:
                    make_widget_ro(e)
                    e.configure(insertofftime=100000, insertontime=0)
                        
                if lv_option['wstyle'] == 'FolderEntry':
                    lf_bcomm = args.get('bcommand', lambda x=1: self.set_value(option_key, filedialog.askdirectory(title='Test open folder')))
                    img = PhotoImage(data=pta_icons.gv_options_openfolder)
                elif lv_option['wstyle'] == 'FileEntry':
                    lf_bcomm = args.get('bcommand', lambda x=1: self.set_value(option_key, filedialog.askopenfilename(title='Test open file')))
                    img = PhotoImage(data=pta_icons.gv_options_openfile)
                elif lv_option['wstyle'] == 'DateEntry':
                    lf_bcomm = lambda x = 1: self.call_calendar(master, option_key)
                    img = PhotoImage(data=pta_icons.gv_options_calendar)
                
                select_btn = Button( lo_frame, image=img, command = lf_bcomm )
                select_btn.img = img                
                select_btn.grid(row=0, column=1, padx=2, pady=2, sticky=N+E+W+S)
                
                lo_frame.columnconfigure(0, weight=1)
                     
                if lv_twoline:
                    lv_r = pr + 1
                    lv_c = pc
                elif title:
                    lv_r = pr
                    lv_c = pc + 1
                else:
                    lv_r = pr
                    lv_c = pc
                    
                lo_frame.grid(row=lv_r, column=lv_c, sticky=E+W, padx=2, pady=2, columnspan=lv_cspan)
                
                lt_items = (e, select_btn)
            elif lv_option['wstyle'] == 'Entry':
                if lv_twoline or not title:
                    lv_cspan = 2
                else:
                    lv_cspan = 1
                    
                if title:
                    l = Label( master, 
                               text=lv_option['desc'],
                               justify='left',
                               wraplength=lv_wraplength)
                    l.grid(row=pr, column=pc, sticky=W)
                    
                e = Entry( master, 
                           width=lv_width, 
                           justify='left', 
                           textvariable = lv_option['storage'] )
                if lv_twoline:
                    lv_r = pr + 1
                    lv_c = pc
                elif title:
                    lv_r = pr
                    lv_c = pc + 1
                else:
                    lv_r = pr
                    lv_c = pc                
                
                e.grid(row=lv_r, column=lv_c, sticky=E+W, padx=2, pady=2, columnspan=lv_cspan)
                
                if lv_ro:
                    make_widget_ro(e)
                lt_items = (e,)
            elif lv_option['wstyle'] == 'PWDEntry':
                if title:
                    l = Label( master, 
                               text=lv_option['desc'],
                               justify='left',
                               wraplength=lv_wraplength)
                    l.grid(row=pr, column=pc, sticky=W)
                e = Entry( master, 
                           width=lv_width, 
                           justify='left', 
                           textvariable = lv_option['storage'],
                           show='*',
                           exportselection=0)
                if title:
                    lv_c = pc + 1
                    e.grid(row=pr, column=lv_c, sticky=E+W, padx=2, pady=2)
                else:
                    lv_c = pc       
                    e.grid(row=pr, column=lv_c, sticky=E+W, padx=2, pady=2, columnspan=2)
                
                if lv_ro:
                    make_widget_ro(e)
                lt_items = (e,)                
            elif lv_option['wstyle'] == 'Lovbox':
                if title:
                    l = Label( master, 
                               text=lv_option['desc'],
                               justify='left',
                               wraplength=lv_wraplength)
                    l.grid(row=pr, column=pc, sticky=W)
                lw_lbox = Lovbox( master, 
                                  values=lv_option['cdata']['values'], 
                                  labels=lv_option['cdata']['labels'], 
                                  width=lv_width, 
                                  justify='center', 
                                  state='readonly',
                                  variable = lv_option['storage'])
                if title:
                    lv_c = pc + 1
                    lw_lbox.grid(row=pr, column=lv_c, sticky=E, padx=2, pady=2)
                else:
                    lv_c = pc       
                    lw_lbox.grid(row=pr, column=lv_c, sticky=E+W, padx=2, pady=2, columnspan=2)
                
                lt_items = (lw_lbox,)                
            elif lv_option['wstyle'] == 'Listbox':
                lv_scroll = args.get('scroll', False)
                lbframe = Frame (master)
                if title:
                    l = Label( lbframe, 
                               text=lv_option['desc'],
                               justify='left',
                               wraplength=lv_wraplength)
                    l.grid(row=0, column=0, sticky=W)
                l = Listbox( lbframe, 
                             width=lv_width, 
                             selectmode='single', 
                             activestyle = lv_activestyle )
                if 'pheight' in args:
                    l.configure( height=args['pheight'] )
                for item in lv_option['storage']:
                    l.insert("end", item)
                l.grid(row=1, column=0, sticky=N+E+W+S, padx=2, pady=2)
                if lv_scroll:
                    sb = Scrollbar(lbframe)
                    sb.config(orient=VERTICAL, command=l.yview)
                    sb.grid(row=1, column=1, sticky=N+S+E)
                    l.config(yscrollcommand=sb.set)
                if lv_ro:
                    make_widget_ro(l)
                lbframe.columnconfigure( 0, weight = 1 )
                lbframe.rowconfigure( 1, weight = 1 )
                lbframe.grid(row=pr, column=pc, sticky=N+E+W+S, padx=2, pady=2)
                lt_items = (l,)
            elif lv_option['wstyle'] == 'AListBox':
                if lv_twoline or not title:
                    lv_cspan = 2
                else:
                    lv_cspan = 1
                
                if title:
                    l = Label( master, 
                               text=lv_option['desc'],
                               justify='left',
                               wraplength=lv_wraplength)
                    l.grid(row=pr, column=pc, sticky=NW, columnspan=lv_cspan)
                ll_cdata = lv_option.get('cdata', None)
                if ll_cdata is not None and isinstance(ll_cdata, list):
                    w = AListBox(master, lv_option['storage'], width=lv_width, style=ALISTBOX_STYLE_COMBO, values=ll_cdata)
                elif ll_cdata is not None and hasattr(ll_cdata, '__call__'):
                    w = AListBox(master, lv_option['storage'], width=lv_width, style=ALISTBOX_STYLE_SENTRY, sentryfunc=ll_cdata)
                else:
                    w = AListBox(master, lv_option['storage'], width=lv_width)
                w.configure( relief=SUNKEN, bd=2, padx=2, pady=2 )
                if 'pheight' in args:
                    w.configure_listbox( height=args['pheight'] )
                    
                if lv_twoline:
                    lv_r = pr + 1
                    lv_c = pc
                elif title:
                    lv_r = pr
                    lv_c = pc + 1
                else:
                    lv_r = pr
                    lv_c = pc
                    
                w.grid(row=lv_r, column=lv_c, sticky=N+E+W+S, padx=2, pady=2, columnspan=lv_cspan)
                
                lt_items = (w,)                  
            elif lv_option['wstyle'] == 'MListBox':
                if lv_twoline or not title:
                    lv_cspan = 2
                else:
                    lv_cspan = 1
                
                if title:
                    l = Label( master, 
                               text=lv_option['desc'],
                               justify='left',
                               wraplength=lv_wraplength)
                    l.grid(row=pr, column=pc, sticky=NW, columnspan=lv_cspan)
                ll_cdata = lv_option.get('cdata', None)
                w = MListBox(master, lv_option['storage'], width=lv_width)
                w.configure( relief=SUNKEN, bd=2, padx=2, pady=2 )
                if 'pheight' in args:
                    w.configure_listbox( height=args['pheight'] )
                    
                if lv_twoline:
                    lv_r = pr + 1
                    lv_c = pc
                elif title:
                    lv_r = pr
                    lv_c = pc + 1
                else:
                    lv_r = pr
                    lv_c = pc
                    
                w.grid(row=lv_r, column=lv_c, sticky=N+E+W+S, padx=2, pady=2, columnspan=lv_cspan)
                
                lt_items = (w,)                  
            elif lv_option['wstyle'] == 'Checkbutton':
                if title:
                    l = Label( master, 
                               text=lv_option['desc'],
                               justify='left',
                               wraplength=lv_wraplength)
                    l.grid(row=pr, column=pc, sticky=W)
                c = Checkbutton( master, 
                                 onvalue=lv_option['maxv'], 
                                 offvalue=lv_option['minv'], 
                                 width=lv_width, 
                                 justify='center', 
                                 state=lv_state,
                                 variable = lv_option['storage'] )
                c.grid(row=pr, column=pc+1, sticky=N+E+S, padx=2, pady=1)
                lt_items = (c,)
            elif lv_option['wstyle'] == 'Combobox':
                if title:
                    l = Label( master, 
                               text=lv_option['desc'],
                               justify='left',
                               wraplength=lv_wraplength)
                    l.grid(row=pr, column=pc, sticky=W)
                if not lv_ro:
                    lv_state = "readonly"
                c = Combobox( master,                               
                              values=lv_option['cdata'], 
                              width=lv_width, 
                              justify='center', 
                              state=lv_state,
                              textvariable = lv_option['storage'] )
                c.grid(row=pr, column=pc+1, sticky=E, padx=2, pady=1)
                lt_items = (c,)
            elif lv_option['wstyle'] == 'xCombobox':
                cdesc = Label( master, 
                               width=lv_descwidth,
                               relief=GROOVE, 
                               text='???', 
                               justify='center')
                if title:
                    l = Label( master, 
                               text=lv_option['desc'],
                               justify='left',
                               wraplength=lv_wraplength)
                    l.grid(row=pr, column=pc, sticky=W)
                c = Combobox( master, 
                              width=lv_width,
                              justify="left", 
                              textvariable = lv_option['storage'],
                              state="readonly",
                              values=list(lv_option['cdata'].keys()) )
                c.grid(row=pr, column=pc+1, sticky=E, padx=2, pady=1)
                cdesc.grid(row=pr+1, column=pc, padx=2, pady=1, columnspan=2, sticky=N+E+W+S)
                # on change
                lv_f = lambda event, p_dict = lv_option['cdata']: cdesc.configure( text = get_translated_dvalue( p_dict, lv_option['storage'].get() ) )
                lv_f(None)
                c.bind('<<ComboboxSelected>>', lv_f)
                c.update_label = lv_f
                
                lt_items = (c, cdesc)  
            elif lv_option['wstyle'] == 'None':
                lt_items = (None,)
                
            # store widget data
            self.__optwidgets[option_key].append(lt_items)

            # overware widget
            if self.has_rules(option_key):
                self.overawe_widget(lt_items[0], option_key, 'rule')
                
            if not lv_ro:
                if lv_option['wstyle'] == 'DateEntry':
                    self.overawe_widget(lt_items[0], option_key, 'validate')
                if lt_items[0]:
                    self.overawe_widget(lt_items[0], option_key, 'audit')
                    
        return lt_items
    
    def validate_item(self, pw_item, pv_key):
        """ simple validate function """
        
        lv_value = self.get_value(pv_key)
        
        lv_check = self.accept_value(pv_key, lv_value)
        if lv_check != 'OK':
            if self.__uimode == OPTIONS_UI_MODE_TK:
                self.set_value(pv_key, '')
                messagebox.showerror(_('Error'),
                                     lv_check,
                                     master=pw_item.winfo_toplevel())
                pw_item.focus_set()
            else:                
                xprint(lv_check)
                
            return "break"     
        
    def call_calendar(self, pw_master, pv_optionkey):
        """ call calendar window """
        
        lv_currvalue = self.get_value(pv_optionkey)
        
        if novl(lv_currvalue, '') != '':
            lv_dtval = validate_date(lv_currvalue, self.get_optionparam(pv_optionkey, 'cdata'))
        else:
            lv_dtval = None
        
        ld_kw = {}
        ld_kw['firstweekday'] = calendar.MONDAY
        ld_kw['selectforeground'] = '#ffffff'
        ld_kw['selectbackground'] = '#0000ff'
        
        if sys.platform == 'win32':
            ld_kw['locale'] = 'C'
        else:
            ld_kw['locale'] = locale.getdefaultlocale()
        
        ld_kw['outformat'] = DATETIME_MAP[self.get_optionparam(pv_optionkey,'cdata')]
        if lv_dtval is not None:
            ld_kw['year'] = lv_dtval.year
            ld_kw['month'] = lv_dtval.month

        lv_value = show_calendar(pw_master,
                                 **ld_kw)
        
        if novl(lv_value, '') != '':
            self.set_value(pv_optionkey, lv_value)
            self.apply_rules(pv_optionkey)
    
    def show_optnotebook(self, master, pd_optopts, **kw):
        """ show options in Notebook widget 
            master - canvas or toplevel for notebook
            pd_optopts - dict with parameters for option's widgets
            kw keys:
                excluded_groups: list of excluded groups
                excluded_options: list of excluded options
        """
        
        ld_result = {}
        
        ll_excluded_grps = kw.get('excluded_groups', [])
        ll_excluded_opts = kw.get('excluded_options', [])
        
        lw_container = Notebook( master )
        
        for tab_header in self.__groupslist:
            if tab_header not in ll_excluded_grps:
                lv_r = lv_c = 0
                tab_frame = Frame( lw_container )
                tab_frame.grid()
                lw_container.add( tab_frame, text=_(tab_header), padding=2 )
                tab_frame.columnconfigure(1, weight=1)
                for option_key in self.__groupsdata[tab_header]:
                    if option_key not in ll_excluded_opts:
                        ld_optopt = pd_optopts.get(option_key, {})
                        if 'title' in ld_optopt:
                            lv_title = ld_optopt.pop('title')
                        else:
                            lv_title = True                    
                        if lv_title == True:
                            items = self.show(tab_frame, option_key, lv_r, lv_c, True, **ld_optopt )
                        else:
                            items = self.show(tab_frame, option_key, lv_r, lv_c, False, **ld_optopt )
                        if ld_optopt.get('twoline', False) == True or self.get_wstyle(option_key) == 'xCombobox':
                            lv_r += 2 
                        else:
                            lv_r += 1                
                            
                        ld_result[option_key] = items                
        
        lw_container.pack(side=TOP, fill=BOTH, expand=YES)
        
        ld_result['optnotebook'] = lw_container
        
        return ld_result
    
    def export_(self, filepath, filename, **kw):
        """ export options to external file """
        
        lv_out = None
        
        lb_makebak = kw.get('makebak', False)
        lb_prevstate = kw.get('prevstate', False)
        
        try:
            ld_copy = {}
                
            # create copy of options - store ONLY values
            for option_key in self.__options:
                lv_option = self.__options[option_key]
                
                lb_expallowed = novl(self.get_optionparam(option_key, 'export'), 0) == 1
                
                if lb_expallowed:                    
                    lv_optdtype = lv_option['datatype']
                
                    if lv_optdtype == 'list':
                        if lb_prevstate:
                            lv_value = self.__prevopt.get(option_key, lv_option['storage'])[:]
                        else:
                            lv_value = lv_option['storage'][:]
                    elif lv_optdtype == 'dict':
                        if lb_prevstate:
                            lv_value = self.__prevopt.get(option_key, lv_option['storage']).copy()
                        else:
                            lv_value = lv_option['storage'].copy()
                    else:
                        if lb_prevstate:
                            lv_value = self.__prevopt.get(option_key, self.get_value(option_key))
                        else:
                            lv_value = self.get_value(option_key)
                            
                        if lv_option['wstyle'] == 'PWDEntry':
                            lv_value = zlib.compress(lv_value, 9)
                            
                    ld_copy[option_key] = lv_value
                                            
            # export copy            
            lv_path = os.path.realpath(filepath)
            lv_file = filename
    
            if novl(lv_path, '') == '' or not os.path.isdir(lv_path):
                lv_path = os.getcwd()
                
            lv_filename = os.path.join(lv_path, lv_file)
            
            if lb_makebak:
                if os.path.isfile( lv_filename ):
                    if os.path.isfile( lv_filename+'.bak' ):
                        os.remove( lv_filename+'.bak' )
                    os.rename( lv_filename, lv_filename+'.bak' )
    
            with open(lv_filename, 'wb+') as lo_f:
                # keep comp. with py3
                lv_protocol = 2                
                pickle.dump(ld_copy, lo_f, lv_protocol)
        except:
            lv_out = get_estr()
            
        return lv_out
    
    def sync_(self, option_key=None):
        """ sync prevopt with current value of option """
        
        if option_key is None:
            for opt_key in self.__options:
                self.__prevopt[opt_key] = self.get_value(opt_key)
        elif option_key in self.__options:
            self.__prevopt[option_key] = self.get_value(option_key)
    
    def import_(self, filepath, filename, **kw):
        """ import options from external file """
        
        lv_out = None
        
        try:
            lv_path = os.path.realpath(filepath)
            lv_file = filename        
            
            lv_filename = os.path.join(lv_path, lv_file)
            
            if os.path.isfile(lv_filename):
                # get option from file
                with open(lv_filename, 'rb') as lo_f:
                    ld_copy = pickle.load(lo_f)
                    
                # set options values
                self.__prevopt = {}
                
                for option_key in self.__options:
                    lb_expallowed = novl(self.get_optionparam(option_key, 'export'), 0) == 1
                    
                    if lb_expallowed:
                        lv_wstyle = self.get_optionparam(option_key,'wstyle')

                        if option_key in ld_copy:
                            lv_value = ld_copy[option_key]
                            if lv_wstyle == 'PWDEntry':
                                lv_value = zlib.decompress(lv_value)
                                
                            lv_accept = self.accept_value(option_key, lv_value)
                            
                            if lv_accept == 'OK':
                                self.set_value(option_key, lv_value, True)
                                
                                self.__prevopt[option_key] = lv_value
                            else:
                                lv_message = 'Failed to import value [%s] of option [%s]: %s' % (lv_value, option_key, lv_accept)
                                xprint(lv_message)
                                
                                self.__prevopt[option_key] = self.get_value(option_key)
                        else:
                            self.__prevopt[option_key] = self.get_value(option_key)
            else:                
                lv_out = '-1'
                
        except:
            lv_out = get_estr()
            
        return lv_out
        