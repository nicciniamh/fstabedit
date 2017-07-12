#!/bin/bash
#
# This script creates a chroot environment that looks like your normal login process. 
# For testing purposes /etc is not added. This directory must be copied to your test dir. 
# 
# Simple process to do this: 
# cd <test-environment-dir> ; tar cf - /etc | tar xf -
# 
# Place this script in <test-environment> and run with bash testenv.sh as your user.
#
if [ ! "$1" == "doit" ] ; then
    user=$(whoami)
    groups=$(id -G | sed 's/ /,/g')
    echo "This program must be run as the super-user. If prompted, please enter YOUR password" 
    exec sudo bash $0 doit $user $groups
    exit
fi
user=$2
groups=$3
#export DISPLAY=:0
sysdirs_pre="srv proc boot dev root sbin usr var run home lib opt bin lib64 sys lib32 tmp"
sysdirs_post="dev/ptmx dev/pts/"
userdirs="$(echo $HOME | sed -e 's/^\///g')"
for d in $sysdirs_pre ; do
    mkdir -p $d
    mount --bind /$d ./$d
done
for d in  $sysdirs_post ; do 
    mkdir -p $d 2>/dev/null
    mount --bind /$d ./$d
done
for d in  $userdirs; do
    mkdir -p $d
    mount --bind /$d ./$d
done
#echo chroot --userspec=$user:$user --groups=$groups . /bin/bash --login
chroot --userspec=$user:$user --groups=$groups . /bin/bash --login
for d in $userdirs ; do
    umount $d
done
for d in $sysdirs_post ; do
    umount $d
done
for d in $sysdirs_pre ; do
    umount $d
    rmdir $d
done
