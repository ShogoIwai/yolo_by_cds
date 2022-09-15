from argparse import ArgumentParser
import os
import sys

import shutil
import re
import zipfile

from pathlib import Path

global opts
opts = {}

def parseOptions():
    argparser = ArgumentParser()
    argparser.add_argument('--dwn', help=':downloaling data set', action='store_true') # use action='store_true' as flag
    argparser.add_argument('--zip', help=':extract zip file and move to images', action='store_true') # use action='store_true' as flag
    args = argparser.parse_args()
    if args.dwn: opts.update({'dwn':args.dwn})
    if args.zip: opts.update({'zip':args.zip})

if __name__ == '__main__':
    parseOptions()
    dataset = 'kagglecatsanddogs_5340.zip'

    if (opts.get('dwn')):
        os.system(f"curl -LO https://download.microsoft.com/download/3/E/1/3E1C3F21-ECDB-4869-8368-6DEBA77B919F/{dataset}")

    if (opts.get('zip')):
        org_dir = './PetImages'
        dst_dir = './images'

        if os.path.isdir(org_dir):
            shutil.rmtree(org_dir)
        if os.path.isdir(dst_dir):
            shutil.rmtree(dst_dir)

        with zipfile.ZipFile(f"./{dataset}") as existing_zip:
            existing_zip.extractall('./')
        os.remove('./CDLA-Permissive-2.0.pdf')
        os.remove('./readme[1].txt')
        os.makedirs(dst_dir)

        p = Path(org_dir)
        image_ary = list(p.glob("**/*.jpg"))
        for image in image_ary:
            m = re.findall('PetImages\/(\w+)\/(\d+)\.jpg', str(image))
            if m[0]:
                cat = m[0][0]
                num = int(m[0][1])
                dst_file = '%s/%s%08d.jpg' % (dst_dir, cat, num)
                print('mv %s to %s' % (image, dst_file))
                shutil.move(image, dst_file)

        if os.path.isdir(org_dir):
            shutil.rmtree(org_dir)
