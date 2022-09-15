from argparse import ArgumentParser
import os

global opts
opts = {}

def parseOptions():
    argparser = ArgumentParser()
    argparser.add_argument('--img', help=':specify picture directry to database') # use action='store_true' as flag
    argparser.add_argument('--prt', help=':only print duplicate pictures', action='store_true') # use action='store_true' as flag
    argparser.add_argument('--mvp', help=':move all found duplicate pictures to the trash', action='store_true') # use action='store_true' as flag
    argparser.add_argument('--shw', help=':show database', action='store_true') # use action='store_true' as flag
    argparser.add_argument('--clr', help=':clear database', action='store_true') # use action='store_true' as flag
    args = argparser.parse_args()
    if args.img: opts.update({'img':args.img})
    if args.prt: opts.update({'prt':args.prt})
    if args.mvp: opts.update({'mvp':args.mvp})
    if args.shw: opts.update({'shw':args.shw})
    if args.clr: opts.update({'clr':args.clr})

fp = os.path.dirname(os.path.abspath(__file__))
dfp = f"python {fp}/duplicate_finder.py"
db = f"~/.dfdb"

def img(dir):
    os.system(f"{dfp} add {dir} --db {db}")

def prt():
    os.system(f"{dfp} find --print --db {db}")

def mvp():
    os.system(f"{dfp} find --delete --db {db}")

def shw():
    os.system(f"{dfp} show --db {db}")

def clr():
    os.system(f"{dfp} clear --db {db}")

if __name__ == '__main__':
    parseOptions()
    if (opts.get('img')): img(opts['img'])
    if (opts.get('prt')): prt()
    if (opts.get('mvp')): mvp()
    if (opts.get('shw')): shw()
    if (opts.get('clr')): clr()
