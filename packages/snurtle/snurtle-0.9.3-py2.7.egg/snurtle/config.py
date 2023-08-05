#!/usr/bin/env python
# Copyright (c) 2012 Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#
from xdg import BaseDirectory
import os
import ConfigParser
 
class Configuration(object):
    
    @staticmethod
    def Path():
        path = os.path.join(BaseDirectory.xdg_config_home, 'snurtle')
        if not os.path.isdir(path):
            os.mkdir(path)
        path = os.path.join(path, 'config.ini')
        
        return path
    
    @staticmethod
    def Load():
        path = Configuration.Path()
        config = ConfigParser.RawConfigParser()
        if not os.path.isfile(path):
            config.add_section('Global')
            Configuration.SetHost(config, '')
            Configuration.SetLogin(config, '')
            Configuration.SetSecure(config, 0)
        else:
            config.read(path)   
        return config
 
    @staticmethod
    def GetHost(config):
        if 'host' in config.options( 'Global' ):
            hostname = config.get('Global', 'host')
        else:
            hostname = ''
        return hostname
 
    @staticmethod
    def SetHost(config, value):
        config.set('Global', 'host', value)
        
    @staticmethod
    def GetLogin(config):
        return config.get('Global', 'login')
 
    @staticmethod
    def SetLogin(config, value):
        config.set('Global', 'login', value)
        
    @staticmethod
    def GetSecure(config):
        if 'secure' in config.items( 'Global' ):
            return config.get('Global', 'secure')
        else:
            return 0
 
    @staticmethod
    def SetSecure(config, value):
        config.set('Global', 'secure', value)        
 
    @staticmethod
    def Save(config):
        path  = Configuration.Path()
        wfile = open(path, 'wb')
        if wfile:
            config.write(wfile)
            wfile.close
