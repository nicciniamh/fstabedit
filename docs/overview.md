# Overview
The Linux/Unix Filesystem Table (/etc/fstab) is a file with deep roots in the UNIX legacy from a time when things needed to be terse so as not to consume space or memory, be fast to parse. Because of this, the format can seem a bit arcane. This leaves these entries prone to error. The use of this file and format dates back to at lease UNIX System V,  dating back to 1973!

The goal of this program is to simplify the editing of this file and to prevent errors from typing mistakes or specifying the wrong options for a filesystem. 

For specifics on the format of /etc/fstab, please see the [manual page](http://man7.org/linux/man-pages/man5/fstab.5.html) for it.

When the file is read and written all lines with comments are preserved and the data are written to the file in the line order in which they were read.  

This program can be run by a normal user, however, to save changes to /etc/fstab, the effective user id of the program must be the super user. This can be accomplished via sudo or gksudo. 

[Next - Main Window](main.md)
