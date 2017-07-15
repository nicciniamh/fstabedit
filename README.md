Filesystem Table Editor
-----------------------
This program is very very alpha!!! 

BACK UP SYSTEM FILES FIRST! 


When /etc/fstab is saved it will be backed up to /etc/fstab~ 

Worst case recovery is you have a backup file is boot from a live cd and mount your root filesystem. Replace the broken /etc/fstab with your backup.

# Testing
In order to aid with testing, without destroying your system files, I have created a shell script that builds a chroot enviornment underwhich to perform testing. All system directories are included except /etc. 

Create a directory to test in, then duplicate your /etc directory with:

    cd <test-environment-dir> ; tar cf - /etc | tar xf -

then run:

    bash <path-to-script>/testenv.sh

You may be prompted for your password when sudo(8) is run. 


# Acknowldgements
This application was developed extensive use of Google, Stack Exchange for help and inspiration. Coding was done using Sublime Text, on Linux Mint 18.2 Sonya. 
Props to my family for hearing me swear at code and dive so deep into coding I ingore everying else. 
