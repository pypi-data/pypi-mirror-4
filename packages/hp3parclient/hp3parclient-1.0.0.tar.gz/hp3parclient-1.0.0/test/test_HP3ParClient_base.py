# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright 2009-2012 10gen, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Test base class of 3Par Client"""

import sys, os
sys.path.insert(0,os.path.realpath(os.path.abspath('../')))

from hp3parclient import client, exceptions
import unittest
import subprocess
import time
import pprint

class HP3ParClientBaseTestCase(unittest.TestCase):

    def setUp(self):
         #if have debug as second argument for the test
         #for example, pythong test_HP3ParClient_CPG.py debug
         #need to manaully start test_HP3ParMockServer_flask.py before run 
         #test
         if len(sys.argv) >= 2:
             self.debug = sys.argv[1]

         self.cl = client.HP3ParClient("http://localhost:5000/api/v1")
         if self.debug == 'debug':
             self.cl.debug_rest(True)
         else: 
             self.mockServer = subprocess.Popen([sys.executable, 
                                                './test_HP3ParMockServer_flask.py'], 
                                                stdout=subprocess.PIPE, 
                                                stderr=subprocess.PIPE, 
                                                stdin=subprocess.PIPE)
             time.sleep(1) 
         
         self.cl.login("user", "hp")

    def tearDown(self):
        self.cl.logout()
        if self.debug != 'debug':
            #TODO: it seems to kill all the process except the last one...
            #don't know why 
            self.mockServer.kill()

    def printHeader(self, name):
        print "\n##Start testing '%s'" % name

    def printFooter(self, name):
        print "##Compeleted testing '%s\n" % name

