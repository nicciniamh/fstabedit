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

import os, sys, re, tempfile, shlex

class fsentry:
    def __init__(self,**kwargs):
        fields = ['dev','devtype','mountpoint','fstype','fsopts','fsfreq','fspass',"new","line"]
        self.new,self.modified = (False, False)
        self.dev = ''
        self.devtype = 'Device'
        self.mountpoint = ''
        self.fstype = ''
        self.fsopts = ''
        self.fsfreq = 0
        self.fspass = 0
        self.line = -1
        for k,v in list(kwargs.items()):
            if k in fields:
                setattr(self,k,v)
        if self.dev == '':
            self.setNew()
    def check(self):
        errors = []
        if self.dev == '':
            errors.append(_("Device"))
        if self.devtype == '':
            errors.append(_("Device Type"))
        if self.mountpoint == '':
            errors.append(_("Mount Point"))
        if self.fsopts == '':
            errors.append(_("Filesystem Options"))
        if len(errors):
            return False,errors
        return True,None

    def setModified(self):
        self.modified = True
    def setNew(self):
        self.modified = True

    def toStr(self):
        dev = self.devstring()
        return '{}\t{}\t{}\t{}\t{} {}'.format(dev,self.mountpoint,self.fstype,self.fsopts,self.fspass,self.fsfreq)
    
    def devstring(self):
        dev = self.dev
        devtype = self.devtype.upper()
        if devtype in ['UUID','LABEL','PARTUUID','PARTLABEL']:
            if 'LABEL' in devtype:
                dev = '{}="{}"'.format(devtype,dev)
            else:
                dev = '{}={}'.format(devtype,dev)
        return dev

    def matchline(self,line):
        if re.split("\s+",line)[0] == self.devstring():
            return True
        return False

class fstab:
    def __init__(self, fstabFilename=None):
        self.entries = []
        self.filename = fstabFilename
        if fstabFilename:
            self.read()

    def searchEntryDev(self,dev):
        for e in self.entries:
            if e.dev == dev:
                return e
        return False

    def searchEntryLine(self,line):
        for e in self.entries:
            if e.matchline(line):
                return e
        return False

    def searchEntryLineNo(self,lineno):
        for e in self.entries:
            if e.line == lineno:
                return e
        return False

    def read(self):
        lineno = 0
        f = open(self.filename)
        for line in f:
            lineno = lineno + 1
            line = line.split('#')[0].strip()
            if len(line):
                fields = shlex.split(line.strip()) #re.split("\s+",line)
                #print fields
                if len(fields) == 4:
                    freq,fpass = 0,0
                elif len(fields) == 5:
                    freq = fields[3]
                    fpass = 0
                elif len(fields) != 6:
                    freq,fpass = 0,0
                else:
                    freq,fpass = fields[4:]
                dev,mpoint,fstype,fsopt = fields[:4]
                if not '=' in dev:
                    if re.match('^/dev/', dev):
                        devtype = 'Device'
                    elif ':' in dev or "//" in dev:
                        devtype = "Path"
                    else:
                        devtype = 'File'
                    if devtype == 'File' and not os.path.exists(dev):
                        devtype = 'Path'
                else:
                    devtype = ''
                    for t in ["UUID", "PARTUUID", "LABEL", "PARTLABEL"]:
                        if re.match('^'+t,dev):
                            devtype = t
                    dev = dev.split('=')[1]

                self.entries.append(fsentry(dev=dev, 
                                devtype = devtype,
                                mountpoint = mpoint,
                                fstype = fstype,
                                fsopts = fsopt,
                                fsfreq = int(freq),
                                fspass = int(fpass),
                                line = lineno))


    def write(self, filename=None):
        if not filename:
            filename = self.filename
        tmp = tempfile.TemporaryFile(mode='w+')
        line = 0
        #print 'Making temp copy'
        with open(self.filename) as f:
            for l in f:
                line = line + 1
                c = l.strip()
                e = self.searchEntryLineNo(line)
                if e and e.modified:
                    #print e.toStr()
                    tmp.write(e.toStr()+'\n')
                else:
                    tmp.write(l)
        tmp.seek(0,0)
        if os.path.exists(filename):
            try:
                rento = filename+'~'
                #print 'renaming {} to {}'.format(filename,rento)
                if os.path.exists(rento):
                    os.remove(rento)
                os.rename(filename,rento)
                #print 'oldfile backed up as',rento
            except OSError as e:
                raise Exception(_("Cannot backup original file\n{}").format(e))
                return
        try:
            f = open(filename,'w')
            for t in tmp:
                f.write(t)
            f.close()
            tmp.close()
            self.filename = filename
        except Exception as e:
            raise Exception(_("Cannot write to {}\n{}").format(filename,e))


if __name__ == "__main__":
    f = fstab('./fstab')
    f.read()
    f.entries[0].devtype = 'Device'
    f.entries[0].dev = '/dev/sda9'
    f.entries[0].setModified()
    if False:
        for i in range(15):
            e = f.searchEntryLineNo(i+1)
            if e:
                print('{} = {}, {}'.format(e.dev,e.line,e.modified))
    f.write()