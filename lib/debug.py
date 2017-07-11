#
# Filesystem Table Editor 
# Copyright 2017 Nicole Stevens
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os, inspect
debugFlag = False
def setdebug(flag):
    global debugFlag
    if(flag):
        debugFlag = True
    else:
        debugFlag = False
def getdebug():
    return debugFlag
def debug(*args):
    global debugFlag
    if debugFlag:
        caller = inspect.getframeinfo(inspect.stack()[1][0])
        fname = str(caller.filename).replace(os.getcwd()+'/','')
        x = ['{}:{} -'.format(fname, caller.lineno)]
        for a in args:
            x.append('{}'.format(a))
        print(' '.join(x))
