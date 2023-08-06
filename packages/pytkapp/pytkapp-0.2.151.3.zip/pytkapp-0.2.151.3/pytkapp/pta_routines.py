#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" common app routines """

# pytkapp: common app routines
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
import time
import locale
import traceback
import encodings.aliases as en_aliases
import imp
import os
import sys
import webbrowser
import subprocess

import gettext
if __name__ == '__main__':
    if    sys.hexversion >= 0x03000000:
        gettext.install(__name__)
    else:
        gettext.install(__name__, unicode=True)
elif '_' not in __builtins__:
    _ = gettext.gettext
    
# fixme: uncomment this block to run script directly OR set pythonpath for your package
#if __name__ == '__main__':
    #import sys
    #import os.path
    #lv_file = __file__
    #while os.path.split(lv_file)[1] != '':
        #lv_file = os.path.split(lv_file)[0]
        #print('append %s'%lv_file)
        #sys.path.append(lv_file)
    
if sys.hexversion >= 0x03000000:
    from pytkapp.cpr.py3routines import *
else:
    from pytkapp.cpr.py2routines import *

###################################
## constants
###################################
gv_encin = locale.getpreferredencoding()
if gv_encin not in en_aliases.aliases.values():
    gv_encin = gv_encin.lower()
    if   gv_encin in en_aliases.aliases:
        gv_encin = en_aliases.aliases[gv_encin]
    else:
        gv_encin = gv_encin.replace('-','_')
        if gv_encin in en_aliases.aliases:
            gv_encin = en_aliases.aliases[gv_encin]
gv_encout = 'utf-8'
if gv_encout not in en_aliases.aliases.values():
    gv_encout = gv_encout.lower()
    if   gv_encout in en_aliases.aliases:
        gv_encout = en_aliases.aliases[gv_encout]
    else:
        gv_encout = gv_encout.replace('-','_')
        if gv_encout in en_aliases.aliases:
            gv_encout = en_aliases.aliases[gv_encout]
gv_defenc = gv_encout

###################################
## routines
###################################
def open_file( pv_url, pv_mode='www', pv_ref=None ):
    """open file """
    
    lv_out = None
    try:
        if os.path.isfile(pv_url):
            lv_url = pv_url
                        
            ld_env = os.environ
            if sys.platform == 'win32' and pv_ref is not None:
                lv_url = lv_url+'#'+pv_ref
            
            if sys.platform == 'win32':
                if pv_mode != 'www':
                    os.startfile(lv_url)
                else:
                    webbrowser.open(lv_url)
            elif sys.platform == 'darwin':
                subprocess.Popen(["open", lv_url])
            elif ld_env.has_key("KDE_FULL_SESSION") or ld_env.has_key("KDE_MULTIHEAD"):
                subprocess.Popen(["kfmclient", "exec", lv_url])
            elif ld_env.has_key("GNOME_DESKTOP_SESSION_ID") or ld_env.has_key("GNOME_KEYRING_SOCKET"):
                subprocess.Popen(['gnome-open', lv_url])
            else:
                subprocess.Popen(['firefox', lv_url])                
        else:
            lv_out = 'File not found'
    except:
        lv_out = get_estr()
        
    return lv_out

def convert_fname( pv_path ):
    """ extract first string from pv_path if it tuple or return it unmodified """
    
    lv_path = pv_path
    if isinstance(lv_path, tuple):
        if len(lv_path) > 0:
            lv_path = lv_path[0]
        else:
            lv_path = None
            
    return lv_path

def xprint( lv_str ):
    """ try to print message with different encodings """
    lv_printed = False
    try:
        print( lv_str )
        lv_printed = True
    except:

        if isinstance( lv_str, unicode_type ):
            try:
                print( lv_str.encode(gv_defenc) )
                lv_printed = True
            except:
                try:
                    print( lv_str.encode(locale.getpreferredencoding()) )
                    lv_printed = True
                except:
                    pass
        else:
            try:
                print( str(lv_str) )
                lv_printed = True
            except:
                try:
                    print( lv_str.decode(locale.getpreferredencoding()) )
                    lv_printed = True
                except:
                    try:
                        print( lv_str.decode(gv_defenc) )
                        lv_printed = True
                    except:
                        pass

    if not lv_printed:
        print('cannot print data with type=%s'%(lv_str.__class__))

# py2exe.org recipe
def main_is_frozen():
    return (hasattr(sys, "frozen") or # new py2exe
            hasattr(sys, "importers") # old py2exe
            or imp.is_frozen("__main__")) # tools/freeze

def get_currentfolder():
    currentfolder = ''
    if not main_is_frozen():
        try:
            currentfolder = os.path.split(os.path.abspath(__file__))[0]
        except:
            currentfolder = os.path.abspath(sys.path[0])
    else:
        currentfolder = os.path.realpath(os.path.dirname(sys.argv[0]))

    return currentfolder

def get_fflogtime(pv_mask="%Y.%m.%d %H:%M:%S"):
    return time.strftime(pv_mask, time.localtime(time.time()))
    
def get_logtime():
    return time.strftime("%Y.%m.%d %H:%M:%S", time.localtime(time.time()))

def get_strdate():
    return time.strftime("%Y.%m.%d", time.localtime(time.time()))

def get_strtime():
    return time.strftime("%H:%M:%S", time.localtime(time.time()))

def get_strdatetime():
    return time.strftime("%Y.%m.%d %H:%M:%S", time.localtime(time.time()))

