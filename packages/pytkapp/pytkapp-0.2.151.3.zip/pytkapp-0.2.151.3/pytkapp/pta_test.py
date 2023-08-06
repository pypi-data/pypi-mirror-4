#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" pattern of app tests """

# pytkapp: pattern of app tests
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
import time
import os
import copy

from pytkapp.pta_routines import get_estr, Others

###################################
## constants
###################################
TEST_SOURCE_DB = 'db'
TEST_SOURCE_FS = 'fs'

TEST_RESULT_PASSED = 1
TEST_RESULT_FAILED = 0
TEST_RESULT_CRASHED = -1

###################################
## globals
###################################

###################################
## routines
###################################

###################################
## classes
###################################
class BaseTest:
    """ regression test """    
    
    def __init__(self, rt_mode, rt_id, rt_name, rt_conn=None, **kw):
        """ constructor """
        
        self.__rt_mode = rt_mode
        self.__rt_id = rt_id
        self.__rt_name = rt_name
        self.__rt_conn = rt_conn
        
        self.__ikw = copy.deepcopy(kw)
        self.__rkw = {}
        
        self._format = None
        self._sdata = None
        self._rdata = None
        self._cdata = None
        
        self._rflag = None
        self._rmessage = None
        
        self._temp_files = []
                
    def epicfail(self):
        """return true if test failed or crashed"""
        
        return True if self._rflag in (TEST_RESULT_CRASHED, TEST_RESULT_FAILED,) else False
        
    def add_temp_file(self, pv_filename):
        """add temp filename to internal list"""
        
        self._temp_files.append(pv_filename)
        
    def remove_temp_files(self):
        """remove all generated temp files"""
        
        for filename in self._temp_files:
            if os.path.isfile(filename):
                lv_path, lv_ext = os.path.splitext(filename.lower())
                if lv_ext == '.py':
                    for pyext in ('.pyo', '.pyc', '.pyd'):
                        if os.path.isfile(lv_path+pyext):
                            os.remove(lv_path+pyext)

                os.remove(filename)                
                
    def get_rt_conn(self):
        """get rt_conn"""
        
        return self.__rt_conn
        
    def get_rt_mode(self):
        """get rt_mode"""
        
        return self.__rt_mode
        
    def get_rt_id(self):
        """get rt_id"""
        
        return self.__rt_id
        
    def get_rt_name(self):
        """get rt_name"""
        
        return self.__rt_name
        
    def get_ikwdata(self, kw_key, def_value=None):
        """get initial kwdata"""
        
        return self.__ikw.get(kw_key, def_value)
    
    def get_rkwdata(self, kw_key, def_value=None):
        """get runtime kwdata"""
        
        return self.__rkw.get(kw_key, def_value)
    
    def set_rkwdata(self, kw_key, kw_value):
        """set runtime kwdata"""
        
        self.__rkw[kw_key] = kw_value    
        
    def get_format(self):
        """ get format """
        
        return self._format
    
    def get_sdata(self):
        """ get source data """
        
        return self._sdata
    
    def get_rdata(self):
        """ get result data """
        
        return self._rdata
    
    def get_cdata(self):
        """ get control data """
        
    def get_rflag(self):
        """ get test result for final report """
        
        return self._rflag
    
    def get_rmessage(self):
        """get test message for final report """
        
        return self._rmessage
    
    def get_rmdata(self):
        """ get result data as tuple """
        
        return (self._rflag, self._rmessage,)
    
    def set_rmdata(self, rflag, rmessage):
        """ set result data"""
        
        self._rflag = rflag
        self._rmessage = rmessage
        
    def process(self, **kw):
        """ execute test
        MUST set rflag to -1/0/1
        """

        raise NotImplementedError
  
    def action_on_error(self, **kw):
        """ custom action that fired when test crash with internal error """
        
        raise NotImplementedError
    
    def action_on_fail(self, **kw):
        """ custom action that fired when test fail = -1 """
        
        raise NotImplementedError
    
    def action_on_success(self, **kw):
        """ custom action that fired when test success = 1 """
        
        raise NotImplementedError
    
    def load_data(self, **kw):
        """ load test-related data from some source """
        
        raise NotImplementedError
    
    def process_data(self, **kw):
        """ execute test"""

        try:
            lv_result = self.get_rflag()
            
            if lv_result not in (TEST_RESULT_CRASHED, TEST_RESULT_FAILED,):        
                self.process()
                
                lv_result = self.get_rflag()
                
                if lv_result == TEST_RESULT_PASSED:
                    self.action_on_success(**kw)
                elif lv_result == TEST_RESULT_FAILED:
                    self.action_on_error(**kw)
                else:
                    self.action_on_fail(**kw)
                    
            self.remove_temp_files()
        except Others:
            lv_errm = get_estr()
            self.set_rmdata(TEST_RESULT_CRASHED, lv_errm)
            
        return self.get_rmdata()
