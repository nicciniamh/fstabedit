#!/usr/bin/env python3
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
import os, sys, gi, re, gettext, locale, pathlib
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk
from gi.repository.GdkPixbuf import Pixbuf
#
# find out where we're running from and go there
#
os.chdir(os.path.dirname(os.path.realpath(sys.argv[0])))
#sys.path.append('lib')
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain('fstabedt', '/usr/share/locale')
gettext.textdomain('fstabedit')
_ = gettext.gettext
gettext.install('fstabedit', '/usr/share/locale')
from lib import fsentry, dialogs, fstab,  debug, browser
defaultFstab = '/etc/fstab'
#defaultFstab = '../etc/fstab'

helpHome = pathlib.Path(os.path.abspath('htmldocs/index.html')).as_uri()
helpToc = helpHome
helpAbout = pathlib.Path(os.path.abspath('htmldocs/about.html')).as_uri()

class App:
    def __init__(self):
        self.listcols = []
        self.app = Gtk.Application.new('com.ducksfeet.fstabedit',0)
        self.title = _("Filesystem Table Editor")
        self.app.connect('startup', self.on_startup)
        self.app.connect('activate', self.on_activate)
        self.app.connect('shutdown', self.on_shutdown)

    def on_startup(self,app):
        self.modified = False
        self.filename = defaultFstab
        self.fstab = fstab.fstab(self.filename)
        builder = Gtk.Builder.new_from_file('fsedit.glade')

        self.builder = builder
        self.window = builder.get_object('AppWindow')
        self.setTitle()
        self.window.set_default_size(640,480)
        self.app.add_window(self.window)
        self.box = builder.get_object('Content')
        self.model = Gtk.ListStore(str,str,str,int)
        self.tree = Gtk.TreeView(model=self.model)
        self.box.add(self.tree)
        self.listcols = [_("Device"),_("Mount Point"),_("Type")]
        self.updateModel()
        for i in range(len(self.listcols)):
            cell = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(self.listcols[i],cell,text=i)
            self.tree.append_column(col)
        self.tree.connect('row-activated',self.cb_itemActivated, self.model)
        self.window.connect('delete-event', self.on_windowDelete)
        builder.connect_signals(self)
        self.window.show_all()
        if defaultFstab.startswith('/etc'):
            if os.geteuid() != 0:
                def response(response):
                    if response != Gtk.ResponseType.YES:
                        self.app.quit()
                dialogs.question(_("You are not root. Changes may not be saved.\nContinue?"),response)

    def error(self,message,*args):
        if len(args):
            message = message + ' '.join(args)
        debug.debug(message)
        dialogs.error(message,parent=self.window)

    def setModified(self,flag=True):
        self.modified = flag
        self.setTitle()

    def setTitle(self):
        savent = self.builder.get_object('FileSave')
        savasent = self.builder.get_object('FileSaveAs')
        if self.filename:
            fname = self.filename
        else:
            fname = '(none)'

        if self.modified:
            if self.filename:
                savent.set_sensitive(True)
            mflag = '*'
        else:
            savent.set_sensitive(False)
            mflag = ''
        if len(self.fstab.entries):
            savasent.set_sensitive(True)
        else:
            savasent.set_sensitive(False)
        self.window.set_title('{}{}'.format(mflag,fname))
    def updateModel(self):
        self.model.clear()
        for i in range(len(self.fstab.entries)):
            fs,mp,typ = self.fstab.entries[i].dev,self.fstab.entries[i].mountpoint,self.fstab.entries[i].fstype
            if self.fstab.entries[i].devtype.upper() in ['LABEL','UUID','PARTUUID','PARTLABEL']:
                if 'LABEL' in self.fstab.entries[i].devtype.upper():
                    fs = '{}="{}"'.format(self.fstab.entries[i].devtype.upper(),fs)
                else:
                    fs = '{}={}'.format(self.fstab.entries[i].devtype.upper(),fs)
            self.model.append((fs,mp,typ,i))

    def run(self, argv):
        self.app.run(argv)

    def cb_itemActivated(self,widget,tree_path, col, store):
        i = store.get_iter(tree_path)
        item  = store.get(i, 1)[0]
        idx = int(store.get(i,3)[0])
        if item:
            self.editfsEntry(idx)

    def cb_FileNew(self,*args):
        def newfstab():
            self.filename = None
            self.fstab = fstab.fstab()
            self.updateModel()
            self.setTitle()
        def response_cb(response):
            if response == Gtk.ResponseType.YES:
                newfstab()
        if self.modified:
            dialogs.question(_("Changes to {} have not been saved?\nContinue?").format(self.filename),response_cb)
        else:
            newfstab()            
    def cb_FileOpen(self,*args):
        def getAndOpenFile():
            dialog = Gtk.FileChooserDialog(_("Please choose a file"), self.window,
                Gtk.FileChooserAction.OPEN,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                 Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                filename = dialog.get_filename()
                try:
                    self.fstab = fstab.fstab(filename)
                    self.filename = filename
                except Exception as e:
                    self.error(_("Cannot open {}: {}").format(filenme,e))
                    return False

                self.setModified(False)
                self.updateModel()
                self.setTitle()
            elif response == Gtk.ResponseType.CANCEL:
                debug.debug("Cancel clicked")
            dialog.destroy()

        def response_cb(response):
            if response == Gtk.ResponseType.YES:
                getAndOpenFile()
        if self.modified:
            dialogs.question(_("Changes to {} have not been saved?\nContinue?").format(self.filename),response_cb)
        else:
            getAndOpenFile()            

    def cb_FileNewFileSystem(self,*args):
        self.editfsEntry(-1)
    
    def cb_FileSave(self, *args):
        try:
            self.fstab.write()
            self.setModified(False)
        except Exception as e:
            self.error(_("Cannot save {}: {}").format(self.filename,e))

    def cb_FileSaveAs(self,*args):
        dialog = Gtk.FileChooserDialog(_("Save Filesystem Table as..."), self.window,
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_SAVE, Gtk.ResponseType.OK), parent=self.window)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            try:
                self.fstab.write(filename)
                self.filename = filename
                self.setModified(False)
            except Exception as e:
                self.error(_("Cannot save {}: {}").format(filename,e))

        elif response == Gtk.ResponseType.CANCEL:
            debug.debug("Cancel clicked")

        dialog.destroy()

    def cb_FileQuit(self, *args):
        if not self.checkShutdown():
            self.app.quit()

    def cb_helpContents(self,*args):
        b = browser.browserDoc(wintitle='Help',input=helpToc, home_uri=helpHome)

    def cb_HelpAbout(self,*args):
        b = browser.browserDoc(wintitle='Help',input=helpAbout, home_uri=helpHome)

    def on_activate(self,app):
        pass
    def on_shutdown(self,*args):
        pass
    def on_windowDelete(self,*args):
        r = self.checkShutdown()
        debug.debug('on_windowDelete',r)
        return  r

    def checkShutdown(self):
        rval = [False]
        def response_cb(response):
            if response == Gtk.ResponseType.YES:
                rval[0] = False
            else:
                rval[0] = True
        if self.modified:
            dialogs.question(_("Changes to {} have not been saved?\nDo you wish to quit?").format(self.filename),response_cb,parent=self.window)
        rval = rval[0]
        return rval

    def editfsEntry(self,index):
        def callbackfn(data):
            if data and data.modified:
                e = self.fstab.searchEntryLineNo(data.line)
                if e:
                    debug.debug('Updating entry:\n{}\n'.format(data.__dict__))
                    for k,v in list(e.__dict__.items()):
                        e.__dict__[k] = data.__dict__[k]
                else:
                    self.fstab.entries.append(data)
                self.setModified(True)
                self.updateModel()
                self.setTitle()
        if index != -1:
            x = fsentry.entry(self.window,self.fstab.entries[index], callbackfn)
        else:
            x = fsentry.entry(self.window,None,callbackfn)

if __name__ == "__main__":
    app = App()
    df = False
    if '-d' in sys.argv or '--debug' in sys.argv:
        df = True
    debug.setdebug(df)
    app.run([sys.argv[0]])
