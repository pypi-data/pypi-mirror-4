#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" logging tools: catching message for stdout/stderr and store into itself """

# pytkapp: logging tools: catching message for stdout/stderr and store into itself
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

from __future__ import print_function

import sys
import time
import atexit
import threading
import os

from pytkapp.pta_routines import get_estr

###################################
## globals
###################################
__go_greedlogger = None
if sys.platform != 'win32':
    lv_homepath = os.getenv('HOME')
else:
    lv_homepath = os.getenv('HOMEDRIVE')
    
gv_globalout = os.path.join(lv_homepath, 'application.log')

###################################
## routines
###################################
def get_greedlogger():
    """ create or return logger-object """
    
    global __go_greedlogger
    
    if __go_greedlogger is None:
        __go_greedlogger = GreedLogger()
        #print('greed logger !!!', end='***', file=open(gv_globalout,'a'))
        
        atexit.register(__go_greedlogger.flush)
        
    return __go_greedlogger

###################################
## classes
###################################
class GreedLogger():
    """ logger """
    
    def __init__(self):
        """ init """
                
        self.__outmethods = {}
        self.__awaitlist = {}
        
        self.__sysstdout = sys.stdout
        self.__sysstderr = sys.stderr
        
        self.__flushout = self.__sysstderr
        
        sys.stderr = self
        sys.stdout = self
        
    def set_globalout(self, pv_filename):
        """ set filename for greedlogger exceptions """
        
        global gv_globalout
        
        gv_globalout = pv_filename
        
    def set_flushout(self, po_out):
        """ set flushout """
        
        self.__flushout = po_out
        
    def get_flushout(self):
        """ get current flushout """
        
        return self.__flushout
    
    def reset_flushout(self):
        """ set initial flushout """
        
        self.__flushout = self.__sysstderr
        
    def write(self, *args, **kw):
        """ write """
    
        lv_message = args[0].rstrip()
        
        #print('catched message: %s'%lv_message, end='***', file=open(gv_globalout,'a'))
        
        if lv_message != '':
            lv_time = time.strftime("%Y.%m.%d %H:%M:%S", time.localtime(time.time()))
            
            lv_outmessage = '%s %s\n' % (lv_time, lv_message)
            
            lo_thread = threading.current_thread()
            
            if lo_thread.ident in self.__outmethods:
                self.out_message(lo_thread.ident, lv_outmessage)                                 
            else:
                if lo_thread.ident not in self.__awaitlist:
                    self.__awaitlist[lo_thread.ident] = []
                #print('put message in waitlist for thread %s'%(lo_thread.ident), end='***', file=open(gv_globalout,'a'))
                self.__awaitlist[lo_thread.ident].append( lv_outmessage )
                    
    def add_outmethod(self, thread_id, pf_method, *args, **kw):
        """ add outmethod """
        
        lb_outawait = False        
        if thread_id not in self.__outmethods:            
            self.__outmethods[thread_id] = []            
            if thread_id in self.__awaitlist:
                lb_outawait = True            
                
        if isinstance(pf_method, str):
            if   pf_method == 'print':
                self.__outmethods[thread_id].append(lambda message: print(message, end='', file=self.__sysstdout))
            elif pf_method == 'flushprint':
                self.__outmethods[thread_id].append(lambda message: print(message, end='', file=self.get_flushout()))
            elif pf_method == 'outprint':
                self.__outmethods[thread_id].append(lambda message: print(message, end='', file=open(gv_globalout,'a')))
        else:
            self.__outmethods[thread_id].append( pf_method )
        
        if lb_outawait:
            self.out_awaitlist(thread_id)
        
    def out_awaitlist(self, thread_id):
        """ out await list for thread """
        
        if thread_id in self.__awaitlist:
            #print('thread %s in awaitlist !'%(thread_id), end='***', file=open(gv_globalout,'a'))
            ll_messages = self.__awaitlist.pop(thread_id)
            for message in ll_messages:
                self.out_message(thread_id, message, True)
        #else:
            #print('thread %s not in awaitlist !'%(thread_id), end='***', file=open(gv_globalout,'a'))
            
    def out_message(self, thread_id, message, force=False):
        """ out message for thread using registered methods """
        
        if force and thread_id not in self.__outmethods:
            #print('add forced print...', end='***', file=open(gv_globalout,'a'))
            self.add_outmethod( thread_id, 'flushprint' )

        #print('th[%s] message: %s' % (thread_id, message), end='***', file=open(gv_globalout,'a'))
            
        if thread_id in self.__outmethods:
            for outmethod in self.__outmethods[thread_id]:
                try:
                    outmethod( message )
                except:
                    lv_err = get_estr()
                    if gv_globalout is not None:
                        print(lv_err, end='', file=open(gv_globalout,'a'))
                    else:
                        print(lv_err, end='', file=self.__sysstderr)
                
    def exclude_thread(self, thread_id):
        """ exclude thread from monitor """
        
        self.out_awaitlist(thread_id)
        
        if thread_id in self.__outmethods:
            del self.__outmethods[thread_id]
            
    def flush(self):
        """ flush all messages """
        
        #print('flush...', end='***', file=open(gv_globalout,'a'))
        for thread_id in list(self.__awaitlist.keys())[:]:
            #print('flush thread %s'%thread_id, end='***', file=open(gv_globalout,'a'))
            self.out_awaitlist(thread_id)
