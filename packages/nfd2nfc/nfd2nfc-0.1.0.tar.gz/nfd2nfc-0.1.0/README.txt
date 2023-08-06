=============================================
Convert NFD unicode filesystem to NFC unicode
=============================================

This tool can convert file system encoded in NFD mode to NFC mode.

On Mac OS X, the filesystem encode file name in NFD unicode 
(http://en.wikipedia.org/wiki/Unicode_normalization#Example).
On GNU/Linux, by default the filesystem encode file name in NFC unicode
but it can also contain file encoded in NFD mode.
You can use this tool to convert NFD to NFC.


Install
=======

::

    $ pip install https://bitbucket.org/harobed/convert-nfd-unicode-filesystem-to-nfc-unicode/downloads/nfd2nfc-0.1.0.tar.gz


Usage
=====

::

    $ nfd2nfc -h
    This tool can convert file system encoded in NFD mode to NFC mode.

    Usage:
      nfd2nfc <path>
      nfd2nfc <url>
      nfd2nfc -h | --help | --version



Examples
========

Convert on local file system (use it on GNU/Linux, not on Mac OS X) :

::

    $ nfd2nfc /home/username/myproject/

You can use ssh url syntax to fix unicode on remote host :

::

    $ nfd2nfc ssh://foobar@example.com:2000:/home/foobar/www/

Home page : https://bitbucket.org/harobed/convert-nfd-unicode-filesystem-to-nfc-unicode
Contact : contact@stephane-klein.info
