Cross-platform Python 2/3 library to dump and restore
binary data to and from hex form.

Placed into public domain
by anatoly techtonik <tectonik@gmail.com>


01 - dump binary data string
============================

Python 2

   >>> import hexdump
   >>> hexdump.hexdump('\x00'*16)
   0000000000: 00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  ................

Python 3

   >>> import hexdump
   >>> hexdump.hexdump('\x00'*16)
   ...
   TypeError: Abstract unicode data (expected bytes)
   >>> hexdump.hexdump(b'\x00'*16)
   0000000000: 00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  ................
 
   Python 3 strings are arrays of abstract indexes in unicode
   table. Single index is an integer which takes more than one
   byte when stored, so you need to specify exactly how to store
   these bytes with encoding.


02 - restore binary data from hex dump string
==============================================

Python 2

   >>> import hexdump
   >>> res = hexdump.restore(
   ... '0000000010: 00 11 22 33 44 55 66 77  88 99 AA BB CC DD EE FF  .."3DUfw........')
   >>> res
   '\x00\x11"3DUfw\x88\x99\xaa\xbb\xcc\xdd\xee\xff'
   >>> type(res)
   <type 'str'>

Python 3

   >>> import hexdump
   >>> res = hexdump.restore(
   ... '0000000010: 00 11 22 33 44 55 66 77  88 99 AA BB CC DD EE FF  .."3DUfw........')
   >>> res
   b'\x00\x11"3DUfw\x88\x99\xaa\xbb\xcc\xdd\xee\xff'
   >>> type(res)
   <class 'bytes'>


---[release checklist]---

| [ ] update version in hexedit.py
| [ ] update ChangeLog in setup.py from hexedit.py
| [ ] python setup.py register sdist upload

