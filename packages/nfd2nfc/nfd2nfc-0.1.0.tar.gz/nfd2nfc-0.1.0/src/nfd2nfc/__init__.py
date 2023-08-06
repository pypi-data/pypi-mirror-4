import os
import sys
import unicodedata
from urlparse import urlparse

from docopt import docopt

__version__ = '0.1.0'

here = os.path.abspath(os.path.dirname(__file__))


def fix_unicode(path, verbose=True):
    for root, dirs, files in os.walk(unicode(path), topdown=False):
        for entry in files:
            nfc = unicodedata.normalize('NFC', entry)
            if entry != nfc:
                os.rename(
                    os.path.join(root, entry),
                    os.path.join(root, nfc))

                if verbose:
                    print os.path.join(root, nfc)

        rootparent, rootentry = os.path.split(root)
        nfc = unicodedata.normalize('NFC', rootentry)
        if rootentry != nfc:
            os.rename(root, os.path.join(rootparent, nfc))
            if verbose:
                print os.path.join(rootparent, nfc)

remote_cmd = """
import os
import sys
import unicodedata

def fix_unicode(path, verbose=True):
    for root, dirs, files in os.walk(unicode(path), topdown=False):
        for entry in files:
            nfc = unicodedata.normalize('NFC', entry)
            if entry != nfc:
                os.rename(
                    os.path.join(root, entry),
                    os.path.join(root, nfc))

                if verbose:
                    print os.path.join(root, nfc)

        rootparent, rootentry = os.path.split(root)
        nfc = unicodedata.normalize('NFC', rootentry)
        if rootentry != nfc:
            os.rename(root, os.path.join(rootparent, nfc))
            if verbose:
                print os.path.join(rootparent, nfc)

if __name__ == '__main__':
    fix_unicode('''%(path)s''', False)
"""


def main():
    arguments = docopt(
"""This tool can convert file system encoded in NFD mode to NFC mode.

On Mac OS X, the filesystem encode file name in NFD unicode
(http://en.wikipedia.org/wiki/Unicode_normalization#Example).
On GNU/Linux, by default the filesystem encode file name in NFC unicode
but it can also contain file encoded in NFD mode.
You can use this tool to convert NFD to NFC.

Usage:
  nfd2nfc <path>
  nfd2nfc <url>
  nfd2nfc -h | --help | --version

Examples :

Convert on local file system (use it on GNU/Linux, not on Mac OS X) :

    $ nfd2nfc /home/username/myproject/

You can use ssh url syntax to fix unicode on remote host :

    $ nfd2nfc ssh://foobar@example.com:2000:/home/foobar/www/

Home page : https://bitbucket.org/harobed/convert-nfd-unicode-filesystem-to-nfc-unicode
Contact : contact@stephane-klein.info
""",
        version=__version__
    )
    path = arguments['<path>']
    if path.startswith('ssh://'):
        url = urlparse(path)
        assert url.scheme == 'ssh'
        host = url.netloc
        port = 22
        user = os.getlogin()
        if ':' in host:
            host, port = host.split(':')

        if '@' in host:
            user, host = host.split('@')

        path_tmpfile = os.tempnam()
        basename_tmpfile = os.path.basename(path_tmpfile)  # NOQA
        f = open(path_tmpfile, 'w')
        f.write(remote_cmd % {'path': url.path})
        f.close()
        os.system('scp -P %(port)s %(path_tmpfile)s %(user)s@%(host)s:/tmp/' % locals())
        os.system('ssh -p %(port)s %(user)s@%(host)s python /tmp/%(basename_tmpfile)s' % locals())
        os.system('ssh -p %(port)s %(user)s@%(host)s rm /tmp/%(basename_tmpfile)s' % locals())
    else:
        if not os.path.exists(path):
            sys.exit('Error, folder not found %s' % path)

        fix_unicode(path)
