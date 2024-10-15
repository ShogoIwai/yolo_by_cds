from argparse import ArgumentParser
import os
import re
import shutil

global opts
opts = {}

def parseOptions():
    argparser = ArgumentParser()
    argparser.add_argument('--file', help=':specify replace file')
    argparser.add_argument('--pre',  help=':specify pre regular expression')
    argparser.add_argument('--post', help=':specify post regular expression')
    args = argparser.parse_args()
    if args.file: opts.update({'file':args.file})
    if args.pre: opts.update({'pre':args.pre})
    if args.post: opts.update({'post':args.post})

def replace():
    file_path = os.path.abspath(opts['file'])
    temp_file = file_path + '.tmp'
    match = 0
    ofs = open(temp_file, mode='w', encoding='utf-8')
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        pattern = '.*' + opts['pre'] + '.*'
        for line in file:
            if re.match(pattern, line):
                match = 1
            line = re.sub(opts['pre'], opts['post'], line)
            ofs.write(line)
    ofs.close()
    if match:
        shutil.copymode(file_path, temp_file)
        shutil.move(temp_file, file_path)
    else:
        os.remove(temp_file)
    
if __name__ == '__main__':
    parseOptions()
    if (opts.get('file') and opts.get('pre') and opts.get('post')):
        replace()
