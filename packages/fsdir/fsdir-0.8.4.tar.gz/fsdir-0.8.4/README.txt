To install it please do:
    python setup.py install
or:
    easy_install fsdir

This is a simple, but handy module,
do a recursive walk returning file and folder information. But with much better performance then os.walk.
For: OSX and Linux.


Current version 0.8.4
----
The 0.8.3 bring code clean up over the 0.8.2
And add the following improvements:
   fsdir.error fuction now return all the files and dirs that couldnt be process
   Inode of the files and dirs add the the output.


PS:This module calculate the size in disk not the size of the file.


== Usage:==
===fsdir.go(path='The path',summary=[True|False], crc32=[True|False])===
            #The true/false flag enable or disable the summary and crc32 mode


== Example: ==
=== Summary off, CRC32 off ===
{{{
>>>import fsdir
>>> fsdir.go(path=".")
[{'permGroup': 'rwx', 'permOwner': 'rwx', 'permOthers': 'r-x', 'Owner': 1000, 'Path': '.', 'Type': 'D', 'Size': 4}, {'permGroup': 'rwx', 'permOwner': 'rwx', 'permOthers': 'r-x', 'Owner': 1000, 'Path': './fsdir.so', 'Type': 'F', 'Size': 40}]
}}}

=== Summary off, CRC32 On ===
{{{
fsdir.go(path=".",crc32=True)
[{'permGroup': 'rwx', 'permOwner': 'rwx', 'permOthers': 'r-x', 'Owner': 1000, 'Path': '.', 'Type': 'D', 'Size': 4}, #Directory's never return CRC32 
{'permGroup': 'rwx', 'CRC32': 2117939917, 'permOwner': 'rwx', 'permOthers': 'r-x', 'Owner': 1000, 'Path': './fsdir.so', 'Type': 'F', 'Size': 40}]
}}}

=== Summary On. ===
{{{
>>>import fsdir
>>> fsdir.go(path=".",summary=True)#Summary is off by default.
[{'Dirs': 1, 'Files': 1, 'Size': 44}]
}}}


===== Files that are ignored, or Error out ======
fsdir.error()
Return a list with the path to the file and the error


Note: Permission always return 3 char string. 
"rwx" If the premession is active or  - if is not: 
Example a file just with read permission will be "r--"

=== where: ===
 {{{
*list[x]["permGroup"]=Permission to the Group
*list[x]["permOwner"]=Permission to the Owner  
*list[x]["permOthers"]=Permission to the Others
*list[x]["CRC32"]=CRC32 hash #If crc32 flag true
*list[x]["Owner"]=numeric id
*list[x]["Path"]=Full Path to the file/dir
*list[x]["Type"]=F|D (F=File, D=Directory)
*list[x]["Size"]=Size in Kilobytes
*list[x]["Inode"]=The inode of the file
}}}

