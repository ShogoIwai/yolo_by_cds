from argparse import ArgumentParser
import re
import shutil

global opts
opts = {}

def parseOptions():
    argparser = ArgumentParser()
    argparser.add_argument('--file', help=':specify replace file') # use action='store_true' as flag
    argparser.add_argument('--pre',  help=':specify pre regular expression') # use action='store_true' as flag
    argparser.add_argument('--post', help=':specify post regular expression') # use action='store_true' as flag
    args = argparser.parse_args()
    if args.file: opts.update({'file':args.file})
    if args.pre: opts.update({'pre':args.pre})
    if args.post: opts.update({'post':args.post})

def replace():
    infile = opts['file']
    match = 0
    with open(infile, 'r') as file:
        for line in file:
            pattern = '.*' + opts['pre'] + '.*'
            match = re.match(pattern, line)
            if (match):
                break

    if (match):
        outfile = opts['file'] + '.tmp'
        ofs = open(outfile, mode='w')
        with open(infile, 'r') as file:
            for line in file:
                line = re.sub(opts['pre'], opts['post'], line)
                ofs.write(line)
        ofs.close()
        shutil.copymode(infile, outfile)
        shutil.move(outfile, infile)

if __name__ == '__main__':
    parseOptions()
    if (opts.get('file') and opts.get('pre') and opts.get('post')):
        replace()
