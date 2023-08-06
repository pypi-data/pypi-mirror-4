python-oletools
===============

`python-oletools <http://www.decalage.info/python/oletools>`_ is a
package of python tools to analyze `Microsoft OLE2 files (also called
Structured Storage, Compound File Binary Format or Compound Document
File
Format) <http://en.wikipedia.org/wiki/Compound_File_Binary_Format>`_,
such as Microsoft Office documents or Outlook messages, mainly for
malware analysis and debugging. It is based on the
`OleFileIO\_PL <http://www.decalage.info/python/olefileio>`_ parser. See
`http://www.decalage.info/python/oletools <http://www.decalage.info/python/oletools>`_
for more info.

Note: python-oletools is not related to OLETools published by BeCubed
Software.

Tools in python-oletools:
-------------------------

-  **olebrowse**: A simple GUI to browse OLE files (e.g. MS Word, Excel,
   Powerpoint documents), to view and extract individual data streams.
-  **oleid**: a tool to analyze OLE files to detect specific
   characteristics that could potentially indicate that the file is
   suspicious or malicious.
-  **pyxswf**: a tool to detect, extract and analyze Flash objects (SWF)
   that may be embedded in files such as MS Office documents (e.g. Word,
   Excel) and RTF, which is especially useful for malware analysis.
-  **rtfobj**: a tool and python module to extract embedded objects from
   RTF files.
-  and a few others (coming soon)

News
----

-  2013-04-18 v0.04: fixed bug in rtfobj, added documentation for rtfobj
-  2012-11-09 v0.03: Improved pyxswf to extract Flash objects from RTF
-  2012-10-29 v0.02: Added oleid
-  2012-10-09 v0.01: Initial version of olebrowse and pyxswf
-  see changelog in source code for more info.

Download:
---------

The archive is available on `the project
page <https://bitbucket.org/decalage/oletools/downloads>`_.

olebrowse:
----------

A simple GUI to browse OLE files (e.g. MS Word, Excel, Powerpoint
documents), to view and extract individual data streams.

::

    Usage: olebrowse.py [file]

If you provide a file it will be opened, else a dialog will allow you to
browse folders to open a file. Then if it is a valid OLE file, the list
of data streams will be displayed. You can select a stream, and then
either view its content in a builtin hexadecimal viewer, or save it to a
file for further analysis.

For screenshots and other info, see
`http://www.decalage.info/python/olebrowse <http://www.decalage.info/python/olebrowse>`_

oleid:
------

oleid is a script to analyze OLE files such as MS Office documents (e.g.
Word, Excel), to detect specific characteristics that could potentially
indicate that the file is suspicious or malicious, in terms of security
(e.g. malware). For example it can detect VBA macros, embedded Flash
objects, fragmentation.

::

    Usage: oleid.py <file>

Example - analyzing a Word document containing a Flash object and VBA
macros:

::

    C:\oletools>oleid.py word_flash_vba.doc
    Filename: word_flash_vba.doc
    OLE format: True
    Has SummaryInformation stream: True
    Application name: Microsoft Office Word
    Encrypted: False
    Word Document: True
    VBA Macros: True
    Excel Workbook: False
    PowerPoint Presentation: False
    Visio Drawing: False
    ObjectPool: True
    Flash objects: 1

oleid project website:
`http://www.decalage.info/python/oleid <http://www.decalage.info/python/oleid>`_

pyxswf:
-------

pyxswf is a script to detect, extract and analyze Flash objects (SWF
files) that may be embedded in files such as MS Office documents (e.g.
Word, Excel), which is especially useful for malware analysis.

pyxswf is an extension to
`xxxswf.py <http://hooked-on-mnemonics.blogspot.nl/2011/12/xxxswfpy.html>`_
published by Alexander Hanel.

Compared to xxxswf, it can extract streams from MS Office documents by
parsing their OLE structure properly, which is necessary when streams
are fragmented. Stream fragmentation is a known obfuscation technique,
as explained on
`http://www.breakingpointsystems.com/resources/blog/evasion-with-ole2-fragmentation/ <http://www.breakingpointsystems.com/resources/blog/evasion-with-ole2-fragmentation/>`_

It can also extract Flash objects from RTF documents, by parsing
embedded objects encoded in hexadecimal format (-f option).

