# -*- coding: utf-8 -*-
# pyzaa, reference implementation for PEP 441.
#
# Daniel Holth <dholth@gmail.com>

import argparse
import os.path
import stat
import sys
import zipfile

class TruncatingZipFile(zipfile.ZipFile):
    """ZipFile that can pop files off the end. This works for ordinary zip
    files that do not contain non-ZIP data interleaved between the compressed
    files."""

    def pop(self):
        """Truncate the last file off this zipfile."""
        if not self.fp:
            raise RuntimeError(
                  "Attempt to pop from ZIP archive that was already closed")
        last = self.infolist().pop()
        del self.NameToInfo[last.filename]
        self.fp.seek(last.header_offset, os.SEEK_SET)
        self.fp.truncate()
        self._didModify = True
            
def pack(filename, sources, python="/usr/bin/env python3", main=None):

    # addToZip copied from zipfile:
    def addToZip(zf, path, zippath):
        if os.path.isfile(path):
            zf.write(path, zippath)
        elif os.path.isdir(path):
            for nm in os.listdir(path):
                addToZip(zf,
                        os.path.join(path, nm), os.path.join(zippath, nm))
        # else: ignore
    
    with file(filename, "wb+") as archive:
        archive.write(("#!"+python).encode(sys.getfilesystemencoding()))
        archive.write("\n# This is a ZIP-archived Python application created with pyzaa.\n".encode('utf-8'))
        
        with zipfile.ZipFile(archive, "a", compression=zipfile.ZIP_DEFLATED) as zf:
            for source in sources:
                addToZip(zf, source, os.path.basename(source))
                
            if main:
                module, function = main.split(':')
                main_contents = ''.join([ '# __main__ written by pyzaa\n',
                                  'import {0}\n'.format(module),
                                  '{0}.{1}()'.format(module, function) ]).encode('utf-8')
                zf.writestr("__main__.py", main_contents)
                
    mode = os.stat(filename).st_mode
    os.chmod(filename, mode | stat.S_IEXEC)

def parser():
    p = argparse.ArgumentParser()
    s = p.add_subparsers(help="commands")
   
    def pack_f(args):
        pack(args.sources[0], args.sources[1:], python=args.python, main=args.main)
    pack_parser = s.add_parser('pack', help='ZIP the contents of directory as directory.pyz')
    pack_parser.add_argument('-m', '--main', help="module.name:function to call from __main__.py")
    pack_parser.add_argument('-p', '--python', help='Python interpreter (on #! line)',
                             default='/usr/bin/env python3')
    pack_parser.add_argument('sources', metavar = "src", nargs="+", help="Source files or directories.")
    pack_parser.set_defaults(func=pack_f)
   
    def help_f(args):
        p.print_help()
    help_parser = s.add_parser('help', help='Show this help')
    help_parser.set_defaults(func=help_f)

    return p

def main():
    p = parser()
    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
