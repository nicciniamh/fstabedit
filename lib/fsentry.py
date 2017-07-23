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
import os, sys, re, glob, gettext, locale, platform, collections, copy
if float(sys.version[:3]) < 3:
    from builtins import open
    from builtins import range
    from builtins import object
    from future import standard_library
    standard_library.install_aliases()
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk
import extrawidgets, fstab, dialogs, diskdevs, debug, browser

locale.setlocale(locale.LC_ALL, '')
_ = gettext.gettext
devTypeMap = ["Device", "UUID", "PARTUUID", "LABEL", "PARTLABEL", "File","Path"]
devTypeKeyed = devTypeMap[:devTypeMap.index('File')] 

commonOpts = [  'auto','noauto','exec','noexec','ro','rw','user','users','nouser',
                'owner','sync','async','dev','nodev','suid','nosuid','noatime',
                'trim','acl','noacl','nodiratime','relatime','discard','flush','nofail',
                'defaults','errors=remount-ro']
commonOpts.sort()

#
# On startup get a run-down of all kernel fileystem types
#
fsTypeMap = ['swap','tmpfs','sshfs','exfat','refs'] # These would not have kernel modules.

for d in glob.glob('/lib/modules/'+platform.release()+'/kernel/fs/*'):
    if os.path.isdir(d):
        if len(glob.glob('{}/*.ko'.format(d))):
            d = os.path.basename(d).split('.')[0]
            fsTypeMap.append(os.path.basename(d))

with open('/proc/filesystems') as file:
    for line in file:
        if not line.startswith('nodev'):
            fs = line.strip()
            if not fs in fsTypeMap:
                fsTypeMap.append(fs)

fsTypeMap.sort()
#print('{} filesystem types detected'.format(len(fsTypeMap)))


