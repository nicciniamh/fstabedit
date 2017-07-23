[//]:NAV
# Main Window
In the main window for the filesystem table editor ([fstabedit](https://github.com/nicciniamh/fstabedit)) you can select and edit each fstab entry. The main window shows an overview of each entry, sparing some details for the [entry editor](entryeditor.md)

When an entry is modified it is noted with an asterisk in the window title and the Save menu option is enabled. The Save-As menu option is always available to allow for saving the file to another location. 

When the program is started by a normal user, a warning is issued stating the /etc/fstab file may not be writable. You may choose to continue or exit. 

## File Menu Entries

### New Filesystem
Create a new filesystem entry in the [entry editor](entryeditor.md)

### New File
Create a new, blank file.

### Open
Open an existing file in the format of [fstab(5)](http://man7.org/linux/man-pages/man5/fstab.5.html)

### Save
Save the current file. This option is disabled if there have been no modifications.

### Save As
Save the current file to a new location.

### Quit
Quit the application.

