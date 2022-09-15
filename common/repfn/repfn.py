from argparse import ArgumentParser
import pathlib
import re
import shutil
import os

global opts
global ext
opts = {}
ext = r'(\.jpg|\.png)$'

def parseOptions():
    argparser = ArgumentParser()
    argparser.add_argument('--src', help=':specify source path') # use action='store_true' as flag
    argparser.add_argument('--wrk', help=':specify work path') # use action='store_true' as flag
    argparser.add_argument('--exe', help=':rename execution', action='store_true') # use action='store_true' as flag
    args = argparser.parse_args()
    if args.src: opts.update({'src':args.src})
    if args.wrk: opts.update({'wrk':args.wrk})
    if args.exe: opts.update({'exe':args.exe})

def replace():
    srcpath = pathlib.Path(opts['src'])
    wrkpath = pathlib.Path(opts['wrk'])

    files = os.listdir(srcpath.resolve())
    files.sort()
    index = 1
    for fn in files:
        m = re.search(ext, fn)
        if (m):
            chgname = 'image' + str(index) + m.groups()[0]
            srcfile = f"{srcpath.resolve()}/{fn}"
            wrkfile = f"{wrkpath.resolve()}/{fn}"
            rnmfile = f"{srcpath.resolve()}/{chgname}"
            print(f"rename {srcfile} to {rnmfile}")
            if (opts.get('exe')):
                shutil.move(f"{srcfile}", f"{wrkfile}")
                shutil.copyfile(f"{wrkfile}", f"{rnmfile}")
            index = index + 1

if __name__ == '__main__':
    parseOptions()
    if (opts.get('src') and opts.get('wrk')):
        replace()