def get_strdatetime_rd():
    return time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(time.time()))

def getcrtime():
    return ('%10.2f' % time.time()).replace('.', '')

def get_estr():
    lv_out = '\n'

    etype, evalue = sys.exc_info()[:2]
    try:
        lv_trlines = traceback.format_exc().splitlines()

        lv_out += tu( '='*20+'\n' )
        lv_out += tu( 'Type = %s\n'%(etype) )
        lv_out += tu( '='*20+'\n' )
        lv_out += tu( 'Value = %s\n'%( recode_str2unicode( str( evalue ), gv_encin ) ) )
        lv_out += tu( '='*20+'\n' )
        lv_out += tu( 'Stack = \n' )
        for i in range( 0, len( lv_trlines ) ):
            lv_out = lv_out + recode_str2unicode(lv_trlines[i], gv_encin)+ '\n'
    except:
        try:
            lv_out += str(etype)+':\n'+str(evalue)+':\n'+str(traceback.format_exc().splitlines())
        except:
            lv_out += str(etype)+':\n'+str(evalue)

    return lv_out

def novl( value, default ):
    if value is None:
        return default
    else:
        return value

def get_translated_dvalue(p_dict, key=''):
    return _(p_dict.get(key,'???'))

def print_envdata(platform_=True, python_=True, path_=True, syspath_=True):
    """ print env data """
    
    if platform_:
        if sys.platform == 'win32':
            lv_version = '%s.%s' % (sys.getwindowsversion()[0], sys.getwindowsversion()[1])
        else:
            lv_version = ''
        print('platform: %s %s' % (sys.platform, lv_version))
    
    if python_:
        print('python: %s' % (sys.version))    

    if path_:    
        if sys.platform == 'win32':
            lv_path = os.environ.get('PATH', None)
            lv_envsep = ';'
        else:
            lv_path = os.environ.get('LD_LIBRARY_PATH', None)
            lv_envsep = ':'
        if lv_path is not None:
            print('os path:')
            for path_key in lv_path.split(lv_envsep):
                print('\t%s' % (path_key))
        
    if syspath_:        
        print('python path:')
        for path_key in sys.path:
            print('\t%s' % (path_key))

def generate_user_layout(pv_appid, pv_cwd, pt_subdirs):
    """ generate user-specific folders """
    
    lb_fail       = False
    ld_appfolders = {}
    lv_message    = ''
    try:
        lv_currentfolder = pv_cwd
        if sys.platform != 'win32':
            lv_userfolder = os.getenv('HOME')
        else:
            lv_userfolder = os.getenv('USERPROFILE')
            
        if novl(lv_userfolder, '').strip() == '':
            lv_appfolder = lv_currentfolder
        else:
            lv_appfolder = os.path.join(os.path.abspath(lv_userfolder), pv_appid)
            
        if not os.path.isdir(lv_appfolder):
            try:
                os.mkdir(lv_appfolder)
            except:
                lv_message = get_estr()
                xprint('create %s: %s' % (lv_appfolder, lv_message,))
                lb_fail = True
                
        if not lb_fail:
            ld_appfolders['app:app'] = lv_appfolder
            
            for subdir in pt_subdirs:
                try:
                    lv_appsubfolder = os.path.join(lv_appfolder, subdir)
                    if not os.path.isdir(lv_appsubfolder):
                        os.mkdir(lv_appsubfolder)
                except:
                    lv_message = get_estr()
                    xprint('create %s: %s' % (lv_appsubfolder, lv_message,)) 
                    lb_fail = True
                    break
                else:
                    ld_appfolders['app:%s' % (subdir.lower(),)] = lv_appsubfolder
     
    except:
        lv_message = get_estr()
        xprint('layout: %s' % (lv_message,))         
        lb_fail = True
        
    return (lb_fail, ld_appfolders, lv_message,)

###################################
## classes
###################################      
class LList:
    """ store several lambda functions """
    
    def __init__(self):
        """ constructor """
        
        self._list = []
        
    def addl(self, pf_lambda):
        """ add lambda """
        
        self._list.append(pf_lambda)
        
    def __call__(self, *args):
        """ execute list """
        
        for lf in self._list:
            lf()
            
class DataClip:
    """ store some data in limited list """
    
    def __init__(self, p_depth, p_default=None):
        """ init object """
        
        if p_depth <= 0:
            raise ValueError
        self.__depth = p_depth
        self.__default = p_default
        self.__list = [p_default for x in range(self.__depth)]
        
    def pop(self, p_index=None):
        """ pop item """
        
        if p_index is None:
            lv_index = self.__depth-1
        else:
            lv_index = p_index
            
        lv_item = self.__list.pop(lv_index)
        self.__list.insert(0, self.__default)
        return lv_item
        
    def get(self, p_index=None):
        """ get item """
        
        if p_index is None:
            lv_index = self.__depth-1
        else:
            lv_index = p_index
            
        return self.__list[lv_index]
    
    def __len__(self):
        """ self lenght """
        
        return self.__depth
    
    def __getitem__(self, key):
        """ get item """
        
        return self.__list[key]
        
    def push( self, p_value=None ):
        """ add item """
        
        self.__list.pop(0)
        self.__list.append( p_value )
        
    def get_depth( self ):
        """ get depth """
        
        return self.__depth
    
    def get_list( self ):
        """ get list of items """
        
        return self.__list
            