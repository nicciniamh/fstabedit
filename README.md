# Filesystem Table Editor For Linux

** *This program is very very alpha!!! BACK UP SYSTEM FILES FIRST!* **


When /etc/fstab is saved it will be backed up to /etc/fstab~ 

Worst case recovery is you have a backup file is boot from a live cd and mount your root filesystem. Replace the broken /etc/fstab with your backup. 

Please see docs in doc/

install.sh is a very basic, self-contained shell script installer.

The script, testenv.sh, creates a chroot environment for testing. This script mounts all system directories except etc so etc can be modified without breaking things.

To use this: 

1. Create a directory to use for testing. 
2. copy contents of /etc to test-dir/etc
3. copy testenv.sh to test-dir
4. run testenv.sh - this will log you into your chroot environment. Upon exit all the system directories mounted will be unmounted and the mount directories are removed.



