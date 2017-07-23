#!/usr/bin/env python3
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
import sys
if float(sys.version[:3]) < 3:
    from builtins import object
    from future import standard_library
    standard_library.install_aliases()
import os, webbrowser, re, gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit', '3.0')
from gi.repository import Gtk, WebKit

uiXml = '''
<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated with glade 3.18.3 -->
<interface>
  <requires lib="gtk+" version="3.12"/>
  <object class="GtkWindow" id="browserWindow">
    <property name="can_focus">False</property>
    <child>
      <object class="GtkBox" id="box1">
        <property name="visible">True</property>
        <property name="can_focus">False</property>
        <property name="orientation">vertical</property>
        <child>
          <object class="GtkButtonBox" id="buttonbox1">
            <property name="visible">True</property>
            <property name="can_focus">False</property>
            <property name="layout_style">start</property>
            <child>
              <object class="GtkButton" id="home">
                <property name="label">gtk-home</property>
                <property name="visible">True</property>
                <property name="can_focus">True</property>
                <property name="receives_default">True</property>
                <property name="use_stock">True</property>
              </object>
              <packing>
                <property name="expand">True</property>
                <property name="fill">True</property>
                <property name="position">0</property>
              </packing>
            </child>
            <child>
              <object class="GtkButton" id="back">
                <property name="label">gtk-go-back</property>
                <property name="visible">True</property>
                <property name="can_focus">True</property>
                <property name="receives_default">True</property>
                <property name="use_stock">True</property>
              </object>
              <packing>
                <property name="expand">True</property>
                <property name="fill">True</property>
                <property name="position">1</property>
              </packing>
            </child>
            <child>
              <object class="GtkButton" id="forward">
                <property name="label">gtk-go-forward</property>
                <property name="visible">True</property>
                <property name="can_focus">True</property>
                <property name="receives_default">True</property>
                <property name="use_stock">True</property>
              </object>
              <packing>
                <property name="expand">True</property>
                <property name="fill">True</property>
                <property name="position">2</property>
              </packing>
            </child>
          </object>
          <packing>
            <property name="expand">False</property>
            <property name="fill">True</property>
            <property name="position">0</property>
          </packing>
        </child>
        <child>
          <object class="GtkScrolledWindow" id="scrolledbrowserWindow">
            <property name="width_request">640</property>
            <property name="height_request">480</property>
            <property name="visible">True</property>
            <property name="can_focus">True</property>
            <property name="hexpand">True</property>
            <property name="vexpand">True</property>
            <property name="shadow_type">in</property>
            <child>
              <placeholder/>
            </child>
          </object>
          <packing>
            <property name="expand">False</property>
            <property name="fill">True</property>
            <property name="position">1</property>
          </packing>
        </child>
        <child>
          <object class="GtkButtonBox" id="buttonbox2">
            <property name="visible">True</property>
            <property name="can_focus">False</property>
            <property name="layout_style">end</property>
            <child>
              <object class="GtkButton" id="close">
                <property name="label">gtk-close</property>
                <property name="visible">True</property>
                <property name="can_focus">True</property>
                <property name="receives_default">True</property>
                <property name="use_stock">True</property>
              </object>
              <packing>
                <property name="expand">True</property>
                <property name="fill">True</property>
                <property name="position">0</property>
              </packing>
            </child>
          </object>
          <packing>
            <property name="expand">False</property>
            <property name="fill">True</property>
            <property name="position">2</property>
          </packing>
        </child>
      </object>
    </child>
  </object>
</interface>
'''
standalone = False
class browserDoc(object):
    def __init__(self,**kwargs):
        self.window = None
        allowed_args = ['input','doctext','winicon','show_navbuttons','home_uri',"base_uri", "wintitle","parent"]
        self.input = None
        self.doctext = None
        self.show_navbuttons = False
        self.home_uri = None
        self.base_uri = None
        self.wintitle = None
        self.winicon = None
        self.parent = None
        for k,v in kwargs.items():
            if k in allowed_args:
                setattr(self,k,v)
        if self.input:
            if not 'show_navbuttons' in kwargs:
                self.show_navbuttons = True
            self.viewFile()
        elif self.doctext:
            self.viewString()
        else:
            raise ValueError('No document specified.')
        if self.parent:
            self.window.set_transient_for(self.parent)
        self.window.show_all()
        if self.winicon:
            self.window.set_icon_name(Gtk.STOCK_HARDDISK)
        self.setButtons()

    def setupWindow(self):
        if self.window:
            return
        builder = Gtk.Builder()
        builder.add_from_string(uiXml)
        self.window = builder.get_object('browserWindow')
        self.home_button = builder.get_object('home')
        self.back_button = builder.get_object('back')
        self.fwd_button = builder.get_object('forward')
        self.navbuttons = builder.get_object('buttonbox1')
        for button in [self.home_button,self.back_button,self.fwd_button]:
            button.connect('clicked',self.navButtonClicked)
        self.close_button = builder.get_object('close')
        self.window.connect('delete-event',self.quit)
        self.close_button.connect('clicked',self.quit)

        self.view = WebKit.WebView()
        self.view.connect('navigation-policy-decision-requested',self.navPolicyReq)
        self.view.connect('title-changed',self.newTitle)
        self.view.connect('load-finished',self.newTitle)
        self.scroller = builder.get_object('scrolledbrowserWindow')
        self.scroller.add(self.view)
        self.home_button.set_label('Contents')

    def newTitle(self,*args):
        self.setButtons()
        doctitle = self.view.get_title()
        if self.wintitle:
            if doctitle:
                doctitle = '{} - {}'.format(self.wintitle,doctitle)
            else:
                doctitle = self.wintitle
        if doctitle:
            self.window.set_title(doctitle)

    def normalizeLocalFile(self,filename):
        if re.match(r'(http.?://)',filename):
            return filename
        filename = re.sub(r'^file\:\/\/','',filename)
        if not self.base_uri or self.base_uri == '':
            return filename
        if filename.startswith('/'):
            return filename
        base = re.sub(r'^file\:\/\/','',filename)
        return os.path.join(base,filename)

    def viewFile(self):
        self.setupWindow()
        self.view.load_uri(self.input)

    def viewString(self):
        self.setupWindow()
        if self.base_uri:
            buri = self.base_uri
        else:
            buri = ''
        self.view.load_string(self.doctext,
            'text/html',
            'utf-8',
            buri)

    def navButtonClicked(self,widget,*args):
        if widget == self.home_button:
            self.view.load_uri(self.home_uri)
        elif widget == self.back_button:
            self.view.go_back()
        elif widget == self.fwd_button:
            self.view.go_forward()

    def setButtons(self):
        if not self.show_navbuttons:
            self.navbuttons.hide()
        backEnable = self.view.can_go_back()
        fwdEnable = self.view.can_go_forward()
        if self.home_uri:
            homeEnable = True
        else:
            homeEnable = False

        for w,s in [(self.back_button,backEnable),(self.fwd_button,fwdEnable),(self.home_button,homeEnable)]:
            w.set_sensitive(s)            
            if s:
                w.set_opacity(1)
            else:
                w.set_opacity(.75)

    def navPolicyReq(self,widget,frame,req,action,decision):
        uri =  req.get_uri()
        if re.match(r'(http.?://)',uri):
            WebKit.WebPolicyDecision.ignore(decision)
            webbrowser.open(uri)
        self.setButtons()
        return False

    def quit(self,*args):
        if standalone:
            Gtk.main_quit()
        else:
            self.window.destroy()


if __name__ == "__main__":
    path=os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
    os.chdir(path)
    standalone = True
    docs = None
    if len(sys.argv) > 1:
        docs = sys.argv[1]
        if not docs.startswith('http'):
            docs = os.path.abspath(docs)
            docs = 'file://'+docs
            title = 'Help Browser'
    elif 'viewdocs' in sys.argv[0]:
        docs = 'file://'+os.path.abspath('htmldocs/index.html')
        title = 'Help Viewer'

    if docs:
        Gtk.init()
        b = browserDoc(winicon=True,wintitle=title, input=docs, home_uri=docs)
        Gtk.main()