from argparse import ArgumentParser
import os
import sys

import re
import requests
from bs4 import BeautifulSoup
import glob

sys.path.append(os.path.abspath('../common'))
from cdd import convert_darknettxt_dataset
from rmminimg import rmminimg
from difPy import dif
from df  import df

import inference

global opts
opts = {}

def parseOptions():
    argparser = ArgumentParser()
    argparser.add_argument('--dwn',  help=':generate download script', action='store_true') # use action='store_true' as flag
    argparser.add_argument('--snm',  help=':specify number of start page') # use action='store_true' as flag
    argparser.add_argument('--psz',  help=':specify number of page size') # use action='store_true' as flag
    argparser.add_argument('--lim',  help=':specify number of image on each name') # use action='store_true' as flag
    argparser.add_argument('--conv', help=':convert image files', action='store_true') # use action='store_true' as flag
    argparser.add_argument('--gentxt', help=':mode to gen bbox txt', action='store_true') # use action='store_true' as flag
    args = argparser.parse_args()
    if args.dwn: opts.update({'dwn':args.dwn})
    if args.snm:  opts.update({'snm':args.snm})
    else: opts.update({'snm':1})   
    if args.psz:  opts.update({'psz':args.psz})
    else: opts.update({'psz':10})   
    if args.lim:  opts.update({'lim':args.lim})
    else: opts.update({'lim':10})   
    if args.conv: opts.update({'conv':args.conv})
    if args.gentxt: opts.update({'gentxt':args.gentxt})

if __name__ == '__main__':
    parseOptions()
    start_num = int(opts['snm'])
    page_size = int(opts['psz'])
    lim = int(opts['lim'])

    imgsubdir = 'images'

    if (opts.get('dwn')):
        if os.path.isfile('site.txt'):
            names = []

            urlSiteAry = convert_darknettxt_dataset.csvread('site.txt')
            for site_idx in range(len(urlSiteAry)):
                urlSite = urlSiteAry[site_idx][0]
                for i in range(page_size):
                    try:
                        idx = str(start_num + i)
                        urlName = f"{urlSite}/{idx}/"
                        print(f"loading : {urlName} ...")
                        url = requests.get(urlName)
                        soup = BeautifulSoup(url.content, 'html.parser')

                        if (re.search(r'top-rated', urlSite)):
                            uls = soup.find_all('ul', class_='gallery-a a d')
                            if (not len(uls)): raise Exception
                            for ul in uls:
                                lis = ul.find_all('li')
                                if (not len(lis)): raise Exception
                                for li in lis:
                                    spans = li.find_all('span')
                                    if (not len(spans)): raise Exception
                                    name = spans[0].text
                                    # print(name)
                                    names.append(name)
                        if (re.search(r'latest-updates', urlSite)):
                            uls = soup.find_all('ul', class_='gallery-a e')
                            if (not len(uls)): raise Exception
                            for ul in uls:
                                lis = ul.find_all('li')
                                if (not len(lis)): raise Exception
                                for li in lis:
                                    tas = li.find_all('a')
                                    if (not len(tas)): raise Exception
                                    name = tas[1].text
                                    # print(name)
                                    names.append(name)
                    except Exception:
                        pass
        else:
            names = ['cat', 'dog']

        exe = 'python ~/rep/yolo_by_ods/common/gid/gid.py'
        KeywordAry = convert_darknettxt_dataset.csvread('kwd.txt')
        names = list(dict.fromkeys(names))
        names.sort()

        dst_dir = f'./{imgsubdir}'
        if not os.path.isdir(dst_dir):
            os.makedirs(dst_dir)
        downcsh = f'{dst_dir}/down.sh'
        ofs = open(downcsh, mode='w')
        ofs.write(f"#!/usr/bin/env bash\n")
        knd = f"%s %s %s" % (KeywordAry[1][0], KeywordAry[1][1], KeywordAry[1][2])
        ofs.write(f"kind='{knd}'\n")
        ofs.write(f"limit='{lim}'\n")
        for name in names:
            tgt = f"%s {name}" % (KeywordAry[0][0])
            ofs.write(f"{exe} --tgt '{tgt}' --knd \"${{kind}}\" --lim \"${{limit}}\"\n")
        ofs.close()

    if (opts.get('conv')):
        rmminimg.rm_min_img(imgsubdir)
        rmminimg.cp_img(imgsubdir)
        inference.main(imgsubdir, opts.get('gentxt'))
        rmminimg.drop_empty_folders(imgsubdir)
        rmminimg.drop_empty_folders(imgsubdir)

        # dif(imgsubdir, delete=True)
        df.img(imgsubdir)
        df.prt()
        df.mvp()
        df.clr()