For this, simply add the -o option to work on OLE streams rather than
raw files, or the -f option to work on RTF files.

::

    Usage: pyxswf.py [options] <file.bad>

    Options:
      -o, --ole             Parse an OLE file (e.g. Word, Excel) to look for SWF
                            in each stream
      -f, --rtf             Parse an RTF file to look for SWF in each embedded
                            object
      -x, --extract         Extracts the embedded SWF(s), names it MD5HASH.swf &
                            saves it in the working dir. No addition args needed
      -h, --help            show this help message and exit
      -y, --yara            Scans the SWF(s) with yara. If the SWF(s) is
                            compressed it will be deflated. No addition args
                            needed
      -s, --md5scan         Scans the SWF(s) for MD5 signatures. Please see func
                            checkMD5 to define hashes. No addition args needed
      -H, --header          Displays the SWFs file header. No addition args needed
      -d, --decompress      Deflates compressed SWFS(s)
      -r PATH, --recdir=PATH
                            Will recursively scan a directory for files that
                            contain SWFs. Must provide path in quotes
      -c, --compress        Compresses the SWF using Zlib

Example 1 - detecting and extracting a SWF file from a Word document on
Windows:

::

    C:\oletools>pyxswf.py -o word_flash.doc
    OLE stream: 'Contents'
    [SUMMARY] 1 SWF(s) in MD5:993664cc86f60d52d671b6610813cfd1:Contents
            [ADDR] SWF 1 at 0x8  - FWS Header

    C:\oletools>pyxswf.py -xo word_flash.doc
    OLE stream: 'Contents'
    [SUMMARY] 1 SWF(s) in MD5:993664cc86f60d52d671b6610813cfd1:Contents
            [ADDR] SWF 1 at 0x8  - FWS Header
                    [FILE] Carved SWF MD5: 2498e9c0701dc0e461ab4358f9102bc5.swf

Example 2 - detecting and extracting a SWF file from a RTF document on
Windows:

::

    C:\oletools>pyxswf.py -xf "rtf_flash.rtf"
    RTF embedded object size 1498557 at index 000036DD
    [SUMMARY] 1 SWF(s) in MD5:46a110548007e04f4043785ac4184558:RTF_embedded_object_0
    00036DD
            [ADDR] SWF 1 at 0xc40  - FWS Header
                    [FILE] Carved SWF MD5: 2498e9c0701dc0e461ab4358f9102bc5.swf

For more info, see
`http://www.decalage.info/python/pyxswf <http://www.decalage.info/python/pyxswf>`_

rtfobj
------

rtfobj is a Python module to extract embedded objects from RTF files,
such as OLE ojects. It can be used as a Python library or a command-line
tool.

::

    Usage: rtfobj.py <file.rtf>

It extracts and decodes all the data blocks encoded as hexadecimal in
the RTF document, and saves them as files named "object\_xxxx.bin", xxxx
being the location of the object in the RTF file.

Usage as python module: rtf\_iter\_objects(filename) is an iterator
which yields a tuple (index, object) providing the index of each
hexadecimal stream in the RTF file, and the corresponding decoded
object. Example:

::

    import rtfobj    
    for index, data in rtfobj.rtf_iter_objects("myfile.rtf"):
        print 'found object size %d at index %08X' % (len(data), index)

For more info, see
`http://www.decalage.info/python/rtfobj <http://www.decalage.info/python/rtfobj>`_

How to contribute:
------------------

The code is available in `a Mercurial repository on
bitbucket <https://bitbucket.org/decalage/oletools>`_. You may use it to
submit enhancements or to report any issue.

If you would like to help us improve this module, or simply provide
feedback, you may also send an e-mail to decalage(at)laposte.net.

How to report bugs:
-------------------

To report a bug or any issue, please use the `issue reporting
page <https://bitbucket.org/decalage/olefileio_pl/issues?status=new&status=open>`_,
or send an e-mail with all the information and files to reproduce the
problem.

License
-------

This license applies to the python-oletools package, apart from the
thirdparty folder which contains third-party files published with their
own license.

The python-oletools package is copyright (c) 2012-2013, Philippe Lagadec
(http://www.decalage.info) All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

-  Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
-  Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
