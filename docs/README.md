# Filesystem Table Editor
-----------------------
A system administration application for Linux that provides a GUI for editing the filesystem table in [/etc/fstab](http://man7.org/linux/man-pages/man5/fstab.5.html) that probes the system for all partitions by device, uuid, partition uuid, partition label and filesystem labels, known filesystem types, and presents controls based on the type of mount a person wants based on device, uuid, etc. making those entries easily editable. A drop down for common filesystem options makes adding some of the more common options a little easier.

This program is very linux specific. It might run on other *NIX systems but don't count on it and that mode of operation is unsupported.

See [program documentation](index.md) here.

# Requirements
**This is important!**

* bash 4 or higher, [base64(1)](http://man7.org/linux/man-pages/man1/base64.1.html) and bzip2 for the installer.
* Python 2.6 or higher
* GTK3 and python3-pygobject3 
* [blkid(8)](http://man7.org/linux/man-pages/man8/blkid.8.html)

# Testing

This code is very new and might break things! Before testing **BACK UP SYSTEM FILES FIRST!**

When /etc/fstab is saved it will be backed up to /etc/fstab~ 

Worst case recovery is you have a backup file is boot from a live cd and mount your root filesystem. Replace the broken /etc/fstab with your backup.

In order to aid with testing, without destroying your system files, I have created a shell script that builds a chroot enviornment underwhich to perform testing. All system directories are included except /etc. 

Create a directory to test in, then duplicate your /etc directory with:

    cd <test-environment-dir> ; tar cf - /etc | tar xf -

then run:

    bash <path-to-script>/testenv.sh

You may be prompted for your password when sudo(8) is run. 


# Acknowldgements
This application was developed extensive use of Google, Stack Exchange for help and inspiration. Coding was done using Sublime Text, on Linux Mint 18.2 Sonya. 
Props to my family for hearing me swear at code and dive so deep into coding I ingore everying else. 
