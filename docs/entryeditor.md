|[TOC](index.md)|[Overview](overview.md)|[Main Window](main.md)|[Entry Editor](entryeditor.md)|[License](license.md)|[About](about.md)|[README](README.md)
-----------------------
# Entry Editor
## Overview
For each filesystem there is an entry in [fstab(5)](http://man7.org/linux/man-pages/man5/fstab.5.html). There are six fields for each entry: node, mount point, filesystem type, file system options, fs freq, and fspassno. I have added another virtual field, *Device Type*

Device type is determined by how the entry is formatted. For example, if an entry's node is 
LABEL=foo, the *Device Type* *will be LABEL. This helps other widgets in the editor to find 
partitions using those types of values. Of course, certain filesystems may fall outside 
of those defintions, and, in those cases as free-form entry is provided. 

## Device Types

* *Device*:
Use a system device, such as /dev/sda1. The program locates all device candidates by looking in */proc/partitions*
* *UUID*:
    Use a partition specified by the filesystem's UUID. This the most persistent way of referring to a filesystem since the UUID of the filesystem is not likely to change unless re-created. Even if the physical device number changes the UUID will still match. Filesystem UUID formats are dependent on the filesystem format. 

* *PARTUUID*:
    Use a partition specified by the partition's UUID. Much like UUID, but, in unusual situations an existing filesystem image may be written to a new partition changing the partition UUID. This only makes sense with gpt partition tables.

* *LABEL*:
    Much like UUID the label is tied to the filesystem. It may not, however be unique (but should be). The way a label is set in the filesystem is dependent on the filesystem format. 

* *PARTLABEL*:
    Again, like LABEL this is a label assigned to the partition. This only make sense with gpt partition tables.

* *File*:
    A filename to be used for a filesystem. This file can be selected with the normal Gtk file selection widgets. 
    
* *Path*:
    A free-form entry. This will be set if the parition's node does not match any of the above. An example of a *Path* *device type would be for a SSH filesystem (sshfs) where you specify node:path. 

When the filesystem entry is written, only UUID,PARTUUID,LABEL,PARTLABEL are used in the node section. Otherwise, just the node without the device type is used. 

# Form fields.
## *Device Type*
The *Device Type* field allows you to select a one of the above device types. For device types of UUID,PARTUUID,LABEL.PARTLABEL or Device, the program attempts to find the appropriate entry for the in the *Node* field for same device, so if you have /dev/sda1 with a UUID of abcd134-a3253fs-352dsvdv and you switch from Device to UUID, then abcd134-a3253fs-352dsvdv will now be selected in the *Node* field. The entries in the *Node* field, now, all be the known filesytem UUID's on the system. 

## *Node*
The contents of the node field are populated based on the selection in the *Device Type* field. Not all systems will have any or all of these. These values are probed from the system iteself.
The *Node* field gets populated, by device type, as follows:

* Device - All known disk partitions on the system, from /proc/partitions.
* UUID - All known filesystem UUID's on the system, from /dev/disk/by-uuid.
* LABEL - All known filesystem labels on the system, from /dev/disk/by-label.
* PARTUUID - All known partition UUID's on the system, from /dev/disk/by-partuuid. 
* PARTLABEL - All known partition labels on the system, from /dev/disk/by-partlabel. 
* File - A file selection widget is provided to open a file to be used as a filesystem-on-file. 
* Path - A free-form entry that is used verbatim. This is useful for remote filesystems, or, for specifying a device type that doesn't exist. Since this is not checked for format, be sure this field is correct. 

## Filesystem Type
The *Filesystem Type* field is populated from a few common fuse systems, swap, entries in /proc/fillesystems and looking in /lib/`uname -r`/kernel/fs/ for any filesystem modules. If the filesystem needed is not present, it may be specified by selecting "Other..." and entering it to the right. When changing the filesystem type, there is warning. Typically the probed value for the filesystem type should be used. 

## Filesystem Options and Common Options
The *Filesystem Options* field is a free-form entry field that specifies the options for the filesystem. Several common options are in the *Common Options* dropdown. When a common option is selected, and, is not already present in the options field, it will be appended to the options. 

## Dump Frequency
From the [fstab(5)](http://man7.org/linux/man-pages/man5/fstab.5.html) page: "This field is used by dump(8) to determine which filesystems need to be dumped." An entry of zero means this file system is ignored by dump(8)

## Check Pass
This field is used by [fsck(8)](http://man7.org/linux/man-pages/man8/fsck.8.html) to determine the order in which filesystem checks are done at boot time. The root filesystem should be specified with a fs_passno of 1.  Other filesystems should have a fs_passno of 2.  Filesystems within a drive will be checked sequentially, but filesystems on different drives will be checked at the same time to utilize paralelism available in the hardware.  Defaults to zero (don't fsck) if not present.

# Partitions Overview
Clicking the button will show an overview of all of the partitions probed and their associated metadata. 
