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
    file = opts['file']
    temp_file = opts['file'] + '.tmp'
    match = 0
    ofs = open(temp_file, mode='w')
    with open(file, 'r') as file:
        pattern = '.*' + opts['pre'] + '.*'
        for line in file:
            if (re.match(pattern, line)): match = 1
            line = re.sub(opts['pre'], opts['post'], line)
            ofs.write(line)
    ofs.close()
    if (match):
        shutil.copymode(file, temp_file)
        shutil.move(temp_file, file)
    else:
        shutil.rmtree(temp_file)

if __name__ == '__main__':
    parseOptions()
    if (opts.get('file') and opts.get('pre') and opts.get('post')):
        replace()
