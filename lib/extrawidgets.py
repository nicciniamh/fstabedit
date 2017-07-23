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
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import os, sys
if float(sys.version[:3]) < 3:
    from builtins import range
    from builtins import str
    from future import standard_library
    standard_library.install_aliases()
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject
# This ugly hack allows the debug module to not exist without breaking code 
dbg = None
def debug(*args):
    if dbg:
        dbg(args)
try:
    from lib import debug as DBG
    dbg = DBG.debug
except:
    pass

class comboBoxText(Gtk.ComboBoxText):
    ''' Gtk.ComboBoxText subclassed to provide set_active_text as a wrapper to set_active 
    includes a few other methods to aid debugging. 
    '''

    def __init__(self,*args,**kwargs):
        if dbg:
            self.name = '{}::comboBoxText:_no_name_:'.format(__name__)
        else:
            self.name = ''
        self.items = []
        if 'name' in kwargs:
            self.name = kwargs['name']
        if 'items' in kwargs:
            self.items = kwargs['items']
            kwargs.__delitem__('items')

        debug('{}.__init__({},{})'.format(self.name,args,kwargs))
        Gtk.ComboBoxText.__init__(self,*args,**kwargs)
        if len(self.items):
            for i in range(len(self.items)):
                itemid=str(i)
                Gtk.ComboBoxText.append(self,itemid,self.items[i])


    def append(self,*args):
        if len(args) == 1:
            item = args[0]
            itemid = None
        elif len(args) == 2:
            itemid,item = args
        else:
            raise TypeError('too many positional arguments')
        self.items.append(item)
        if itemid == None:
            itemid = str(self.items.index(item))

        Gtk.ComboBoxText.append(self,itemid,item)

    def __contains__(self,s):
        return self.items.__contains__(s)

    def set_name(self,name):
        self.name = name
        Gtk.ComboBoxText.set_name(self,name)

    def set_active_text(self,text):
        if text in self.items:
            index = self.items.index(text)
            debug('{}.set_active(text=="{}", {})'.format(self.name,text,index))
            Gtk.ComboBoxText.set_active(self,index)
        else:
            debug('No {} in {}'.format(text,self.items))
            debug('{}.set_active(text=="{}", {})'.format(self.name,text,-1))
            Gtk.ComboBoxText.set_active(self,-1)