PARTFUNC_LIST,PARTFUNC_QUERY, PARTFUNC_WIDGET = list(range(0,3))
class entry(object):
    ''' 
    Class for a UI to manage an entry in an fstab file. Widgets are dynamically changed 
    to use specific elements present on system. 
    '''
    def __init__(self, parent, fsent, callback):
        self.cbComboCount = 0
        self.devfile = None
        self.devices = diskdevs.devices()
        self.partFuncs = {"Device":     [self.devices.allDevices, self.devices.byDevice, None],
                          "UUID":       [self.devices.allUUIDs, self.devices.byUUID, None],
                          "PARTUUID":   [self.devices.allPartUUIDs, self.devices.byPartUUID, None],
                          "LABEL":      [self.devices.allLabels,self.devices.byLabel, None],
                          "PARTLABEL":  [self.devices.allPartLabels,self.devices.byPartLabel, None]
                          }
        self.widgets = {    "node":         ("entry", self.cb_entryChanged),
                            "mountpoint":   ("dir",self.cb_fileChooserChanged),
                            "otherfstype":  ("entry",self.cb_entryChanged),
                            "fsopts":       ("entry",self.cb_entryChanged),
                            "fsfreq":       ("sb",self.cb_spinButtonChanged),
                            "fspass":       ("sb",self.cb_spinButtonChanged),
                            "commonopts":   ('cb',self.cb_comboChanged),
                            "cancelBtn":    ("button",self.cb_button),
                            "okBtn":        ("button",self.cb_button)
                        }

        if not fsent:
            debug.debug('Creting new fsentry')
            self.fsent = fstab.fsentry()
        else:
            self.fsent = fsent
        debug.debug('fsentry is',self.fsent)
        self.dev = self.fsent.dev
        for k in ['dev','devtype','mountpoint','fstype','fsopts','fsfreq','fspass']:
            setattr(self,k,self.fsent.__dict__[k])
        try:
            if self.devtype in devTypeKeyed and self.devtype != 'Device':
                self.devtype = self.fsent.devtype.upper()
            else:
                self.devtype = self.devtype.title()
        except ValueError:
            self.devtype = None

        if self.devtype == 'File' or self.devtype == 'Path':
            self.devfile = self.dev

        if self.devtype in list(self.partFuncs.keys()):
            self.partition = self.partFuncs[self.devtype][PARTFUNC_QUERY](self.dev)
        else:
            self.partition = None

        self.callback = callback
        self.builder = Gtk.Builder()
        self.builder.add_from_file('lib/fsentry.glade')
        self.grid = self.builder.get_object('grid1')
        self.fstypecont = self.builder.get_object('fstypecont')
        self.devtypecont = self.builder.get_object('devtypecont')

        for wname,wdata in list(self.widgets.items()):
            wtype,wcb = wdata
            wprop = '{}_{}'.format(wtype,wname)
            widget = self.builder.get_object(wname)
            widget.set_name(wprop)
            if not widget:
                raise ValueError('Cannot get widget for {}'.format(x))
            setattr(self,wprop,widget)

        self.nodeelement = self.builder.get_object('nodeelement')
        self.cb_devtype = extrawidgets.comboBoxText(name='cb_devtype',items=devTypeMap)
        self.devtypecont.add(self.cb_devtype)
        self.cb_devtype.show()
        self.widgets['devtype'] = ('cb',self.cb_comboChanged)

        for wname in list(self.partFuncs.keys()):
            wprop = 'cb_{}'.format(wname)
            items = self.partFuncs[wname][PARTFUNC_LIST]()
            if items:
                items.sort()
            else:
                items = []
            widget = extrawidgets.comboBoxText(name=wprop, items=items)
            self.partFuncs[wname][PARTFUNC_WIDGET] = widget
            setattr(self,wprop,widget)
            self.widgets[wname] = ('cb', self.cb_comboChanged)

        self.file_devchoose = Gtk.FileChooserButton(_("Choose filesytem file"),Gtk.FileChooserAction.OPEN)
        self.widgets["devchoose"] = ('file',self.cb_fileChooserChanged)
  
        self.window = self.builder.get_object('fsentry')
        self.window.set_transient_for(parent)
        self.window.show_all()

        self.cb_fstype = extrawidgets.comboBoxText(name='cb_fstype',items=fsTypeMap)
        self.widgets["fstype"] = ('cb',self.cb_comboChanged)

        self.cb_fstype.append('Other...')
        self.fstypecont.add(self.cb_fstype)
        self.cb_fstype.show()
        self.setFsField()

        self.cb_devtype.set_active_text(self.devtype)

        self.mpextra = Gtk.CheckButton.new_with_label(_("No mount pount."))
        self.dir_mountpoint.set_extra_widget(self.mpextra)


        for i in range(len(commonOpts)):
            self.cb_commonopts.append(None,commonOpts[i])

        self.cb_fstype.set_active_text(self.fstype)
        if self.fstype == None or not self.fstype in fsTypeMap:
            self.entry_otherfstype.set_text(self.fsent.fstype)
            self.entry_otherfstype.show()
        else:
            self.entry_otherfstype.hide()

        self.entry_node.set_text(self.dev)
        self.sb_fsfreq.set_value(self.fsent.fsfreq)
        self.sb_fspass.set_value(self.fsent.fspass)
        self.entry_fsopts.set_text(self.fsent.fsopts)
        if self.fsent.mountpoint != '':
            self.dir_mountpoint.set_filename(self.fsent.mountpoint)

        if self.dev != '':
            self.title = '{}'.format(self.dev)
        else:
            self.title = _("(New Entry)")

        self.overview_button = self.builder.get_object('overview')
        self.overview_button.connect('clicked',self.formatOverview)
        self.setNodeField(self.devtype)
        self.fsent.modified = False
        self.setTitle()

        ## Now we connect all these widgets and signals.
      
        for wname,wdata in list(self.widgets.items()):
            signals = []
            wtype,wcb = wdata
            widget = self.__dict__['{}_{}'.format(wtype,wname)]
            if wtype == 'sb':
                signals = ['value_changed','change-value']
            elif wtype == 'dir' or wtype == 'file':
                signals = ['file-set']
            elif wtype == 'button':
                signals = ['clicked']
            else:
                signals = ['changed']
            for s in signals:
                #debug.debug('Connecting signal for {}:{}  - {}'.format(wname,s,wcb))
                widget.connect(s,wcb,wname)

    def setTitle(self):
        self.button_okBtn.set_sensitive(self.fsent.modified)
        if self.fsent.modified:
            self.button_okBtn.set_opacity(1)
            mflag = '*'
        else:
            self.button_okBtn.set_opacity(.75)
            mflag = ''
        self.window.set_title('{}{}'.format(mflag,self.title))
 
    def setModified(self):
        self.fsent.setModified()
        self.setTitle()

    def setFsField(self):
        if self.fstype in fsTypeMap:
            self.cb_fstype.set_active_text(self.fstype)
            self.entry_otherfstype.hide()
        else:
            self.cb_fstype.set_active_text('Other...')
            self.entry_otherfstype.show()


    def setNodeField(self,newtype=None):
        oldwidget = None
        try:
            oldwidget = self.nodeelement.get_children()[0]
        except:
            pass
        nwidget = None
        if not newtype:
            newtype = self.devtype
        debug.debug('old type: {}, newtype {}, old widget: {}'.format(self.devtype,newtype, oldwidget.get_name()))
        if newtype in list(self.partFuncs.keys()):
            nwidget = self.partFuncs[newtype][PARTFUNC_WIDGET]
            newtypel = newtype.lower()
            if self.partition and newtypel in self.partition:
                newdev = self.partition[newtypel]
            else:
                newdev = ''
            nwidget.set_active_text(newdev)
            self.dev = newdev
            self.entry_node.set_text(newdev)
        elif newtype == 'File':
            if self.devfile:
                self.file_devchoose.set_filename(self.devfile)
            nwidget = self.file_devchoose
            self.dev = ''
            self.entry_node.set_text('')
        elif newtype == 'Path':
            nwidget = self.entry_node
            self.entry_node.set_text(self.dev)
        if nwidget:
            if debug.getdebug():
                if oldwidget:
                    oldname = oldwidget.get_name()
                else:
                    oldname = 'None'
                newname = nwidget.get_name()
                debug.debug('setting nodeelement -- oldwidget {}, new {}'.format(oldname,newname))
            if oldwidget:
                self.nodeelement.remove(oldwidget)
            self.nodeelement.add(nwidget)
            nwidget.show()
            self.devtype = newtype
            self.setFsField()

    def cb_comboChanged(self,widget,what,*args):
        self.cbComboCount += 1
        self.cb_comboChangedBody(widget,what)
        self.cbComboCount -= 1
        if self.cbComboCount < 0:
            self.cbComboCount = 0

    def cb_comboChangedBody(self,widget,what):
        debug.debug('cb_comboChanged({},{})'.format(widget.get_name(),what))
        if what == 'devtype':
            newtype = self.cb_devtype.get_active_text()
            debug.debug('cb_comboChanged: newtype is {}, oldwas {}'.format(newtype,self.devtype))
            if newtype == self.devtype:
                self.inComboCB = False
                return
            self.setNodeField(newtype)
            self.setModified()
            return
        if what in list(self.partFuncs.keys()):
            newdev = widget.get_active_text()
            debug.debug('cb_comboChanged: newdev is {}, oldwas {}'.format(newdev,self.dev))
            if newdev == self.dev:
                return
            newpart = self.partFuncs[what][PARTFUNC_QUERY](newdev)
            if newpart:
                self.partition = newpart
                self.dev = self.partition[self.devtype.lower()]
                if 'type' in self.partition:
                    self.fstype = self.partition['type']
                else:
                    self.fstype = ''
            else:
                self.partition = None
                self.dev = ''
            self.setNodeField()
            self.setFsField()
            self.setModified()
            return
        if what == 'fstype':
            newtype = self.cb_fstype.get_active_text()
            if self.cbComboCount == 1:
                if self.partition and 'type' in self.partition and self.partition['type'] != newtype:
                    dialogs.message(_("Changing the filesystem type from what is detected\nmay cause problems mounting the partition."),parent=self.window)
            if newtype == 'Other...':
                if self.partition:
                    if 'type' in self.partition:
                        debug.debug('Setting otherfstype to {}'.format(self.partition['type']))
                        self.entry_otherfstype.set_text(self.partition['type'])
                    else:
                        debug.debug('Cannot determine filesystem type from partition data {}'.format(self.partition))
                else:
                    debug.debug('No current partition data. This is not an error but cannot populate otherfstype field')
                self.entry_otherfstype.show()
            else:
                self.entry_otherfstype.hide()
            return
        if what == 'commonopts':
            co = widget.get_active_text()
            opts = self.entry_fsopts.get_text()
            if not co in opts:
                if opts == '':
                    opts = co
                else:
                    opts = '{},{}'.format(opts,co)
                self.entry_fsopts.set_text(opts)
                self.setModified()
            return

    def cb_fileChooserChanged(self,widget,what,*args):
        self.setModified()

    def cb_entryChanged(self,widget,what,*args):
        self.setModified()

    def cb_spinButtonChanged(self,widget,what,*args):
        self.setModified()


    def cb_button(self,widget,*args):
        devtype = ''
        node = ''
        callval = None
        debug.debug('cb_button, widget',widget.get_name(),'status',self.fsent.check())
        if widget == self.button_okBtn:
            self.fsent.dev = self.dev
            self.fsent.devtype = self.devtype
            self.fsent.mountpoint = self.dir_mountpoint.get_filename()
            fstype = self.cb_fstype.get_active_text()
            if fstype == 'Other...':
                fstype = self.entry_otherfstype.get_text()
                debug.debug('Other fstype is {}'.format(fstype))
            self.fsent.fstype = fstype
            self.fsent.fsfreq = self.sb_fsfreq.get_value_as_int()
            self.fsent.fspass = self.sb_fspass.get_value_as_int()
            self.fsent.fsopts = self.entry_fsopts.get_text()
            if self.fsent.fsopts == '':
                dialogs.message(_("No filesystem options selected, using 'defaults'"),parent=self.window)
                self.fsent.fsopts = 'defaults'
            status, errors = self.fsent.check()
            if not status:
                dialogs.error(_("Error(s): These field(s) need values:\n{}").format(', '.join(errors)))
                return False
            callval = self.fsent
        else:
            callval = False
        if isinstance(self.callback, collections.Callable):
            self.callback(callval)
        self.window.close()

    def formatOverview(self,*args):
        deviceOverview(self.window,self.devices)

def deviceOverview(window,devices=None):
    if not devices:
        devices = diskdevs.devices()
    fkeys = ['device','type','label','uuid', 'partlabel','partuuid']
    line = '<tr>'
    for f in fkeys:
        line = '{}<th>{}</th>'.format(line,f)
    line = line + '</tr>'
    lines = [line]
    devlist = list(devices.partitions.keys())
    devlist.sort()
    for dev in devlist:
        line = '<tr>'
        for f in fkeys:
            if f in devices.partitions[dev]:
                fdata = devices.partitions[dev][f]
            else:
                fdata = ''
            line = '{}<td>{}</td>'.format(line,fdata)
        line = line + '</td>'
        lines.append(line)
    htmldoc = '''
    <html>
    <body>
    <table border="0">
    {}
    </table>
    </body>
    </html>'''.format('\n'.join(lines))
    window.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.WATCH))
    b = browser.browserDoc(wintitle="Device Overview",doctext=htmldoc, parent=window)
    window.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.WATCH))
