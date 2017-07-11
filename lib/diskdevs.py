#!/usr/bin/env python3
# Get and list filesystems 
# 
# This only works on linux systems with procfs mounted. 
#
# Uses /proc/partitions and /dev/disk/by-{uuid,label} to build the devs 
# dictionary. 
#
# Run from a command-line, this script will list all partitions and uuid 
# and/or labels if set without being root. 
#
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

#
# A lot of this functionality duplicates what the shell command blkid does and will 
# attempt to use the output of blkid before probing /dev and /proc to get this information

import os, sys, re, glob, subprocess, shlex

class devices:
    '''
    Class to query partition and filesystem information using various attributes.

    Build and query a dictionary of disk partitions listing attributes such
    as uuid, label, partuuid, partlabel. 

    Partitions can be queried by each of these as well as the device node itself.
    lists of devices, labels, and uuids can be obtained for partitions or 
    filesystems to use to query with by<attribute>
    a rescan method is provided for getting new data if the device list changes
    dynamically. 
    '''

    def __init__(self):
        self.partitions = {}
        self.rescan()

    #
    # This is kind of a hack. I need a binding for libblkid that can give me all this information
    # that is also documented.
    #
    def __parseBlkId(self):
        '''
        Attempt to return a partitions dict by parsing the output of blkid(8)
        '''
        partitions = {}
        for x in subprocess.getoutput('blkid 2>/dev/null').split('\n'):
            dev,info = x.split(':')
            partitions[dev] = {"device":dev}
            fields = shlex.split(info.strip())
            for f in fields:
                k,v = f.split('=')
                k = k.lower()
                partitions[dev][k] = v
        if len(list(partitions.keys())):
            return partitions
        return None

    def rescan(self):
        ''' 
            Rescan for partitions. This will update any added or removed since first run. 
        '''
        p = self.__parseBlkId()
        if p:
            self.partitions = p
            return
        self.partitions = {}
        for l in open('/proc/partitions').read().split('\n')[1:]: # Get all but first line
            l = l.strip()
            if l == '':
                continue
            maj,minor,blocks,dev = re.split("\s+",l)
            if minor != '0' and re.search(r'[0-9]',dev):
                dev = '/dev/{}'.format(dev)
                ptype = None
                self.partitions[dev] = {'device':dev}

        for d in glob.glob('/dev/disk/by-uuid/*'):
            dev = os.path.realpath(d)
            self.partitions[dev]['uuid'] = os.path.basename(d)

        for d in glob.glob('/dev/disk/by-label/*'):
            dev = os.path.realpath(d)
            self.partitions[dev]['label'] = os.path.basename(d)

        for d in glob.glob('/dev/disk/by-partlabel/*'):
            dev = os.path.realpath(d)
            d = d.replace('/dev/disk/by-partlabel','').decode('string-escape').decode('string-escape')
            self.partitions[dev]['partlabel'] = os.path.basename(d)

        for d in glob.glob('/dev/disk/by-partuuid/*'):
            dev = os.path.realpath(d)
            self.partitions[dev]['partuuid'] = os.path.basename(d)

    def byDevice(self,device):
        ''' Return partition dictionary for given device name. e.g: /dev/sda1 
            or None if not found.
        '''
        for d in list(self.partitions.keys()):
            if 'device' in list(self.partitions[d].keys()):
                if self.partitions[d]['device'] == device:
                    return self.partitions[d]
        return None

    def allDevices(self):
        ''' Return a list strings of all device nodes '''
        return list(self.partitions.keys())

    def byUUID(self,uuid):
        ''' Return partition dictionary for given filesystem UUID 
            or None if not found.
        '''
       
        for d in list(self.partitions.keys()):
            if 'uuid' in list(self.partitions[d].keys()):
                if self.partitions[d]['uuid'] == uuid:
                    return self.partitions[d]
        return None

    def allUUIDs(self):
        ''' Return a list of strings of all filesystem UUIDs or None if none exist. '''
        uuids = []
        for d,p in list(self.partitions.items()):
            if 'uuid' in list(p.keys()):
                uuids.append(p['uuid'])
        if len(uuids):
            return uuids
        return None

    def byPartUUID(self,uuid):
        ''' Return partition dictionary for given partition UUID 
            or None if not found.
        '''
        for d in list(self.partitions.keys()):
            if 'partuuid' in list(self.partitions[d].keys()):
                if self.partitions[d]['partuuid'] == uuid:
                    return self.partitions[d]
        return None

    def allPartUUIDs(self):
        ''' Return a list of strings of all partition UUIDs or None if none exist. '''
        uuids = []
        for d,p in list(self.partitions.items()):
            if 'partuuid' in list(p.keys()):
                uuids.append(p['partuuid'])
        if len(uuids):
            return uuids
        return None

    def byLabel(self,label):
        ''' Return partition dictionary for given filesystem label
            or None if not found.
        '''
        for d in list(self.partitions.keys()):
            if 'label' in list(self.partitions[d].keys()):
                if self.partitions[d]['label'] == label:
                    return self.partitions[d]
        return None

    def allLabels(self):
        ''' Return a list of strings of all filesystem labels or None if none exist. '''
        labels = []
        for d,p in list(self.partitions.items()):
            if 'label' in list(p.keys()):
                labels.append(p['label'])
        if len(labels):
            return labels
        return None

    def byPartLabel(self,label):
        ''' Return partition dictionary for given partition label
            or None if not found.
        '''
        for d in list(self.partitions.keys()):
            if 'partlabel' in list(self.partitions[d].keys()):
                if self.partitions[d]['partlabel'] == label:
                    return self.partitions[d]
        return None

    def allPartLabels(self):
        ''' Return a list of strings of all partition labels or None if none exist. '''
        labels = []
        for d,p in list(self.partitions.items()):
            if 'partlabel' in list(p.keys()):
                labels.append(p['partlabel'])
        if len(labels):
            return labels
        return None

if __name__ == "__main__":
    # flimsy command-line processing 

    arg = None
    dev = devices()
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == '--showall':
            arg = 'all'
        else: #sys.argv[1] == '--help' or sys.argv[1] == '-h':
            print('{0} usage: {0} [--showall]'.format(os.path.basename(sys.argv[0])))
            sys.exit(0)
    def show(what=None):
        '''
            Show all partitions defined on the system, 'all' shows as much info as is defined.
        '''
        if what and what == 'all':
            partkeys = ['uuid','label','partuuid','partlabel','type']
        else:
            partkeys = ['uuid','label','type']
        devKeys = list(dev.partitions.keys())
        devKeys.sort()
        for d in devKeys:
            part = dev.partitions[d]
            linedata = ['{}:'.format(d)]
            for k in partkeys:
                if k in list(part.keys()):
                    linedata.append('{}="{}"'.format(k.upper(),part[k]))
            print(' '.join(linedata))
    show(arg)
