#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" release tools: incrementor for app build number """

# pytkapp: release tools: incrementor for app build number
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

import sys
import codecs
import re
import os

gp_major = re.compile('(?P<prefix>__appmajor__\s*=\s*)(?P<value>\d+)')
gp_minor = re.compile('(?P<prefix>__appminor__\s*=\s*)(?P<value>\d+)')
gp_build = re.compile('(?P<prefix>__appbuild__\s*=\s*)(?P<value>\d+)')
gp_state = re.compile('(?P<prefix>__appstate__\s*=\s*)(?P<value>\d+)')

def incbuilder(pv_path, pv_key=None):
    """ get and increment build tag 
        key: major, minor, None/build, state    
    """
    
    print('incbuilder started...')
    
    print('in >>>')
    print('path: %s' % pv_path)    
    print('key: %s' % pv_key)
    
    if pv_key and pv_key not in ('major', 'minor', 'build', 'state'):
        print('Invalid key !')
        sys.exit(1)
    
    if not pv_key:
        pv_key = 'build'    
    
    lv_path = os.path.abspath(pv_path)

    print('abs path: %s' % lv_path)

    lv_dmajor = None
    lv_dminor = None
    lv_dbuild = None
    lv_dstate = None
    
    if pv_key == 'major':
        lt_repats = (gp_major, gp_minor, gp_build, gp_state,)
        lv_dmajor = 1
        lv_dminor = 0
        lv_dbuild = 0
        lv_dstate = 0        
    elif pv_key == 'minor':
        lt_repats = (gp_minor, gp_build, gp_state,)
        lv_dminor = 1
        lv_dbuild = 0
        lv_dstate = 0        
    elif pv_key == 'build':
        lt_repats = (gp_build, gp_state,)
        lv_dbuild = 1
        lv_dstate = 0        
    else:
        lt_repats = (gp_state,)
        lv_dstate = 1
            
    ll_content = []
    with codecs.open(lv_path, 'rb', 'utf-8') as f_in:
        for source_line in f_in:
            lv_str = source_line
            
            for repat in lt_repats:
                lr_search = repat.search(lv_str)
                if lr_search is not None:
                    ld_data = lr_search.groupdict()
                    
                    lv_prefix = ld_data['prefix']
                    lv_value  = int(ld_data['value'])
                    
                    if repat == gp_major:
                        lv_value = lv_value+lv_dminor if lv_dmajor != 0 else lv_dmajor
                    elif repat == gp_minor:
                        lv_value = lv_value+lv_dminor if lv_dminor != 0 else lv_dminor
                    elif repat == gp_build:
                        lv_value = lv_value+lv_dbuild if lv_dbuild != 0 else lv_dbuild
                    else:
                        if lv_value < 3 or lv_dstate == 0:
                            lv_value = lv_value+lv_dstate if lv_dstate != 0 else lv_dstate
                    
                    lv_str = '%s%s\n' % (lv_prefix, lv_value)    
                    
                    print('%s was changed to %s !' % (lv_prefix.strip(), lv_value))
                
            ll_content.append(lv_str)
        
    with codecs.open(lv_path, 'w+', 'utf-8') as f_out:
        f_out.writelines(ll_content)
        
    print('incbuilder finished...')

if __name__ == '__main__':
    lv_userpath = raw_input('process filename:')
    incbuilder(lv_userpath)
